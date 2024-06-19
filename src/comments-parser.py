import json
from sys import argv
from csv import writer
from os import path, makedirs
from pathlib import Path
from datetime import datetime

def get_curr_datetime() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

def log(msg):
    print(get_curr_datetime(), msg)

def get_root_dir() -> str:
    return path.dirname(__file__)[:-len("src")]

def parse_comment(comment: dict) -> list:
    """Returns [id, author_id, text, likes, published_at, updated_at, parent_id]"""
    fields = []
    id: str = comment.get("id")
    if id == None:
        raise Exception("Comment field 'id' is missing")
    snippet: dict = comment.get("snippet")
    if snippet == None:
        raise Exception("Comment field 'snippet' is missing")
    channel_id: dict = snippet.get("authorChannelId")
    fields.append(id)
    fields.append("NULL" if channel_id == None else channel_id.get("value", "NULL"))
    fields.append(snippet.get("textOriginal", "NULL"))
    fields.append(snippet.get("likeCount", "NULL"))
    fields.append(snippet.get("publishedAt", "NULL"))
    fields.append(snippet.get("updatedAt", "NULL"))
    fields.append(snippet.get("parentId", "NULL"))
    return fields

def parse_raw_comment_data(data: dict) -> list[list]:
    comments = []
    snippet: dict = data.get("snippet")
    if snippet == None:
        raise Exception("Root field 'snippet' is missing")
    parent_comment: dict = snippet.get("topLevelComment")
    comments.append(parse_comment(parent_comment))
    replies: dict = data.get("replies")
    if replies != None:
        child_comments: list[dict] = replies.get("comments")
        if child_comments != None:
            for child_comment in child_comments:
                comments.append(parse_comment(child_comment))
    return comments

###### MAIN #######
try:
    raw_data_path = argv[1]
except:
    raise Exception("Raw data path is not provided. It should be provided as an argument.\n"
                    "E.g. need to run like this:\n"
                    "python src/comments-parser.py '/home/your-username/yt-comment-research/output/raw/dQw4w9WgXcQ_1970_12_31T23:59:59.json'")
log("Will fetch raw data from {}".format(raw_data_path))
raw_data_file = open(raw_data_path, "r")

filename_wo_ext = Path(raw_data_path).stem
output_dir_path = path.join(get_root_dir(), "output/parsed")
makedirs(output_dir_path, exist_ok=True)
output_file_path = path.join(output_dir_path, "{}.csv".format(filename_wo_ext))
output_file = open(output_file_path, "w")

raw_lines = 0
total_comments = 0
output_file.write("id,author_id,text,likes,published_at,updated_at,parent_id\n")
csv_writer = writer(output_file)
while True:
    line = raw_data_file.readline().strip()
    if not line:
        log("Reached EOF")
        break
    raw_lines += 1
    comment_raw: dict = json.loads(line)
    comments = parse_raw_comment_data(comment_raw)
    total_comments += len(comments)
    csv_writer.writerows(comments)

raw_data_file.close()
output_file.close()
log("Saved results to {}".format(output_file_path))


###### Notes on raw data structure ######

# Entire object is comment thread, so it contains info on both root comment and its replies.
# Actual comments can be found here:
# snippet.topLevelComment -> parent_comment
# replies.comments[x] -> child_comment
#
# Comment structure is the same, except child_comment has 'parentId' field

# From each comment these fields look useful enough, so we're saving them:
# id -> id (looks like <parent_id>.<child_id> for child_comment)
# snippet.authorChannelId.value -> author_id (can be accessed by "https://www.youtube.com/channel/{author_id}")
# snippet.textOriginal -> text
# snippet.likeCount -> likes
# snippet.publishedAt -> published_at
# snippet.updatedAt -> updated_at
# snippet.parentId -> parent_id

# Comment example. If there're no replies, 'replies' fields doesn't exist
# {
#     "kind": "youtube#commentThread",
#     "etag": "H9T4DJiCWJk05Mx4j62bqWGWMkY",
#     "id": "UgxHaiu03Sy97r07q5J4AaABAg",
#     "snippet": {
#         "channelId": "UC4u77JhpmafFQ-Z9Lsoakug",
#         "videoId": "Bcxw0wCJYtU",
#         "topLevelComment": {
#             "kind": "youtube#comment",
#             "etag": "J-Y1JFWAGrah4jl6V7C60hw6SHY",
#             "id": "UgxHaiu03Sy97r07q5J4AaABAg",
#             "snippet": {
#                 "channelId": "UC4u77JhpmafFQ-Z9Lsoakug",
#                 "videoId": "Bcxw0wCJYtU",
#                 "textDisplay": "I am getting witcher 3 vibes from 4:46",
#                 "textOriginal": "I am getting witcher 3 vibes from 4:46",
#                 "authorDisplayName": "@santiagofinal0000",
#                 "authorProfileImageUrl": "https://yt3.ggpht.com/ytc/AIdro_ld13SNXqH5Xrtra9xKVOFfSIzQCmiKbDtHGni-6lk=s48-c-k-c0x00ffffff-no-rj",
#                 "authorChannelUrl": "http://www.youtube.com/@santiagofinal0000",
#                 "authorChannelId": {
#                     "value": "UC37cL8cZKsG9rIe0A4sM91Q"
#                 },
#                 "canRate": true,
#                 "viewerRating": "none",
#                 "likeCount": 28,
#                 "publishedAt": "2018-06-29T16:55:01Z",
#                 "updatedAt": "2018-06-29T16:55:01Z"
#             }
#         },
#         "canReply": true,
#         "totalReplyCount": 1,
#         "isPublic": true
#     },
#     "replies": {
#         "comments": [
#             {
#                 "kind": "youtube#comment",
#                 "etag": "KQuF2VeYkU5Q3TPewsO4xoZcdfk",
#                 "id": "UgxHaiu03Sy97r07q5J4AaABAg.8i4w7coe0Oo8k9x2X2qmkm",
#                 "snippet": {
#                     "channelId": "UC4u77JhpmafFQ-Z9Lsoakug",
#                     "videoId": "Bcxw0wCJYtU",
#                     "textDisplay": "Whispers of Oxenfurt",
#                     "textOriginal": "Whispers of Oxenfurt",
#                     "parentId": "UgxHaiu03Sy97r07q5J4AaABAg",
#                     "authorDisplayName": "@crok8349",
#                     "authorProfileImageUrl": "https://yt3.ggpht.com/ytc/AIdro_lMXbul82KnUBE4PyxLFAUa-EJzvmPPut7vunU165Rn2Zo=s48-c-k-c0x00ffffff-no-rj",
#                     "authorChannelUrl": "http://www.youtube.com/@crok8349",
#                     "authorChannelId": {
#                         "value": "UC0PgoDCh0dI4COI0iErP0ig"
#                     },
#                     "canRate": true,
#                     "viewerRating": "none",
#                     "likeCount": 2,
#                     "publishedAt": "2018-08-20T08:42:03Z",
#                     "updatedAt": "2018-08-20T08:42:03Z"
#                 }
#             }
#         ]
#     }
# }
