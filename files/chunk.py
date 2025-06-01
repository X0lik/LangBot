"""
Читает текстовый файл и разбивает его на чанки не больше chunk_size символов.
Если чанк заканчивается не на пробел, функция откатывается до предыдущего пробела.
Возвращает список строк (чанков).
"""
def getChunks(text, chunk_size=2048):

    chunks = []
    start = 0
    length = len(text)

    while start < length:
        end = start + chunk_size
        if end >= length:
            chunks.append(text[start:])
            break
        if text[end] != ' ':
            space_pos = text.rfind(' ', start, end)
            if space_pos == -1 or space_pos <= start:
                chunks.append(text[start:end])
                start = end
            else:
                chunks.append(text[start:space_pos])
                start = space_pos + 1
        else:
            chunks.append(text[start:end])
            start = end + 1

    return chunks