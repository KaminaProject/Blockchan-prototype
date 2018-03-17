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
    database = json.loads(config.read())[database]
    if os.path.isfile(database):
        conn = sqlite3.connect(database)
        db = conn.cursor()
    else:
        conn = sqlite3.connect(database)
        db = conn.cursor()
        db.execute("CREATE TABLE posts (id,timestamp,subject,comment,image)")


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

class blockchan():

    def encode_image(path):
        with open(path,"rb") as image:
            image = base64.b64encode(image.read())
        image = image.decode("utf-8")
        return image

    def pack_post(subject,comment,file,user_id):
        image = blockchan.encode_image(file)
        timestamp = str(get_timestamp())
        author_id = user_id
        post_id = make_hash(author_id,timestamp)
        post = {
        "post_id" : post_id,
        "author" : author_id,
        "timestamp" : timestamp,
        "subject" : subject,
        "comment" : comment,
        "image" : image
        }
        return json.dumps(post)


    def save_post(post):
        post = json.loads(post)
        post_id = post['post_id']
        timestamp = post['timestamp']
        subject = post['subject']
        comment = post['comment']
        image = post['image']
        if db.execute("INSERT INTO posts (id,timestamp,subject,comment,image) VALUES(?,?,?,?,?)",(post_id,timestamp,subject,comment,image)):
            conn.commit()
            return 1
        else:
            return 0
