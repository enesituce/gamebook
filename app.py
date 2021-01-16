from flask import Flask , render_template



app= Flask(__name__)

@app.route("/")

def index():
    return render_template("index.html")


@app.route("/channels")

def channels():
    return render_template("channels.html")

if __name__=="__main__":
    app.run(debug = True)

