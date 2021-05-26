from datetime import datetime


class TimeManager:

    def __init__(self):
        pass

    @staticmethod
    def str_to_milliseconds(datetime_str="2020-01-01 08:30:00"):
        datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        return TimeManager.datetime_to_milliseconds(datetime_obj)

    @staticmethod
    def datetime_to_milliseconds(datetime_obj: datetime):
        return int(datetime_obj.timestamp() * 1000)

    @staticmethod
    def milliseconds_to_datetime(milliseconds: float = 10000000):
        return datetime.fromtimestamp(milliseconds / 1000.0)

    @staticmethod
    def milliseconds_to_str(milliseconds: float = 10000000):
        return TimeManager.milliseconds_to_datetime(milliseconds).strftime("%Y-%m-%d %H:%M:%S")
