import requests

def uploadFile(file):
    link = 'https://tmpfiles.org/api/v1/upload'
    response = requests.post(link, files={'file': file}).json()

    return response['data']['url']
