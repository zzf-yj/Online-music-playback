import pygame
import requests
import os
pygame.mixer.init()
while True:
    search_text = input("请输入音乐名称：")
    url = f"https://music.163.com/api/search/get/web?csrf_token=hlpretag=&hlposttag=&s={search_text}&type=1"
    response = requests.get(url)
    result = response.json()
    songs = result['result']['songs']
    for song in songs:
        fee_type = song['fee']
        fee_str = "VIP" if fee_type == 1 else "免费" if fee_type == 0 else "付费"
        print(song['name'],song['id'],fee_str)
    song_id = input("请输入音乐ID:")
    api_url = f"https://music.163.com/song/media/outer/url?id={song_id}.mp3"
    print(api_url)
    save_dir = "music"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    save_path = os.path.join(save_dir, f"{song_id}.mp3")
    response = requests.get(api_url)
    real_url = response.url
    print(real_url)
    response = requests.get(real_url)
    response.raise_for_status()
    with open(save_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    print(save_path)
    pygame.mixer.music.stop()
    pygame.mixer.music.load(save_path)
    pygame.mixer.music.play()
    print("正在播放音乐。。。")
    clock = pygame.time.Clock()
    while pygame.mixer.music.get_busy():
        clock.tick(10)
        quit = input("结束：")
        if quit.lower() == 'quit':
            pygame.mixer.music.stop()
            continue