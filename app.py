from flask import Flask, request, render_template, session, redirect, url_for
from models.user import User
from models.rawpicture import Rawpicture
from models.savepicture import Savepicture
from models.comment import Comment
from random import choice
import mlab
mlab.connect()

def func_top100pics():
    # Tìm tất cả những bức tranh đã hoàn thành:
    finished_list = Savepicture.objects(picstatus='finished', piclikes__ne=0)
    # Tìm 100 bức có số like lớn nhất và lưu số likes đó vào 1 list:
    likes_list = []
    for pic in finished_list:
        likes_list.append(pic.piclikes)
    likes_list.sort(reverse=True) # sắp xếp theo thứ tự giảm dần
    if len(likes_list) > 100:
        likes_list = likes_list[:101]
    likes_list = list(dict.fromkeys(likes_list)) # loại bỏ các giá trị trùng nhau
    # Tạo Top 100 bằng cách tìm ngược likes trong list trên ở database ảnh:
    top100pics = []
    for i, v in enumerate(likes_list):
        for pic in finished_list:
            if pic.piclikes == v:
                Savepicture.objects(id=pic.id).first().update(set__picpositionintop100=i+1)
                artist = User.objects(username=pic.picartist).first()
                toppic = {
                    'picpositionintop100': pic.picpositionintop100,
                    'picname': pic.picname,
                    'piclink': pic.piclink,
                    'piclikes': pic.piclikes, 
                    'picartist': artist.fullname,
                    'username': artist.username,
                    'picid': pic.id
                }
                top100pics.append(toppic)
    return top100pics
    # Các biến được dùng để hiển thị trên HTML:
    # 1. Tên bức tranh: picname
    # 2. Link ảnh để hiển thị ảnh: piclink
    # 3. Số lượng like: piclikes
    # 4. Tác giả: picartist  

def func_top100artists():
    # Tìm tất cả các artist:
    artist_list = User.objects(totallikes__ne=0)
    # Tìm 100 artist có likes lớn nhất và lưu số like đó vào 1 list:
    likes_list = []
    for artist in artist_list:
        likes_list.append(artist.totallikes)
    likes_list.sort(reverse=True) # sắp xếp theo thứ tự giảm dần
    if len(likes_list) > 100:
        likes_list = likes_list[:101]
    likes_list = list(dict.fromkeys(likes_list)) # loại bỏ các giá trị trùng nhau
    # Tạo top 100 Artist bằng cách tìm ngược likes trong database user:
    top100artists = []
    for i, v in enumerate(likes_list):
        for artist in artist_list:
            if artist.totallikes == v:
                # Update Position trong top 100:
                User.objects(username=artist.username).first().update(set__positionintop100=i+1)
                # Số tranh đã hoàn thành:
                finished_list = Savepicture.objects(picartist=artist.username, picstatus='finished')
                # # Số tranh trong top 100 pics:
                # picsintop100 = 0
                # top100pics = func_top100pics()
                # for pic in top100pics:
                #     if pic['picartist'] == artist.username:
                #         picsintop100 += 1
                # User.objects(username=artist.username).first().update(set__picsintop100=picsintop100)
                # Tìm bức tranh có nhiều like nhất của artist đó:
                likes = []
                for pic in finished_list:
                    likes.append(pic.piclikes)
                bestpic = Savepicture.objects(picartist=artist.username, picstatus='finished', piclikes=max(likes)).first()
                # Đưa các thông tin của artist đó vào list top 100 artist:
                topartist = {
                    'positionintop100': artist.positionintop100,
                    'fullname': artist.fullname,
                    'username': artist.username,
                    # 'picsintop100': picsintop100,
                    'totallikes': artist.totallikes,
                    # 'finishedarts': len(finished_list),
                    'bestpic': bestpic.piclink
                }
                top100artists.append(topartist)
    return top100artists
    # Các biến dùng để hiển thị trên HTML:
    # 1. Thứ hạng của artist: positionintop100
    # 2. Tên đầy đủ của artist: fullname
    # 3. Số lượng pic nằm trong top100pics: picsintop100
    # 4. Tổng like: totallikes
    # 5. Số bức vẽ đã hoàn thành: finishedarts
    # 6. Link bức vẽ được nhiều like nhất để hiển thị: bestpic

def func_artist_infor(artist):
    # Fullname của artist:
    artist_fullname = User.objects(username=artist).first().fullname
    # Số bức tranh đã hoàn thành:
    finished_list = Savepicture.objects(picartist=artist, picstatus='finished')
    finished_arts = len(finished_list)
    # Số bức tranh đang làm dở:
    working_list = Savepicture.objects(picartist=artist, picstatus='working')
    working_arts = len(working_list)
    # Tính tổng like của artist: 
    ##### Liệu có cách nào tự động kết nối data user vs data picture để tự tính tổng like?
    totallikes = 0
    for art in finished_list:
        totallikes += art.piclikes
    # # Tổng số bức tranh trong top 100 pics:
    # picsintop100 = 0
    # top100pics = func_top100pics()
    # for pic in top100pics:
    #     if pic['picartist'] == artist:
    #         picsintop100 += 1
    # User.objects(username=artist).first().update(set__picsintop100=picsintop100)
    # # Tìm thứ hạng trong top 100:    
    # positionintop100 = 0
    # top100artists = func_top100artists()
    # for a in top100artists:
    #     if a['username'] == artist:
    #         positionintop100 = a['positionintop100']
    # Tạo 1 dictionary lưu thông tin của artist:
    artist_infor = {
        'fullname': artist_fullname,
        'username': artist,
        'finished_arts': finished_arts,
        'working_arts': working_arts,
        'totallikes': totallikes,
        # 'picsintop100': picsintop100,
        # 'positionintop100': positionintop100
    }
    return artist_infor
    # Thông tin của artist: 
    #   - Tên đầy đủ của artist: fullname
    #   - Số bức tranh đã hoàn thành: finished_arts
    #   - Số bức tranh đang vẽ: working_arts
    #   - Tổng số likes của artist đó: totallikes
    #   - Bỏ: Số bức tranh trong top 100: picsintop100 (bằng 0 là không có bức nào)
    #   - Bỏ: Thứ hạng của artist: positionintop100 (bằng 0 là không được vào top)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'teamcolorpictures'

@app.route('/') # Hiển thị trang chủ
def home():
    return render_template('homepage.html')

@app.route('/homepage') # Hiển thị trang chủ
def homepage():
    return redirect(url_for('home'))

@app.route('/signup', methods=['GET', 'POST']) # Đăng ký tài khoản
def signup():
    if 'token' in session:
        return render_template('homepage.html')
    if request.method == 'GET':
        return render_template("signup.html")
    else:
        form = request.form
        f = form['fullname']
        u = form['username']
        p = form['password']
        # e = form['email']
        new_user = User(fullname=f, username=u, password=p) #, email=e)
        user_check = User.objects(username=u).first()        
        # email_check = User.objects(email=e).first()
        warning = ''
        if len(u) < 6:
            warning = 'Username cần ít nhất 6 ký tự'
        if f == '' or u == '' or p == '': #or e == '':
            warning = 'Vui lòng nhập đầy đủ thông tin'
        elif ' ' in u or ' ' in p:
            warning = 'Username hoặc password không được chứa dấu cách'
        # Check xem có tồn tại username hoặc email đó chưa:
        elif user_check is not None:
            warning = 'Username đã tồn tại'
        # elif email_check is not None:
        #     warning = 'Email đã tồn tại'
        if warning != '':
            return render_template('signup.html', warning=warning)
        else:
            new_user.save()
            session['token'] = u
            # Đăng ký xong thì trả về giao diện trang Welcome
            return render_template('welcome.html', fullname=f, u=u)

@app.route('/login', methods=['GET', 'POST']) # Đăng nhập
def login():
    if 'token' in session:
        return render_template('homepage.html')
    if request.method == 'GET':
        return render_template('login.html')
    else:
        form = request.form
        u = form['username']
        p = form['password']
        user_check = User.objects(username=u).first()
        # Check xem có nhập username và password hay không và nhập đúng hay không:
        warning = ''
        if u == '':
            warning = 'Bạn chưa nhập username'
        elif user_check is None:
            warning = 'Username không tồn tại'
        else:
            if p == '':
                warning = 'Vui lòng nhập password'
            elif p != user_check.password:
                warning = 'Password sai'
        if warning != '':
            return render_template('login.html', warning=warning)
        else:
            session['token'] = u
            # Đăng nhập đúng thì trả về giao diện trang Welcome
            return render_template('welcome.html', fullname=User.objects(username=u).first().fullname, u=u) 

@app.route('/logout') # Đăng xuất
def logout():
    if 'token' in session:
        del session['token']
    return redirect(url_for('homepage'))

@app.route('/top100pics') # Hiển thị 100 Pics đc nhiều like nhất
def top100pics():
    top100pics = func_top100pics()
    return render_template('top100pics.html', top100pics=top100pics)

@app.route('/top100artists') # Hiển thị 100 Artists đc nhiều like nhất
def top100artists():
    top100artists = func_top100artists()
    return render_template('top100artists.html', top100artists=top100artists)

@app.route('/profile/<artist>') # Hiển thị profile
def profile(artist):
    if artist == 'me':
        artist = session['token']
    # Chạy hàm func_artist_infor và trả về các thông tin của artist đó
    artist_infor = func_artist_infor(artist) 
    # Các bức tranh đã hoàn thành sắp xếp theo số lượng like:
    # Tạo 1 list gồm số like của các bức tranh của artist đó
    likes_list = []
    finished_list = Savepicture.objects(picartist=artist, picstatus='finished')
    for pic in finished_list:
        likes_list.append(pic.piclikes)
    likes_list.sort(reverse=True)
    likes_list = list(dict.fromkeys(likes_list)) # loại bỏ các giá trị trùng nhau
    # Tạo 1 list các bức tranh sắp xếp theo số lượng like để sau đó hiển thị trên trang profile của artist
    artist_finised_arts = []
    for i in likes_list:
        for pic in finished_list:
            if pic.piclikes == i:
                # # Tìm thứ hạng của pic đó trong top 100 pics nếu có:
                # top100pics = func_top100pics()
                # positionintop100 = 0
                # for toppic in top100pics:
                #     if toppic['picid'] == pic.id:
                #         positionintop100 = toppic['picpositionintop100']
                # Tìm số lượng comment trong bức tranh đó:
                comment_list = Comment.objects(picid=pic.id)
                # Đưa các thông tin của các bức vẽ vào list các bức vẽ của artist đó
                toppic = {
                    # 'positionintop100': positionintop100,
                    'picname': pic.picname,
                    'piclink': pic.piclink,
                    'piclikes': pic.piclikes, 
                    'piccomments': len(comment_list)
                }
                artist_finised_arts.append(toppic)
    # Danh sách những bức đang vẽ
    # artist_working_arts = []
    # if session['token'] == artist:
    working_list = Savepicture.objects(picartist=artist, picstatus='working')

    return render_template('profile.html', artist_infor=artist_infor, artist_finised_arts=artist_finised_arts, working_list=working_list)
    # Các biến được dùng để hiển thị trên HTML:
    # 1. Thông tin của artist:  
    #   - Tên đầy đủ của artist: artist_fullname
    #   - Số bức tranh đã hoàn thành: finished_arts
    #   - Số bức tranh đang vẽ: working_arts. (Cái này chỉ hiện ra nếu ở trang profile của mình, còn của người khác chỉ hiện finished_arts thôi)
    #   - Bỏ: Số bức tranh trong top 100: picsintop100 (bằng 0 là không có bức nào)
    #   - Bỏ: Thứ hạng trong 100 artist: positionintop100 (bằng 0 là không nằm trong danh sách)
    # 2. Thông tin từng bức vẽ đã hoàn thành, bao gồm:
    #   - Bỏ: Thứ hạng trong top 100 pics nếu bức đó lọt vào: positionintop100
    #   - Tên bức tranh: picname
    #   - Link ảnh để hiển thị: piclink
    #   - Số lượng like: piclikes
    #   - Số lượng comment: piccomments
    
@app.route('/category') # Hiển thị trang Category tổng
def full_category():
    return render_template('category.html')

# Bên dưới đang làm tiếp
# @app.route('/category/<category>') # Hiển thị 1 trang category cụ thể
# def one_category(category):
#     pic_list = Rawpicture.objects(category__icontains=category)
#     cap_category = category.title()
#     return render_template('one_category.html', pic_list=pic_list, category=cap_category)

# @app.route('/new_picture') # Hiển thị trang vẽ tranh của 1 bức tranh
# def new_picture():
#     piclink = '...'
#     return render_template('new_picture.html', piclink=piclink)

# @app.route('/<picname>') # Hiển thị trang phóng to của 1 bức ảnh đã hoàn thành để có thể comment


if __name__ == '__main__':
  app.run(debug=True)
