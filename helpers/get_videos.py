import numpy as np
import pandas as pd
import ollama


SIMILARITIES_RESULTS_THRESHOLD = 0.2


def cosine_similarity(a, b):
    if len(a) > len(b):
        # thêm các giá trị vào mảng b để có cùng chiều dài với mảng a
        b = np.pad(b, (0, len(a) - len(b)), 'constant')
    elif len(b) > len(a):
        a = np.pad(a, (0, len(b) - len(a)), 'constant')
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def get_videos(query: str, rows: int, collection) -> pd.core.frame.DataFrame:
    query_embeddings = ollama.embeddings(model="mxbai-embed-large", prompt=query)["embedding"]
    video_vectors = list(collection.find({}, {"ada_v2":1}))
    for video in video_vectors:
        ada_v2_vector = np.array(video["ada_v2"])
        similarity = cosine_similarity(np.asarray(query_embeddings), ada_v2_vector)
        video["similarity"] = similarity
     
    # filter the video by similarity
    filtered_videos = [video for video in video_vectors if video["similarity"] >= SIMILARITIES_RESULTS_THRESHOLD]
    # sort the video by similarity
    sorted_videos = sorted(filtered_videos, key=lambda x:x["similarity"], reverse=True)
    top_videos = sorted_videos[:rows]
    
    return top_videos
