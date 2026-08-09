import os
import time
import streamlit as st
from youtube import download_progress, start_background_download

st.set_page_config(page_title="SkyDownloader", page_icon="☁️", layout="centered")


def local_css(file_name):
  try:
    with open(file_name) as f:
      st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
  except:
    pass


local_css("style.css")

st.markdown(
    "<h1 style='text-align: center; color: #01579b;'>☁️ SkyTube Downloader</h1>",
    unsafe_allow_html=True,
)
st.write("---")

url = st.text_input(
    "Paste your YouTube link here:", placeholder="https://youtube.com/..."
)

if st.button("Start Download 🚀", type="primary"):
  if url.strip():
    with st.spinner("Fetching video info..."):
      success, title, uploader, thumbnail_url, download_id = (
          start_background_download(url)
      )

    if success:
      card_placeholder = st.empty()
      while True:
        prog_data = download_progress.get(
            download_id, {"percent": 0.0, "status": "starting"}
        )
        current_percent = prog_data["percent"]
        status = prog_data["status"]

        if "error" in status:
          card_placeholder.error(f"❌ {status}")
          break
        elif status == "completed" or current_percent >= 100.0:
          # Find the downloaded file in downloads folder
          download_dir = "./downloads"
          downloaded_file_path = None
          if os.path.exists(download_dir):
            for file in os.listdir(download_dir):
              if file.lower().endswith((".mp4", ".mkv", ".webm", ".mp3")):
                downloaded_file_path = os.path.join(download_dir, file)
                break

          card_placeholder.markdown(
              f"""
            <div class="download-card">
                <img src="{thumbnail_url}" class="square-thumbnail"/>
                <div class="video-info">
                    <div class="video-title">{title}</div>
                    <div class="video-channel">{uploader}</div>
                    <div class="download-status" style="color: #00c853;">✅ Download Completed!</div>
                </div>
            </div>
          """,
              unsafe_allow_html=True,
          )

          # Show native Streamlit download button for mobile/PC
          if downloaded_file_path and os.path.exists(downloaded_file_path):
            with open(downloaded_file_path, "rb") as f:
              st.download_button(
                  label="📥 Save File to Device / Gallery",
                  data=f,
                  file_name=os.path.basename(downloaded_file_path),
                  mime="video/mp4",
                  type="primary",
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
        time.sleep(1)
    else:
      st.error(
          "❌ Error fetching video. Make sure the link is public and valid."
      )
  else:
    st.error("Please enter a valid URL.")