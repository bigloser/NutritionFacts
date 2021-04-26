import re
import pickle
import urllib.request
import datetime
import bs4 as bs
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build

api_key = st.secrets['api_key']


@st.cache
def get_new_video_data(set_new_videos):
    youtube = build('youtube', 'v3', developerKey=api_key)
    new_video_data = []
    for video_id in set_new_videos:
        request = youtube.videos().list(part='snippet', id=video_id)
        result = request.execute()

        title = result['items'][0]['snippet']['title']
        date_published = result['items'][0]['snippet']['publishedAt']
        datetime_obj = datetime.datetime.strptime(
                date_published, '%Y-%m-%dT%H:%M:%SZ')
        date_str = datetime_obj.strftime('%B %Y')

        video_transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join(i['text'] for i in video_transcript)
        new_video_data.append(
                [video_id, f'{title} {date_str}', text, video_transcript])
    return new_video_data


def get_list_valid_yt_id(html_soup_obj):
    pattern = r'you.*(watch\?v=)?([a-zA-Z_0-9-]{11})'
    list_valid_yt_id = []
    tags = html_soup_obj.find_all('a')
    for tag in tags:
        link = tag.get('href')
        valid_yt_url = re.search(pattern, link)
        if valid_yt_url:
            list_valid_yt_id.append(valid_yt_url.group(2))
    return list_valid_yt_id


@st.cache
def check_new_videos(saved_file_data):
    old_videos_url = (
            'https://web.archive.org/web/20200729153409/'
            'nutritionfacts.org/live')
    try:
        old_videos = urllib.request.urlopen(old_videos_url).read()
        current_videos = urllib.request.urlopen(
            'https://nutritionfacts.org/live/').read()
    except Exception:
        pass
    else:
        old_videos_html = bs.BeautifulSoup(
                old_videos,
                'html.parser',
                from_encoding='utf-8')
        current_videos_html = bs.BeautifulSoup(
                current_videos,
                'html.parser',
                from_encoding='utf-8')

        list_valid_yt_id = []

        current_videos_valid_yt_id = get_list_valid_yt_id(current_videos_html)
        old_videos_valid_yt_id = get_list_valid_yt_id(old_videos_html)

        list_valid_yt_id = current_videos_valid_yt_id + old_videos_valid_yt_id
        list_valid_yt_id = set(list_valid_yt_id)
        list_valid_yt_id.remove('ionFactsOrg')

        set_new_videos = list_valid_yt_id - set(
                [i[0] for i in saved_file_data])
        if set_new_videos:
            new_video_data = get_new_video_data(set_new_videos)
            saved_file_data = saved_file_data + new_video_data
            with open('file.pkl', 'wb') as handle:
                pickle.dump(saved_file_data, handle, protocol=4)

    return saved_file_data
