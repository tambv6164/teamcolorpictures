import mlab
from models.comment import Comment

mlab.connect()

Comment(comment='Bức này đẹp quá đi mà', whocomment='tambui', picid='5c1129016fc2cb1034646779').save()
Comment(comment='That is great', whocomment='tambui', picid='5c1129016fc2cb1034646779').save()
Comment(comment='Đỉnh cao', whocomment='tambui', picid='5c1129016fc2cb1034646779').save()
Comment(comment='Xuất sắc', whocomment='tambui', picid='5c1129016fc2cb1034646779').save()
Comment(comment='Đẹp quá đi mà', whocomment='tambui', picid='5c1129016fc2cb1034646779').save()
Comment(comment='Bao nhiêu tiền', whocomment='tambui', picid='5c1129016fc2cb1034646779').save()