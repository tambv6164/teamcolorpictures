from mongoengine import Document, StringField, IntField, DateTimeField

class Savepicture(Document):
    picname = StringField() # Tên bức tranh
    piclink = StringField() # link tranh để hiển thị trên web
    picstatus = StringField() # working ỏ finished
    picartist = StringField() 
    picartistfullname = StringField()
    piclikes = IntField(default=0) 
    piccomments = IntField(default=0) 
    picrawid = StringField() # id của bức ảnh gốc đã tạo nên bức này