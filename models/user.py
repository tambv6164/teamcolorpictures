from mongoengine import Document, StringField, IntField, DateTimeField

class User(Document):
    fullname = StringField() # Tên đầy đủ
    username = StringField() 
    password = StringField()
    email = StringField(default='abcd1234')
    finished_arts = IntField(default=0)
    working_arts = IntField(default=0)
    totallikes = IntField(default=0)
    picsintop100 = IntField(default=0)
    positionintop100 = IntField(default=0)
    # joineddate = DateTimeField() # Ngày tham gia trang web
