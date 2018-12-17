import urllib
import urllib.request
import requests
from bs4 import BeautifulSoup
from models.rawpicture import Rawpicture
import mlab
import base64


mlab.connect()

# def base64encode(url):
#     return base64.b64encode(requests.get(url).content)


def make_soup(url):
    thepage = urllib.request.urlopen(url)
    soupdata = BeautifulSoup(thepage,"html.parser")
    return soupdata
    
soup = make_soup("http://www.coloring-book.info/coloring/coloring_page.php?id=7")
infor_list = soup.findAll('img')
sourcelist = []
for i in infor_list:
    if '.jpg' in i.get('src'):
        sourcelist.append(i)
for img in sourcelist:
    temp = img.get('src')
    tmp = temp.replace("_m","").replace("/thumbs","")
    image = "http://www.coloring-book.info/coloring/" + tmp if "http" not in tmp else tmp
#     image = base64encode(image)
    category = ''
    for i in tmp:
        if i != "/":
            category += i
        else:
            break
    picname = tmp.replace(category,'').replace('.jpg', '').replace('/', '')
    print(picname,image,category)

    rawpic = Rawpicture(picname=picname, piclink=image, category=category)
    rawpic.save()


    