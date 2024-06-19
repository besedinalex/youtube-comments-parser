# YouTube comments parser
Fun project to fetch YouTube comments to some format which is possible to parse & analyze by something (at least by Excel, so end result is CSV file, which is easy to use there as well).

The background: [YouTube is to introduce a new design in 2024](https://ux-news.com/youtube-is-testing-a-new-design-that-youll-probably-hate/) and I argued with a friend that while it might feel horrid, it does help to read comments without leaving video behind. Friend's argument was that usually all comments are trash anyway and they not worth a read to begin with. So the idea was to download them, parse, analyze somehow, and see in numbers if this is the case.

## Prerequisite
1. Create a Google API Key (might need to create some new proj): https://console.cloud.google.com/apis/credentials
1. Enable YouTube Data API: https://console.cloud.google.com/apis/api/youtube.googleapis.com
1. Put your Google API Key to `secrets/google-api-key` file.
1. Have Python on your local (I personally use [Pyenv](https://github.com/pyenv/pyenv))
1. Install required libraries by running `pip install -r requirements.txt`.

## Running applications
```
# Fetching raw comments
python src/comments-fetcher.py  <video_id>
# Example if url is https://www.youtube.com/watch?v=dQw4w9WgXcQ
python src/comments-fetcher.py 'dQw4w9WgXcQ'

# Parsing raw data to CSV format
python src/comments-parser.py <raw-data-path>
# Example
python src/comments-parser.py '/home/your-username/yt-comment-research/output/raw/dQw4w9WgXcQ_1970_12_31T23:59:59.json'
```
