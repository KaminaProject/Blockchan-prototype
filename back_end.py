import htmlPy
import json
from blockchan_utils import *
import time

with open('config.json',"r+") as conf_file:
    config = json.loads(conf_file.read())
    if config['user_id'] == 0:
        user_id = blockchan_utils.get_user_id()
        config['user_id'] = user_id
        conf_file.truncate(0)
        conf_file.seek(0)
        conf_file.write(json.dumps(config))
        conf_file.close()
    else:
        user_id = config['user_id']
        conf_file.close()



class BackEnd(htmlPy.Object):
    def __init__(self, app):
        super(BackEnd, self).__init__()
        self.app = app


    @htmlPy.Slot(str, result=str)
    def new_post(self,data):
        data = json.loads(data)
        subject = data['subject']
        comment = data['comment']
        file = data['file']
        post = blockchan.prepare_post(subject,comment,file,user_id)
        post_id = post['post_id']
        if blockchan.save_post(post):
            print('Post '+post_id+' written successfully')
            self.app.evaluate_javascript('alert("Post created successfully")')
            self.app.evaluate_javascript('document.getElementById("form").reset();')
            self.app.evaluate_javascript('new_thread()')
        else:
            self.app.evaluate_javascript('alert("Something went wrong...check console")')


    @htmlPy.Slot()
    def load_posts(self):
        tbr_posts = []
        posts = blockchan.load_all_posts()
        for post in posts:
            post = {
            "post_id" : post[0],
            "timestamp" : post[1],
            "subject" : post[2],
            "comment" : post[3],
            "image" : post[4]
            }
            tbr_posts.append(post)
        tbr_posts = blockchan.pack_json(tbr_posts)
        print('Rendering posts...')
        self.app.evaluate_javascript("render_post('{}')".format(tbr_posts))
