# TBD

## Prerequisite
1. Create a Google API Key (might need to create some new proj): https://console.cloud.google.com/apis/credentials
1. Enable YouTube Data API: https://console.cloud.google.com/apis/api/youtube.googleapis.com
1. Put your Google API Key to `secrets/google-api-key` file.
1. Have Python on your local (I personally use [Pyenv](https://github.com/pyenv/pyenv))
1. Install required libraries by running `pip install -r requirements.txt`.

## Running applications
```
python src/fetch-comments.py  <video_id>

# Example if url is https://www.youtube.com/watch?v=dQw4w9WgXcQ
python src/fetch-comments.py dQw4w9WgXcQ
# or just to be safe
python src/fetch-comments.py 'dQw4w9WgXcQ'
```
