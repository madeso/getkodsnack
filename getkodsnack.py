#!/usr/bin/env python3

##############################################################################
## Imports

import urllib.request
import urllib.error
import re
import os
import os.path
import html
import argparse
import itertools
import collections
from bs4 import BeautifulSoup


##############################################################################
## Constants

# source: https://github.com/peterdalle/svensktext
SWEDISH_STOP_WORDS = [
        'aderton', 'adertonde', 'adjö', 'aldrig', 'all', 'alla', 'allas', 'allt', 'alltid', 'alltså', 'andra', 'andras', 'annan', 'annat', 'artonde', 'artonn', 'att', 'av', 'bakom', 'bara', 'behöva',
        'behövas', 'behövde', 'behövt', 'beslut', 'beslutat', 'beslutit', 'bland', 'blev', 'bli', 'blir', 'blivit', 'borde', 'bort', 'borta', 'bra', 'bäst', 'bättre', 'båda', 'bådas', 'både',
        'dag', 'dagar', 'dagarna', 'dagen', 'de', 'del', 'delen', 'dem', 'den', 'denna', 'deras', 'dess', 'dessa', 'det', 'detta', 'dig', 'din', 'dina', 'dit', 'ditt',
        'dock', 'dom', 'du', 'där', 'därför', 'då', 'efter', 'eftersom', 'elfte', 'eller', 'elva', 'en', 'enkel', 'enkelt', 'enkla', 'enligt', 'er', 'era', 'ert', 'ett',
        'ettusen', 'fall', 'fanns', 'fast', 'fem', 'femte', 'femtio', 'femtionde', 'femton', 'femtonde', 'fick', 'fin', 'finnas', 'finns', 'fjorton', 'fjortonde', 'fjärde', 'fler', 'flera', 'flesta',
        'fram', 'framför', 'från', 'fyra', 'fyrtio', 'fyrtionde', 'få', 'får', 'fått', 'följande', 'för', 'före', 'förlåt', 'förra', 'första', 'ge', 'genast', 'genom', 'ger', 'gick',
        'gjorde', 'gjort', 'god', 'goda', 'godare', 'godast', 'gott', 'gälla', 'gäller', 'gällt', 'gärna', 'gå', 'gång', 'går', 'gått', 'gör', 'göra', 'ha', 'hade', 'haft',
        'han', 'hans', 'har', 'hela', 'heller', 'hellre', 'helst', 'helt', 'henne', 'hennes', 'heter', 'hit', 'hjälp', 'hon', 'honom', 'hundra', 'hundraen', 'hundraett', 'hur', 'här',
        'hög', 'höger', 'högre', 'högst', 'i', 'ibland', 'idag', 'igen', 'igår', 'imorgon', 'in', 'inför', 'inga', 'ingen', 'ingenting', 'inget', 'innan', 'inne', 'inom', 'inte',
        'inuti', 'ja', 'jag', 'jämfört', 'kan', 'kanske', 'knappast', 'kolla', 'kom', 'komma', 'kommer', 'kommit', 'kr', 'kunde', 'kunna', 'kunnat', 'kvar', 'kör', 'legat', 'ligga',
        'ligger', 'lika', 'likställd', 'likställda', 'lilla', 'lite', 'liten', 'litet', 'lägga', 'länge', 'längre', 'längst', 'lätt', 'lättare', 'lättast', 'långsam', 'långsammare', 'långsammast', 'långsamt', 'långt',
        'man', 'med', 'mellan', 'men', 'menar', 'mer', 'mera', 'mest', 'mig', 'min', 'mina', 'mindre', 'minst', 'mitt', 'mittemot', 'mot', 'mycket', 'många', 'måste', 'möjlig',
        'möjligen', 'möjligt', 'möjligtvis', 'ned', 'nederst', 'nedersta', 'nedre', 'nej', 'ner', 'ni', 'nio', 'nionde', 'nittio', 'nittionde', 'nitton', 'nittonde', 'nog', 'noll', 'nr', 'nu',
        'nummer', 'när', 'nästa', 'någon', 'någonting', 'något', 'några', 'nån', 'nåt', 'nödvändig', 'nödvändiga', 'nödvändigt', 'nödvändigtvis', 'och', 'också', 'ofta', 'oftast', 'olika', 'olikt', 'om',
        'oss', 'på', 'rakt', 'redan', 'rätt', 'sade', 'sagt', 'samma', 'samt', 'sedan', 'sen', 'senare', 'senast', 'sent', 'sex', 'sextio', 'sextionde', 'sexton', 'sextonde', 'sig',
        'sin', 'sina', 'sist', 'sista', 'siste', 'sitt', 'sju', 'sjunde', 'sjuttio', 'sjuttionde', 'sjutton', 'sjuttonde', 'själv', 'sjätte', 'ska', 'skall', 'skulle', 'slutligen', 'små', 'smått',
        'snart', 'som', 'stor', 'stora', 'stort', 'står', 'större', 'störst', 'säga', 'säger', 'sämre', 'sämst', 'sätt', 'så', 'ta', 'tack', 'tar', 'tidig', 'tidigare', 'tidigast',
        'tidigt', 'till', 'tills', 'tillsammans', 'tio', 'tionde', 'tjugo', 'tjugoen', 'tjugoett', 'tjugonde', 'tjugotre', 'tjugotvå', 'tjungo', 'tolfte', 'tolv', 'tre', 'tredje', 'trettio', 'trettionde', 'tretton',
        'trettonde', 'tro', 'tror', 'två', 'tvåhundra', 'under', 'upp', 'ur', 'ursäkt', 'ut', 'utan', 'utanför', 'ute', 'vad', 'var', 'vara', 'varför', 'varifrån', 'varit', 'varje',
        'varken', 'varsågod', 'vart', 'vem', 'vems', 'verkligen', 'vet', 'vi', 'vid', 'vidare', 'viktig', 'viktigare', 'viktigast', 'viktigt', 'vilka', 'vilken', 'vilket', 'vill', 'visst', 'väl',
        'vänster', 'vänstra', 'värre', 'vår', 'våra', 'vårt', 'än', 'ändå', 'ännu', 'är', 'även', 'åtminstone', 'åtta', 'åttio', 'åttionde', 'åttonde', 'över', 'övermorgon', 'överst', 'övre',
        'nya', 'procent', 'ser', 'skriver', 'tog', 'året'
    ]

STOP_WORDS = list(
            itertools.chain(SWEDISH_STOP_WORDS, ['kodsnack', 'ju'])
        )


##############################################################################
## Structs


class Episode:
    def __init__(self, url, date, title, num, titles, sort):
        self.url = url
        self.date = date
        self.title = title
        self.number = num
        self.sort = sort
        self.titles = titles


##############################################################################
## Functions

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


def get_episodes():
    episodes_soup = BeautifulSoup(request_url('https://kodsnack.se/avsnitt/', 'episodes'), 'html.parser')
    episodes_post_list = episodes_soup.find_all('span', class_='post-list')
    for episode_post in episodes_post_list:
        episode_date = episode_post.time.string
        episode_url = episode_post.a['href']
        episode_soup = BeautifulSoup(request_url(episode_url, extract_number_from_url(episode_url)), 'html.parser')

        # default properties
        episode_number = ''
        episode_title = ''
        episode_sort = ''
        download_file = ''
        episode_titles = []

        title_result = episode_soup.find('h1', class_='post-title')
        if title_result != None:
            episode_title = title_result.string.strip()
            episode_sort = episode_title
            episode_number_result = re.search('[Kk]odsnack ([0-9]+(\.[0-9]+)?)', episode_title)
            if episode_number_result != None:
                rest = episode_title[episode_number_result.end():].strip().lstrip('-').strip()
                episode_title = rest
                episode_number = episode_number_result.group(1)



        download_result = episode_soup.find('span', class_='post-download')
        if download_result != None:
            download_file = download_result.a['href']

        for titles_id in ['titlar', 'titles']:
            titles_result = episode_soup.find('h2', id=titles_id)
            if titles_result != None:
                ul = None
                for s in titles_result.next_siblings:
                    if s.name == 'ul':
                        ul = s
                        break
                if ul != None:
                    for li in ul.find_all('li'):
                        alt_title = li.string
                        if alt_title != None:
                            alt_title = alt_title.strip()
                            if alt_title != episode_title:
                                episode_titles.append(alt_title)
        
        yield Episode(download_file, episode_date, episode_title, episode_number, episode_titles, episode_sort)


def title_words_from_episodes(episodes):
    titles = itertools.chain.from_iterable(itertools.chain([e.title], e.titles) for e in episodes)
    title_words = itertools.chain.from_iterable(re.findall(r'\w+', title.lower()) for title in titles)
    return (w for w in title_words if not w.isdigit())


##############################################################################
## Commandline functions

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
            print('{} - {}'.format(episode.number, episode.title))


def handle_titles(args):
    for episode in get_episodes():
        print(episode.title)
        for t in episode.titles:
            print(t)
        print()


def handle_stats(args):
    episodes = list(get_episodes())
    shortest = min(episodes, key=lambda e: len(e.title))
    longest = max(episodes, key=lambda e: len(e.title))
    most_titles = max(episodes, key=lambda e: len(e.titles))
    fewest_titles = min((e for e in episodes if len(e.titles)>0), key=lambda e: len(e.titles))
    title_words = title_words_from_episodes(episodes)
    top10 = collections.Counter(w for w in title_words if w not in STOP_WORDS).most_common(10)

    print('Shortest: {}'.format(shortest.title))
    print('Longest: {}'.format(longest.title))
    print('Most titles: {} with {}'.format(most_titles.title, len(most_titles.titles)))
    print('Fewest titles: {} with {}'.format(fewest_titles.title, len(fewest_titles.titles)))
    print('Top 10 words in titles:')
    for t in top10:
        print('  {} with {}'.format(t[0], t[1]))
    print()


def handle_words(args):
    allwords = title_words_from_episodes(get_episodes())
    stopwords = STOP_WORDS if args.include_stopwords else []
    words = (w for w in allwords if not w in stopwords)
    wordlist = words if args.all else itertools.islice(words, 20)
    for w in wordlist:
        print(w)


##############################################################################
## Main

def main():
    parser = argparse.ArgumentParser(description='download and probe tool for kodsnack episodes')
    sub_parsers = parser.add_subparsers(dest='command_name', title='Commands', help='', metavar='<command>')

    sub = sub_parsers.add_parser('download', help='Download episode mp3s to your computer')
    sub.add_argument('--no-download', dest='download', action='store_false', help="don't download the episodes")
    sub.add_argument('--no-fix', dest='fix_id3', action='store_false', help="don't fix the id3 tags")
    sub.set_defaults(func=handle_download)

    sub = sub_parsers.add_parser('ls', help='List all episodes')
    sub.add_argument('--quiet', dest='print', action='store_false', help="don't print anything")
    sub.set_defaults(func=handle_ls)

    sub = sub_parsers.add_parser('titles', help='List all titles, including alternate titles')
    sub.set_defaults(func=handle_titles)

    sub = sub_parsers.add_parser('stats', help='Print some funny stats')
    sub.set_defaults(func=handle_stats)

    sub = sub_parsers.add_parser('words', help='Print all the words in titles, perfect for sending to a wordcloud generator')
    sub.add_argument('--stopwords', dest='include_stopwords', action='store_false', help='also include stopwords')
    sub.add_argument('--all', action='store_true', help='print all words')
    sub.set_defaults(func=handle_words)

    args = parser.parse_args()
    if args.command_name is not None:
        args.func(args)
    else:
        parser.print_help()


##############################################################################
## Entry point

if __name__ == '__main__':
    main()

