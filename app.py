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
    for i, v in enumerate(finished_list):
        if i == 100:
            break
        # Đưa các thông tin của pic đó vào list top 100 pics:
        toppic = {
            'picpositionintop100': i + 1,
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
    piclist = Savepicture.objects(picstatus='finished').order_by('piclikes')
    if len(piclist) == 0:
        notice = 'Danh sách trống'
    return render_template('roomoffame.html', notice=notice, piclist=piclist)

@app.route('/view/<picid>', methods=['GET', 'POST']) # Hiển thị 1 bức tranh đã hoàn thành để like và comment theo id của bức tranh đó
def view(picid):
    pic = Savepicture.objects(id=picid).first()
    picname = pic.picname
    piclikes = pic.piclikes
    artist = User.objects(username=pic.picartist).first()
    comment_list = Comment.objects(picid=picid)
    warning = 'hide'
    likebutton = 'Like'
    display = 'no'
    if 'token' not in session:
        warning = 'show'
        display = 'no'
    else:
        warning = 'hide'
        if session['token'] == artist.username:
            display = 'yes'
        else: 
            display = 'no'
    if request.method == 'GET':
        if 'token' in session:
            like_check = Like.objects(who_username=session['token'], picid=picid).first()
            if  like_check is None :
                likebutton = 'Like'
            else:
                likebutton = 'Dislike'
        return render_template("view.html", display=display, pic=pic, picname=picname, piclikes=piclikes, artist=artist, comment_list=comment_list, likebutton=likebutton, warning=warning)
    elif request.method == 'POST':
        form = request.form
        like_check = Like.objects(who_username=session['token'], picid=picid).first()
        # Xử lý đổi tên:
        if 'picname' in form:
            newname = form['picname']
            if newname != '':
                picname = newname
                pic.update(set__picname=newname)
        # Xử lý form comment:
        if 'comment' in form:
            if  like_check is None :
                likebutton = 'Like'
            else:
                likebutton = 'Dislike'
            comment = form['comment']
            user = User.objects(username=session['token']).first()
            new_comment = Comment(comment=comment, who_fullname=user.fullname, who_username=user.username, picid=picid)
            pic.update(set__piccomments=pic.piccomments + 1)
            new_comment.save()
        # Xử lý form like:
        if 'like' in form:
            if  like_check is None:
                piclikes = pic.piclikes + 1
                # Update like vào số like của bức tranh và của user vẽ bức tranh đó:
                pic.update(set__piclikes=pic.piclikes + 1)
                artist.update(set__totallikes=artist.totallikes + 1)
                # Lưu like vào data:
                new_like = Like(who_username=session['token'], picid=picid)
                new_like.save()
                likebutton = 'Dislike' # chuyển thành nút dislike
            else:
                piclikes = pic.piclikes - 1
                # Update like vào số like của bức tranh và của user vẽ bức tranh đó:
                pic.update(set__piclikes=pic.piclikes - 1)
                artist.update(set__totallikes=artist.totallikes - 1)
                # Xóa like khỏi database
                like_check.delete()
                likebutton == 'Like' # chuyển thành nút like
        return render_template('view.html', display=display, pic=pic, picname=picname, piclikes=piclikes, artist=artist, comment_list=comment_list, warning=warning, likebutton=likebutton)

@app.route('/category') # Hiển thị trang Category tổng
def full_category():
    # Lấy id của 1 random pic, sử dụng trong mục Get me a random pic:
    pic_list = Rawpicture.objects()
    random_pic = choice(pic_list)
    categories = ['Aladdin', 'Christmas', 'Cinderella', 'Angry-Birds', 'Dragon Ball Z', 'Ben-10', 'Adiboo', '101 Dalmatians']
    category_list = []
    for c in categories:
        piclink = Rawpicture.objects(category__icontains=c).first().piclink
        category = {'category': c, 'name': c.replace('-',' ').title(), 'label': piclink}
        category_list.append(category)
    return render_template('category.html', random_pic=random_pic, category_list=category_list)

@app.route('/category/<category>') # Hiển thị 1 trang category cụ thể
def one_category(category):
    pic_list = Rawpicture.objects(category__icontains=category)
    cap_category = category.replace('-',' ').title()
    return render_template('one_category.html', pic_list=pic_list, category=cap_category)

@app.route('/profile/<artist>', methods=['GET', 'POST']) # Hiển thị profile
def profile(artist):
    artist_infor = User.objects(username=artist).first()
    working_arts = artist_infor.working_arts
    finished_arts = artist_infor.finished_arts
    totallikes = artist_infor.totallikes
    finished_list = Savepicture.objects(picartist=artist, picstatus='finished') # .order_by('-piclikes')
    working_list = Savepicture.objects(picartist=artist, picstatus='working')
    display = 'no'
    if 'token' in session:
        if session['token'] == artist:
            display = 'yes'
    if request.method == 'GET':
        return render_template('profile.html', display=display, artist_infor=artist_infor, working_arts=working_arts, finished_arts=finished_arts, totallikes=totallikes, finished_list=finished_list, working_list=working_list)
    elif request.method == 'POST':
        form = request.form
        for fpic in finished_list:
            df = 'df' + str(fpic.id)
            if df in form:
                f_picid = form[df]
                pic = Savepicture.objects(id=f_picid).first()
                pic.delete()
                finished_arts = artist_infor.finished_arts - 1
                totallikes = artist_infor.totallikes - pic.piclikes
                artist_infor.update(set__finished_arts=artist_infor.finished_arts - 1, set__totallikes=artist_infor.totallikes - pic.piclikes)
        for wpic in working_list:
            up = 'up' + str(wpic.id)
            dw = 'dw' + str(wpic.id)
            if up in form:
                u_picid = form[up]
                Savepicture.objects(id=u_picid).first().update(set__picstatus="finished")
                working_arts = artist_infor.working_arts - 1
                artist_infor.update(set__working_arts=artist_infor.working_arts - 1)
                finished_arts = artist_infor.finished_arts + 1
                artist_infor.update(set__finished_arts = artist_infor.finished_arts + 1)
            if dw in form:
                w_picid = form[dw]
                Savepicture.objects(id=w_picid).first().delete()
                working_arts = artist_infor.working_arts - 1
                artist_infor.update(set__working_arts=artist_infor.working_arts - 1)
        
        finished_list = Savepicture.objects(picartist=artist, picstatus='finished') # .order_by('-piclikes')
        working_list = Savepicture.objects(picartist=artist, picstatus='working')
        return render_template('profile.html', display=display, artist_infor=artist_infor, working_arts=working_arts, finished_arts=finished_arts, totallikes=totallikes, finished_list=finished_list, working_list=working_list)

@app.route('/new_picture/<picid>', methods=['GET', 'POST']) # Hiển thị trang vẽ tranh của 1 bức tranh theo id của bức tranh đó
def new_picture(picid):
    pic = Rawpicture.objects(id=picid).first()
    piclinkb64 = base64encode(pic.piclink)
    token = ''
    if 'token' in session:
        token = session['token']
    if request.method == 'GET':
        return render_template('new_picture.html', piclinkb64=piclinkb64, token=token)
    elif request.method == 'POST':
        form = request.form
        picname = form['picname']
        piclink = form['piclink']
        picstatus = form['picstatus']
        picartist = token
        picartistfullname = User.objects(username=token).first().fullname
        newlink = Savepicture(piclink=piclink, picname=picname, picstatus=picstatus, picartist=picartist, picartistfullname=picartistfullname, picrawid=picid)
        newlink.save()
        newid = Savepicture.objects(piclink=piclink).first().id

        # Update database của user tương ứng:
        working_arts = User.objects(username=token).first().working_arts
        finished_arts = User.objects(username=token).first().finished_arts
        if picstatus == 'working':
            User.objects(username=token).first().update(set__working_arts=working_arts+1)
        elif picstatus == 'finished':
            User.objects(username=token).first().update(set__finished_arts=finished_arts+1)
        return redirect(url_for('saved', picid=newid))

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
        if request.method == 'GET':
            return render_template('keep_continue.html', pic=pic, piclinkb64=piclinkb64, token=token)
        elif request.method == 'POST':
            form = request.form
            picname = form['picname']
            piclink = form['piclink']
            picstatus = form['picstatus']
            # Update:
            if picname != '':
                pic.update(set__picname=picname)
            working_arts = User.objects(username=token).first().working_arts
            finished_arts = User.objects(username=token).first().finished_arts
            if picstatus == 'working':
                pic.update(set__piclink=piclink)
            elif picstatus == 'finished':
                pic.update(set__piclink=piclink, set__picstatus=picstatus)
                User.objects(username=token).first().update(set__finished_arts=finished_arts+1)
                User.objects(username=token).first().update(set__working_arts=working_arts-1)
            return redirect(url_for('saved', picid=picid))

@app.route("/saved/<picid>") # Hiển thị trang lưu ảnh thành công
def saved(picid):
    pic = Savepicture.objects(id=picid).first()
    return render_template('saved.html', pic=pic)

if __name__ == '__main__':
  app.run(debug=True)