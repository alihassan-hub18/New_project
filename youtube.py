import os
import threading
import yt_dlp

# Global dictionary to track progress for active downloads
download_progress = {}


def run_background_download(url, download_id):
  try:
    download_dir = "./downloads"
    if not os.path.exists(download_dir):
      os.makedirs(download_dir)

    ffmpeg_path = r"C:\Users\short\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.2-full_build\bin"

    def progress_hook(d):
      if d['status'] == 'downloading':
        try:
          # Extracting exact percentage string from yt-dlp output
          percent_str = (
              d.get('_percent_str', '0%')
              .replace('%', '')
              .replace('\u001b[0;94m', '')
              .replace('\u001b[0m', '')
              .strip()
          )
          percent_val = float(percent_str)
          download_progress[download_id] = {
              'percent': percent_val,
              'status': 'downloading',
          }
        except Exception:
          pass
      elif d['status'] == 'finished':
        download_progress[download_id] = {
            'percent': 100.0,
            'status': 'completed',
        }

    ydl_opts = {
        'noplaylist': True,
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'progress_hooks': [progress_hook],
    }

    ydl_opts = {k: v for k, v in ydl_opts.items() if v is not None}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      ydl.download([url])

  except Exception as e:
    download_progress[download_id] = {'percent': 0.0, 'status': f'error: {e}'}


def start_background_download(url):
  try:
    with yt_dlp.YoutubeDL({'noplaylist': True}) as ydl:
      info = ydl.extract_info(url, download=False)
      title = info.get('title', 'Video')
      uploader = info.get('uploader', 'Channel')
      thumbnail_url = info.get('thumbnail', '')

    download_id = url
    download_progress[download_id] = {'percent': 0.0, 'status': 'starting'}

    # Run in background thread so it keeps downloading even if browser is closed
    thread = threading.Thread(
        target=run_background_download, args=(url, download_id)
    )
    thread.daemon = True
    thread.start()

    return True, title, uploader, thumbnail_url, download_id
  except Exception as e:
    return False, '', '', '', str(e)