import threading
from queue import Queue
import os
import re
import logging
import sys
import tempfile
import subprocess
import json

from flask import Flask, request, jsonify
from helixdam import HelixDAM, HelixDAMAuthException, HelixDAMException


# Environment variables
DAM_URL = os.environ.get("DAM_URL")
ACCOUNT_KEY = os.environ.get("ACCOUNT_KEY")

METADATA_FIELDS = {
    "Height": "ImageHeight",
    "Width": "ImageHeight",
    "Layer Count": "LayerCount",
    "Layer Names": "LayerNames",
    "Project Name": "ProjectName",
    "Animation?": "AnimationEnabled",
    "Timeline Name": "TimeLineName",
    "Frame Rate": "FrameRate",
    "Frame Count": "EndFrame - StartFrame",
}
METADATA_UUIDS = {}  # This gets populated on first run.

hd = HelixDAM(url=DAM_URL, account_key=ACCOUNT_KEY)

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s - %(levelname)s] %(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger(__name__)

app = Flask(__name__)


# Queue for processing tasks
process_queue = Queue()


def process_file(depot_path: str) -> None:
    logger.info(f"Downloading file: {depot_path}")
    with tempfile.NamedTemporaryFile() as temp_file:
        try:
            hd.download_file(depot_path, temp_file)
        except HelixDAMException as e:
            logger.error(f"Error downloading file: {e}")
            return
        temp_file.seek(0)
        file_data = extract_clip_data(temp_file)

    if file_data:
        try:
            hd.upload_preview(depot_path, file_data["image_data"])
        except HelixDAMException as e:
            logger.error(f"Error sending preview: {e}")
        try:
            send_metadata_to_dam(depot_path, file_data)
        except HelixDAMException as e:
            logger.error(f"Error sending metadata: {e}")


def extract_clip_data(temp_file: tempfile.NamedTemporaryFile) -> dict:
    # Run clip_extractor on the temp file, request b64 bytes output, and use verbose mode
    command = ["clip_extractor", "-i", temp_file.name, "-f", "bytes", "-v"]
    logger.debug(f"Running command: {' '.join(command)}")
    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    logger.debug(f"Command output: {result.stderr}")

    if result.returncode == 0:
        try:
            output_json: dict = json.loads(result.stdout)
            return output_json
        except json.JSONDecodeError:
            raise ValueError("Failed to decode JSON output.")
    else:
        # Handle errors or non-zero exit codes if necessary
        raise RuntimeError(
            f"Subprocess failed with exit code {result.returncode}: {result.stderr}"
        )


def send_metadata_to_dam(depot_path: str, file_data: dict) -> None:
    # Calculate our metadata values first
    metadata = {
        name: file_data["metadata"][id]
        for name, id in METADATA_FIELDS.items()
        if id in file_data["metadata"]
    }
    metadata["Animation?"] = "True" if metadata["Animation?"] else "False"
    if "StartFrame" in file_data["metadata"] and "EndFrame" in file_data["metadata"]:
        metadata["Frame Count"] = str(
            int(file_data["metadata"]["EndFrame"])
            - int(file_data["metadata"]["StartFrame"])
        )
    logger.debug(f"Sending metadata to DAM: {metadata}")
    hd.update_file_metadata(
        depot_path=depot_path,
        uuid_value_dict={
            METADATA_UUIDS[name]: value for name, value in metadata.items()
        },
    )
    logger.info(f"Successfully uploaded metadata to DAM for {depot_path}")


def get_or_create_metadata_fields(field_names: set) -> dict:
    results = {name: hd.create_metadata_field(name, "text") for name in field_names}
    return results


def worker():
    while True:
        depot_path = process_queue.get()
        process_file(depot_path)
        process_queue.task_done()


# Start worker thread
threading.Thread(target=worker, daemon=True).start()


@app.route("/webhook", methods=["POST"])
def webhook():
    logging.debug(f"Received webhook request. {request}")
    data = request.json
    if not data:
        logging.error("No JSON data in request")
        return jsonify({"error": "No JSON data in request"}), 400

    clip_files = []

    for update in data:
        if (
            "objects" not in update
            or "files" not in update["objects"]
            or (
                "added" not in update["objects"]["files"]
                and "modified" not in update["objects"]["files"]
            )
        ):
            logging.warning(
                "Skipping update: No added or modified 'objects' or 'files' in update"
            )
            logging.debug(str(update))
            continue

        for action in ["added", "modified"]:
            for file in update["objects"]["files"][action]:
                if re.search(r"\.clip$", file, re.IGNORECASE):
                    clip_files.append(file)

    for depot_path in clip_files:
        process_queue.put(depot_path)

    return jsonify({"message": f"Queued {len(clip_files)} files for processing"}), 200


if __name__ == "__main__":
    if not DAM_URL or not ACCOUNT_KEY:
        logger.error("DAM_URL and ACCOUNT_KEY must be set as environment variables")
        exit(1)

    METADATA_UUIDS = get_or_create_metadata_fields(METADATA_FIELDS.keys())
    app.run(host="0.0.0.0", port=8080, debug=False)
