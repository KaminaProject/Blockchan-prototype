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
        db.execute("CREATE TABLE posts (thread,author_name,id,timestamp,subject,comment,image)")


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
    return hash_object.hexdigest()[:32]

def get_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def get_user_id():
    regkey = regkey_value("HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion","ProductId")
    ip = json.loads(urlopen('https://api.ipify.org?format=json').read().decode("utf-8"))['ip']
    return make_hash(regkey_value,ip)

class Post():
    id = ""
    author_name = ""
    timestamp = ""
    subject = ""
    comment = ""
    image = ""
    thread = ""

    def save_post(self):
        id = self.id
        author_name = self.author_name
        subject = self.subject
        comment = self.comment
        image = self.image
        timestamp = self.timestamp
        if db.execute("INSERT INTO posts (thread,id,author_name,timestamp,subject,comment,image) VALUES(0,?,?,?,?,?,?)",(id,author_name,timestamp,subject,comment,image)):
            conn.commit()
            return 1
        else:
            return 0

    def add_comment(self,comm):
        author_name = comm.author_name
        timestamp = comm.timestamp
        subject = comm.subject
        image = comm.image
        comment = comm.comment
        post_id = self.id
        id = make_hash(timestamp,post_id)
        if db.execute("INSERT INTO posts(thread,author_name,id,timestamp,subject,comment,image) values(?,?,?,?,?,?,?)",(post_id,author_name,id,timestamp,subject,comment,image)):
            conn.commit()
            return 1
        else:
            return 0

    def get_comment_count(self):
        db.execute("SELECT count(*) FROM posts WHERE thread=?",(self.id,))
        return db.fetchone()[0]

    def get_comments(self):
        comments = []
        db.execute("SELECT id,timestamp,subject,comment,image,author_name FROM posts WHERE thread=?",(self.id,))
        for res in db.fetchall():
            comm = Post()
            comm.thread = self.id
            comm.id = res[0]
            comm.timestamp = res[1]
            comm.subject = res[2]
            comm.comment = res[3]
            comm.image = res[4]
            comm.author_name = res[5]
            comm.replies = []
            db.execute("SELECT id,timestamp,subject,comment,image FROM posts WHERE thread=?",(comm.id,))
            for res2 in db.fetchall():
                reply = Post()
                reply.thread = self.id
                reply.id = res[0]
                reply.timestamp = res[1]
                reply.subject = res[2]
                reply.comment = res[3]
                reply.image = res[4]
                reply.author_name = res[5]
                comm.replies.append(reply)
            comments.append(comm)
        return comments

    def pack_json(self):
        post = {
        "post_id" : self.id,
        "timestamp" : self.timestamp,
        "comment" : self.comment,
        "subject" : self.subject,
        "image" : self.image
        }
        return json.dumps(post)



class blockchan():

    def encode_image(path):
        with open(path,"rb") as image:
            image = base64.b64encode(image.read())
        image = image.decode("utf-8")
        return image

    def make_post(name,subject,comment,file,user_id,post_id=0,thread=0):
        if file != '':
            image = blockchan.encode_image(file)
        else:
            image = 0
        timestamp = str(get_timestamp())
        author_id = user_id
        if post_id == 0:
            post_id = make_hash(timestamp,author_id)
        post = Post()
        post.id = post_id
        post.author_name = name
        post.timestamp = timestamp
        post.subject = subject
        post.comment = comment
        post.image = image
        post.thread = thread
        return post


    def get_all_posts():
        db.execute("SELECT author_name,timestamp,subject,comment,image,id FROM posts WHERE thread=0 ORDER BY timestamp DESC")
        posts = []
        for res in db.fetchall():
            post = Post()
            post.author_name = res[0]
            post.timestamp = res[1]
            post.subject = res[2]
            post.comment = res[3]
            post.image = res[4]
            post.id = res[5]
            posts.append(post)
        return posts


    def post_exists(id):
        db.execute("SELECT id FROM posts WHERE id=?",(id,))
        if db.fetchone():
            return 1


    def get_post(id):
        db.execute("SELECT id,author_name,timestamp,subject,comment,image FROM posts WHERE id=?",(id,))
        res = db.fetchone()
        post = Post()
        post.id = res[0]
        post.author_name = res[1]
        post.timestamp = res[2]
        post.subject = res[3]
        post.comment = res[4]
        post.image = res[5]
        return post


    def get_post_ids():
        db.execute("SELECT id FROM posts")
        return db.fetchall()
