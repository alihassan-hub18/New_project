import os
import threading
import yt_dlp

download_progress = {}


def run_background_download(url, download_id):
  try:
    download_dir = "./downloads"
    if not os.path.exists(download_dir):
      os.makedirs(download_dir)

    def progress_hook(d):
      if d["status"] == "downloading":
        try:
          percent_str = (
              d.get("_percent_str", "0%")
              .replace("%", "")
              .replace("\u001b[0;94m", "")
              .replace("\u001b[0m", "")
              .strip()
          )
          percent_val = float(percent_str)
          download_progress[download_id] = {
              "percent": percent_val,
              "status": "downloading",
          }
        except Exception:
          pass
      elif d["status"] == "finished":
        download_progress[download_id] = {
            "percent": 100.0,
            "status": "completed",
        }

    ydl_opts = {
    'format': 'best',
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'cookiefile': 'cookies.txt',  # Agar cookies file use ho rahi hai
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Sec-Fetch-Mode': 'navigate',
    }
}

    if os.path.exists("cookies.txt"):
      ydl_opts["cookiefile"] = "cookies.txt"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      ydl.download([url])

  except Exception as e:
    download_progress[download_id] = {"percent": 0.0, "status": f"error: {e}"}


def start_background_download(url):
  try:
    ydl_opts = {
    'format': 'best',
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'extractor_args': {
        'youtube': {
            'player_client': ['android', 'web']
        }
    }
}

    if os.path.exists("cookies.txt"):
      ydl_opts["cookiefile"] = "cookies.txt"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      info = ydl.extract_info(url, download=False)
      title = info.get("title", "Video")
      uploader = info.get("uploader", "Channel")
      thumbnail_url = info.get("thumbnail", "")

    download_id = url
    download_progress[download_id] = {"percent": 0.0, "status": "starting"}

    thread = threading.Thread(
        target=run_background_download, args=(url, download_id)
    )
    thread.daemon = True
    thread.start()

    return True, title, uploader, thumbnail_url, download_id
  except Exception as e:
    return False, "", "", "", str(e)