import requests

def download_file(url, filename):
    resp = requests.get(url)
    with open(filename, 'wb') as fd:
        for chunk in resp.iter_content(chunk_size=128):
            fd.write(chunk)