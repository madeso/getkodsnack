#!/usr/bin/env python3

import urllib.request
import urllib.error
import re
import os
import os.path

import html

#print EasyID3.valid_keys.keys()
    # ['albumartistsort', 'musicbrainz_albumstatus', 'lyricist', 'musicbrainz_workid', 'releasecountry', 'date', 'performer',
    # 'musicbrainz_albumartistid', 'composer', 'catalognumber', 'encodedby', 'tracknumber', 'musicbrainz_albumid', 'album',
    # 'asin', 'musicbrainz_artistid', 'mood', 'copyright', 'author', 'media', 'length', 'acoustid_fingerprint', 'version',
    # 'artistsort', 'titlesort', 'discsubtitle', 'website', 'musicip_fingerprint', 'conductor', 'musicbrainz_releasegroupid',
    # 'compilation', 'barcode', 'performer:*', 'composersort', 'musicbrainz_discid', 'musicbrainz_albumtype', 'genre', 'isrc',
    # 'discnumber', 'musicbrainz_trmid', 'acoustid_id', 'replaygain_*_gain', 'musicip_puid', 'originaldate', 'language', 'artist',
    # 'title', 'bpm', 'musicbrainz_trackid', 'arranger', 'albumsort', 'replaygain_*_peak', 'organization', 'musicbrainz_releasetrackid']

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

    avsnitts = bytetostr(urllib.request.urlopen('http://kodsnack.se/avsnitt/').read())
    for mo in re.findall('<li><span class="post-list"><time>(.*)</time> <a href="(.*)">', avsnitts):
        req = urllib.request.urlopen(mo[1])
        encoding=req.headers['content-type'].split('charset=')[-1]
        content = bytetostr(req.read())
        webFile = content
        dodownload = True

        #  <h1 class="post-title">Kodsnack 74 - Resten av livet med dina handleder</h1>
        title = re.search('<h1 class="post-title">(.*)</h1>', webFile)
        if title == None:
            print("Missing title for ", index)
            dodownload = False
        #print(title.group(1))

        # <span class="post-download"><a href="http://traffic.libsyn.com/kodsnack/24_oktober.mp3">Ladda ner (mp3)</a></span>
        download = re.search('<span class="post-download"><a href="(.*)">', webFile)
        if download == None:
            print("Missing download for ", title.group(1))
            dodownload = False
        #print(download.group(1))
        
        episodere = None
        if dodownload:
            episodere = re.search('[Kk]odsnack ([0-9]+)', title.group(1))
            if episodere == None:
                print("Unable to parse episode num")
                dodownload = False
        if dodownload:
            episodenum = int(episodere.group(1))
            episodetitle = title.group(1)
            episodetitle = html.unescape(episodetitle)
            # we should change to the same extension that the source has, someday...
            dlfile(download.group(1), sanefilename(episodetitle)+ ".mp3", mo[0], episodetitle, episodenum, download_file, fix_id3)

if __name__ == '__main__':
    main()
