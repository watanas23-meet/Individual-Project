from urllib import response
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from flask import session as login_session
import requests,json, sys
import pyrebase


config = {
  "apiKey": "AIzaSyCz4TxQUGk3PPs96-oD4vOuX9DwmEyY7NM",
  "authDomain": "meettutorial-cda45.firebaseapp.com",
  "projectId": "meettutorial-cda45",
  "storageBucket": "meettutorial-cda45.appspot.com",
  "messagingSenderId": "314514460185",
  "appId": "1:314514460185:web:fc5e02feb1e45076ae6488",
  "databaseURL": "https://meettutorial-cda45-default-rtdb.europe-west1.firebasedatabase.app/"
};


firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

app = Flask(  # Create a flask app
    __name__,
    template_folder='templates',  # Name of html file folder
    static_folder='static'  # Name of directory for static files
)

app.config['SECRET_KEY'] = 'super-secret-key'


@app.route('/', methods=['GET', 'POST'])
def signin():
    print('Hello world!', file=sys.stderr)
    error=""
    if request.method == "POST":
        login_session['email'] = request.form['email']
        login_session['password'] = request.form['password']
        try:
            login_session['user'] = user = auth.sign_in_with_email_and_password(login_session["email"], login_session["password"])
            return(redirect('main'))
        except:
            error="problem"
    else: 
        return render_template("signin.html")



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error=""
    if request.method == "POST":
        login_session['email']= request.form['email']
        login_session['password'] = request.form['password']
        login_session['full_name']= request.form['full_name']
        login_session['fav']= request.form['fav']
        try:
            login_session['user'] = auth.create_user_with_email_and_password(login_session["email"], login_session["password"])
            user= {"email": request.form['email'],"password": request.form['password'],"full_name": request.form['full_name'],"fav": request.form['fav']}
            user = db.child("Users").child(login_session['user']['localId']).set(user)
            return redirect('main')
        except:
            return render_template("signup.html", error="problem")
    else:
        return render_template("signup.html")


@app.route('/signout')
def signout():
    login_session['user'] = None
    auth.current_user = None
    return redirect(url_for('signin'))


@app.route('/main', methods=['GET', 'POST'])
def main():
    isFetched = False
    if request.method == "POST":
        api_url =  "https://api.edamam.com/search?q=" + request.form['search'] + "&app_id=e49b953f&app_key=9f1cd52de97f5d9e826d37dae13ea45d"
        response = requests.get(api_url)
        data = json.loads(response.content)
        isFetched = True
        print(data, file=sys.stderr)
        print(type(data["to"]), file=sys.stderr)
        if data["more"] == False:
            isFetched = False
            return render_template("main.html", name=login_session['full_name'], error="Come on bro you can even eat this thing that you wrote !! :angry_face;" ,isFetched = isFetched)
        else:
            return render_template("main.html", name=login_session['full_name'], data=data, isFetched = isFetched)


    return render_template("main.html", name=login_session['full_name'] ,isFetched = isFetched)

@app.route('/recommended', methods=['GET', 'POST'])
def recommend():
    api_url =  "https://api.edamam.com/search?q=" + db.child("Users").child(login_session['user']['localId']).child("fav").get().val() + "&app_id=e49b953f&app_key=9f1cd52de97f5d9e826d37dae13ea45d"
    response = requests.get(api_url)
    data = json.loads(response.content)
    isFetched = True
    print(data, file=sys.stderr)
    return render_template('recommended.html', data = data, fav = db.child("Users").child(login_session['user']['localId']).child("fav").get().val() )

#app.route('/all_tweets', methods=['GET', 'POST'])
#def all_tweets():
    #return render_template("tweets.html", tweets=db.child("Tweets").get().val())



if __name__ == '__main__':
    app.run(debug=True)