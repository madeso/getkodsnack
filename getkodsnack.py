import urllib2
import re
import os
import os.path

def sanefilename(filename):
	for c in r'[]/\;,><&*:%=+@!#^()|?^':
		filename = filename.replace(c,'')
	return filename

def dlfile(url, localfilename):
    # Open the url
	try:
		print "DL " + url + " to " + localfilename
		
		if os.path.isfile(localfilename) == False:
			f = urllib2.urlopen(url)
			with open(localfilename, "wb") as local_file:
				local_file.write(f.read())
	#handle errors
	except urllib2.HTTPError, e:
		print "HTTP Error:", e.code, url
	except urllib2.URLError, e:
		print "URL Error:", e.reason, url


def main():
	avsnitts = urllib2.urlopen('http://kodsnack.se/avsnitt/').read()
	for mo in re.findall('<li><span class="post-list"><time>(.*)</time> <a href="(.*)">', avsnitts):
		req = urllib2.urlopen(mo[1])
		encoding=req.headers['content-type'].split('charset=')[-1]
		content = req.read()
		ucontent = unicode(content, encoding)
		webFile = content
		try:
			webFile = ucontent.encode('CP1252')
		except UnicodeEncodeError, e:
			# for some reason encoding as 1252 fails on some pages, but not others, ignoring that error seems to work
			pass
			
		dodownload = True

		#  <h1 class="post-title">Kodsnack 74 - Resten av livet med dina handleder</h1>
		title = re.search('<h1 class="post-title">(.*)</h1>', webFile)
		if title == None:
			print "Missing title for ", index
			dodownload = False
		#print(title.group(1))

		# <span class="post-download"><a href="http://traffic.libsyn.com/kodsnack/24_oktober.mp3">Ladda ner (mp3)</a></span>
		download = re.search('<span class="post-download"><a href="(.*)">', webFile)
		if download == None:
			print "Missing download for ", title.group(1)
			dodownload = False
		#print(download.group(1))
		
		if dodownload:
			# we should change to the same extension that the source has, someday...
			dlfile(download.group(1), sanefilename(title.group(1))+ ".mp3")

if __name__ == '__main__':
	main()