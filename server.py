import flask
from flask import Flask,session
from flask import request
app = Flask(__name__)
from blockchan_utils import *

#Config parsing
with open('server_cfg.json',"r+") as conf_file:
    config = json.loads(conf_file.read())
    user_id = config['user_id']
    exts = set(config['file_exts'])
    hash_length = int(config['hash_length'])
    session_expire = int(config['max_session_time'])
    app.config['MAX_CONTENT_LENGTH'] = int(config['max_size'])*1024^2
    app.config['JSONIFY_MIMETYPE'] = config['json_mimetype']
    app.config['SECRET_KEY'] = config['secret_key']
    app.config['SESSION_COOKIE_NAME'] = config['session_name']

#Login function
@app.route('/login',methods=['GET','POST'])
def login():
    if 'bid' in request.args:
        id = request.args['bid']
    elif 'bid' in request.cookies:
        id = request.cookies['bid']
    else:
        return flask.make_response('<h1>Error 400</h1><br>No ID provided or found. Go register',400)
    if 's_bid' in session:
        db.execute("SELECT invalid FROM sessions WHERE sid=?",(session['s_bid'],))
        if not db.fetchone()[0]:
            return flask.make_response('<h1>Error 403</h1><br>You are already logged in',403)
    db.execute("SELECT ip_addr FROM users WHERE id=?",(id,))
    ip_addr = db.fetchone()
    if ip_addr:
        print(ip_addr)
        print(id)
        if ip_addr[0] == request.remote_addr:
            session_id = make_hash(id,get_timestamp(),length=64)
            session['s_bid'] = session_id
            db.execute("INSERT INTO sessions(bid,sid,time) values(?,?,?)",(id,session_id,get_epoch()))
            conn.commit()
            resp = flask.make_response(flask.jsonify({'session_id':session_id}))
        else:
            resp = flask.make_response('<h1>Error 403</h1><br>The server could not verify your IP Address. Contact support',403)
    else:
        resp = flask.make_response('<h1>Error 403</h1><br>The server could not find you in the database. Go register',403)
    return resp

#Logout function
@app.route('/logout')
def logout():
    if 's_bid' in session:
        id = session['s_bid']
    else:
        return flask.make_response('<h1>Error 403</h1><br>You are not logged in',403)
    db.execute("SELECT bid FROM sessions WHERE sid=?",(id,))
    result = db.fetchone()
    if not result:
        return flask.make_response('<h1>Error 403</h1><br>You dont exist',403)
    bid = result[0]
    if db.execute("UPDATE sessions SET invalid=1 WHERE sid=?",(id,)):
        conn.commit()
        return flask.make_response(flask.jsonify({'blockchan_id':bid,'session_id':id,'time':get_timestamp()}),200)
    else:
        return flask.make_response('<h1>Error 500</h1><br>An error occured. Please try again later',500)

#Register function
@app.route('/register',methods=['GET','POST'])
def register():
    if 'bid' in request.cookies or 's_bid' in session:
        return flask.make_response('<h1>Error 403</h1><br>You are already registered or logged in',403)
    username = request.args['username']
    ip_addr = request.remote_addr
    db.execute("SELECT id FROM users WHERE username=?",(username,))
    if db.fetchone():
        return flask.make_response('That username is already taken',403)
    db.execute("SELECT id FROM users WHERE ip_addr=?",(ip_addr,))
    if db.fetchone():
        return flask.make_response('That IP Address is already registered. Contact support',403)
    user_id = make_hash(ip_addr,get_timestamp())
    if db.execute("INSERT INTO users(username,id,ip_addr,reg_date) values(?,?,?,?)",(username,user_id,ip_addr,get_timestamp())):
        conn.commit()
        resp = flask.make_response(flask.jsonify({'blockchan_id':user_id,'ip_addr':ip_addr,'username':username,'registration_date':get_timestamp()}),201)
        resp.set_cookie('bid',user_id,expires=int(get_epoch())+315569260)
    else:
        resp = flask.make_response('<h1>Error 500</h1><br>An error occured. Please try again later',500)
    return resp

#Valid session check
def valid_session():
    if 's_bid' in session and 'bid' in request.cookies:
        id = session['s_bid']
        bid = request.cookies['bid']
    else:
        return 0
    db.execute("SELECT time,bid,invalid FROM sessions WHERE sid=?",(id,))
    result = db.fetchone()
    if result and get_epoch() - int(result[0]) < session_expire and result[1] == bid and not result[2]:
        return 1
    else:
        return 0

#Gets all post IDs currently on the server
@app.route('/get_posts',methods=['GET'])
def get_posts():
    if not valid_session():
        return flask.make_response('<h1>Error 401</h1><br>Please login or register first',401)
    sort = request.args['sort']
    result = blockchan.get_post_ids(sort=sort)
    if result != 0:
        response = flask.make_response(flask.jsonify(result),200)
    else:
        response = flask.make_response('<h1>Error 400</h1><br>Bad arguments',400)
    return response


#Gets a specific post by ID
@app.route('/get_post',methods=['GET'])
def get_post():
    if not valid_session():
        return flask.make_response('<h1>Error 401</h1><br>Please login or register first',401)
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


#Gets the comment count of a post
@app.route('/get_comment_count',methods=['GET'])
def get_comment_count():
    if not valid_session():
        return flask.make_response('<h1>Error 401</h1><br>Please login or register first',401)
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


#Handy little function to check if a file is allowed (aka is an image)
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in exts
#Makes a post and saves it
@app.route('/make_post',methods=['POST'])
def make_post():
    if not valid_session():
        return flask.make_response('<h1>Error 401</h1><br>Please login or register first',401)
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


#Adds a comment to a post
@app.route('/add_comment',methods=['GET','POST'])
def add_comment():
    if not valid_session():
        return flask.make_response('<h1>Error 401</h1><br>Please login or register first',401)
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
                resp = flask.make_response(flask.jsonify({'post_id':post.id,'reply_id':reply.id}),201)
            else:
                resp = flask.make_response('<h1>Error 500</h1><br>An error occured. Please try again later.',500)
        else:
            resp = flask.make_response('<h1>Error 405</h1><br>Post_ID is a comment',405)
    else:
        resp = flask.make_response('<h1>Error 404</h1><br>Post does not exist',404)
    return resp



app.run(debug=True,host='127.0.0.1',port=5000)
