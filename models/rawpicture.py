from mongoengine import Document, StringField, IntField

class Rawpicture(Document):
    picname = StringField() # Tên ảnh
    piclink = StringField() # Link ảnh để hiển thị
    category = StringField() # Thuộc catetory nào: Animals, Nature, ....
