import mongoengine

# mongodb://<dbuser>:<dbpassword>@ds159880.mlab.com:59880/colorpictures

host = "ds159880.mlab.com"
port = 59880
db_name = "colorpictures"
user_name = "admin"
password = "admin1"


def connect():
    mongoengine.connect(db_name, host=host, port=port, username=user_name, password=password)