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
        private = request.form.get("private")
        

        if not name:
            # has another way to do this using flash
            return render_template("home.html", error="Please enter a name", code=code, name=name, rooms=rooms)

        if join != False and not code:
            return render_template("home.html", error="Please enter room code", code=code, name=name, rooms=rooms)
        
        room = code
        if create != False:
            room = generate_unique_code(4)
            if private is None:
                rooms[room] = {"members": 0, "messages":[], "names":[], "private":"no"}
            else:
                rooms[room] = {"members": 0, "messages":[], "names":[], "private":"yes"}

        elif code not in rooms:
            ## handling if the user passed a code that dont exist
            return render_template("home.html", error="Room does not exists.", code=code, name=name, rooms=rooms)
        
        ## i dont understand very well how does this works
        session["room"] = room
        session["name"] = name
        return redirect(url_for("room"))


    ## add the rooms created to the base file
    return render_template("home.html", rooms=rooms)

@app.route("/room")
def room():
    room = session.get("room")

    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))

    return render_template("room.html", room=room, messages=rooms[room]["messages"])

@socketio.on("message")
def message(data):
    room = session.get("room")

    if room not in rooms:
        return
    
    content = {
        "name": session.get("name"),
        "message": data["data"] ## getting the data from the javascript client side
    }

    send(content, to=room)
    rooms[room]["messages"].append(content)
    #print(f"{session.get('name')} said: {data['data']}")

# for default connect and disconnect trigger a message to everyone connected in the room socket so messages of connection probably have ways to not do this
@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")

    if not room or not name:
        return
    
    if room not in rooms:
        leave_room(room)
        return
    ## this join room creates a separate room, i dont know how this works
    ## collection of different users that allow us to send menssage to this room
    join_room(room)

    send({"name": name, "message":"has entered the room"}, to=room) ## this send only to the join_room
    rooms[room]["members"] += 1

    if name not in rooms[room]["names"]:
        rooms[room]["names"].append(name)

    #print(f"{name} joined room {room}")


@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            ## deleting the room if anyone in
            del rooms[room]

    send({"name": name, "message":"has left the room"}, to=room)
    #print(f"{name} has left the room {room}" )

if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0")