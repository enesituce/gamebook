from flask import Flask , render_template , flash , redirect , url_for , session , logging , request
from flask_mysqldb import MySQL
from wtforms import Form, StringField , IntegerField, TextAreaField , PasswordField , validators
from functools import wraps

#user registiration

class RegisterForm(Form):
    name = StringField("Name Surname")
    username = StringField("Username")
    email = StringField("E-mail")
    age = IntegerField("Age")
    gameplay_preference=StringField("Gameplay preference(casual/competitive)")
    gender = StringField("Gender")
    password=PasswordField("Password")

class LoginForm(Form):
    username = StringField("Username")
    password = PasswordField("Password")


class PostForm(Form):
    title = StringField("Post Title", validators=[validators.Length(min = 5, max = 50)])
    content = TextAreaField("Post Content",validators=[validators.Length(min = 10)])
    gameName=StringField("Enter the game name.")

class FriendRequest(Form):
    to_user=StringField("Username")


app= Flask(__name__)
app.secret_key="gamebook"

app.config["MYSQL_HOST"]="localhost"
app.config["MYSQL_USER"]="root"
app.config["MYSQL_PASSWORD"]=""
app.config["MYSQL_DB"]="gamebook"
app.config["MYSQL_CURSORCLASS"]="DictCursor"


mysql = MySQL(app)


@app.route("/")

def index():
    return render_template("index.html")



@app.route("/login", methods=["GET","POST"])

def login():
    form=LoginForm(request.form)
    if request.method == "POST":
        username=form.username.data
        password_entered = form.password.data

        cursor=mysql.connection.cursor()

        query = "Select * from users where username = %s"

        result = cursor.execute(query,(username,))

        if result>0:
            data = cursor.fetchone()
            user_id=data["id"]
            real_password = data["password"]
            username=data["username"]
            name = data["name"]
            email=data["email"]
            gender=data["gender"]
            gameplay_preference = data["gameplay_preference"]
            age =data["age"]
            if password_entered==real_password:
                flash("Login success!","success")

                session["logged_in"]=True
                session["username"] = username
                session["name"] = name
                session["email"]= email
                session["gender"] = gender
                session["gameplay_preference"]= gameplay_preference
                session["age"] = age
                session["id"] = user_id
                return redirect(url_for("profile"))
            else:
                flash("Wrong Password!","danger")
                return redirect(url_for("login"))

        else:
            flash("Wrong username", "danger")
            return redirect(url_for("login"))

    return render_template("login.html",form=form)


@app.route("/profile")
def profile():
    return render_template("profile.html")


#sign up function
@app.route("/signup",methods = ["GET","POST"])
def signup():
    form = RegisterForm(request.form)

    if request.method == "POST":
        name=form.name.data
        username=form.username.data
        email = form.email.data
        age = form.age.data
        gameplay_preference = form.gameplay_preference.data
        gender = form.gender.data
        password=form.password.data
        cursor = mysql.connection.cursor()
        addToDb = "Insert into users(name,username,email,age,gameplay_preference,gender,password) VALUES(%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(addToDb,(name,username,email,age,gameplay_preference,gender,password))
        mysql.connection.commit()
        cursor.close()
        flash("Signed up succesfully!","success")
        return redirect(url_for("login"))
    
    else:
        return render_template("signup.html",form=form)

#edit account
@app.route("/editacc/<string:id>", methods = ["GET","POST"])

def editacc(id):
    if request.method == "GET":
        cursor=mysql.connection.cursor()
        q = "Select * from users where id = %s"
        result = cursor.execute(q,(id,))

        if result == 1:
            user = cursor.fetchone()
            form = RegisterForm()
            form.name.data = user["name"]
            form.email.data = user ["email"]
            form.username.data = user ["username"]
            form.age.data = user ["age"]
            form.gameplay_preference.data = user ["gameplay_preference"]
            form.gender.data = user ["gender"]
            return render_template("editacc.html",form=form)
    else:
        form = RegisterForm(request.form)
        newName = form.name.data
        newEmail = form.email.data
        newUsername = form.username.data
        newAge = form.age.data
        newGameplay_preference = form.gameplay_preference.data
        newGender = form.gender.data

        session["username"] = newUsername
        session["name"] = newName
        session["email"]= newEmail
        session["gender"] = newGender
        session["gameplay_preference"]= newGameplay_preference
        session["age"] = newAge

        p="Update users Set name=%s,email=%s,username=%s,age=%s,gameplay_preference=%s,gender=%s where id = %s"
        cursor = mysql.connection.cursor()
        cursor.execute(p,(newName,newEmail,newUsername,newAge,newGameplay_preference,newGender,id))
        mysql.connection.commit()
        flash("Your account updated succesfully!","success")
        return redirect(url_for("profile"))

    return



#edit post
@app.route("/editpost/<string:id>", methods = ["GET","POST"])

def editpost(id):
    if request.method == "GET":
        cursor=mysql.connection.cursor()
        q = "Select * from posts where id = %s"
        result = cursor.execute(q,(id,))

        if result == 1:
            post = cursor.fetchone()
            form = PostForm()
            form.title.data = post["title"]
            form.content.data = post ["content"]
            form.gameName.data = post ["game_name"]
            return render_template("editpost.html",form=form)
    else:
        form = PostForm(request.form)
        newTitle = form.title.data
        newContent = form.content.data
        newGameName = form.gameName.data
        

        p="Update posts Set title=%s,content=%s,game_name=%s where id = %s"
        cursor = mysql.connection.cursor()
        cursor.execute(p,(newTitle,newContent,newGameName,id))
        mysql.connection.commit()
        flash("Your post updated succesfully!","success")
        return redirect(url_for("channels"))
    
    return

@app.route("/deletepost/<string:id>")
def deletepost(id):
    cursor=mysql.connection.cursor()
    q = "Select * from posts where id = %s"
    result = cursor.execute(q,(id,))

    if result>0:
        p = "Delete from posts where id=%s"
        cursor.execute(p,(id,))
        mysql.connection.commit()
        return redirect(url_for("channels"))


#delete account
@app.route("/deleteacc/<string:id>")

def deleteacc(id):
    cursor=mysql.connection.cursor()
    q = "Select * from users where id = %s"
    result = cursor.execute(q,(id,))

    if result>0:
        p = "Delete from users where id=%s"
        cursor.execute(p,(id,))
        mysql.connection.commit()
        session["logged in"] = False
        return redirect(url_for("logout"))

@app.route("/channels")

def channels():
    return render_template("channels.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/valorant", methods = ["GET","POST"])
def valorant():
    form = PostForm(request.form)
    if request.method == "POST" and form.validate():
        title = form.title.data
        content = form.content.data
        gameName=form.gameName.data
        cursor=mysql.connection.cursor()
        q = ("Insert into posts(title,creator,content,game_name) VALUES(%s,%s,%s,%s) ")
        cursor.execute(q,(title,session["username"],content, gameName))
        mysql.connection.commit()
        cursor.close()
        flash("Posted succesfully!","success")
        return redirect(url_for("valorant"))

    cursor = mysql.connection.cursor()
    p = "Select * from posts where game_name = %s "
    result = cursor.execute(p,("valorant",))

    if result > 0:
        posts = cursor.fetchall()
        return render_template("valorant.html",posts = posts,form=form)
    return render_template("valorant.html",form = form)

@app.route("/csgo", methods = ["GET","POST"])
def csgo():
    form = PostForm(request.form)
    if request.method == "POST" and form.validate():
        title = form.title.data
        content = form.content.data
        gameName=form.gameName.data
        cursor=mysql.connection.cursor()
        q = ("Insert into posts(title,creator,content,game_name) VALUES(%s,%s,%s,%s) ")
        cursor.execute(q,(title,session["username"],content, gameName))
        mysql.connection.commit()
        cursor.close()
        flash("Posted succesfully!","success")
        return redirect(url_for("csgo"))

    cursor = mysql.connection.cursor()
    p = "Select * from posts where game_name = %s "
    result = cursor.execute(p,("csgo",))

    if result > 0:
        posts = cursor.fetchall()
        return render_template("csgo.html",posts = posts,form=form)
    return render_template("csgo.html",form = form)


@app.route("/lol", methods = ["GET","POST"])
def lol():
    form = PostForm(request.form)
    if request.method == "POST" and form.validate():
        title = form.title.data
        content = form.content.data
        gameName=form.gameName.data
        cursor=mysql.connection.cursor()
        q = ("Insert into posts(title,creator,content,game_name) VALUES(%s,%s,%s,%s) ")
        cursor.execute(q,(title,session["username"],content, gameName))
        mysql.connection.commit()
        cursor.close()
        flash("Posted succesfully!","success")
        return redirect(url_for("lol"))

    cursor = mysql.connection.cursor()
    p = "Select * from posts where game_name = %s "
    result = cursor.execute(p,("lol",))

    if result > 0:
        posts = cursor.fetchall()
        return render_template("lol.html",posts = posts,form=form)
    return render_template("lol.html",form = form)



#add friend
@app.route("/friendlist",methods=["GET","POST"])
def friendlist():
    form = FriendRequest(request.form)
    if request.method=="POST":
        to_user=form.to_user.data
        from_user = session["username"]
        cursor = mysql.connection.cursor()
        p=("Select * from friend_requests where from_user = %s and to_user = %s")
        checkIfAlreadyFriend = ("Select * from friends where user_username=%s and friend_username=%s")
        resultx=cursor.execute(checkIfAlreadyFriend,(from_user,to_user))
        if resultx>0:
            flash("You are already friends!","danger")
            return redirect(url_for("friendlist"))
        result1 = cursor.execute(p,(from_user,to_user))
        if result1>0:
            friend_request = cursor.fetchone()
            invite_id = friend_request["id"]
            z = "Update friend_requests Set from_user=%s,to_user=%s,status=%s where id = %s "
            cursor.execute(z,(from_user,to_user,"waiting",invite_id))
            mysql.connection.commit()
            flash("Friend request sent again!","success")
            return redirect(url_for("friendlist"))

        q=("Insert into friend_requests(status,from_user,to_user) VALUES(%s,%s,%s)")
        cursor.execute(q,("waiting",from_user,to_user))
        mysql.connection.commit()
        cursor.close()
        flash("Friend request sent!","success")
        return redirect(url_for("friendlist"))

    cursor = mysql.connect.cursor()
    alfa=("Select * from friends where user_username=%s")
    cursor.execute(alfa,(session["username"],))
    friends = cursor.fetchall()


    p="Select * from friend_requests where to_user=%s and status = %s"
    cursor.execute(p,(session["username"],"waiting" ))

    friend_requests=cursor.fetchall()  
    return render_template("friendlist.html",form=form,friend_requests=friend_requests,friends=friends)

@app.route("/accept/<string:id>")
def accept(id):
    cursor = mysql.connection.cursor()
    p=("Select * from friend_requests where id=%s")
    result1 = cursor.execute(p,(id, ))
    if result1>0:
        friend_request=cursor.fetchone()
        friend_username = friend_request["from_user"]
        q = ("Insert into friends(user_username,friend_username) VALUES(%s,%s)")
        cursor.execute(q,(session["username"],friend_username))
        t = ("Insert into friends(user_username,friend_username) VALUES(%s,%s)")
        cursor.execute(t,(friend_username,session["username"]))
        s = "Delete from friend_requests where id=%s"
        cursor.execute(s,(id,))
        mysql.connection.commit()
        return redirect(url_for("friendlist"))
    return


@app.route("/decline/<string:id>")
def decline(id):
    cursor = mysql.connection.cursor()
    p=("Select * from friend_requests where id=%s")
    result1 = cursor.execute(p,(id, ))
    if result1>0:
        friend_request=cursor.fetchone()
        sender_username = friend_request["from_user"]
        reciever_username=friend_request["to_user"]
       
        q = ("Update friend_requests Set from_user=%s,to_user=%s,status=%s where id = %s")
        cursor.execute(q,(sender_username,reciever_username,"ignored",id))
 

        mysql.connection.commit()
        return redirect(url_for("friendlist"))
    return


#delete friend
@app.route("/deletefriend/<string:id>")
def deletefriend(id):
    cursor=mysql.connection.cursor()
    q = "Select * from friends where id = %s"
    result = cursor.execute(q,(id,))
    if result>0:
        friends = cursor.fetchone()
        p = "Delete from friends where id=%s"
        cursor.execute(p,(id,))
        friend_username=friends["friend_username"]
        user_username=friends["user_username"]
        t="Delete from friends where user_username = %s and friend_username=%s "
        cursor.execute(t,(friend_username,user_username))
        mysql.connection.commit()
        flash("Friend deleted succesfully!","success")
        return redirect(url_for("friendlist"))
    return


if __name__=="__main__":
    app.run(debug = True)

