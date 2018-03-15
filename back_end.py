import htmlPy
import json
from blockchan_utils import blockchan

with open('config.json',"r+") as conf_file:
    config = json.loads(conf_file.read())
    if config['user_id'] == 0:
        user_id = blockchan_utils.get_user_id()
        config['user_id'] = user_id
        conf_file.truncate(0)
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
        post = blockchan.pack_post(subject,comment,file,user_id)
        post_id = json.loads(post)['post_id']
        p_file = open("data/posts/"+post_id+".json","w")
        p_file.write(post)
        p_file.close()
        print('Post '+post_id+' written successfully')
        self.app.evaluate_javascript('alert("Post created successfully")')
        self.app.evaluate_javascript('document.getElementById("form").reset();')
        self.app.evaluate_javascript('new_thread()')
