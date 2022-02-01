import pathlib
import os
import dotenv
import requests
import shutil
from urllib import parse

import praw

dotenv.load_dotenv()


class RedditMemeCollector:
    REDDIT_IMAGE_URI = "https://i.redd.it/"
    BASE_MEMES_DIR = pathlib.Path(__file__).parent

    def create_reddit_client(self):
        client = praw.Reddit(
            client_id=os.environ.get("CLIENT_ID"),
            client_secret=os.environ.get("CLIENT_SECRET"),
            user_agent=os.environ.get("USER_AGENT"),
        )
        return client

    def _is_image(self, post):
        try:
            return post.post_hint == "image"
        except ArithmeticError:
            return False

    def get_image_url(self, client: praw.Reddit, subreddit_name: str, limit: int):
        hot_memes = client.subreddit(subreddit_name).hot(limit=limit)
        image_urls = list()

        for post in hot_memes:
            if self.REDDIT_IMAGE_URI in post.url:
                if self._is_image(post):
                    image_urls.append(post.url)
        return image_urls

    def get_image_name(self, image_url: str) -> str:
        image_name = parse.urlparse(image_url).path
        base_name = os.path.basename(image_name)
        return base_name

    def _create_folder(self, folder_name: str):
        os.mkdir(self.BASE_MEMES_DIR.joinpath("memes", folder_name))

    def store_images(self, folder_name: str, raw_response, image_name: str):
        """
        This method stores all the downloaded images into a folder.
        """
        create_in = self.BASE_MEMES_DIR.joinpath("memes", folder_name)
        if not os.path.exists(create_in):
            self._create_folder(folder_name)
        store_path = pathlib.Path(__file__).parent.joinpath("memes", folder_name)
        with open(f"{store_path}/{image_name}", "wb") as image_file:
            shutil.copyfileobj(raw_response, image_file)

    def _download_image(self, subreddit_name, image_url: str):
        image_name = self.get_image_name(image_url)
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            self.store_images(
                folder_name=subreddit_name,
                raw_response=response.raw,
                image_name=image_name,
            )

    def download_images(self, subreddit_name: str, limit: int = 30):
        """
        This method downloads memes based on subreddit_name passed to it
        and its limitation.
        """
        client = self.create_reddit_client()
        image_urls = self.get_image_url(
            client=client, subreddit_name=subreddit_name, limit=limit
        )
        for image_url in image_urls:
            self._download_image(subreddit_name, image_url)
        return "Done :)"


if __name__ == "__main__":
    r = RedditMemeCollector()
    r.download_images("memes", limit=5)
