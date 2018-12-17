import mlab
from models.user import User

mlab.connect()

User(fullname='Bùi Văn Tâm', username='tambui', password='321', email='abcd', totallikes=12).save()
User(fullname='Nguyễn Thành Công', username='thanhcong', password='321', email='abcd', totallikes=23).save()
User(fullname='Hoàng Anh Minh', username='anhminh', password='321', email='abcd', totallikes=345).save()
User(fullname='Hoàng Cương', username='hoangcuong', password='321', email='abcd', totallikes=57).save()
User(fullname='Nguyễn Anh Quân', username='anhquan', password='321', email='abcd', totallikes=125).save()
User(fullname='Nguyễn Quang Huy', username='quanghuy', password='321', email='abcd', totallikes=3435).save()