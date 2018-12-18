from mongoengine import Document, StringField, IntField, DateTimeField

class Comment(Document):
    comment = StringField() # comment là gì
    who_fullname = StringField() # tên đầy đủ người comment
    who_username = StringField() # username
    picid = StringField() # comment của bức tranh nào (dùng id của bức tranh để định danh)
    # whencomment = DateTimeField() # thời gian comment
