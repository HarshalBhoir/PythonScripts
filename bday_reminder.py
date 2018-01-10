from datetime import *
from dateutil.rrule import rrule, YEARLY

# GLOBAL CONFIG
td_8am = timedelta(seconds=3600*8)
td_jobfrequency = timedelta(seconds=3600) # hourly job


# USER DATA::
# birthday: assumed to be retrieved from some data source
bday = date(1960, 5, 12)
# reminder delta: number of days before the b-day
td_delta = timedelta(days=6)
# difference between the user TZ and the server TZ
tz_diff = timedelta(seconds=3600*5) # example: +5h


# from current time minus the job periodicity and the delta
sday = date.today()
# occr will return the first birthday from today on
occr = rrule(YEARLY, bymonth=bday.month, bymonthday=bday.day, dtstart=sday, count=1)[0]

# adjust: subtract the reminder delta, fixed 8h (8am) and tz difference
occr -= (td_delta + td_8am + tz_diff)

# send the reminder when the adjusted occurance is within this job time period
if datetime.now() - td_jobfrequency < occr < datetime.now():
    print occr, '@todo: send the reminder'
else:
    print occr, 'no reminder'