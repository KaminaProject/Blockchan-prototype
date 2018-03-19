import base64
from datetime import datetime
import json
import hashlib
import winreg
import codecs
from urllib.request import urlopen
import sqlite3
import os

with open("config.json","r") as config:
    database = json.loads(config.read())['database']
    if os.path.isfile(database):
        conn = sqlite3.connect(database)
        db = conn.cursor()
    else:
        conn = sqlite3.connect(database)
        db = conn.cursor()
        db.execute("CREATE TABLE posts (thread,id,timestamp,subject,comment,image)")


def regkey_value(path, name="", start_key = None):
    if isinstance(path, str):
        path = path.split("\\")
    if start_key is None:
        start_key = getattr(winreg, path[0])
        return regkey_value(path[1:], name, start_key)
    else:
        subkey = path.pop(0)
    with winreg.OpenKey(start_key, subkey) as handle:
        assert handle
        if path:
            return regkey_value(path, name, handle)
        else:
            desc, i = None, 0
            while not desc or desc[0] != name:
                desc = winreg.EnumValue(handle, i)
                i += 1
            return desc[1]

def make_hash(*args):
    tobehashed = ''
    for arg in args:
        tobehashed = tobehashed+str(arg)
    tobehashed = tobehashed.encode("utf-8")
    hash_object = hashlib.sha256(tobehashed)
    return hash_object.hexdigest()

def get_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def get_user_id():
    regkey = regkey_value("HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion","ProductId")
    ip = json.loads(urlopen('https://api.ipify.org?format=json').read().decode("utf-8"))['ip']
    return make_hash(regkey_value,ip)

class Post():
    id = ""
    timestamp = ""
    subject = ""
    comment = ""
    image = ""
    thread = ""

    def save_post(self):
        id = self.id
        subject = self.subject
        comment = self.comment
        image = self.image
        timestamp = self.timestamp
        if db.execute("INSERT INTO posts (thread,id,timestamp,subject,comment,image) VALUES(0,?,?,?,?,?)",(id,timestamp,subject,comment,image)):
            conn.commit()
            return 1
        else:
            return 0

    def add_comment(self,comm):
        timestamp = comm['timestamp']
        subject = comm['subject']
        image = comm['image']
        post_id = self.id
        id = make_hash(timestamp,post_id)
        db.execute("INSERT INTO posts(thread,id,timestamp,subject,comment,image) values(?,?,?,?,?,?)",(post_id,id,timestamp,subject,comment,image))
        conn.commit()

    def get_comment_count(self):
        db.execute("SELECT COUNT id FROM posts WHERE thread=?",(self.id,))
        return db.fetchone()[0]

    def get_comments(self):
        comments = []
        db.execute("SELECT id,timestamp,subject,comment,image FROM posts WHERE thread=?",(self.id,))
        for res in db.fetchall():
            comm = Post()
            comm.thread = self.id
            comm.id = res[0]
            comm.timestamp = res[1]
            comm.subject = res[2]
            comm.comment = res[3]
            comm.image = res[4]
            comments.append(comm)
        return comments



class blockchan():

    def encode_image(path):
        with open(path,"rb") as image:
            image = base64.b64encode(image.read())
        image = image.decode("utf-8")
        return image

    def make_post(subject,comment,file,user_id,post_id=0,thread=0):
        image = blockchan.encode_image(file)
        timestamp = str(get_timestamp())
        author_id = user_id
        if post_id == 0:
            post_id = make_hash(timestamp,author_id)
        post = Post()
        post.id = post_id
        post.timestamp = timestamp
        post.subject = subject
        post.comment = comment
        post.image = image
        return post


    def get_all_posts():
        db.execute("SELECT id,timestamp,subject,comment,image FROM posts ORDER BY timestamp DESC")
        posts = []
        for res in db.fetchall():
            post = Post()
            post.id = res[0]
            post.timestamp = res[1]
            post.subject = res[2]
            post.comment = res[3]
            post.image = res[4]
            posts.append(post)
        return posts


    def post_exists(id):
        db.execute("SELECT id FROM posts WHERE id=?",(id,))
        if db.fetchone():
            return 1
        else:
            return 0


    def get_post(id):
        db.execute("SELECT id,timestamp,subject,comment,image FROM posts WHERE id=?",(id,))
        res = db.fetchone()
        post = Post()
        post.id = res[0]
        post.timestamp = res[1]
        post.subject = res[2]
        post.comment = res[3]
        post.image = res[4]
        return post
