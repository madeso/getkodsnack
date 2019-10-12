#!/usr/bin/env python3

import urllib.request
import urllib.error
import re
import os
import os.path
import html
import argparse
from bs4 import BeautifulSoup


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
        # todo(Gustav): ignore cache if it's older than 'some time'
        with open(cache, 'r') as f:
            return f.read()
    else:
        content = bytetostr(urllib.request.urlopen(url).read())
        with open(cache, 'w') as f:
            f.write(content)
        return content


class Episode:
    def __init__(self, url, date, title, num):
        self.url = url
        self.date = date
        self.title = title
        self.num = num
        self.alt_titles = []


def get_episodes():
    episodes_soup = BeautifulSoup(request_url('https://kodsnack.se/avsnitt/', 'episodes'), 'html.parser')
    episodes_post_list = episodes_soup.find_all('span', class_='post-list')
    for episode_post in episodes_post_list:
        episode_date = episode_post.time.string
        episode_url = episode_post.a['href']

        episode_content = request_url(episode_url, extract_number_from_url(episode_url))

        # default properties
        episode_number = -1
        episode_title = ''
        download_file = ''

        #  <h1 class="post-title">Kodsnack 74 - Resten av livet med dina handleder</h1>
        title_result = re.search('<h1 class="post-title">(.*)</h1>', episode_content)
        if title_result != None:
            episode_title = html.unescape(title_result.group(1))

        # <span class="post-download"><a href="http://traffic.libsyn.com/kodsnack/24_oktober.mp3">Ladda ner (mp3)</a></span>
        download = re.search('<span class="post-download"><a href="(.*)">', episode_content)
        if download != None:
            download_file = download.group(1)
        
        episode_number_result = re.search('[Kk]odsnack ([0-9]+)', episode_title)
        if episode_number_result == None:
            print("Unable to parse episode num")
            episode_parse_ok = False
            episode_number = int(episode_number_result.group(1))

        yield Episode(download_file, episode_date, episode_title, episode_number)


def handle_download(args):
    download_file = args.download
    fix_id3 = args.fix_id3
    for episode in get_episodes():
        # we should change to the same extension that the source has, someday...
        if episode.url == '':
            print('Missing download for {}'.format(episode.title))
        else:
            dlfile(episode.url, sanefilename(episode.title)+ ".mp3", episode.date, episode.title, episode.num, download_file, fix_id3)


def handle_ls(args):
    for episode in get_episodes():
        if args.print:
            print(episode.title)


def handle_titles(args):
    for episode in get_episodes():
        print(episode.title)
        for t in episode.alt_titles:
            print(t)

        print()


def main():
    parser = argparse.ArgumentParser(description='download and probe tool for kodsnack episodes')
    sub_parsers = parser.add_subparsers(dest='command_name', title='Commands', help='', metavar='<command>')

    sub = sub_parsers.add_parser('download', help='')
    sub.add_argument('--no-download', dest='download', action='store_false', help="don't download the episodes")
    sub.add_argument('--no-fix', dest='fix_id3', action='store_false', help="don't fix the id3 tags")
    sub.set_defaults(func=handle_download)

    sub = sub_parsers.add_parser('ls', help='')
    sub.add_argument('--quiet', dest='print', action='store_false', help="don't print anything")
    sub.set_defaults(func=handle_ls)

    sub = sub_parsers.add_parser('titles', help='')
    sub.set_defaults(func=handle_titles)

    args = parser.parse_args()
    if args.command_name is not None:
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

