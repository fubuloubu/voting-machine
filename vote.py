import os
import secrets
import tempfile

from flask import Flask, flash, request, redirect, url_for, send_from_directory, session
from werkzeug.utils import secure_filename

POSITIONS = {"mayor", "president", "representative", "vice-president"}
PARTIES = {"iris", "rose"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = tempfile.gettempdir()
app.secret_key = secrets.token_urlsafe(32)


@app.route("/", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            return "No file part"

        file = request.files["file"]

        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == "":
            return "No selected file"

        filename = secrets.token_urlsafe(12)
        session["filename"] = filename

        if (
            file
            and "." in file.filename
            and file.filename.rsplit(".", 1)[1].lower() in {"html", "txt"}
        ):
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], f"{filename}.html"))
            return redirect(url_for("ballot"))

    return """
    <!DOCTYPE html>
    <title>Test Voting Machine</title>
    <h1>Upload Your HTML File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    """


@app.route("/ballot")
def ballot():
    filename = session.get("filename", None)
    if not filename:
        redirect(url_for("upload"))
    return send_from_directory(app.config["UPLOAD_FOLDER"], f"{filename}.html")


@app.route("/vote", methods=["POST"])
def vote():
    form_data = request.form
    votes = {i: 0 for i in PARTIES.union(POSITIONS)}
    for position, party in form_data.items():
        if position not in POSITIONS:
            return f'Position (name="{position}") must be one of {POSITIONS}'
        if party not in PARTIES:
            return f'Party (value="{party}") must be one of {PARTIES}'
        votes[position] += 1
        votes[party] += 1

    missing = {p for p in POSITIONS if votes[p] == 0}
    if len(missing) > 0:
        return f"Ballot corrupted: missing votes for {missing}"

    return f"""
    <!DOCTYPE html>
    <title>Ballot Submitted!</title>
    <h1>Results</h1>
    <p>Iris Party: {votes['iris']}</p>
    <p>Rose Party: {votes['rose']}</p>
    """
