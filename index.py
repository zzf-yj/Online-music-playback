import tkinter as tk
from tkinter import ttk, messagebox
import pygame
import requests
import os
import tempfile
import json


class MusicPlayer:
    def __init__(self):
        pygame.mixer.init()
        self.window = tk.Tk()
        self.window.title("音乐播放器")
        self.window.geometry("600x500")

        self.temp_dir = tempfile.mkdtemp()

        # 设置请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://music.163.com/',
        }

        # 搜索框架
        search_frame = tk.Frame(self.window)
        search_frame.pack(pady=20)

        # 搜索输入框
        self.search_entry = tk.Entry(search_frame, width=50)
        self.search_entry.pack(side=tk.LEFT, padx=5)

        # 搜索按钮
        self.search_button = tk.Button(search_frame, text="搜索", command=self.search_music)
        self.search_button.pack(side=tk.LEFT)

        # 搜索结果列表框
        self.result_frame = tk.Frame(self.window)
        self.result_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.result_list = tk.Listbox(self.result_frame, width=60, height=10)
        self.result_list.pack(pady=10)

        # 双击播放
        self.result_list.bind('<Double-Button-1>', self.play_selected)

        # 状态标签
        self.status_label = tk.Label(self.window, text="当前未播放")
        self.status_label.pack(pady=10)

        # 存储搜索结果
        self.search_results = []

    def search_music(self):
        search_text = self.search_entry.get()
        if not search_text:
            messagebox.showwarning("警告", "请输入搜索内容!")
            return

        try:
            # 使用网易云音乐搜索API
            url = f"https://music.163.com/api/search/get/web?csrf_token=hlpretag=&hlposttag=&s={search_text}&type=1"
            response = requests.get(url, headers=self.headers)
            result = response.json()

            # 清空之前的搜索结果
            self.result_list.delete(0, tk.END)
            self.search_results.clear()

            if 'result' in result and 'songs' in result['result']:
                songs = result['result']['songs']
                for song in songs:
                    # 获取更详细的信息
                    song_name = song['name']
                    artist = song['artists'][0]['name']
                    album = song['album']['name']
                    duration = int(song['duration'] / 1000)  # 转换为秒
                    minutes, seconds = divmod(duration, 60)

                    # 获取付费类型
                    fee_type = song['fee']
                    fee_str = "VIP" if fee_type == 1 else "免费" if fee_type == 0 else "付费"

                    # 格式化显示信息
                    display_text = f"{song_name} - {artist} | 专辑: {album} | 时长: {minutes}:{seconds:02d} | {fee_str}"

                    self.result_list.insert(tk.END, display_text)
                    self.search_results.append({
                        'id': song['id'],
                        'name': song_name,
                        'artist': artist,
                        'fee': fee_type
                    })
            else:
                messagebox.showinfo("提示", "未找到相关音乐")

        except Exception as e:
            messagebox.showerror("错误", f"搜索失败: {str(e)}")

    def download_music(self, url, song_id):
        try:
            temp_file = os.path.join(self.temp_dir, f"{song_id}.mp3")

            if os.path.exists(temp_file):
                return temp_file

            response = requests.get(url, headers=self.headers, allow_redirects=True)
            real_url = response.url

            response = requests.get(real_url, headers=self.headers, stream=True)
            response.raise_for_status()

            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            return temp_file

        except Exception as e:
            raise Exception(f"下载失败: {str(e)}")

    def play_selected(self, event):
        selection = self.result_list.curselection()
        if not selection:
            return

        # 因为search_results中存储的是字典，所以要获取其中的id
        song_info = self.search_results[selection[0]]
        song_id = song_info['id']
        self.play_music(song_id)

    def play_music(self, song_id):
        try:
            self.status_label.config(text="正在加载音乐...")
            self.window.update()

            api_url = f"https://music.163.com/song/media/outer/url?id={song_id}.mp3"
            local_file = self.download_music(api_url, str(song_id))  # 转换为字符串

            pygame.mixer.music.stop()
            pygame.mixer.music.load(local_file)
            pygame.mixer.music.play()

            # 获取歌曲信息
            selected_index = self.result_list.curselection()[0]
            song_info = self.result_list.get(selected_index)
            self.status_label.config(text=f"正在播放: {song_info}")

        except Exception as e:
            messagebox.showerror("错误", f"播放失败: {str(e)}")
            self.status_label.config(text="播放失败")

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