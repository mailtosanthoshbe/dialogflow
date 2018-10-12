import ast
import base64
import html
import json
import os
import re
import urllib.request
import vlc
import logger
import requests
import urllib3.request
from bs4 import BeautifulSoup
from mutagen.mp4 import MP4, MP4Cover
from pySmartDL import SmartDL
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from pyDes import *

# Pre Configurations
urllib3.disable_warnings()
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
unicode = str
raw_input = input


def addtags(filename, json_data, playlist_name):
    audio = MP4(filename)
    audio['\xa9nam'] = unicode(json_data['song'])
    audio['\xa9ART'] = unicode(json_data['primary_artists'])
    audio['\xa9alb'] = unicode(json_data['album'])
    audio['aART'] = unicode(json_data['singers'])
    audio['\xa9wrt'] = unicode(json_data['music'])
    audio['desc'] = unicode(json_data['starring'])
    audio['\xa9gen'] = unicode(playlist_name)
    # audio['cprt'] = track['copyright'].encode('utf-8')
    # audio['disk'] = [(1, 1)]
    # audio['trkn'] = [(int(track['track']), int(track['maxtracks']))]
    audio['\xa9day'] = unicode(json_data['year'])
    audio['cprt'] = unicode(json_data['label'])
    # if track['explicit']:
    #    audio['rtng'] = [(str(4))]
    cover_url = json_data['image'][:-11] + '500x500.jpg'
    fd = urllib.request.urlopen(cover_url)
    cover = MP4Cover(fd.read(), getattr(MP4Cover, 'FORMAT_PNG' if cover_url.endswith('png') else 'FORMAT_JPEG'))
    fd.close()
    audio['covr'] = [cover]
    audio.save()


def setProxy():
    base_url = 'http://h.saavncdn.com'
    proxy_ip = ''
    if ('http_proxy' in os.environ):
        proxy_ip = os.environ['http_proxy']
        print("proxy_ip %s" %proxy_ip)
    proxies = {
        'http': proxy_ip,
        'https': proxy_ip,
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0'
    }
    return proxies, headers


def setDecipher():
    return des(b"38346591", ECB, b"\0\0\0\0\0\0\0\0", pad=None, padmode=PAD_PKCS5)


def searchSongs(query):
    songs_json = []
    albums_json = []
    playLists_json = []
    topQuery_json = []
    respone = requests.get(
        'https://www.saavn.com/api.php?_format=json&query={0}&__call=autocomplete.get'.format(query))
    if respone.status_code == 200:
        respone_json = json.loads(respone.text.splitlines()[6])
        albums_json = respone_json['albums']['data']
        songs_json = respone_json['songs']['data']
        playLists_json = respone_json['playlists']['data']
        topQuery_json = respone_json['topquery']['data']
    return {"albums_json": albums_json,
            "songs_json": songs_json,
            "playLists_json": playLists_json,
            "topQuery_json": topQuery_json}

def extractdata(url, html_doc, meta_data_list):
    """
    :param url: Link of the song.
    :param html_doc: Webpage corresponding to url
    :param meta_data_list: Saves relevant information.
    """
    count = 0

    # Removes quotes from Title name.
    html_doc = re.sub(r'\(From .*?\)', "", html_doc.decode('utf-8'))
    # Visit https://github.com/LinuxSDA/InstaGaana/issues/2 for more info.

    soup = BeautifulSoup(html_doc, 'html.parser')

    song_list = map(str, soup.find_all("div", "hide song-json"))

    for x in song_list:
        count += 1
        try:
            song_info = json.loads(x[28:-6])
        except Exception as e:
            print("Unexpected Error: " + str(e) + "\nReport Bug.")
            continue

        meta_data = {}

        if url is None or url[23:] == song_info['perma_url'][23:]:
            meta_data['title'] = song_info['title']
            meta_data['singers'] = song_info['singers']
            meta_data['url'] = song_info['url']
            meta_data['album'] = song_info['album']
            meta_data['image_url'] = song_info['image_url']
            meta_data['duration'] = song_info['duration']
            meta_data['year'] = song_info['year']
            meta_data['perma_url'] = song_info['perma_url']
            meta_data['album_url'] = song_info['album_url']

            meta_data_list.append(meta_data)

            if url is not None or count == 6:
                break

def getPlayList(listId):
    songs_json = []
    headers = {
            'Pragma': 'no-cache',
            'Origin': 'http://www.saavn.com',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en-US;q=0.8,en;q=0.6',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/57.0.2987.98 Safari/537.36',
        }
    url = 'https://www.saavn.com/api.php?listid={0}&_format=json&__call=playlist.getDetails'.format(listId)
    print("Download url %s" % url)
    try:
        html_doc = requests.get(url=url, headers=headers)
        print("response %s" % html_doc.content)
    except Exception as e:
        print("Unexpected Error: " + str(e) + "\nCheck URL.")
        exit()
    extractdata(None, html_doc.content, None)

    respone = requests.get(
        'https://www.saavn.com/api.php?listid={0}&_format=json&__call=playlist.getDetails'.format(listId), verify=False)
    if respone.status_code == 200:
        songs_json = json.loads(respone.text.splitlines()[4])
    return songs_json


def getAlbum(albumId):
    songs_json = []
    respone = requests.get(
        'https://www.saavn.com/api.php?_format=json&__call=content.getAlbumDetails&albumid={0}'.format(albumId),
        verify=False)
    if respone.status_code == 200:
        songs_json = json.loads(respone.text.splitlines()[6])
    return songs_json


def getSong(songId):
    songs_json = []
    respone = requests.get(
        'http://www.saavn.com/api.php?songid={0}&_format=json&__call=song.getDetails'.format(songId), verify=False)
    if respone.status_code == 200:
        print(respone.text)
        songs_json = json.loads(respone.text.splitlines()[5])
    return songs_json


def getHomePage():
    playlists_json = []
    respone = requests.get(
        'https://www.saavn.com/api.php?__call=playlist.getFeaturedPlaylists&_marker=false&language=tamil&offset=1&size=250&_format=json',
        verify=False)
    if respone.status_code == 200:
        playlists_json = json.loads(respone.text.splitlines()[2])
        playlists_json = playlists_json['featuredPlaylists']
    return playlists_json


def downloadSongs(songs_json):
    des_cipher = setDecipher()
    for song in songs_json['songs']:
        try:
            enc_url = base64.b64decode(song['encrypted_media_url'].strip())
            dec_url = des_cipher.decrypt(enc_url, padmode=PAD_PKCS5).decode('utf-8')
            dec_url = dec_url.replace('_96.mp4', '_320.mp4')
            filename = html.unescape(song['song']) + '.m4a'
            filename = filename.replace("\"", "'")
        except Exception as e:
            logger.error('Download Error' + str(e))
        try:
            location = os.path.join(os.path.sep, os.getcwd(), "songs", filename)
            if os.path.isfile(location):
               print("Downloaded %s" % filename)
            else :
                print("Downloading %s" % filename)
                obj = SmartDL(dec_url, location)
                obj.start()
                name = songs_json['name'] if ('name' in songs_json) else songs_json['listname']
                addtags(location, song, name)
                print('\n')
        except Exception as e:
             logger.error('Download Error' + str(e))


if __name__ == '__main__':
    #input_url = input('Enter the url:').strip()
    song = {
    "id":"vlc9ShNl",
    "type":"",
    "song":"Un Kadhal Irundhal Podhum",
    "album":"Kavalai Vendam",
    "year":"2016",
    "music":"Leon James",
    "music_id":"471083",
    "primary_artists":"Armaan Malik, Leon James, Shashaa Tirupati",
    "primary_artists_id":"464656, 471083, 697946",
    "featured_artists":"",
    "featured_artists_id":"",
    "singers":"Leon James, Armaan Malik & Shashaa Tirupati, Armaan Malik, Leon James, Shashaa Tirupati",
    "starring":"Jiiva, Kajal Aggarwal",
    "image":"https:\/\/c.saavncdn.com\/629\/Kavalai-Vendam-Tamil-2016-150x150.jpg",
    "label":"Sony Music Entertainment",
    "albumid":"2848119",
    "language":"tamil",
    "origin":"playlist",
    "play_count":"49501",
    "copyright_text":"(P) 2016 Sony Music Entertainment India Pvt. Ltd.",
    "320kbps":"true",
    "explicit_content":0,
    "has_lyrics":"false",
    "encrypted_media_url":"ID2ieOjCrwfgWvL5sXl4B1ImC5QfbsDyLlNyB0Lri+gNeNBc2J8dZZpn69UFqVQ39gk4mJRfHTPtu9D\/0CmK7Bw7tS9a8Gtq",
    "encrypted_media_path":"NMKyboFo\/Fi+0Csd3pfq6ecqdo1j89aRsxCTZYkrupNQII9tMjOwvrOLUtP9AwaV",
    "media_preview_url":"https:\/\/preview.saavncdn.com\/629\/f917810aa7fe39ee3ac2799ebb911621_96_p.mp4",
    "perma_url":"https:\/\/www.saavn.com\/s\/song\/tamil\/Kavalai-Vendam\/Un-Kadhal-Irundhal-Podhum\/BgQICCdYeV8",
    "album_url":"https:\/\/www.saavn.com\/s\/album\/tamil\/Kavalai-Vendam-2016\/y3H54e8BA-k_",
    "duration":"271",
    "release_date":"2016-10-17"
    }
    des_cipher = setDecipher()
    Instance = vlc.Instance()
    try:
        enc_url = base64.b64decode(song['encrypted_media_url'].strip())
        print("enc_url %s" % enc_url)
      
        dec_url = des_cipher.decrypt(enc_url, padmode=PAD_PKCS5).decode('utf-8')
        print("dec_url 1 %s" % dec_url)
        dec_url = dec_url.replace('_96.mp4', '_320.mp4')
        print("dec_url 2 %s" % dec_url)
        filename = html.unescape(song['song']) + '.m4a'
        filename = filename.replace("\"", "'")
        print("filename %s" % filename)
      
    except Exception as e:
        logger.error('Download Error' + str(e))
    try:
        location = os.path.join(os.path.sep, os.getcwd(), "songs", filename)
        print("location %s" % location)
      
        if os.path.isfile(location):
            print("Downloaded %s" % filename)
        else :
            print("Downloading %s" % filename)
            obj = SmartDL(dec_url, location)
            obj.start()
            #name = songs_json['name'] if ('name' in songs_json) else songs_json['listname']
            name = "Mumbai To Chennai"
            #addtags(location, song, name)
          
            print('\n')
    except Exception as e:
            logger.error('Download Error' + str(e))

# getSongID = soup.select(".current-song")[0]["data-songid"]
# if getSongID is not None:
#    print(getPlayListID)
#    sys.exit()
# for playlist in getHomePage():
#     print(playlist)
#     id = raw_input()
#     if id is "1":
#       downloadSongs(getPlayList(playlist['listid']))
# queryresults = searchSongs('nannare')
# print(json.dumps(getSong(queryresults['topQuery_json'][0]['id']), indent=2))
# response = requests.head(dec_url)
# if os.path.isfile(location) if (os.stat(location).st_size >  int(response.headers["Content-Length"])) else False: