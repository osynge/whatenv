import datetime
import time

time_format_definition = "%Y-%m-%dT%H:%M:%SZ"
def datetime_encoded_str(obj = None):
    if obj == None:
        obj = datetime.datetime.now()
    return obj.strftime(time_format_definition)

def datetime_str_decode(stringform):
    return datetime.datetime(*(time.strptime(stringform, time_format_definition)[0:7]))
