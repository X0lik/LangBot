import sqlite3
from tg.language import lang

class DB:
    users = {}
    def Registration(id, slan, clan="en"):
        connection = sqlite3.connect('anonymous.sqlite')
        cursor = connection.cursor()
        cursor.execute('INSERT OR IGNORE INTO users (id, systemLang, choosenLang, reminder) VALUES (?, ?, ?, ?)', (id, slan, clan, "null"))
        connection.commit()
        connection.close()

        DB.users[id] = {
            "systemLang": slan,
            "choosenLang": clan,
        }

    def UpdateSystem(id, lang):
        connection = sqlite3.connect('anonymous.sqlite')
        cursor = connection.cursor()
        cursor.execute('UPDATE users SET systemLang = ? WHERE id = ?', (lang, id))
        connection.commit()
        connection.close()
        DB.users[id]["systemLang"] = lang

    def UpdateChoosen(id, lang):
        connection = sqlite3.connect('anonymous.sqlite')
        cursor = connection.cursor()
        cursor.execute('UPDATE users SET choosenLang = ? WHERE id = ?', (lang, id))
        connection.commit()
        connection.close()
        DB.users[id]["choosenLang"] = lang

    def UpdateReminder(id, remind):
        connection = sqlite3.connect('anonymous.sqlite')
        cursor = connection.cursor()
        cursor.execute('UPDATE users SET reminder = ? WHERE id = ?', (remind, id))
        connection.commit()
        connection.close()

    def Load(id):
        connection = sqlite3.connect('anonymous.sqlite')
        cursor = connection.cursor()
        cursor.execute('SELECT systemLang, choosenLang FROM users WHERE id = ?', (id,))
        res = cursor.fetchall()
        connection.close()

        if len(res) != 0:
            DB.users[id] = {
                "systemLang": res[0][0],
                "choosenLang": res[0][1],
            }

    def LoadAll():
        connection = sqlite3.connect('anonymous.sqlite')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM users')
        res = cursor.fetchall()
        connection.close()

        for data in res:
            DB.users[data[0]] = {
                "systemLang": data[1],
                "choosenLang": data[2],
            }

    def Validate(id):
        if id not in DB.users:
            DB.Load(id)

    def GetSystemLang(id):
        if id in DB.users:
            return lang[DB.users[id]["systemLang"]]
        else:
            return lang["en"]

    def GetChoosenLang(id):
        if id in DB.users:
            return lang[DB.users[id]["choosenLang"]]
        else:
            return lang["en"]

    def WriteChunks(id, fileName, chunks):
        connection = sqlite3.connect('anonymous.sqlite')
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM chunks WHERE id = ? AND filename = ?', (id,fileName + str(1)))
        res = cursor.fetchall()

        if len(res) == 0:
            for i in range(len(chunks)):
                cursor.execute('INSERT INTO chunks (id, data, filename) VALUES (?, ?, ?)', (id, chunks[i], fileName + str(i)))
                connection.commit()
        else:
            print( "Data already exists!" )

        connection.close()

    def GetChunks(id):
        connection = sqlite3.connect('anonymous.sqlite')
        cursor = connection.cursor()

        cursor.execute('SELECT data FROM chunks WHERE id = ?', (id,))
        res = cursor.fetchall()
        connection.close()

        chunks = [row[0] for row in res] if res else []
        return chunks

    def ClearChunks(id):
        connection = sqlite3.connect('anonymous.sqlite')
        cursor = connection.cursor()

        cursor.execute('DELETE FROM chunks WHERE id = ?', (id,))
        connection.commit()
        connection.close()

    def GetReminders():
        connection = sqlite3.connect('anonymous.sqlite')
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM users')
        res = cursor.fetchall()
        connection.close()

        return res