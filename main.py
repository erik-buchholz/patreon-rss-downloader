#!/usr/bin/env python3
import logging
import os
import re
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime
from xml.etree.ElementTree import Element

import requests

# Constants
OUTPUT_DIR = "out"
INPUT_FILE = "rss.xml"

# Logging
logging.basicConfig(level=logging.INFO)


def download_file(url: str, file_path: str):
    """
    Download the file at the given URL to the given path.
    From:
    https://stackoverflow.com/questions/33488179/how-do-i-download-pdf-file-over-https-with-python
    :param url: URL to download from
    :param file_path: file to write into
    """
    r = requests.get(url, auth=('usrname', 'password'),
                     stream=True)
    r.raw.decode_content = True
    with open(file_path, 'wb') as f:
        shutil.copyfileobj(r.raw, f)


def remove_special(string: str) -> str:
    """

    :param input_string:
    :return:
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

    tree = ET.parse(INPUT_FILE)
    rss: Element = tree.getroot()
    channel: Element = rss[0]
    i = 0
    child: Element
    for child in channel:
        if child.tag == "item":
            title = ""
            url = ""
            data_type = ""
            for tag in child:
                tag: Element
                if tag.tag == "title":
                    title = title + remove_special(tag.text)
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


