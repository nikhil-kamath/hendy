from googleapiclient.discovery import build
import asyncio
import time
import config

api_key = config.youtube_api_key


async def youtube_get_comments(youtube, video_id, comments=None, token='', scrolls=5):
    if comments is None:
        comments = []

    if not scrolls:
        return comments

    video_response = youtube.commentThreads().list(part='snippet',
                                                   videoId=video_id,
                                                   pageToken=token).execute()
    for item in video_response['items']:
        comment = item['snippet']['topLevelComment']
        text = comment['snippet']['textDisplay']
        comments.append(text)
    if "nextPageToken" in video_response:
        return await youtube_get_comments(youtube, video_id, comments, video_response['nextPageToken'], scrolls=scrolls-1)
    else:
        return comments


async def youtube_search_keyword(youtube, query, max_results=10):
    # sourcery skip: for-append-to-extend, list-comprehension
    search_keyword = youtube.search().list(q=query, part="id, snippet",
                                           maxResults=max_results).execute()

    results = search_keyword.get("items", [])

    titles = []
    ids = []
    for result in results:
        if result['id']['kind'] == "youtube#video":
            ids.append(result['id']['videoId'])
            titles.append(result["snippet"]["title"])


    return ids, titles


