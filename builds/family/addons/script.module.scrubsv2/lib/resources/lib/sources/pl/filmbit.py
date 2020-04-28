# -*- coding: utf-8 -*-
'''
    Covenant Add-on
    Copyright (C) 2018 :)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import requests

try:
    import urlparse
except:
    import urllib.parse as urlparse
try:
    import HTMLParser
    from HTMLParser import HTMLParser
except:
    from html.parser import HTMLParser
try:
    import urllib2
except:
    import urllib.request as urllib2

from resources.lib.modules import source_utils
from resources.lib.modules import cleantitle
from resources.lib.modules import client


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['pl']
        self.domains = ['filmbit.ws']

        self.base_link = 'https://filmbit.ws'
        self.search_link = 'https://filmbit.ws/wyszukiwarka?phrase='
        self.session = requests.Session()

    def contains_word(self, str_to_check, word):
        if str(word).lower() in str(str_to_check).lower():
            return True
        return False

    def contains_all_words(self, str_to_check, words):
        for word in words:
            if not self.contains_word(str_to_check, word):
                return False
        return True

    def search(self, title, localtitle, year, is_movie_search):
        try:

            titles = []
            titles.append(cleantitle.normalize(cleantitle.getsearch(title)))
            titles.append(cleantitle.normalize(cleantitle.getsearch(localtitle)))

            for title in titles:
                url = self.search_link + str(title)
                result = client.request(url)
                result = result.decode('utf-8')
                h = HTMLParser()
                result = h.unescape(result)
                result = client.parseDOM(result, 'div', attrs={'class': 'row'})

                for item in result:
                    try:
                        link = str(client.parseDOM(item, 'a', ret='href')[0])
                        if link.startswith('//'):
                            link = "https:" + link
                        nazwa = str(client.parseDOM(item, 'img', ret='alt')[0])
                        name = cleantitle.normalize(cleantitle.getsearch(nazwa))
                        rok = link
                        name = name.replace("  ", " ")
                        title = title.replace("  ", " ")
                        words = title.split(" ")
                        if self.contains_all_words(name, words) and str(year) in rok:
                            return link
                    except:
                        continue
        except:
            return

    def movie(self, imdb, title, localtitle, aliases, year):
        return self.search(title, localtitle, year, True)

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        if localtvshowtitle == "Vikings":
            localtvshowtitle = "Wikingowie"
        titles = (tvshowtitle, localtvshowtitle)
        return titles, year

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        return self.search_ep(url[0], season, episode, url[1])  # url = titles & year

    def search_ep(self, titles, season, episode, year):
        query = 'S{:02d}E{:02d}'.format(int(season), int(episode))
        try:
            titles_tv = []
            titles_tv.append(cleantitle.normalize(cleantitle.getsearch(titles[0])))
            titles_tv.append(cleantitle.normalize(cleantitle.getsearch(titles[1])))

            for title in titles_tv:
                url = self.search_link + str(title)
                result = client.request(url)
                result = result.decode('utf-8')
                h = HTMLParser()
                result = h.unescape(result)
                result = client.parseDOM(result, 'div', attrs={'class': 'row'})
                result = client.parseDOM(result[5], 'div', attrs={'class': 'col-sm-4'})
                for item in result:
                    try:
                        link = str(client.parseDOM(item, 'a', ret='href')[0])
                        if link.startswith('//'):
                            link = "https:" + link
                        nazwa = str(client.parseDOM(item, 'img', ret='alt')[0])
                        name = cleantitle.normalize(cleantitle.getsearch(nazwa))
                        name = name.replace("  ", " ")
                        title = title.replace("  ", " ")
                        words = title.split(" ")
                        if self.contains_all_words(name, words):
                            result = client.request(link)
                            result = client.parseDOM(result, 'ul', attrs={'id': "episode-list"})
                            result = client.parseDOM(result, 'li')
                            for episode in result:
                                nazwa = client.parseDOM(episode, 'a')[0]
                                link = str(client.parseDOM(episode, 'a', ret='href')[0])
                                if query.lower() in nazwa.lower():
                                    return link

                    except:
                        continue
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            import base64
            import json

            result = client.request(url)
            result = result.decode('utf-8')
            h = HTMLParser()
            result = h.unescape(result)
            tabela = client.parseDOM(result, 'div', attrs={'class': "link-to-video"})
            # items = client.parseDOM(tabela, 'tr')
            for item in tabela:
                try:
                    jezyk = client.parseDOM(item, 'span')[0].replace('<b>', '').replace("</b>", '')
                    jezyk, wersja = self.get_lang_by_type(jezyk)
                    # quality = client.parseDOM(item, 'td')[2]
                    link = json.loads(client.parseDOM(result, 'a', ret='data-iframe')[0].decode('base64'))['src']
                    valid, host = source_utils.is_host_valid(link, hostDict)
                    sources.append(
                        {'source': host, 'quality': 'SD', 'language': jezyk, 'url': link, 'info': wersja,
                         'direct': False,
                         'debridonly': False})
                except:
                    pass
            return sources
        except:
            return sources

    def get_lang_by_type(self, lang_type):
        if "dubbing" in lang_type.lower():
            if "kino" in lang_type.lower():
                return 'pl', 'Dubbing Kino'
            return 'pl', 'Dubbing'
        elif 'lektor pl' in lang_type.lower():
            return 'pl', 'Lektor'
        elif 'lektor' in lang_type.lower():
            return 'pl', 'Lektor'
        elif 'napisy pl' in lang_type.lower():
            return 'pl', 'Napisy'
        elif 'napisy' in lang_type.lower():
            return 'pl', 'Napisy'
        elif 'POLSKI' in lang_type.lower():
            return 'pl', None
        elif 'pl' in lang_type.lower():
            return 'pl', None
        return 'en', None

    def resolve(self, url):
        link = str(url).replace("//", "/").replace(":/", "://").split("?")[0]
        return str(link)
