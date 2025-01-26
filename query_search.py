from typing import Tuple

from helpers.load_dataset import load_dataset
from helpers.get_videos import get_videos
from helpers.display_results import display_results

from output_parser import (Title, 
                           Summary, 
                           Similarity, 
                           Speaker,)



def query_search(input: str, collection) -> Tuple[Title, Summary, Similarity, Speaker, str]:
    videos = get_videos(input, 5, collection)
    # print(videos)
    title, summary, url, similarity, speaker = display_results(videos, input, collection)

    title_vid: Title = title
    summary_vid: Summary = summary
    similarity_score: Similarity = similarity
    speaker_vid: Speaker = speaker

    return (title_vid, summary_vid, similarity_score, speaker_vid, url)


if __name__ == "__main__":
    pass



