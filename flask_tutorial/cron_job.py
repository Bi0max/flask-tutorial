"""
for crontab to work, type "crontab -e" in the terminal and add the following:
* * * * * python /home/bi0max/projects/tutorials/flask_tutorial/flask_tutorial/cron_job.py

it will run it every minute

"""


from datetime import datetime

path = "/home/bi0max/projects/tutorials/flask_tutorial/cron_test.txt"
with open(path, "w") as f:
    f.write(str(datetime.now()))
 
