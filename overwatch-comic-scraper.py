#!/usr/bin/env python3

import os
import sys
from bs4 import BeautifulSoup
import requests


def get_page() -> str:
    """
    Gets the page from the Overwatch website.
    """
    url = "https://playoverwatch.com/en-us/media/stories/"
    page = requests.get(url)

    if page.status_code != 200:
        print("Error while fetching main story page: " + str(page.status_code))

    return page.text


def get_story_urls(page: str) -> list:
    """
    Gets the story urls from the given HTML.
    """
    soup = BeautifulSoup(page, "html.parser")

    story_urls = soup.find_all("a", {"class": "CardLink"})

    return [link["href"] for link in story_urls]


def get_story_page(url: str) -> str:
    """
    Gets the story page from the given URL.
    """
    # The hrefs aren't absolute, so we need to add the base url.
    if "https://playoverwatch.com/en-us" not in url:
        url = "https://playoverwatch.com/en-us" + url

    page = requests.get(url)

    if page.status_code != 200:
        print(f"Error while fetching story page {url}: " + str(page.status_code))

    return page.text


def get_download_link(page: str) -> str:
    """
    Gets the download link from the given HTML.
    """
    soup = BeautifulSoup(page, "html.parser")

    return soup.find("a", {"class": "MediaSection-link--download"})["href"]


def download_story(url: str, file_name: str, path=os.getcwd()) -> None:
    """
    Downloads the story from the given URL.
    """

    if file_name.endswith(".pdf") is False:
        file_name += ".pdf"

    page = requests.get(url)

    if page.status_code != 200:
        print(f"Error while downloading story {url}: " + str(page.status_code))
        return

    with open(os.path.join(path, file_name), "wb") as f:
        f.write(page.content)
        f.close()


def get_story_name(page: str) -> str:
    """
    Gets the story name from the given HTML.
    """
    soup = BeautifulSoup(page, "html.parser")
    return soup.find("h2", {"class": "MediaHeader-title"}).text


if __name__ == "__main__":
    page = get_page()
    story_urls = get_story_urls(page)

    print(f"Found {len(story_urls)} stories.")

    for story_url in story_urls:
        story_page = get_story_page(story_url)
        download_link = get_download_link(story_page)
        file_name = get_story_name(story_page)

        if download_link is None:
            print(f"Couldn't find download link for {story_url}, exiting.")
            exit(1)

        print(f"Downloading {file_name} ({download_link})")

        # This could be done in parallel, but I'm lazy. (thanks copilot lol)
        if len(sys.argv) <= 1:
            download_story(download_link, file_name)
        else:
            download_story(download_link, file_name, sys.argv[1])
