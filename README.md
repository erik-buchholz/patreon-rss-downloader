# Patreon RSS Downloader
Small script that allows to download all audios from a Patreon Premium RSS Link.
This script targets the _Private RSS links_ you can find on `patreon.com/CREATOR/membership`.

## Usage

### URL Mode

Download all Audios from the provided RSS feed.

    python3 main.py -u URL -o OUTPUT_DIRECTORY
    
### File Mode

Download all Audios in the local RSS XML file.

    python3 main.py -f FILENAME -o OUTPUT_DIRECTORY
