from flask import Flask,render_template,session,request, jsonify, Response, redirect, url_for
from model import entities
from database import connector
import json

def format(a):
    a = a.replace(" ","_")
    return a.lower()



app = Flask(__name__)
db = connector.Manager()
cache={}
cache2={}
engine = db.createEngine()


#--------------------------------------------------------------------------------------------
@app.route('/')
def front_page():
    return render_template('login.html')

@app.route('/dologin',  methods = ['POST'])
def do_login():

    data = request.form
    session = db.getSession(engine)
    users = session.query(entities.User)
    for user in users:
        if user.username == data['username'] and user.password == data['password']:
            if(user.position == 'admin'):
                return redirect(url_for('manage'))
            else:
                return redirect(url_for('lookup'))
    return render_template('login.html')


#--------------------------------------------------------------------------------------------

@app.route('/management')
def manage():
    return render_template('admin_interface.html')

@app.route('/search')
def lookup():
    return render_template('user_interface.html')

@app.route('/search_for_content', methods = ['POST'])
def search():
    data = request.form
    looking_for = format(data['search'])
    if looking_for != "login" and looking_for != "user_interface":
        try:
            return render_template(looking_for+'.html')

        except Exception as e:
            return 'This show has not been added yet. Click here to suggest the admin'
    else:
        return "You don't have access to this page at the moment"

html_string = """
<html>
<head>
</head>
<body>
<form action="/add", method="post">
    <input type="text" name="showname" value="ChangeInFunction" readonly>
    <input type="number" placeholder="rating" name="rating">
    <button type="submit">Send</button>
</form>
</body>
</html>
"""


@app.route('/updateShows')
def create_htmls():
    session = db.getSession(engine)
    shows = session.query(entities.Show)
    name = ""
    for show in shows:
        name = show.name+".html"
        try:
            f = open("templates/"+name)
            f.write(html_string)
            f.close()
        except Exception as e:
            f = open("templates/"+name, "w+")
            f.write(html_string)
            f.close()
    return redirect(url_for('manage'))

@app.route('/static/manageUsers')
def mUsers():
    return render_template('crud_users.html')

@app.route('/static/manageShows')
def mShows():
    return render_template('crud_shows.html')

@app.route('/add',methods = ['POST'])
def add():
    data = request.form
    return "You rated "+data['showname']+" with " + data['rating'] +" stars"


#--------------------------------------------------------------------------------------------


@app.route('/static/<content>')
def content(content):
    return render_template(content)

#--------------------------------------------------------------------------------------------




@app.route('/users', methods = ['GET'])
def get_users():
    key = 'getUsers'
    if key not in cache.keys():
        session = db.getSession(engine)
        dbResponse = session.query(entities.User)
        cache[key] = dbResponse;
        print("From DB")
    else:
        print("From Cache")

    users = cache[key]
    data = []
    for user in users:
        data.append(user)

    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype='application/json')

@app.route('/users/<id>', methods = ['GET'])
def get_user(id):
    session = db.getSession(engine)
    users = session.query(entities.User).filter(entities.User.id == id)
    for user in users:
        js = json.dumps(user, cls=connector.AlchemyEncoder)
        return  Response(js, status=200, mimetype='application/json')

    message = { "status": 404, "message": "Not Found"}
    return Response(message, status=404, mimetype='application/json')


@app.route('/users', methods = ['DELETE'])
def remove_user():
    id = request.form['key']
    session = db.getSession(engine)
    users = session.query(entities.User).filter(entities.User.id == id)
    for user in users:
        session.delete(user)
    session.commit()
    return "Deleted User"


@app.route('/users', methods = ['POST'])
def create_user():
    c =  json.loads(request.form['values'])
    #c = request.get_json(silent=True)
    print(c)
    user = entities.User(
        id=c['id'],
        position=c['position'],
        username=c['username'],
        password=c['password']
    )
    session = db.getSession(engine)
    session.add(user)
    session.commit()
    return 'Created User'

@app.route('/users', methods = ['PUT'])
def update_user():
    session = db.getSession(engine)
    id = request.form['key']
    user = session.query(entities.User).filter(entities.User.id == id).first()
    c =  json.loads(request.form['values'])
    for key in c.keys():
        setattr(user, key, c[key])
    session.add(user)
    session.commit()
    return 'Updated User'


#--------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------


@app.route('/shows', methods = ['GET'])
def get_shows():
    key = 'getShows'
    if key not in cache2.keys():
        session = db.getSession(engine)
        dbResponse = session.query(entities.Show)
        cache2[key] = dbResponse
        print("From DB")
    else:
        print("From Cache")

    shows = cache2[key]
    data = []
    for show in shows:
        data.append(show)

    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype='application/json')

@app.route('/shows/<id>', methods = ['GET'])
def get_show(id):
    session = db.getSession(engine)
    shows = session.query(entities.Show).filter(entities.Show.id == id)
    for show in shows:
        js = json.dumps(show, cls=connector.AlchemyEncoder)
        return  Response(js, status=200, mimetype='application/json')

    message = { "status": 404, "message": "Not Found"}
    return Response(message, status=404, mimetype='application/json')


@app.route('/shows', methods = ['DELETE'])
def remove_show():
    id = request.form['key']
    session = db.getSession(engine)
    shows = session.query(entities.Show).filter(entities.Show.id == id)
    for show in shows:
        session.delete(show)
    session.commit()
    return "Deleted Show"


@app.route('/shows', methods = ['POST'])
def create_show():
    c =  json.loads(request.form['values'])
    #c = request.get_json(silent=True)
    print(c)
    show = entities.Show(
        id=c['id'],
        name=c['name'],
        imageurl=c['imageurl'],
        description=c['description'],
        rating=c['rating'],
        rank=c['rank']
    )
    session = db.getSession(engine)
    session.add(show)
    session.commit()
    return 'Created Show'



@app.route('/shows', methods = ['PUT'])
def update_show():
    session = db.getSession(engine)
    id = request.form['key']
    show = session.query(entities.Show).filter(entities.Show.id == id).first()
    c =  json.loads(request.form['values'])
    for key in c.keys():
        setattr(show, key, c[key])
    session.add(show)
    session.commit()
    return 'Updated Show'







if __name__ == '__main__':
    app.run()
