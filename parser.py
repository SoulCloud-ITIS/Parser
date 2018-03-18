# coding=utf-8
# -*- coding: utf-8 -*-
import socks
import socket
from bs4 import BeautifulSoup
from StringIO import StringIO
from zipfile import ZipFile
import re

import slate

TAG_RE = re.compile(r'<[^>]+>')


def remove_tags(text):
    res_txt = ''
    for text_str in text.contents:
        res_txt += TAG_RE.sub('', str(text_str.encode('utf-8')))
    return res_txt


def create_connection(address, timeout=None, source_address=None):
    sock = socks.socksocket()
    sock.connect(address)
    return sock


socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9150)

socket.socket = socks.socksocket
socket.create_connection = create_connection

import urllib2


def innerHTML(element):
    return element.decode_contents(formatter="html")


base_url = 'http://flibustahezeous3.onion'
book_format = '/fb2'
u = urllib2.urlopen(base_url + '/g')
html = u.read()

soup = BeautifulSoup(html, 'html.parser')

genres = list()
for ul in soup.find(id="main").find_all("ul"):
    for li in ul.find_all("li"):
        a = li.a.a
        genres.append({
            "link": a.attrs[u'href'],
            "name": innerHTML(a)
        })
input_genre = raw_input().decode('utf-8')
# input_genre = 'кино'.decode('utf-8')

found_genre = None

for genre in genres:
    if genre['name'].lower() == input_genre.lower():
        found_genre = genre
        break

if found_genre:
    u = urllib2.urlopen(base_url + found_genre["link"])
    html = u.read()
    soup = BeautifulSoup(html, 'html.parser')
    soup.find(id="main").ol.find_all('h5')
    for link_a in soup.find(id="main").ol.find_all('a'):
        link = link_a["href"]
        if link[1] == 'b':
            r = urllib2.urlopen(base_url + link + book_format)
            zip_file = ZipFile(input_genre + '.zip', "w")
            if r.headers['content-type'] == 'application/zip':
                print(base_url + link + book_format)
                zipfile = ZipFile(StringIO(r.read()))
                filename = zipfile.NameToInfo.keys()[0]
                filename_txt = filename[:-3] + 'txt'
                fb2_text = zipfile.open(filename).read()
                fb2_soup = BeautifulSoup(fb2_text, 'lxml')
                file_txt = ''
                for fb2_str in fb2_soup.find('body').find_all('p'):
                    file_txt += remove_tags(fb2_str) + '\n'
                zip_file.writestr(filename_txt, file_txt)
            else:
                file_name = r.headers['content-disposition'][22:-1]
                doc = slate.PDF(StringIO(r.read()))
                zip_file.writestr(file_name, doc.text())
            zip_file.close()
else:
    print "Genre doesn't exist"
