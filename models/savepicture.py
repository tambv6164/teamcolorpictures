from mongoengine import Document, StringField, IntField, DateTimeField

class Savepicture(Document):
    picname = StringField() # Tên bức tranh
    piclink = StringField() # link tranh để hiển thị trên web
    picstatus = StringField(default='working') # 'working' là đang vẽ dở, mình sẽ update thành 'finished' là đã tô xong
    piclikes = IntField(defalt=0) # số like, ban đầu mặc định là 0, tăng lên mỗi khi có ngươi like
    picartist = StringField(default=None) # tranh này tác giả là ai, ban đầu mặc định là None. Nếu người dùng click vào save thì sẽ tính là tranh của người đó
    picpositionintop100 = IntField(default=0) # ban đầu chưa được xếp hạng (chưa có like)
    # starttime = DateTimeField() # Ngày bắt đầu tô
    # finishtime = DateTimeField() # Ngày hoàn thành
