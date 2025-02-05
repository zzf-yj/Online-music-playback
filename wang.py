import tkinter as tk
from tkinter import ttk, messagebox
import pygame
import requests
import os
import tempfile


class MusicPlayer:
    def __init__(self):
        pygame.mixer.init()
        self.window = tk.Tk()
        self.window.title("音乐播放器")
        self.window.geometry("400x250")

        self.temp_dir = tempfile.mkdtemp()

        # 设置请求头和代理
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://music.163.com/',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }

        search_frame = tk.Frame(self.window)
        search_frame.pack(pady=20)

        tk.Label(search_frame, text="输入歌曲ID:").pack(side=tk.LEFT)

        self.entry = tk.Entry(search_frame, width=20)
        self.entry.pack(side=tk.LEFT, padx=5)

        self.play_button = tk.Button(search_frame, text="播放", command=self.play_music)
        self.play_button.pack(side=tk.LEFT)

        self.status_label = tk.Label(self.window, text="当前未播放")
        self.status_label.pack(pady=10)

    def download_music(self, url, song_id):
        try:
            temp_file = os.path.join(self.temp_dir, f"{song_id}.mp3")

            if os.path.exists(temp_file):
                return temp_file

            # 先获取真实的音乐URL
            response = requests.get(url, headers=self.headers, allow_redirects=True)
            real_url = response.url

            # 下载音乐文件
            response = requests.get(real_url, headers=self.headers, stream=True)
            response.raise_for_status()

            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            return temp_file

        except Exception as e:
            raise Exception(f"下载失败: {str(e)}")

    def play_music(self):
        song_id = self.entry.get().strip()
        if not song_id:
            messagebox.showwarning("警告", "请输入歌曲ID!")
            return

        try:
            self.status_label.config(text="正在加载音乐...")
            self.window.update()

            # 使用备用API获取音乐URL
            api_url = f"https://music.163.com/song/media/outer/url?id={song_id}.mp3"
            local_file = self.download_music(api_url, song_id)

            pygame.mixer.music.stop()
            pygame.mixer.music.load(local_file)
            pygame.mixer.music.play()

            self.status_label.config(text=f"正在播放: 歌曲ID {song_id}")

        except Exception as e:
            messagebox.showerror("错误", f"播放失败: {str(e)}")
            self.status_label.config(text="播放失败")

            # 尝试使用备用方法
            try:
                # 使用另一个API接口
                backup_url = f"http://music.163.com/api/song/enhance/player/url?id={song_id}&ids=[{song_id}]&br=320000"
                response = requests.get(backup_url, headers=self.headers)
                data = response.json()
                if data['code'] == 200 and data['data'][0]['url']:
                    local_file = self.download_music(data['data'][0]['url'], song_id)
                    pygame.mixer.music.load(local_file)
                    pygame.mixer.music.play()
                    self.status_label.config(text=f"正在播放: 歌曲ID {song_id}")
            except:
                self.status_label.config(text="所有尝试均失败")

    def cleanup(self):
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
        except:
            pass

    def run(self):
        try:
            self.window.mainloop()
        finally:
            self.cleanup()


if __name__ == "__main__":
    player = MusicPlayer()
    player.run()