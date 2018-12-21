from flask import Flask, request, render_template, session, redirect, url_for, json, jsonify
# import các Class
from models.user import User
from models.rawpicture import Rawpicture
from models.savepicture import Savepicture
from models.comment import Comment
from models.like import Like
# import một số hàm chức năng sẽ dùng
from random import choice
import base64
import requests
# Kết nối với database
import mlab
mlab.connect()

# Hàm chuyển link ảnh sang định dạng base64
def base64encode(url):
    link1 = base64.b64encode(requests.get(url).content)
    link2 = str(link1)
    link = link2.replace("b'","data:image/jpeg;base64,").replace("'","")
    return link

app = Flask(__name__)
app.config['SECRET_KEY'] = 'teamcolorpictures'

@app.route('/') # Hiển thị trang chủ
def home():
    return render_template('homepage.html')

@app.route('/signup', methods=['GET', 'POST']) # Trang đăng ký tài khoản
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
        # # Tạm bỏ email cùng các phần liên quan bên dưới. 
        # # Khi nào cần thì bật lại vì trên database vẫn để email với giá trị default.
        # e = form['email']
        new_user = User(fullname=f, username=u, password=p) #, email=e)
        user_check = User.objects(username=u).first()        
        # email_check = User.objects(email=e).first()
        warning = ''
        if f == '' or u == '' or p == '': #or e == '':
            warning = 'Vui lòng nhập đầy đủ thông tin!'
        elif ' ' in u or ' ' in p:
            warning = 'Username hoặc password không được chứa dấu cách!'
        # Check xem có tồn tại username hoặc email đó chưa:
        elif user_check is not None:
            warning = 'Username đã tồn tại!'
        # elif email_check is not None:
        #     warning = 'Email đã tồn tại'
        if warning != '':
            return render_template('signup.html', warning=warning)
        else:
            new_user.save()
            session['token'] = u
            # Đăng ký xong thì trả về giao diện trang Welcome
            return render_template('welcome.html', fullname=f, u=u)

@app.route('/login', methods=['GET', 'POST']) # Trang đăng nhập
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
            warning = 'Bạn chưa nhập username!'
        elif user_check is None:
            warning = 'Username không tồn tại!'
        else:
            if p == '':
                warning = 'Vui lòng nhập password!'
            elif p != user_check.password:
                warning = 'Password sai!'
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
    return redirect(url_for('home'))

@app.route('/top100pics') # Hiển thị 100 Pics đc nhiều like nhất
def top100pics():
    notice = ''
    top100pics = []
    # Tìm những bức tranh có like khác 0:
    finished_list = Savepicture.objects(picstatus='finished', piclikes__ne=0).order_by('-piclikes')
    if len(finished_list) == 0:
        notice = 'Danh sách trống'
    top100pics = []
    for i, v in enumerate(finished_list):
        picpositionintop100 = i + 1
        # Đưa các thông tin của pic đó vào list top 100 pics:
        toppic = {
            'picpositionintop100': picpositionintop100,
            'picname': v.picname,
            'piclink': v.piclink,
            'piclikes': v.piclikes, 
            'picartistfullname': v.picartistfullname,
            'picartist': v.picartist,
            'picid': v.id
        }
        top100pics.append(toppic)
    return render_template('top100pics.html', notice=notice, top100pics=top100pics)

@app.route('/top100artists') # Hiển thị 100 Artists đc nhiều like nhất
def top100artists():
    notice = ''
    top100artists = []
    # Tìm tất cả các artist:
    artist_list = User.objects(totallikes__ne=0).order_by('-totallikes')
    if len(artist_list) == 0:
        notice = 'Danh sách trống'
    for i, artist in enumerate(artist_list):
        if i == 100:
            break
        # Tìm bức tranh có nhiều like nhất của artist đó:
        bestpic = Savepicture.objects(picartist=artist.username, picstatus='finished').order_by('-piclikes').first()
        topartist = {
            'positionintop100': i + 1,
            'fullname': artist.fullname,
            'username': artist.username,
            'totallikes': artist.totallikes,
            'bestpiclink': bestpic.piclink,
            'bestpicid': bestpic.id
        }
        top100artists.append(topartist)
    return render_template('top100artists.html', notice=notice, top100artists=top100artists)

@app.route('/roomoffame') # Hiển thị tất cả những bức ảnh finished để cộng đồng vào xem và like
def roomoffame():
    notice = ''
    piclist = Savepicture.objects(picstatus='finished')
    if len(piclist) == 0:
        notice = 'Danh sách trống'
    return render_template('roomoffame.html', notice=notice, piclist=piclist)

@app.route('/view/<picid>', methods=['GET', 'POST']) # Hiển thị 1 bức tranh đã hoàn thành để like và comment theo id của bức tranh đó
def view(picid):
    pic = Savepicture.objects(id=picid).first()
    piclikes = pic.piclikes
    artist = User.objects(username=pic.picartist).first()
    comment_list = Comment.objects(picid=picid)
    warning = ''
    likebutton = 'Like'
    if request.method == 'GET':
        # Kiểm tra user có đăng nhập hay không để hiển thị nút like tương ứng:
        if 'token' in session:
            like_check = Like.objects(who_username=session['token'], picid=picid).first()
            if  like_check is None :
                likebutton = 'Like'
            else:
                likebutton = 'Dislike'
        else:
            likebutton = 'Like'
        return render_template("view.html", pic=pic, piclikes=piclikes, artist=artist, comment_list=comment_list, likebutton=likebutton)
    else:
        if 'token' not in session:
            warning = 'Vui lòng đăng nhập để like & comment!'
        else:
            form = request.form
            # Xử lý form comment:
            if 'comment' in form:
                comment = form['comment']
                user = User.objects(username=session['token']).first()
                new_comment = Comment(comment=comment, who_fullname=user.fullname, who_username=user.username, picid=picid)
                if comment == '':
                    warning = 'Bạn chưa viết gì nên không có gì để đăng!'
                else:
                    # Update số comment vào số comment của bức tranh trên database:
                    pic.update(set__piccomments=pic.piccomments + 1)
                    new_comment.save()
            # Xử lý form like:
            if 'like' in form:
                like_check = Like.objects(who_username=session['token'], picid=picid).first()
                if  like_check is None:
                    piclikes = pic.piclikes + 1
                    # Update like vào số like của bức tranh và của user vẽ bức tranh đó:
                    pic.update(set__piclikes=pic.piclikes + 1)
                    artist.update(set__totallikes=artist.totallikes + 1)
                    # Lưu like vào data:
                    new_like = Like(who_username=session['token'], picid=picid)
                    new_like.save()
                    likebutton = 'Dislike'
                else:
                    piclikes = pic.piclikes - 1
                    # Update like vào số like của bức tranh và của user vẽ bức tranh đó:
                    pic.update(set__piclikes=pic.piclikes - 1)
                    artist.update(set__totallikes=artist.totallikes - 1)
                    # Xóa like khỏi database
                    like_check.delete()
                    likebutton == 'Like'
        return render_template('view.html', pic=pic, piclikes=piclikes, artist=artist, comment_list=comment_list, warning=warning, likebutton=likebutton)

@app.route('/category') # Hiển thị trang Category tổng
def full_category():
    # Lấy id của 1 random pic, sử dụng trong mục Get me a random pic:   
    pic_list = Rawpicture.objects()
    random_picid = choice(pic_list).id
    # category_list = Rawpicture.objects() # Sau sẽ xử lý hiển thị tất cả các category trong html bằng vòng for
    return render_template('category.html', random_picid=random_picid)

@app.route('/category/<category>') # Hiển thị 1 trang category cụ thể
def one_category(category):
    pic_list = Rawpicture.objects(category__icontains=category)
    cap_category = category.title()
    return render_template('one_category.html', pic_list=pic_list, category=cap_category)

@app.route('/profile/<artist>', methods=['GET', 'POST']) # Hiển thị profile
def profile(artist):
    artist_infor = User.objects(username=artist).first()
    working_arts = User.objects(username=artist).first().working_arts
    finished_arts = User.objects(username=artist).first().finished_arts
    # Các bức tranh đã hoàn thành sắp xếp theo số lượng like:
    finished_list = Savepicture.objects(picartist=artist, picstatus='finished').order_by('-piclikes')
    working_list = []
    if 'token' in session:
        if session['token'] == artist:
            working_list = Savepicture.objects(picartist=artist, picstatus='working')
    if request.method == 'POST':
        form = request.form
        picid = form['picid']
        # Update database:
        Savepicture.objects(id=picid).first().update(set__picstatus="finished")
        User.objects(username=artist).first().update(set__finished_arts=finished_arts+1)
        User.objects(username=artist).first().update(set__working_arts=working_arts-1)
    return render_template('profile.html', artist_infor=artist_infor, finished_arts=finished_arts, working_arts=working_arts, finished_list=finished_list, working_list=working_list)

@app.route('/new_picture/<picid>', methods=['GET', 'POST']) # Hiển thị trang vẽ tranh của 1 bức tranh theo id của bức tranh đó
def new_picture(picid):
    pic = Rawpicture.objects(id=picid).first()
    piclinkb64 = base64encode(pic.piclink)
    token = ''
    aftersave = ''
    if 'token' in session:
        token = session['token']
    if request.method == 'GET':
        aftersave = 'no'
        return render_template('new_picture.html', piclinkb64=piclinkb64, token=token, aftersave=aftersave)
    elif request.method == 'POST':
        aftersave = 'yes'
        form = request.form
        picname = form['picname']
        piclink = form['piclink']
        picstatus = form['picstatus']
        picartist = token
        picartistfullname = User.objects(username=token).first().fullname
        newlink = Savepicture(piclink=piclink, picname=picname, picstatus=picstatus, picartist=picartist, picartistfullname=picartistfullname)
        newlink.save()
        # Update database của user tương ứng:
        working_arts = User.objects(username=token).first().working_arts
        finished_arts = User.objects(username=token).first().finished_arts
        if picstatus == 'working':
            User.objects(username=token).first().update(set__working_arts=working_arts+1)
        elif picstatus == 'finished':
            User.objects(username=token).first().update(set__finished_arts=finished_arts+1)
        return render_template('new_picture.html', piclinkb64=piclink, aftersave=aftersave)

@app.route('/keep_continue/<picid>', methods=['GET', 'POST']) # Trang vẽ tiếp 1 bức đang vẽ dở
def keep_continue(picid):
    token = ''
    warning = 'Bạn chưa đăng nhập!'
    if 'token' not in session:
        return render_template('login.html', warning=warning)
    else:
        token = session['token']
        pic = Savepicture.objects(id=picid).first()
        piclinkb64 = pic.piclink
        aftersave = ''
        if request.method == 'GET':
            aftersave = 'no'
            return render_template('keep_continue.html', piclinkb64=piclinkb64, token=token, aftersave=aftersave)
        elif request.method == 'POST':
            aftersave = 'yes'
            form = request.form
            piclink = form['piclink']
            picstatus = form['picstatus']
            # Update:
            working_arts = User.objects(username=token).first().working_arts
            finished_arts = User.objects(username=token).first().finished_arts
            if picstatus == 'working':
                pic.update(set__piclink=piclink)
            elif picstatus == 'finished':
                pic.update(set__piclink=piclink, set__picstatus=picstatus)
                User.objects(username=token).first().update(set__finished_arts=finished_arts+1)
                User.objects(username=token).first().update(set__working_arts=working_arts-1)
            return render_template('keep_continue.html', piclinkb64=piclink, aftersave=aftersave)

if __name__ == '__main__':
  app.run(debug=True)