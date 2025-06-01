import os
from datetime import datetime
import logging
from typing import List
from files.chunk import getChunks
from files.pdf import readPDF
from files.docx import readDOCX
from database.db import DB

class FileUploadError(Exception):
    """Базовое исключение для ошибок загрузки файлов"""
    pass


class UnsupportedFileTypeError(FileUploadError):
    """Неподдерживаемый тип файла"""

    def __init__(self, file_ext: str, allowed_extensions: List[str]):
        self.file_ext = file_ext
        self.allowed_extensions = allowed_extensions
        super().__init__(f"Unsupported file type: {file_ext}")


class FileTooLargeError(FileUploadError):
    """Файл слишком большого размера"""
    pass


class FileUploader:
    def __init__(self, bot, upload_folder='uploads', max_size_mb=10):
        self.bot = bot
        self.upload_folder = upload_folder
        self.max_size = max_size_mb * 1024 * 1024  # Конвертируем в байты
        self.allowed_extensions = ['.txt', '.pdf', '.docx']  # Разрешенные расширения
        self.logger = logging.getLogger(__name__)

        # Создаем папку для загрузок, если её нет
        os.makedirs(self.upload_folder, exist_ok=True)

    def get_supported_formats(self) -> str:
        """Возвращает строку с поддерживаемыми форматами"""
        return ", ".join(self.allowed_extensions)

    def handle_upload_command(self, message) -> None:
        """Обработчик команды /upload"""
        self.bot.reply_to(
            message,
            f"📤 Пожалуйста, отправьте файл для загрузки.\n"
            f"Поддерживаемые форматы: {self.get_supported_formats()}\n"
            f"Максимальный размер: {self.max_size // (1024 * 1024)} МБ"
        )

    def is_file_allowed(self, file_name: str) -> bool:
        """Проверяет, разрешено ли расширение файла"""
        return any(file_name.lower().endswith(ext) for ext in self.allowed_extensions)

    def validate_file(self, message) -> None:
        """Проверяет файл на соответствие требованиям"""
        file_name = message.document.file_name
        file_size = message.document.file_size

        if not self.is_file_allowed(file_name):
            raise UnsupportedFileTypeError(
                file_ext=os.path.splitext(file_name)[1],
                allowed_extensions=self.allowed_extensions
            )

        if file_size > self.max_size:
            raise FileTooLargeError(
                f"File size {file_size} exceeds maximum allowed {self.max_size}"
            )

    def save_chunks_to_file(self, chunks: List[str], file_path: str) -> None:
        """Сохраняет чанки в отдельные файлы (для удобства отладки)"""
        chunk_dir = os.path.join(os.path.dirname(file_path), "chunks")
        os.makedirs(chunk_dir, exist_ok=True)

        for i, chunk in enumerate(chunks, 1):
            chunk_file = os.path.join(chunk_dir, f"chunk_{i}.txt")
            with open(chunk_file, 'w', encoding='utf-8') as f:
                f.write(chunk)

    def handle_document(self, message) -> None:
        """Обработчик получения документа"""
        try:
            file_name = message.document.file_name
            self.validate_file(message)

            # Получаем файл с серверов Telegram
            file_info = self.bot.get_file(message.document.file_id)
            downloaded_file = self.bot.download_file(file_info.file_path)

            # Создаем папку для пользователя
            user_folder = os.path.join(self.upload_folder, str(message.chat.id))
            os.makedirs(user_folder, exist_ok=True)

            # Генерируем уникальное имя файла
            new_filename = f"{file_name}"
            file_path = os.path.join(user_folder, new_filename)

            # Сохраняем файл
            with open(file_path, 'wb') as new_file:
                new_file.write(downloaded_file)

            # Если файл текстовый (.txt) — разбиваем на чанки
            if file_name.lower().endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                    chunks = getChunks(text)  # Разбиваем на чанки по 2048 символов
                    DB.WriteChunks(message.chat.id, file_name, chunks)
            elif file_name.lower().endswith(".pdf"):
                text = readPDF(file_path)
                chunks = getChunks(text)  # Разбиваем на чанки по 2048 символов
                DB.WriteChunks(message.chat.id, file_name, chunks)
            elif file_name.lower().endswith(".docx"):
                text = readDOCX(file_path)
                chunks = getChunks(text)  # Разбиваем на чанки по 2048 символов
                DB.WriteChunks(message.chat.id, file_name, chunks)

            os.remove(file_path)

            self.bot.reply_to(message, f"✅ Файл '{file_name}' успешно сохранён и разбит на чанки")
            self.logger.info(f"User {message.chat.id} uploaded file: {file_path}")

        except UnsupportedFileTypeError as e:
            self.logger.warning(f"Unsupported file type: {e.file_ext}")
            self.bot.reply_to(
                message,
                f"❌ Формат {e.file_ext} не поддерживается.\n"
                f"Доступные форматы: {self.get_supported_formats()}\n"
                "Пожалуйста, используйте один из поддерживаемых форматов."
            )

        except FileTooLargeError:
            self.logger.warning(f"File too large: {message.document.file_size}")
            self.bot.reply_to(
                message,
                f"❌ Файл слишком большой. Максимальный размер: {self.max_size // (1024 * 1024)} МБ"
            )

        except Exception as e:
            self.logger.error(f"Unexpected error during file upload: {str(e)}", exc_info=True)
            self.bot.reply_to(
                message,
                "❌ Произошла непредвиденная ошибка при загрузке файла. "
                "Попробуйте ещё раз или обратитесь к администратору."
            )