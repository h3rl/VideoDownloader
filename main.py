from operator import truediv
from yt_dlp import YoutubeDL
import os
from threading import Thread
import argparse
from collections import deque
import time

def sleep(ms):
    time.sleep(ms/1000)

def get_clipboard():
    try:
        clipboard = os.popen("powershell.exe Get-Clipboard").read().strip()
        return clipboard
    except:
        return None

#TODO: after adding all files from todownload.txt, remove them.
# attach to callback and verify video was downloaded. then remove from file

class VideoDownloader:
    def __init__(self,max_resolution:int = 1080) -> None:
        self.queue = deque()
        self.last_queued = get_clipboard()

        self.ydl_opts = {
            # 'quiet': True,
            # 'noprogress': True,
            # 'nowarnings': True,
            'format': f'bestvideo[height<={max_resolution}]+bestaudio/best',
            #'progress_hooks': [dlp_progress_hook],
        }
        self.ydl = YoutubeDL(self.ydl_opts)
        
        self.thread = Thread(target=self.queue_loop,daemon=True)
    
    def queue_loop(self):
        while True:
            if len(self.queue) == 0:
                sleep(100)
                continue
            
            print(f"There are {len(self.queue)} videos in queue")

            url = self.queue.popleft()
            try:
                self.ydl.download(url)
            except:
                pass

            if len(self.queue) == 0:
                print("No more videos in queue, done for now..")
    
    def start(self):
        self.thread.start()
        while True:
            try:
                # get clipboard url
                url = get_clipboard()
                
                if not url or url == self.last_queued or url in self.queue:
                    sleep(100)
                    continue
                
                #print(f"Appending {url}\nlast_queued: {self.last_queued}\n\n")
                self.queue.append(url)
                self.last_queued = url
            except:
                pass
    
    def check_download_file(self,filepath):
        if not os.path.exists(filepath):
            return
        
        lines = []
        try:
            with open(filepath,"r") as f:
                lines = f.readlines()
                if len(lines) <= 0:
                    return
                lines = [line.strip() for line in lines]
        except:
            return
        
        
        print(f"Found {len(lines)} urls in {os.path.basename(filepath)}")
        response = input("Would you like to download them? [y/n]")
        if "y" in response.lower():
            print("Added them queue")
            for url in lines:
                if url not in self.queue:
                    self.queue.append(url)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("resolution", type=int, help="max resolution for video eg 720, 1080. if -1 then it uses your screen resolution",default=-1)
    args = parser.parse_args()
    max_resolution = None
    try:
        max_resolution = int(args.resolution)
    except:
        print(f"Got invalid resolution {max_resolution}")
        exit()

    if max_resolution == -1:
        # get display ressolution
        import ctypes
        user32 = ctypes.windll.user32
        max_resolution = user32.GetSystemMetrics(1)

    print(f"using {max_resolution}p")

    downloader = VideoDownloader(max_resolution)
    downloader.check_download_file("todownload.txt")
    downloader.start()
