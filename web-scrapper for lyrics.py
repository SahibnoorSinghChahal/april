#imports
import pandas as pd
from bs4 import BeautifulSoup
import requests
import time
import re
import time
import os
import pickle
from tqdm import tqdm_notebook as tqdm
from langdetect import detect

def preprocess(lyric):
    lyric.replace("\n", " ")
    lyric=re.sub(r'\[.+\]','',lyric)
    lyric=re.sub(r'Usage.+that.','',lyric)
    return lyric

def data_collection(path = "data/songs/csv6"):
    songs = []
    artist = []
    serial = []
    files = os.listdir(path)
    for i in files:
        data = pd.read_csv(os.path.join(path, i))
        #print(data)
        songs.extend(data['Song'])
        artist.extend(data['Artist'])
        serial.extend(data['Serial'])
   
    #print(songs[0])
    #combination = zip(artist, songs, serial)

    return songs,artist


def generate_corpus():
    songs,artist = data_collection()
    length=len(songs)
    lyrics = []
    for i in tqdm(range(length)):
        #print("Song ", i[2], ": ", i[1])
        try:
            ar=artist[i].replace("'","")
            so=songs[i].replace("'","")
            URL='https://www.azlyrics.com/lyrics/{0}/{1}.html'.format(ar.replace(' ', ''),so.replace(' ',''))
            URL=URL.replace(',','')
            URL=URL.replace(' ','')
            #print(URL)
            page = requests.get(URL)
            html = BeautifulSoup(page.text, "html.parser")
            page_lyric = html.find_all("div", limit=22)[-1]
            lyric = ''.join(page_lyric.find_all(text=True))
            
            lyric=preprocess(lyric)
            #print(lyric)
            if type(lyric) == 'en':
                lyrics.append(lyric)
        except (AttributeError,ConnectionResetError, ConnectionError,requests.exceptions.RequestException):
            try:
                ar=artist[i].replace("'","")
                so=songs[i].replace("'","")
                URL='http://genius.com/amp/{0}-{1}-lyrics'.format(ar.replace(' ', '-'),so.replace(' ','-'))
                URL=URL.replace(',','')
                URL=URL.replace('--','-')
                #print(URL)
                #urlopen_with_retry(URL)
                page = requests.get(URL)
                html = BeautifulSoup(page.text, "html.parser")
                lyric = html.find("div", class_="lyrics").get_text()
                #lyric = html.find("div",class_="song").get_text()
                lyric=preprocess(lyric)
                if type(lyric) == 'en':
                    lyrics.append(lyric)
            except(AttributeError,ConnectionResetError,requests.exceptions.RequestException):
                pass
                #time.sleep(10)
                #print("")
            #print("")
            time.sleep(10)
        
    filename = 'data/model/corpuscsv6' + str(len(lyrics)) + '.pkl'
    pickle.dump(lyrics, open(filename, 'wb'))
    print("Corpus file generated!")

# In[]:

generate_corpus()