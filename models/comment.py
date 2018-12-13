from mongoengine import Document, StringField, IntField, DateTimeField

class Comment(Document):
    comment = StringField() # comment là gì
    whocomment = StringField() # ai là người comment
    picid = StringField() # comment của bức tranh nào (dùng id của bức tranh để định danh)
    # whencomment = DateTimeField() # thời gian comment
