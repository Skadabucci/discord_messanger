import argparse
import os
import random
import requests
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
DATA_BASEDIR = Path(os.path.dirname(__file__)) / 'data'
HOME_CONCERT_SKIPS: int = 1

class TinyDeskBot:
    def __init__(self, data_file, webhook_urls: list[str]):
        self.home_concert_skips = HOME_CONCERT_SKIPS
        self.data_file = DATA_BASEDIR / data_file
        self.webhook_urls = webhook_urls
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        self.sent_videos_file = DATA_BASEDIR / 'sent_videos.txt'
        self.sent_videos = self.load_sent_videos()

    def load_sent_videos(self) -> list[str]:
        if not os.path.exists(self.sent_videos_file):
            return list()
        with open(self.sent_videos_file, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file]

    def save_sent_video(self, video):
        with open(self.sent_videos_file, 'a', encoding='utf-8') as file:
            file.write(video + '\n')
        self.sent_videos.add(video)

    def get_random_concert(self):
        with open(self.data_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        available_lines = [line for line in lines if line.strip() not in self.sent_videos]
        if not available_lines:
            raise Exception("No more new concerts available.")

        choice: str = random.choice(available_lines).strip()
        while self.home_concert_skips > 0 and '(Home)' in choice:
            self.home_concert_skips -= 1
            choice = random.choice(available_lines).strip()
        return choice

    def search_youtube(self, query):
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&key={self.youtube_api_key}"
        response = requests.get(url)
        data = response.json()
        if 'items' in data and len(data['items']) > 0:
            return f"https://www.youtube.com/watch?v={data['items'][0]['id']['videoId']}"
        else:
            raise Exception(f"No YouTube video found for the query {query}.")

    def post_to_discord(self, message):
        data = {
            "content": message
        }
        responses = []
        for webhook_url in self.webhook_urls:
            responses.append(requests.post(webhook_url, json=data))
        for response in responses:
            if response.status_code != 204:
                raise Exception(f"Failed to send message to Discord webhook. Status code: {response.status_code}")

    def run(self):
        try:
            concert = self.get_random_concert()
            youtube_link = self.search_youtube(concert)
            self.post_to_discord(youtube_link)
            self.save_sent_video(concert)
        except Exception as e:
            print(f"Error: {e}")
    
    def backfill(self):
        self.load_sent_videos()
        for video in self.sent_videos:
            youtube_link = self.search_youtube(video)
            self.post_to_discord(youtube_link)
            time.sleep(5)

def main():
    parser = argparse.ArgumentParser(description='Tiny Desk Bot')
    parser.add_argument('--data-file', type=str, default='npr_tiny_desk_concerts.txt', help='The data file to use')
    parser.add_argument('--backfill', action='store_true', help='Run backfill instead of the default run')
    args = parser.parse_args()

    discord_urls = os.getenv('DISCORD_WEBHOOK_URLS').split(',')
    bot = TinyDeskBot(args.data_file, discord_urls)

    if args.backfill:
        bot.backfill()
    else:
        bot.run()

if __name__ == '__main__':
    main()
