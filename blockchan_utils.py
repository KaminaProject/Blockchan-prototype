import base64
from datetime import datetime
import json
import hashlib
import winreg
import codecs
from urllib.request import urlopen


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

    def pack_post(subject,comment,file,user_id):
        with open(file,"rb") as image:
            image = base64.b64encode(image.read())
        image = image.decode("utf-8")
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
        post = json.dumps(post)
        return post
