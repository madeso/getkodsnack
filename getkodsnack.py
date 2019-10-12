#!/usr/bin/env python3

import urllib.request
import urllib.error
import re
import os
import os.path
import html


def sanefilename(filename):
    for c in r'[]/\;,><&*:%=+@!#^()|?^':
        filename = filename.replace(c,'')
    return filename


def fix_id3(localfilename, ttt, date, num):
    # https://mutagen.readthedocs.org/en/latest/tutorial.html
    from mutagen.easyid3 import EasyID3
    tags = EasyID3(localfilename)
    
    # http://www.richardfarrar.com/what-id3-tags-should-you-use-in-a-podcast/
    tags.delete() # start fresh for consitency
    tags["artist"] = u"Kodsnack"
    tags["album"] = u"kodsnack.se"
    tags["titlesort"] = title # = Kodsnack 12 - Here comes the title
    tags["title"] = ttt # = Here comes the title
    tags["releasecountry"] = u'Sweden'
    tags["genre"] = u'Speech' # or vocal, podcast isn't supported
    tags["date"] = date
    tags["originaldate"] = date
    tags["website"] = u'www.kodsnack.se'
    tags["tracknumber"] = str(num)

    tags.save()

def dlfile(url, localfilename, date, title, num, download_file, fix_id3):
    ttt = title[len("kodsnack %d - ".format(num)):]
    
    try:
        print("DL " + url + " to " + localfilename)
        
        if os.path.isfile(localfilename) == False:
            if download_file:
                f = urllib.request.urlopen(url)
                with open(localfilename, "wb") as local_file:
                    local_file.write(f.read())

            if download_file and fix_id3:
                fix_id3(localfilename, ttt, date, num)
    # display errors
    except urllib.error.HTTPError as e:
        print("HTTP Error:", e.code, url)
    except urllib.error.URLError as e:
        print("URL Error:", e.reason, url)


def bytetostr(b):
    return b.decode('utf-8')


def extract_number_from_url(url):
    last_char = url[len(url)-1:]
    if last_char == '/':
        url = url[:-1]
    url = url.rsplit('/', 1)[1]
    return url


def request_url(url, name):
    cache_folder = os.path.join(os.getcwd(), '.cache')
    os.makedirs(cache_folder, exist_ok=True)
    cache = os.path.join(cache_folder, name+'.html')
    if os.path.isfile(cache):
        with open(cache, 'r') as f:
            return f.read()
    else:
        content = bytetostr(urllib.request.urlopen(url).read())
        with open(cache, 'w') as f:
            f.write(content)
        return content


def main():
    download_file = False
    fix_id3 = False

    episodes_content = request_url('https://kodsnack.se/avsnitt/', 'episodes')
    for episode_href in re.findall('<li><span class="post-list"><time>(.*)</time> <a href="(.*)">', episodes_content):
        episode_content = request_url(episode_href[1], extract_number_from_url(episode_href[1]))
        episode_parse_ok = True

        #  <h1 class="post-title">Kodsnack 74 - Resten av livet med dina handleder</h1>
        title_result = re.search('<h1 class="post-title">(.*)</h1>', episode_content)
        if title_result == None:
            print("Missing title for ", index)
            episode_parse_ok = False
        episode_title = html.unescape(title_result.group(1))
        #print(episode_title)

        # <span class="post-download"><a href="http://traffic.libsyn.com/kodsnack/24_oktober.mp3">Ladda ner (mp3)</a></span>
        download = re.search('<span class="post-download"><a href="(.*)">', episode_content)
        if download == None:
            print("Missing download for ", episode_title)
            episode_parse_ok = False
        #print(download.group(1))
        
        episode_number_result = None
        if episode_parse_ok:
            episode_number_result = re.search('[Kk]odsnack ([0-9]+)', episode_title)
            if episode_number_result == None:
                print("Unable to parse episode num")
                episode_parse_ok = False
        if episode_parse_ok:
            episodenum = int(episode_number_result.group(1))
            # we should change to the same extension that the source has, someday...
            dlfile(download.group(1), sanefilename(episode_title)+ ".mp3", episode_href[0], episode_title, episodenum, download_file, fix_id3)


if __name__ == '__main__':
    main()

