""" This script will get the speaker name from the YouTube video metadata and the first minute of the transcript using the OpenAI Functions entity extraction."""

import json
import os
import glob
import threading
import logging
import queue
import time
import argparse
import openai
# from openai.embeddings_utils import get_embedding
import ollama
from rich.progress import Progress
from tenacity import (
    retry,
    wait_random_exponential,
    stop_after_attempt,
    retry_if_not_exception_type,
)


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

TRANSCRIPT_FOLDER = r"/transcripts"
PROCESSING_THREADS = 6
SEGMENT_MIN_LENGTH_MINUTES = 3
OPENAI_REQUEST_TIMEOUT = 60

OPENAI_MAX_TOKENS = 512

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--folder")
parser.add_argument("--verbose", action="store_true")
args = parser.parse_args()
if args.verbose:
    logger.setLevel(logging.DEBUG)

if not TRANSCRIPT_FOLDER:
    logger.error("Transcript folder not provided")
    exit(1)

get_speaker_name = {
    "name": "get_speaker_name",
    "description": "Get the speaker names for the session.",
    "parameters": {
        "type": "object",
        "properties": {
            "speakers": {
                "type": "string",
                "description": "The speaker names.",
            }
        },
        "required": ["speaker_name"],
    },
}


openai_functions = [get_speaker_name]

# these maps are used to make the function name string to the function call
definition_map = {"get_speaker_name": get_speaker_name}

q = queue.Queue()

errors = 0


class Counter:
    """thread safe counter"""

    def __init__(self):
        """initialize the counter"""
        self.value = 0
        self.lock = threading.Lock()

    def increment(self):
        """increment the counter"""
        with self.lock:
            self.value += 1
            return self.value


counter = Counter()


@retry(
    wait=wait_random_exponential(min=6, max=10),
    stop=stop_after_attempt(4),
    retry=retry_if_not_exception_type(ollama.RequestError),
)
def get_speaker_info(text):
    """Gets the OpenAI functions from the text."""

    function_name = None
    arguments = None
    # Sửa lại content chỉ để return về name thui
    response_1 = ollama.chat(model="llama3", messages=[
            {
                "role": "system",
                "content": """You are an AI assistant that can extract speaker names from text as a list of comma separated names. 
                Try and extract the speaker names from the title. Speaker names are usually less than 3 words long.
                Just return the name only.""",
            },
            {
                "role": "user",
                "content": text,
            }]
            
            )


    # The assistant's response includes a function call. We extract the arguments from this function call
    result = response_1['message']['content']
    return result


def clean_text(text):
    """clean the text"""
    text = text.replace("\n", " ")  # remove new lines
    text = text.replace("&#39;", "'")
    text = text.replace(">>", "")  # remove '>>'
    text = text.replace("  ", " ")  # remove double spaces
    text = text.replace("[inaudible]", "")  # [inaudible]

    return text


def get_first_segment(file_name):
    """Gets the first segment from the filename"""

    text = ""
    current_seconds = None
    segment_begin_seconds = None
    segment_finish_seconds = None

    vtt = file_name.replace(".json", ".json.vtt")

    with open(vtt, "r", encoding="utf-8") as json_file:
        json_vtt = json.load(json_file)

        for segment in json_vtt:
            current_seconds = segment.get("start")

            if segment_begin_seconds is None:
                segment_begin_seconds = current_seconds
                # calculate the finish time from the segment_begin_time
                segment_finish_seconds = (
                    segment_begin_seconds + SEGMENT_MIN_LENGTH_MINUTES * 60
                )

            if current_seconds < segment_finish_seconds:
                # add the text to the transcript
                text += clean_text(segment.get("text")) + " "

    return text


def process_queue():
    for fname in os.listdir(TRANSCRIPT_FOLDER):
        if fname.endswith('.json'):
            filename = os.path.join(TRANSCRIPT_FOLDER, fname)
            with open(filename, "r", encoding="utf-8") as json_file:
                metadata = json.load(json_file)

                base_text = 'The title is: ' +  metadata['title'] + " " + metadata["description"] + " " + get_first_segment(filename)
                # replace new line with empty string
                base_text = base_text.replace("\n", " ")

                speakers = get_speaker_info(base_text)
                if speakers == "":
                    print(f"From function call: {filename}\t---MISSING SPEAKER---")
                    continue
                else:
                    print(f"From function call: {filename}\t{speakers}")

                metadata["speaker"] = speakers
                json.dump(metadata, open(filename, "w", encoding="utf-8"))

print("Strating speaker name update ...")
process_queue()
print("Finish!")
