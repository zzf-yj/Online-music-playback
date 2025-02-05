import tkinter as tk
from tkinter import messagebox

import requests


def search_message():
    search_text = entry.get()
    if search_text:
        messagebox.showinfo("搜索结果：",f"您搜索的内容是: {search_text}")
        url = f"https://music.163.com/api/search/get/web?csrf_token=hlpretag=&hlposttag=&s={search_text}&type=1"
        response = requests.get(url)
        result = response.json()
        print(result)
    else:
        messagebox.showinfo("警告","请输入内容")
window = tk.Tk()
window.title("XX音乐播放器")
window.geometry("600x500")

entry = tk.Entry(window,width=50)
entry.pack(pady=20)

search = tk.Button(window,text="搜索",command=search_message)
search.pack()

window.mainloop()