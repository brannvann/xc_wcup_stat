
#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from urllib.request import Request, urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup


class xcwcup_parser():
    wiki_url = "https://en.wikipedia.org"
    start_page = "https://en.wikipedia.org/wiki/FIS_Cross-Country_World_Cup"
    safe_headers = {
	'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0'
    }

    def __init__(self):
        pass

    def get_data(self):
        req = Request(url = self.start_page, data=None, headers=self.safe_headers )
        html = None
        try:
            html = urlopen(req)
        except HTTPError as err:
            print(f"cannot read {self.start_page}, error={str(err.code)}")
        if html:
            bs = BeautifulSoup(html, 'html.parser')
            tbls = bs.find_all('table')
            for tbl in tbls:
                h3title = tbl.find_all('h3')
                if h3title and h3title[0].getText() == 'Men[edit]':
                    links_tbl = tbl.find_all('table')[0]
                    rows = links_tbl.tbody.find_all('tr')
                    skip_rows = True
                    wc_urls = []
                    for row in rows:
                        if skip_rows:
                            row_text = row.getText()
                            if 'Official' in row_text:
                                skip_rows = False
                        else:
                            td = row.find_all('td')[0]
                            link = td.find('a')
                            url = f"{self.wiki_url}{link.get('href')}"
                            wc_urls.append(url)
                        pass
                    for url in wc_urls:
                        self.get_year_data(url)
                    break
                pass
            pass
        return True

    def get_year_data(self, url):
        print(url)
        pass


def main(args):
    m = xcwcup_parser()
    m.get_data()

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
