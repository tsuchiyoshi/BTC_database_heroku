import datetime
import pytz

now_1 = datetime.datetime.now()
now_2 = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))

print(now_1,now_2)