import os

import google.oauth2.credentials
import requests
from bs4 import BeautifulSoup
import random
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from dhooks import Webhook

hook = Webhook('webhookhere')
hook.send("**The client has successfully loaded. Please use the following link to authenticate your google account with the api**\n\nhttps://accounts.google.com/o/oauth2/auth?response_type=code&client_id=117631906657-amn0mk9dafpuvd87l6hfb0jfh9uhd4io.apps.googleusercontent.com&redirect_uri=urn%3Aietf%3Awg%3Aoauth%3A2.0%3Aoob&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fyoutube.force-ssl&state=0KIujlptgQita7nsISD6AydOGZX39l&prompt=consent&access_type=offline")

CLIENT_SECRETS_FILE = "client_secret.json"

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

def get_authenticated_service():
  flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
  credentials = flow.run_console()
  return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

def print_response(response):
  print(response)

def build_resource(properties):
  resource = {}
  for p in properties:
    prop_array = p.split('.')
    ref = resource
    for pa in range(0, len(prop_array)):
      is_array = False
      key = prop_array[pa]

      if key[-2:] == '[]':
        key = key[0:len(key)-2:]
        is_array = True

      if pa == (len(prop_array) - 1):
        if properties[p]:
          if is_array:
            ref[key] = properties[p].split(',')
          else:
            ref[key] = properties[p]
      elif key not in ref:
        ref[key] = {}
        ref = ref[key]
      else:
        ref = ref[key]
  return resource

def remove_empty_kwargs(**kwargs):
  good_kwargs = {}
  if kwargs is not None:
    for key, value in kwargs.items():
      if value:
        good_kwargs[key] = value
  return good_kwargs

def comment_threads_insert(client, properties, **kwargs):
  resource = build_resource(properties)

  kwargs = remove_empty_kwargs(**kwargs)

  response = client.commentThreads().insert(
    body=resource,
    **kwargs
  ).execute()

  return print_response(response)

def scrape(keyword):
    url = 'https://www.youtube.com/results?q={}&sp=CAISAggBUBQ%253D'.format(keyword)
    source_code = requests.get(url)
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text, 'html.parser')
    f = open(r'links.txt', 'w')
    for link in soup.findAll('a', {'class': 'yt-uix-tile-link'}):
        href = link.get('href')
        newhref = href.replace("/watch?v=", "")
        f.write(newhref + '\n')

if __name__ == '__main__':
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
  client = get_authenticated_service()



with open(r'comments.txt', 'r') as f:
    foo = [line.strip() for line in f]

# keyword
with open(r'keywords.txt', 'r') as f:
    foooo = [line.strip() for line in f]

keywords = open(r'keywords.txt', 'r')
i = 1
while i <= 19:
    for line in keywords:
        scrape(line)

        with open(r"links.txt", 'r+') as f:
            f.readline()
            data = f.read()
            f.seek(0)
            f.write(data)
            f.truncate()

            try:
                with open(r'links.txt', 'r') as f:
                    urls = []
                    for url in f:
                        rand = random.choice(foo)

                        comment_threads_insert(client,
                        {'snippet.channelId': 'UCNlM-pgjmd0NNE5I6MzlEGg',
                         'snippet.videoId': url,
                         'snippet.topLevelComment.snippet.textOriginal': rand},
                        part='snippet')
                        hook.send(f"**The comment:** ``{rand}`` **was successfully posted on the following video**\n\nhttps://youtube.com/watch?v={url}")
                        i += 1
            except:
                pass
            print("Scraping urls for relevance")
            hook.send("Scraping urls for relevance based on keywords")
