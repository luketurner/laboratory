import requests
import os

def download_file(url: str, filename: str, mode=None):
    resp = requests.get(url)
    def opener(path, flags):
        return os.open(path, flags, mode=mode)
    with open(filename, 'wb', opener=opener) as fd:
        for chunk in resp.iter_content(chunk_size=128):
            fd.write(chunk)