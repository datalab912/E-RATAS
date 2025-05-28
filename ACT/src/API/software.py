import json
from flask import Flask, flash, jsonify, request, redirect
import requests
from werkzeug.utils import secure_filename
from pathlib import Path


from ACT.src.act import ACTTree
from log.log import Log


UPLOAD_FOLDER = (
    Path(__file__).parent.parent.parent / "uploads"
)  # Path to the uploads folder
JSON_FOLDER = Path(__file__).parent.parent.parent / "data" / "processed" / "act"
ALLOWED_EXTENSIONS = {"txt", "pdf", "json"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["JSON_FOLDER"] = JSON_FOLDER


def allowed_file(filename):
    """
    Check if the given filename has an allowed extension.

    Args:
        filename (str): The name of the file.

    Returns:
        bool: True if the file has an allowed extension, False otherwise.
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


logger = Log("software", "software.log")


@app.route("/software/act", methods=["GET", "POST"])
def upload_file():
    """
    Handle the file upload for ACT processing.

    Returns:
        str: The HTML form for uploading a file.
    """
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = Path(app.config["UPLOAD_FOLDER"]) / "act" / filename
            file.save(save_path)

            logger.info(f"File saved at {save_path}, processing...")

            url = "http://127.0.0.1:5000/build-act"
            files = {"file": open(save_path, "rb")}
            headers = {"Content-Type": "application/pdf"}

            try:
                response = requests.post(url, files=files)
                response.raise_for_status()
                return jsonify(response.json())

            except requests.exceptions.RequestException as e:
                logger.error(f"Error forwarding to webhook: {e}")
                return f"Error forwarding to webhook: {e}"
    return """
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    """


@app.route("/software/act_webhook", methods=["POST"])
def handle_webhook():
    """
    Handle the webhook request for ACT processing.

    Returns:
        str: The response message.
    """
    if request.headers["Content-Type"] == "application/json":
        try:
            json_data = request.get_json()
            act_tree = ACTTree(json_data)

            print(act_tree.print_tree())

            logger.info("ACT tree received and processed")
            return jsonify(
                {"status": "success", "message": "ACT tree received and processed"}
            )

        except json.JSONDecodeError as e:
            logger.info(f"Invalid JSON format: {e}")
            return (
                jsonify({"status": "error", "message": f"Invalid JSON format: {e}"}),
                400,
            )
    else:
        logger.info("Unsupported content type")
        return jsonify({"status": "error", "message": "Unsupported content type"}), 415


if __name__ == "__main__":
    app.debug = True
    app.run(host="127.0.0.1", port=6000)
