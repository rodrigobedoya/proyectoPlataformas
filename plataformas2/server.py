from flask import Flask,render_template,session,request, jsonify, Response, redirect, url_for,flash
from sqlalchemy import or_, and_
from model import entities
from database import connector
from file_creator import create_html,create_ajax_html
from server_handling import format_to_file_name,format_to_url,rankShows
import json


app = Flask(__name__)
db = connector.Manager()
engine = db.createEngine()


#--------------------------------------------------------------------------------------------
@app.route('/')
def front_page():
    session.clear()
    session['logged'] = False
    session['askingData'] = False
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/registerUser',methods=['POST'])
def registerUser():
    data = request.form
    sessiondb = db.getSession(engine)
    users = sessiondb.query(entities.User)
    usernames = []
    emails = []
    for user in users:
        usernames.append(user.username)
        emails.append(user.email)
    if data['email'] in emails:
        return "This email is already linked to an account"
    if data['username'] in usernames:
        return "Username already taken"
    if data['password'] != data['copassword']:
        return "Passwords don't match"
    User = entities.User(
        position="user",
        username=data['username'],
        password=data['password'],
        email=data['email'],
        question=data['question'],
        answer=data['answer']
    )
    sessiondb.add(User)
    sessiondb.commit()
    return render_template('login.html')

@app.route('/termsOfService')
def tos():
    return "No one reads this"

@app.route('/dologin',  methods = ['POST'])
def do_login():

    data = request.form

    """
    #Uncomment this if statement only if database has been reset
    if data['username'] == "admin" and data['password'] == "admin":
        session['logged'] = True
        session['username'] = "admin"
        session['id'] = 1
        session['position'] = "admin"
        return redirect(url_for('manage'))
    """

    sessiondb = db.getSession(engine)
    user = sessiondb.query(entities.User).filter(entities.User.username == data['username']).first()
    if user == None:
        return redirect(url_for('front_page'))
    elif user.password == data['password']:
        session['logged'] = True
        session['username'] = user.username
        session['user_id'] = user.id
        session['position'] = user.position
        if(user.position == 'admin'):
            return redirect(url_for('manage'))
        else:
            return redirect(url_for('lookup'))
    return redirect(url_for('front_page'))

@app.route('/loggedAs')
def logged_as():
    try:
        return "Hi "+session['username']+". You have "+session['position']+" powers."
    except Exception as e:
        return "You need to log in first!"
#--------------------------------------------------------------------------------------------

@app.route('/management')
def manage():
    if session['logged'] == False:
        return "You need to log in first!"
    elif session['position'] != "admin":
        return "Only admins may do this"
    return render_template('admin_interface.html')

@app.route('/search')
def lookup():
    if session['logged'] == False:
        return "You need to log in first!"
    return render_template('user_interface.html')

@app.route('/search_for_content', methods = ['POST'])
def search():
    if session['logged'] == False:
        return "You need to log in first!"
    data = request.form
    looking_for = format_to_file_name(data['search'])
    nonsearchable_htmls = ["login","userinterface","admininterface","crudshows","crudusers","ranking","error404","showslist"]
    if looking_for not in nonsearchable_htmls:
        try:
            render_template('shows/'+looking_for+'.html')
            return redirect('/s/'+looking_for)
        except Exception as e:
            return render_template('error404.html')
    else:
        return "You don't have access to this page at the moment"


@app.route('/s/<name>')
def rateShow(name):
    if session['logged'] == False:
        return "You need to log in first!"
    string = name+'.html'
    try:
        return render_template('shows/'+string)
    except Exception as e:
        return render_template('error404.html')

@app.route('/showList')
def showlist():
    if session['logged'] == False:
        return "You need to log in first!"
    session['askingData'] = True
    return render_template('showslist.html')

@app.route('/updateShows')
def create_htmls():
    if session['logged'] == False:
        return "You need to log in first!"
    elif session['position'] != "admin":
        return "Only admins may do this"
    sessiondb = db.getSession(engine)
    shows = sessiondb.query(entities.Show)
    for show in shows:
        create_ajax_html(show)
    return redirect(url_for('manage'))

@app.route('/static/manageUsers')
def mUsers():
    if session['logged'] == False:
        return "You need to log in first!"
    elif session['position'] != "admin":
        return "Only admins may do this"
    return render_template('cruds/crud_users.html')

@app.route('/static/manageShows')
def mShows():
    if session['logged'] == False:
        return "You need to log in first!"
    elif session['position'] != "admin":
        return "Only admins may do this"
    return render_template('cruds/crud_shows.html')

@app.route('/add',methods = ['POST'])
def add():
    if session['logged'] == False:
        return "You need to log in first!"
    session['askingData'] = True

    data = request.form
    showName = data['showName']



    rating = data['star']
    sessiondb = db.getSession(engine)
    shows = sessiondb.query(entities.Show)
    show = sessiondb.query(entities.Show).filter(entities.Show.name == showName).first()

    user_id = str(session['user_id'])
    userRatings = sessiondb.query(entities.Vote).filter(entities.Vote.voterId == user_id)
    ratedShows = []
    for userRating in userRatings:
        if userRating != None:
            ratedShows.append(userRating.showId)


    #if user hasnt rated this show yet
    if str(show.id) not in ratedShows:
        if(show.votes == "0"):
            show.votes = "1"
            show.rating = str(int(rating))
        else:
            show.rating = str(round(float(show.rating)+(float(rating)-float(show.rating))/(int(show.votes)+1),12))
            show.votes = str(int(show.votes) + 1)
        sessiondb.commit()

        vote = entities.Vote(
            voterId=user_id,
            showId=str(show.id),
            rating=str(rating)
        )
        sessiondb.add(vote)
        sessiondb.commit()
    #if user has already rated this show
    else:
        if(show.votes == "1"):
            show.rating = str(int(rating))
        else:
            #subtract old value
            value = sessiondb.query(entities.Vote).filter(entities.Vote.voterId == user_id,entities.Vote.showId == str(show.id)).first()
            value = float(value.rating)
            average = float(show.rating)
            nbValues = float(show.votes)
            show.rating = str(round(((average * nbValues) - value) / (nbValues - 1),12))
            show.votes = str(int(show.votes)-1)
            sessiondb.commit()
            #add new value
            show.rating = str(round(float(show.rating) + (float(rating) - float(show.rating)) / (int(show.votes) + 1), 12))
            show.votes = str(int(show.votes) + 1)
        sessiondb.commit()
        oldVote = sessiondb.query(entities.Vote).filter(entities.Vote.voterId == user_id,entities.Vote.showId == str(show.id)).first()
        oldVote.rating = rating
        sessiondb.commit()
    #RANK SHOWS
    rankedData = rankShows(shows)
    i = 0
    for item in rankedData:
        i = i + 1
        for show in shows:
            if show.name == item['name']:
                show.rank = i
    sessiondb.commit()
    return redirect("/s/"+format_to_file_name(showName))
    #return "You rated "+data['showName']+" with " + data['star'] +" stars"

@app.route('/getTop10')
def top10():
    if session['logged'] == False:
        return "You need to log in first!"
    sessiondb = db.getSession(engine)
    rankedData = []
    for i in range(1,11):
        show = sessiondb.query(entities.Show).filter(entities.Show.rank == i).first()
        if show == None:
            break
        else:
            rankedData.append(show)
    return Response(json.dumps(rankedData, cls=connector.AlchemyEncoder), mimetype='application/json')


@app.route('/seeRanking')
def top():
    session['askingData'] = True
    if session['logged'] == False:
        return "You need to log in first!"
    return render_template("ranking.html")


@app.route('/json/<name>')
def getJsonOfShow(name):
    if session['logged'] == False:
        return "You need to log in first!"
    sessiondb = db.getSession(engine)
    shows = sessiondb.query(entities.Show)
    data = []
    for show in shows:
        if format_to_file_name(show.name) == name:
            data.append(show)
            break
    return Response(json.dumps(data, cls=connector.AlchemyEncoder),mimetype='application/json')

@app.route('/resetVotes')
def reset_votes():
    if session['logged'] == False:
        return "You need to log in first!"
    if session['position'] != "admin":
        return "This must only be done by an admin!"
    sessiondb = db.getSession(engine)
    shows = sessiondb.query(entities.Show)
    votes = sessiondb.query(entities.Vote)
    i = 1
    for show in shows:
        show.rating = "0"
        show.rank = str(i)
        show.votes = "0"
        i=i+1
    for vote in votes:
        sessiondb.delete(vote)
    sessiondb.commit()
    return redirect(url_for('manage'))

#--------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------
#----------DATABASE CRUD HANDLING------------------------------------------------------------
#--------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------



@app.route('/static/<content>')
def content(content):
    if session['logged'] == False:
        return "You need to log in first!"
    elif session['position'] != "admin":
        return "Only admins may do this"
    try:
        return render_template('cruds/'+content)
    except Exception as e:
        return "You either made a typo or the content you're looking for doesn't exist"

#--------------------------------------------------------------------------------------------

@app.route('/votes', methods = ['GET'])
def get_votes():
    if session['logged'] == False:
        return "You need to log in first!"
    elif session['position'] != "admin":
        return "Only admins may do this"
    sessiondb = db.getSession(engine)
    votes = sessiondb.query(entities.Vote)
    data = []
    for vote in votes:
        data.append(vote)
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype='application/json')



@app.route('/users', methods = ['GET'])
def get_users():
    if session['logged'] == False:
        return "You need to log in first!"
    elif session['position'] != "admin":
        return "Only admins may do this"
    sessiondb = db.getSession(engine)
    users = sessiondb.query(entities.User)
    data = []
    for user in users:
        data.append(user)

    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype='application/json')

@app.route('/users/<id>', methods = ['GET'])
def get_user(id):
    if session['logged'] == False:
        return "You need to log in first!"
    elif session['position'] != "admin":
        return "Only admins may do this"
    sessiondb = db.getSession(engine)
    users = sessiondb.query(entities.User).filter(entities.User.id == id)
    for user in users:
        js = json.dumps(user, cls=connector.AlchemyEncoder)
        return  Response(js, status=200, mimetype='application/json')

    message = { "status": 404, "message": "Not Found"}
    return Response(message, status=404, mimetype='application/json')


@app.route('/users', methods = ['DELETE'])
def remove_user():
    if session['logged'] == False:
        return "You need to log in first!"
    elif session['position'] != "admin":
        return "Only admins may do this"
    id = request.form['key']
    sessiondb = db.getSession(engine)
    users = sessiondb.query(entities.User).filter(entities.User.id == id)
    for user in users:
        sessiondb.delete(user)
    sessiondb.commit()
    return "Deleted User"


@app.route('/users', methods = ['POST'])
def create_user():
    if session['logged'] == False:
        return "You need to log in first!"
    elif session['position'] != "admin":
        return "Only admins may do this"
    c =  json.loads(request.form['values'])
    #c = request.get_json(silent=True)
    print(c)
    user = entities.User(
        position=c['position'],
        username=c['username'],
        password=c['password'],
        email=c['email'],
        question=c['question'],
        answer=c['answer']
    )
    sessiondb = db.getSession(engine)
    sessiondb.add(user)
    sessiondb.commit()
    return 'Created User'

@app.route('/users', methods = ['PUT'])
def update_user():
    if session['logged'] == False:
        return "You need to log in first!"
    elif session['position'] != "admin":
        return "Only admins may do this"
    sessiondb = db.getSession(engine)
    id = request.form['key']
    user = sessiondb.query(entities.User).filter(entities.User.id == id).first()
    c =  json.loads(request.form['values'])
    for key in c.keys():
        setattr(user, key, c[key])
    sessiondb.add(user)
    sessiondb.commit()
    return 'Updated User'


#--------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------


@app.route('/shows', methods = ['GET'])
def get_shows():
    if session['logged'] == False:
        return "You need to log in first!"
    if session['askingData'] ==True:
        session['askingData'] = False
    elif session['position'] != "admin":
        return "Only admins may do this"
    sessiondb=db.getSession(engine)
    shows = sessiondb.query(entities.Show)
    data = []
    for show in shows:
        data.append(show)

    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype='application/json')

@app.route('/shows/<id>', methods = ['GET'])
def get_show(id):
    if session['logged'] == False:
        return "You need to log in first!"
    elif session['position'] != "admin":
        return "Only admins may do this"
    sessiondb = db.getSession(engine)
    shows = sessiondb.query(entities.Show).filter(entities.Show.id == id)
    for show in shows:
        js = json.dumps(show, cls=connector.AlchemyEncoder)
        return  Response(js, status=200, mimetype='application/json')

    message = { "status": 404, "message": "Not Found"}
    return Response(message, status=404, mimetype='application/json')


@app.route('/shows', methods = ['DELETE'])
def remove_show():
    if session['logged'] == False:
        return "You need to log in first!"
    elif session['position'] != "admin":
        return "Only admins may do this"
    id = request.form['key']
    sessiondb = db.getSession(engine)
    shows = sessiondb.query(entities.Show).filter(entities.Show.id == id)
    for show in shows:
        sessiondb.delete(show)
    sessiondb.commit()
    return "Deleted Show"


@app.route('/shows', methods = ['POST'])
def create_show():
    if session['logged'] == False:
        return "You need to log in first!"
    elif session['position'] != "admin":
        return "Only admins may do this"
    c =  json.loads(request.form['values'])
    #c = request.get_json(silent=True)
    print(c)
    show = entities.Show(
        name=c['name'],
        imageurl=c['imageurl'],
        description=c['description'],
        seasons=c['seasons'],
        episodes=c['episodes'],
        votes=str(0),
        rating=str(0),
        rank=str(1)
    )
    sessiondb = db.getSession(engine)
    sessiondb.add(show)
    sessiondb.commit()


    #ORDER SHOWS(BASICALLY PUT NEW SHOW AT THE END)
    shows = sessiondb.query(entities.Show)
    rankedData = rankShows(shows)
    i = 0
    for item in rankedData:
        i = i + 1
        for show in shows:
            if show.name == item['name']:
                show.rank = i
    sessiondb.commit()

    return 'Created Show'



@app.route('/shows', methods = ['PUT'])
def update_show():
    if session['logged'] == False:
        return "You need to log in first!"
    elif session['position'] != "admin":
        return "Only admins may do this"
    sessiondb = db.getSession(engine)
    id = request.form['key']
    show = sessiondb.query(entities.Show).filter(entities.Show.id == id).first()
    c =  json.loads(request.form['values'])
    for key in c.keys():
        setattr(show, key, c[key])
    sessiondb.add(show)
    sessiondb.commit()
    return 'Updated Show'

app.secret_key = "I'm a key"

if __name__ == '__main__':
    TEMPLATES_AUTO_RELOAD = True
    app.run()

