import vlc, time, requests, youtube_dl, json
import urllib3, sys
import urllib.parse, re, requests
from urllib.error import URLError
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
from tkinter import messagebox
import emoji
import unicodedata

title_list=[]
mix_list=[]
max_song=0

yt_ops={'quiet': True}
headers = {
                        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36 OPR/67.0.3575.115', 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9'}
yt_init='https://www.youtube.com/watch?v='

def media_finish(event):
	print("--  media finish  --")
	print(event)

def chk(na):
    #print(na)
    req = urllib.request.Request(urllib.parse.unquote(na))
    try:
        res = urllib.request.urlopen(req, timeout=2)
        print(res.status)
        if(res.status!=200):
            return "Forbidden"
        else:
            return "200"
    except urllib.error.HTTPError as e:
        return "Forbidden"
    except URLError as error:
        print(error.reason)
        if isinstance(error.reason, socket.timeout):
            return "200"
        elif(len(str(error.reason).split("Errno"))>0):
            if str(error.reason).split("Errno")[1].split("]")[0].strip()=="101":
                return "200"
        else:
            print("other error")
            return "Forbidden"


def get_media(url,name):
    h=0
    while True:
        if(h>2):
            print("Unable to extract URL with")
            return "Unable"
        info=None
        with youtube_dl.YoutubeDL(yt_ops) as ydl:
            try:
                info = ydl.extract_info(url, download=False)['formats']
            except youtube_dl.utils.DownloadError as e:
                h+=1
                continue
        
        for myInfo in info:
            #if 'mp4a' in myInfo['acodec'] and myInfo['vcodec']=='none':
            if myInfo['format_id'] == '140':
                #print(myInfo)
                urls = myInfo['url']
                if(urls.split() == ""):
                    h+=1
                    continue
                if(chk(urls)=="200"):
                    return urls
                else:
                    continue
def removeEmoji2(value):
    new_subject = ""
    astral = re.compile(r'([^\u0000-\uffff])')
    for j, ss in enumerate(re.split(astral, value)):
        if not j%2:
            new_subject += ss
        else:
            new_subject += '?' 
    return new_subject
def removeEmoji(value):
    em = emoji.get_emoji_regexp().sub(u'',unicodedata.normalize('NFKC', value))
    return em

def ytpl_parse(j1):
    toGet=[]
    titleList=[]

    for i in j1['contents']['twoColumnWatchNextResults']['playlist']['playlist']['contents']:
        if(len(str(i).split("playlistPanelVideoRenderer"))>1):
            if 'unplayableText' not in i['playlistPanelVideoRenderer']:
                
                vid = i['playlistPanelVideoRenderer']['videoId']
                video_title=i['playlistPanelVideoRenderer']['title']['simpleText']
                toGet.append(yt_init+vid)
                em = removeEmoji(video_title)  
                try:
                    titleList.append(em)
                except:
                    em = removeEmoji2(video_title)
                    titleList.append(em)

    return titleList, toGet
	
def get_pl(url):
    mix = None
    while True:
        print("while")
        try:
            if(url.find('playlist?list=')!=-1 or url.find('&list=')!=-1):
                mix = requests.get(url, timeout=5, headers=headers)
            else:
                return False, False
        except (requests.ConnectionError, requests.Timeout) as exception:
            print("no internet")
        
        except Exception as e:
            print("Exception  "+str(e))
            time.sleep(2)
            continue

        soup = BeautifulSoup(mix.content, 'html.parser', from_encoding="utf8")
        search_results = str(soup.findAll("script"))

        if ("var ytInitialData = " in str(search_results)):
            str1 = search_results.strip().split('var ytInitialData = ')[1].split(';</script>')[0]
            j1 = json.loads(str1, encoding='utf8', strict=False)

            try:
                print("try 1")
                if(url.find('&list=')!=-1):
                    print(url)
                    titleList, toGet = ytpl_parse(j1)
                    return titleList, toGet
                elif(url.find('?list=')!=-1):

                    u = str(j1['contents']['twoColumnBrowseResultsRenderer']).split("playlistVideoRenderer")
                    for i in range(1, 2):
                        my = str(u[i])
                        
                        parses=urlparse(url)
                        pl_init= parse_qs(parses.query)['list'][0]
                        pl_vid = my.split(r"videoId': ")[1][1:].split(",")[0][:-1]
                    vurl='https://www.youtube.com/watch?v=%s&list=%s'%(pl_vid, pl_init)
                    print(vurl)

                    mix = requests.get(vurl, timeout=5, headers=headers)
                    soup = BeautifulSoup(mix.content, 'html.parser', from_encoding="utf8")
                    search_results = str(soup.findAll("script"))

                    if ("var ytInitialData = " in str(search_results)):

                        str1 = search_results.strip().split('var ytInitialData = ')[1].split(';</script>')[0]
                        j1 = json.loads(str1, encoding='utf8', strict=False)
                        titleList, toGet = ytpl_parse(j1)
                    
                        return titleList, toGet
                    else:
                        return "notAdd", False

            except:
                print("에러1")
                return False, False

        else:
            print("에러")
            return False, False

def openReal(yturl):
    global title_list,mix_list, max_song
    title_list1, mix_list1 = get_pl(yturl)
    if(title_list1 == False):
        messagebox.showerror("오류", '올바른 플레이리스트 URL인지 확인하여주세요')
    else:
        title_list = title_list + title_list1
        mix_list = mix_list + mix_list1
        max_song=len(mix_list)
        num=len(mix_list1)
        messagebox.showinfo("안내", "성공적으로 %s개의 곡을 추가하였습니다"%(str(num)))


address = 'https://www.youtube.com/playlist?list=PL4fGSI1pDJn6jXS_Tv_N9B8Z0HTRVJE0m'
print("address  "+str(address))
openReal(address)

print("end openReal")

vlc_instance = vlc.Instance('--verbose -1')
player = vlc_instance.media_player_new()
player.audio_set_volume(50)

my_event_manger = player.event_manager()
my_event_manger.event_attach(vlc.EventType.MediaPlayerEndReached, media_finish)

print("mix_list")
print(mix_list[0])
print("title_list")
print(title_list[0])

source = get_media(mix_list[0], title_list[0])
# creating a media
media = vlc_instance.media_new(source)

print(source)


player.set_media(media)
time.sleep(0.5)
player.play()
time.sleep(1)
duration = player.get_length()
print("duration : "+str(duration))
