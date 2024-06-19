import json
import requests
from sys import argv
from io import TextIOWrapper
from os import path, makedirs
from datetime import datetime

YOUTUBE_FETCH_COMMENTS_URL = "https://www.googleapis.com/youtube/v3/commentThreads"
YOUTUBE_FETCH_MAX_RESULTS = 100
YOUTUBE_FETCH_TEXT_FORMAT = "plainText"
YOUTUBE_FETCH_PART = "snippet,replies"
MAX_FETCH_BATCHES = 250 # To not use too much quota

def get_curr_datetime() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

def log(msg):
    print(get_curr_datetime(), msg)

def get_root_dir() -> str:
    return path.dirname(__file__)[:-len("src")]

def load_google_api_key() -> str:
    key_path = path.join(get_root_dir(), "secrets/google-api-key")
    try:
        f = open(key_path, "r")
    except:
        raise FileNotFoundError("Google API key is missing, it should be stored in {} file\n"
                                "If you do not have one, you can make one here: https://console.cloud.google.com/apis/credentials\n"
                                "You also need to enable YouTube Data API: https://console.cloud.google.com/apis/api/youtube.googleapis.com".format(key_path))
    secret = f.read()
    return secret.strip()

def prepare_youtube_fetch_url(google_api_key: str, video_id: str) -> str:
    return "{yt_url}?key={key}&textFormat={text_format}&part={part}&maxResults={max_results}&videoId={video_id}".format(
        yt_url=YOUTUBE_FETCH_COMMENTS_URL,
        key=google_api_key,
        text_format=YOUTUBE_FETCH_TEXT_FORMAT,
        part=YOUTUBE_FETCH_PART,
        max_results=YOUTUBE_FETCH_MAX_RESULTS,
        video_id=video_id,
    )

def append_next_page_token(original_fetch_url: str, next_page_token: str) -> str:
    return "{orinal_fetch_url}&pageToken={next_page_token}".format(
        original_fetch_url=original_fetch_url,
        next_page_token=next_page_token,
    )

def fetch_all_comments(original_fetch_url: str, output_file: TextIOWrapper):
    log("Starting to fetch comments in batches...\nMax size of each batch is {}". format(YOUTUBE_FETCH_MAX_RESULTS))
    next_page_token = None
    batch_number = 1
    found_comments = 0
    while True:
        log("Loading batch {}...".format(batch_number))
        fetch_url = append_next_page_token(original_fetch_url, next_page_token) if next_page_token != None else original_fetch_url 
        http_res = requests.get(url=fetch_url)
        if http_res.status_code != 200:
            raise Exception("Failed to fetch comments", http_res.text)
        res_body: dict = http_res.json()
        comments = res_body.get("items")
        if comments == None or len(comments) < 1:
            log("Batch {batch} has zero comments\nResponse body: {response}".format(
                batch=batch_number,
                response=http_res.text,
            ))
            break
        found_comments += len(comments)
        process_comments(comments, output_file)
        if batch_number >= MAX_FETCH_BATCHES:
            log("Hit the app limit of batches (max is {}), will finish here to not overuse API quota".format(MAX_FETCH_BATCHES))
            break
        next_page_token = res_body.get("nextPageToken")
        if next_page_token == None:
            log("Batch {} was the last one".format(batch_number))
            break
        batch_number += 1
    log("Finished fetching comments\nFound {comments} comments in {batches} batches".format(
        comments=found_comments,
        batches=batch_number,
    ))

def process_comments(comments: list[dict], output_file:TextIOWrapper):
    for comment in comments:
        formatted_json = json.dumps(comment, separators=(',', ':'), ensure_ascii=False)
        output_file.write(formatted_json + "\n")

###### MAIN #######
try:
    video_id = argv[1]
except:
    raise Exception("YouTube video ID is not provided. It should be provided as an argument.\n"
                    "E.g. if url is https://www.youtube.com/watch?v=dQw4w9WgXcQ\n"
                    "then run this: python src/comments-fetcher.py 'dQw4w9WgXcQ'")
log("Fetching comments for video https://www.youtube.com/watch?v={}".format(video_id))
google_api_key = load_google_api_key()
fetch_url = prepare_youtube_fetch_url(google_api_key, video_id)

output_dir_path = path.join(get_root_dir(), "output/raw")
makedirs(output_dir_path, exist_ok=True)
output_file_path = path.join(output_dir_path, "{video_id}_{time}.json".format(
    video_id=video_id,
    time=get_curr_datetime(),
))
output_file = open(output_file_path, "w")
fetch_all_comments(fetch_url, output_file)
output_file.close()
log("Saved results to {}".format(output_file_path))
