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


def dlfile(url, localfilename, date, title, num, download_file, fix_id3):
    ttt = title[len("kodsnack %d - ".format(num)):]
    
    # Open the url
    try:
        print("DL " + url + " to " + localfilename)
        
        if os.path.isfile(localfilename) == False:
            if download_file:
                f = urllib.request.urlopen(url)
                with open(localfilename, "wb") as local_file:
                    local_file.write(f.read())

            if download_file and fix_id3:
                # https://mutagen.readthedocs.org/en/latest/tutorial.html
                from mutagen.easyid3 import EasyID3
                audiofile = EasyID3(localfilename)
                
                # http://www.richardfarrar.com/what-id3-tags-should-you-use-in-a-podcast/
                
                audiofile.delete() # start fresh for consitency
                audiofile["artist"] = u"Kodsnack"
                audiofile["album"] = u"kodsnack.se"
                audiofile["titlesort"] = title # = Kodsnack 12 - Here comes the title
                audiofile["title"] = ttt # = Here comes the title
                audiofile["releasecountry"] = u'Sweden'
                audiofile["genre"] = u'Speech' # or vocal, podcast isn't supported
                audiofile["date"] = date
                audiofile["originaldate"] = date
                audiofile["website"] = u'www.kodsnack.se'
                audiofile["tracknumber"] = str(num)

                audiofile.save()
    #handle errors
    except urllib.error.HTTPError as e:
        print("HTTP Error:", e.code, url)
    except urllib.error.URLError as e:
        print("URL Error:", e.reason, url)


def bytetostr(b):
    return b.decode('utf-8')


def main():
    download_file = False
    fix_id3 = False

    episodes_content = bytetostr(urllib.request.urlopen('http://kodsnack.se/avsnitt/').read())
    for episide_href in re.findall('<li><span class="post-list"><time>(.*)</time> <a href="(.*)">', episodes_content):
        episode_request = urllib.request.urlopen(episide_href[1])
        encoding = episode_request.headers['content-type'].split('charset=')[-1]
        episode_content = bytetostr(episode_request.read())
        episode_parse_ok = True

        #  <h1 class="post-title">Kodsnack 74 - Resten av livet med dina handleder</h1>
        title_result = re.search('<h1 class="post-title">(.*)</h1>', episode_content)
        if title_result == None:
            print("Missing title for ", index)
            episode_parse_ok = False
        #print(title_result.group(1))

        # <span class="post-download"><a href="http://traffic.libsyn.com/kodsnack/24_oktober.mp3">Ladda ner (mp3)</a></span>
        download = re.search('<span class="post-download"><a href="(.*)">', episode_content)
        if download == None:
            print("Missing download for ", title_result.group(1))
            episode_parse_ok = False
        #print(download.group(1))
        
        episode_number_result = None
        if episode_parse_ok:
            episode_number_result = re.search('[Kk]odsnack ([0-9]+)', title_result.group(1))
            if episode_number_result == None:
                print("Unable to parse episode num")
                episode_parse_ok = False
        if episode_parse_ok:
            episodenum = int(episode_number_result.group(1))
            episodetitle = title_result.group(1)
            episodetitle = html.unescape(episodetitle)
            # we should change to the same extension that the source has, someday...
            dlfile(download.group(1), sanefilename(episodetitle)+ ".mp3", episide_href[0], episodetitle, episodenum, download_file, fix_id3)


if __name__ == '__main__':
    main()

