from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase

app = Flask(__name__)
app.config["SECRET_KEY"] = "jdakjdsakdjsak"
socketio = SocketIO(app)

rooms = {}

def generate_unique_code(length):
    while True:
        code =""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        
        if code not in rooms:
            break
    
    return code

@app.route("/", methods=["POST","GET"])
def home():

    session.clear()

    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        ## the False tries to get from the request dictionary, if it doesnt send the default is False, otherwise True
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if not name:
            # has another way to do this using flash
            return render_template("home.html", error="Please enter a name", code=code, name=name)

        if join != False and not code:
            return render_template("home.html", error="Please enter room code", code=code, name=name)
        
        room = code
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {"members": 0, "messages":[]}
        elif code not in rooms:
            ## handling if the user passed a code that dont exist
            return render_template("home.html", error="Room does not exists.", code=code, name=name)
        
        ## i dont understand very well how does this works
        session["room"] = room
        session["name"] = name
        return redirect(url_for("room"))


    ## add the rooms created to the base file
    return render_template("home.html")



if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0")