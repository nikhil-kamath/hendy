import logging
from googleapiclient.discovery import build
import asyncio
import time
import config
import socket
socket.setdefaulttimeout(10000)

api_key = config.youtube_api_key


def youtube_get_comments(key, video_id, comments=None, token='', scrolls=5):
    if comments is None:
        comments = []

    if not scrolls:
        return comments

    youtube = build("youtube", "v3", developerKey=config.youtube_api_key)
    video_response = youtube.commentThreads().list(part='snippet',
                                                   videoId=video_id,
                                                   pageToken=token).execute()
    for item in video_response['items']:
        comment = item['snippet']['topLevelComment']
        text = comment['snippet']['textDisplay']
        comments.append(text)
    if "nextPageToken" in video_response:
        return youtube_get_comments(youtube, video_id, comments, video_response['nextPageToken'], scrolls=scrolls-1)
    else:
        return comments


def youtube_search_keyword(api_key, query, max_results=10):
    # sourcery skip: for-append-to-extend, list-comprehension
    print("HELOOOOOOOOOOOOOO")
    youtube = build("youtube", "v3", developerKey=config.youtube_api_key)
    search_keyword = youtube.search().list(q=query, part="id, snippet",
                                           maxResults=max_results).execute()

    results = search_keyword.get("items", [])

    titles = []
    ids = []
    channels = []
    for result in results:
        if result['id']['kind'] == "youtube#video":
            ids.append(result['id']['videoId'])
            titles.append(result["snippet"]["title"])
            channels.append(result["snippet"]["channelTitle"])


    return ids, titles, channels


