import pandas as pd
import streamlit as st


def display_results(videos, query: str, collection):
    def _gen_yt_url(video_id: str, seconds: int) -> str:
        return f"https://youtube.com/embed/{video_id}?start={seconds}"
    
    print(f"\nVideos similar to '{query}':")
    titles = []
    summaries = []
    you_urls = []
    similarities = []
    speakers = []
    for video in videos:
        video_id = video["_id"] # output: ObjectId('66e7a5f164811f5239959389')
        videoId = (collection.find_one({"_id":video_id},{"videoId":1, "_id":0}))["videoId"]
        seconds = (collection.find_one({"_id":video_id},{"seconds":1, "_id":0}))["seconds"]
        youtube_url = _gen_yt_url(videoId, seconds)
        
        if youtube_url:
           
            titles.append((collection.find_one({"_id":video_id},{"title":1, "_id":0}))["title"])
            summaries.append((collection.find_one({"_id":video_id},{"summary":1, "_id":0}))["summary"])
            you_urls.append(youtube_url) 
            similarities.append(video["similarity"])
            speakers.append((collection.find_one({"_id":video_id},{"speaker":1, "_id":0}))["speaker"])
            
    return (titles,
            summaries,
            you_urls,
            similarities,
            speakers)
