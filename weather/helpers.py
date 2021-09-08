
import datetime as dt

def kelvin_to_celisus(kelvin):
    celisus = kelvin - 273.15
    celisus = round(celisus,2)
    return celisus


# unix time to IST
def UtcToIst(utc_date):
    return (dt.datetime.fromtimestamp(int(utc_date)).strftime('%Y-%m-%d %H:%M:%S'))



def ConverTime(time_stamp):
    from datetime import datetime
    d = datetime.strptime(time_stamp, "%Y-%m-%d %H:%M:%S").time()
    return d


    

