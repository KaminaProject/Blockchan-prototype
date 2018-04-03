import flask
from flask import Flask
from flask import request
app = Flask(__name__)
from blockchan_utils import *

with open('server_cfg.json',"r+") as conf_file:
    config = json.loads(conf_file.read())
    database = config['database']
    if os.path.isfile(database):
        conn = sqlite3.connect(database, check_same_thread=False)
        db = conn.cursor()
    else:
        conn = sqlite3.connect(database)
        db = conn.cursor()
        db.execute("CREATE TABLE posts (thread,author_name,id,timestamp,subject,comment,image)")
        db.execute("CREATE TABLE users (id,ip_addr)")
    user_id = config['user_id']
    exts = set(config['file_exts'])
    hash_length = config['hash_length']
    app.config['MAX_CONTENT_LENGTH'] = int(config['max_size'])*1024^2
    app.config['JSONIFY_MIMETYPE'] = config['json_mimetype']
    app.config['SECRET_KEY'] = config['secret_key']
    app.config['SESSION_COOKIE_NAME'] = config['session_name']


@app.route('/get_posts',methods=['GET'])
def get_posts():
    sort = request.args['sort']
    result = blockchan.get_post_ids(sort=sort)
    if result != 0:
        response = flask.make_response(flask.jsonify(result),200)
    else:
        response = flask.make_response('<h1>Error 400</h1><br>Bad arguments',400)
    return response


@app.route('/get_post',methods=['GET'])
def get_post():
    pid = request.args['pid']
    if blockchan.post_exists(pid):
        post = blockchan.get_post(pid)
        postt = {
        "post_id" : post.id,
        "author_name" : post.author_name,
        "timestamp" : post.timestamp,
        "subject" : post.subject,
        "comment" : post.comment,
        "image" : post.image,
        "comments" : []
        }
        if post.thread == 0:
            comments = post.get_comments()
            for comment in comments:
                postt['comments'].append(comment.id)
        resp = flask.make_response(flask.jsonify(postt),200)
    else:
        resp = flask.make_response('<h1>Error 404</h1><br>Post does not exist',404)
    return resp


@app.route('/get_comment_count',methods=['GET'])
def get_comment_count():
    pid = request.args['pid']
    if blockchan.post_exists(pid):
        if blockchan.get_post(pid).thread == 0:
            result = blockchan.get_post(pid).get_comment_count()
            resp = flask.make_response(flask.jsonify({'post_id':pid,'comment_count':result}),200)
        else:
            resp = flask.make_response('<h1>Error 405</h1><br>Post_ID is a comment',405)
    else:
        resp = flask.make_response('<h1>Error 404</h1><br>Post does not exist',404)
    return resp


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in exts
@app.route('/make_post',methods=['POST'])
def make_post():
    author_name = request.form['author_name']
    subject = request.form['subject'][:subject_l]
    comment = request.form['comment'][:comment_l]
    if 'file' in request.files and allowed_file(request.files['file'].filename):
        file = request.files['file']
    else:
        file = ''
    post = blockchan.make_post(author_name,subject,comment,file,user_id)
    if post.save_post():
        resp = flask.make_response(flask.jsonify({'post_id':post.id}),200)
    else:
        resp = flask.make_response('<h1>Error 500</h1><br>An error occured. Please try again later.',500)
    return resp


@app.route('/add_comment',methods=['GET','POST'])
def add_comment():
    pid = request.args['pid']
    author_name = request.form['author_name']
    subject = request.form['subject'][:subject_l]
    comment = request.form['comment'][:comment_l]
    if 'file' in request.files and allowed_file(request.files['file'].filename):
        file = request.files['file']
    else:
        file = ''
    reply = blockchan.make_post(author_name,subject,comment,file,user_id)
    if blockchan.post_exists(pid):
        if blockchan.get_post(pid).thread == 0:
            if blockchan.get_post(pid).add_comment(reply):
                resp = flask.make_response(flask.jsonify({'post_id':post.id,'reply_id':reply.id}),200)
            else:
                resp = flask.make_response('<h1>Error 500</h1><br>An error occured. Please try again later.',500)
        else:
            resp = flask.make_response('<h1>Error 405</h1><br>Post_ID is a comment',405)
    else:
        resp = flask.make_response('<h1>Error 404</h1><br>Post does not exist',404)
    return resp



app.run(debug=True,host='127.0.0.1',port=5000)
