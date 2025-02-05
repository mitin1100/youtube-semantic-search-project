""" Summarize a youtube transcript using chatgpt"""

import json
import os
import queue
import threading
import logging
import argparse
import ollama
from tenacity import (
    retry,
    wait_random_exponential,
    stop_after_attempt,
    retry_if_not_exception_type,
)
from rich.progress import Progress


MAX_TOKENS = 512
PROCESSOR_THREADS = 10
OPENAI_REQUEST_TIMEOUT = 30

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("--verbose", action="store_true")
parser.add_argument("-f", "--folder")
args = parser.parse_args()

TRANSCRIPT_FOLDER = r"/transcripts"
if not TRANSCRIPT_FOLDER:
    logger.error("Transcript folder not provided")
    exit(1)

if args.verbose:
    logger.setLevel(logging.DEBUG)

segments = []
output_segments = []
total_segments = 0

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
    wait=wait_random_exponential(min=10, max=45),
    stop=stop_after_attempt(20),
    retry=retry_if_not_exception_type(ollama.RequestError),
)
def chatgpt_summary(text):
    """generate a summary using chatgpt"""

    messages = [
        {
            "role": "system",
            "content": "You're an AI Assistant for video, write an authoritative 60 word summary.Avoid starting sentences with 'This video'.",
        },
        {
            "role": "user", 
            "content": text
        },
    ]
    response = ollama.chat(model="llama3", messages=messages)
    text = response['message']['content']
    return text


def process_queue(segments):
    """process the queue"""
    for segment in segments:
        text = segment.get("text")
        # get a summary of the text using chatgpt
        try:
            summary = chatgpt_summary(text)
        except ollama.RequestError as invalid_request_error:
            logger.warning("Error: %s", invalid_request_error)
            summary = text
        except Exception as e:
            logger.warning("Error: %s", e)
            summary = text

        # add the summary and text hash to the segment dictionary
        segment["summary"] = summary

        output_segments.append(segment.copy())


logger.debug("Starting OpenAI summarization")

# load the segments from a json file
input_file = os.path.join(TRANSCRIPT_FOLDER, "output", "master_transcriptions.json")
with open(input_file, "r", encoding="utf-8") as f:
    segments = json.load(f)

total_segments = len(segments)
print(total_segments)
logger.debug("Total segments to be processed: %s", len(segments))
process_queue(segments)

# convert time '00:01:20' to seconds
def convert_time_to_seconds(value):
    """convert time to seconds"""
    time_value = value.split(":")
    if len(time_value) == 3:
        h, m, s = time_value
        return int(h) * 3600 + int(m) * 60 + int(s)
    else:
        return 0


# sort the output segments by videoId and start
output_segments.sort(key=lambda x: (x["videoId"], convert_time_to_seconds(x["start"])))

logger.debug("Total segments processed: %s", len(output_segments))

# save the output segments to a json file
output_file = os.path.join(TRANSCRIPT_FOLDER, "output", "master_enriched.json")
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(output_segments, f, ensure_ascii=False, indent=4)
