import time
import streamlit as st
from youtube import download_progress, start_background_download


st.set_page_config(page_title="YouTube Downloader", page_icon="📥", layout="centered")
# 2. Function to load external CSS safely
def local_css(file_name):
  try:
    with open(file_name) as f:
      st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
  except FileNotFoundError:
    pass


# Load the external CSS file
local_css("style.css")

st.markdown(
    """
    <style>
        .download-card {
            display: flex;
            background-color: #1e1e1e;
            padding: 15px;
            border-radius: 12px;
            gap: 20px;
            align-items: center;
            margin-top: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        .square-thumbnail {
            width: 160px;
            height: 120px;
            object-fit: cover;
            border-radius: 8px;
        }
        .video-info { color: #ffffff; font-family: sans-serif; }
        .video-title { font-size: 16px; font-weight: 600; margin-bottom: 5px; }
        .video-channel { font-size: 14px; color: #aaa; margin-bottom: 8px; }
        .download-status { font-size: 14px; color: #3b82f6; font-weight: 600; }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("📥 YouTube Video Downloader")
st.write(
    "Paste your YouTube link below. The download runs in the background with"
    " live percentage tracking!"
)

url = st.text_input("Video or Short URL", placeholder="Paste YouTube link here...")

if st.button("Start Download", type="primary"):
  if url.strip():
    with st.spinner("Fetching video info..."):
      success, title, uploader, thumbnail_url, download_id = (
          start_background_download(url)
      )

    if success:
      card_placeholder = st.empty()

      # Live loop to poll background progress and update UI
      while True:
        prog_data = download_progress.get(
            download_id, {'percent': 0.0, 'status': 'starting'}
        )
        current_percent = prog_data['percent']
        status = prog_data['status']

        if 'error' in status:
          card_placeholder.error(f'❌ {status}')
          break
        elif status == 'completed' or current_percent >= 100.0:
          card_placeholder.markdown(
              f"""
                    <div class="download-card">
                        <img src="{thumbnail_url}" class="square-thumbnail"/>
                        <div class="video-info">
                            <div class="video-title">{title}</div>
                            <div class="video-channel">{uploader}</div>
                            <div class="download-status" style="color: #22c55e;">🎉 Download Completed! (100%)</div>
                        </div>
                    </div>
                    """,
              unsafe_allow_html=True,
          )
          st.balloons()
          break
        else:
          card_placeholder.markdown(
              f"""
                    <div class="download-card">
                        <img src="{thumbnail_url}" class="square-thumbnail"/>
                        <div class="video-info">
                            <div class="video-title">{title}</div>
                            <div class="video-channel">{uploader}</div>
                            <div class="download-status">Downloading... {current_percent:.1f}%</div>
                        </div>
                    </div>
                    """,
              unsafe_allow_html=True,
          )
        time.sleep(1)  # Refresh every 1 second
    else:
      st.error(f'❌ Error: {download_id}')
  else:
    st.error('Please enter a valid URL.')