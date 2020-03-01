#!/usr/bin/env python3
"""
A simple downloader for all audio files from a Patreon Premium Audio RSS.
"""
import logging
import os
import re
import tempfile

from clint.textui import progress
import xml.etree.ElementTree as ET
from datetime import datetime
from xml.etree.ElementTree import Element
import requests

# Constants
OUTPUT_DIR = "out"
INPUT_FILE = "rss.xml"
URL = ""
MODE = "URL"  # FILE for reading from FILE and URL otherwise.

# Logging
FORMAT = '%(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)


def download_file(url: str, file_path: str) -> None:
    """
    Download the file at the given URL to the given path, but skip if the file
    exists and has the correct size. Otherwise overwrite.
    From:
    https://stackoverflow.com/questions/15644964/python-progress-bar-and-downloads/15645088
    :param url: URL to download from.
    :param file_path: File path to write into.
    """
    r = requests.get(url, stream=True)
    total_length = int(r.headers.get('content-length'))
    if os.path.exists(file_path):
        # Compare length
        file_size = os.path.getsize(file_path)
        if file_size == total_length:
            logging.info("Skipping because file exists.")
            return
    with open(file_path, 'wb') as f:
        for chunk in progress.bar(r.iter_content(chunk_size=1024),
                                  expected_size=(total_length / 1024) + 1):
            if chunk:
                f.write(chunk)
                f.flush()


def get_filename(string: str) -> str:
    """
    Replace umlauts and other special character to create a legal filename.
    Adapted from:
    https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename
    :param string: string to convert.
    :return: Converted string that can be used as filename.
    """
    import unicodedata
    string = string.replace("ä", "ae")
    string = string.replace("ö", "oe")
    string = string.replace("ü", "ue")
    string = string.replace("ß", "ss")
    string = string.replace(".", "-")
    string = unicodedata.normalize('NFKD', string).encode('ascii',
                                                          'ignore')
    string = string.decode('ascii')
    string = re.sub('[^\w\s-]', '', string).strip().lower()
    string = re.sub('[\s]+', '_', string)

    return string


def determine_ending(data_type: str) -> str:
    """
    Determine the suitable file ending based on the given mimetype.
    :param data_type: Mime Type in the RSS.
    :return: File ending as string.
    """
    if data_type == "audio/x-wav":
        return ".wav"
    elif data_type == "audio/mpeg":
        return ".mp3"
    elif data_type == "audio/x-m4a":
        return ".m4a"
    else:
        raise RuntimeError("Unknown data type: " + data_type)


if __name__ == "__main__":
    # Create dir
    current_dir = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_DIR = current_dir + "/" + OUTPUT_DIR
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if MODE == "FILE":
        tree = ET.parse(INPUT_FILE)
    elif MODE == "URL":
        r = requests.get(URL, stream=True)
        tmp_file = tempfile.NamedTemporaryFile(mode="w+")
        tmp_file.write(r.content.decode())
        tree = ET.parse(tmp_file.name)
    else:
        raise RuntimeError("Unknown MODE, only 'FILE' and 'URL' allowed.")
    rss: Element = tree.getroot()
    channel: Element = rss[0]
    i = 0
    child: Element
    # Count elements first:
    for child in channel:
        if child.tag == "item":
            i += 1
    logging.info(f"Found {i} Items to download.")
    for child in channel:
        if child.tag == "item":
            title = ""
            url = ""
            data_type = ""
            for tag in child:
                tag: Element
                if tag.tag == "title":
                    title = title + get_filename(tag.text)
                if tag.tag == "pubDate":
                    d = datetime.strptime(tag.text, "%a, %d %b %Y %H:%M:%S "
                                                    "GMT")
                    date = d.strftime("%Y-%m-%d_")
                    title = date + title
                if tag.tag == "enclosure":
                    url = tag.get("url")
                    data_type = tag.get("type")
            if title == "" or url == "" or data_type == "":
                raise RuntimeError(f"Could not identify item: Title - "
                                   f"{title}, Type - {data_type}, URL - {url}")
            ending = determine_ending(data_type)
            filename = title + ending
            file_path = OUTPUT_DIR + '/' + filename
            logging.info(f"Downloading: {filename}")
            download_file(url, file_path)
            logging.info(f"Download completed.")
