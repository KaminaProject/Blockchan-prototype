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
        author_name = data['username']
        subject = data['subject']
        comment = data['comment']
        file = data['file']
        if 'thread' in data:
            thread = data['thread']
            reply = blockchan.make_post(author_name,subject,comment,file,user_id)
            if blockchan.get_post(thread).add_comment(reply):
                print("Comment written successfully")
                self.app.evaluate_javascript('alert("Comment written successfully")')
                self.app.evaluate_javascript('document.getElementById("form").reset();')
                self.app.evaluate_javascript('new_thread()')
                return 1
            else:
                self.app.evaluate_javascript('alert("Something went wrong...check console")')
                return 1
        post = blockchan.make_post(author_name,subject,comment,file,user_id)
        post_id = post.id
        if post.save_post():
            print('Post '+post_id+' written successfully')
            self.app.evaluate_javascript('alert("Post created successfully")')
            self.app.evaluate_javascript('document.getElementById("form").reset();')
            self.app.evaluate_javascript('new_thread()')
        else:
            self.app.evaluate_javascript('alert("Something went wrong...check console")')


    @htmlPy.Slot()
    def load_posts(self):
        tbr_posts = []
        posts = blockchan.get_all_posts()
        for post in posts:
            post = {
            "post_id" : post.id,
            "author_name" : post.author_name,
            "timestamp" : post.timestamp,
            "subject" : post.subject,
            "comment" : post.comment,
            "image" : post.image,
            "comm_count": post.get_comment_count()
            }
            tbr_posts.append(post)
        tbr_posts = json.dumps(tbr_posts)
        print('Rendering posts...')
        self.app.evaluate_javascript("render_posts('{}')".format(tbr_posts))
        return 1


    @htmlPy.Slot(str, result=str)
    def open_post(self,pid):
        print('Opening post '+pid)
        post = blockchan.get_post(pid)
        comments = post.get_comments()
        postt = {
        "post_id" : post.id,
        "author_name" : post.author_name,
        "timestamp" : post.timestamp,
        "subject" : post.subject,
        "comment" : post.comment,
        "image" : post.image,
        "comments" : []
        }
        for comment in comments:
            posttt = {
            "post_id" : comment.id,
            "author_name" : comment.author_name,
            "timestamp" : comment.timestamp,
            "subject" : comment.subject,
            "comment" : comment.comment,
            "image" : comment.image
            }
            postt['comments'].append(posttt)
        self.app.evaluate_javascript("open_post('{}')".format(json.dumps(postt)))
        print('Opening post')
