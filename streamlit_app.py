import pickle
import re
import streamlit as st
import SessionState
import utils
import streamlit_analytics


session_state = SessionState.get(session='')

streamlit_analytics.start_tracking()
st.title('NutritionFacts.Org Live Q&A Browser')

st.markdown(
        """
        This tool allows for a quick search for a specific term\
        on all Live Q&As ever recorded.

        Source: [NutritionFacts](https://nutritionfacts.org/live/)
        """
        )

with open('file.pkl', 'rb') as saved_file:
    saved_file_data = pickle.load(saved_file)

if not session_state.session:
    saved_file_data = utils.check_new_videos(saved_file_data)
    session_state.session = True

query = st.text_input('Enter your search term', '')
if len(query) < 1:
    st.stop()

search_results = {}
n = 0
for video in saved_file_data:
    if re.findall(query, video[2], flags=re.IGNORECASE):
        list_of_start_times = []
        link = f'https://www.youtube.com/watch?v={video[0]}'
        for caption in video[3]:
            if re.search(query, caption['text'], flags=re.IGNORECASE):
                start_time = caption['start']
                list_of_start_times.append(start_time)
        for i in range(len(list_of_start_times) - 1, 0, -1):
            if list_of_start_times[i] - list_of_start_times[i - 1] < 20:
                del list_of_start_times[i]
        search_results[n] = {
                'title': video[1],
                'link': link,
                'occurrences': list_of_start_times}
        n += 1
if n == 0:
    st.write("Nothing found")
    st.stop()

selected_video = st.selectbox(
        'Select your video',
        [search_results[i]['title'] for i in search_results.keys()])

for k, v in search_results.items():
    if selected_video == v['title']:
        if len(v['occurrences']) > 1:
            occurrence = st.selectbox(
                    'Select occurence:',
                    [i for i in range(len(v['occurrences']))], index=0)
            st.video(v['link'], start_time=int(v['occurrences'][occurrence]))
        else:
            st.video(v['link'], start_time=int(v['occurrences'][0]))

streamlit_analytics.stop_tracking()
