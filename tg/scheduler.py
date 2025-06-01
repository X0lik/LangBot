import time

from database.db import DB
from tg.main import Remind


def startReminder():
    named_tuple = time.localtime() # получить struct_time
    time_string = time.strftime("%H:%M", named_tuple)

    res = DB.GetReminders()
    for i in range(len(res)):
        if res[i][3] == time_string:
            Remind.send(res[i][0])

startReminder()