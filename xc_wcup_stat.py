
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from urllib.request import Request, urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import json
import matplotlib.pyplot as plt

class xcwcup_parser():
    wiki_url = "https://en.wikipedia.org"
    start_page = "https://en.wikipedia.org/wiki/FIS_Cross-Country_World_Cup"
    safe_headers = {
	'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0'
    }
    km_data = {}
    race_data = {}

    def __init__(self):
        pass

    def process_data(self):
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
                        self.process_year_data(url)
                    break
                pass
            pass
        else:
            print(f"cannot read main page {self.start_page}")
        return True

    def process_year_data(self, url):
        print(url)
        req = Request(url = url, data=None, headers=self.safe_headers )
        html = None
        try:
            html = urlopen(req)
        except HTTPError as err:
            print(f"cannot read {url}, error={str(err.code)}")
        if not html:
            print(f"data for {url} is empty")
            return False
        bs = BeautifulSoup(html, 'html.parser')
        h1title = bs.find_all('h1')[0]
        year = h1title.getText().split('–')[0]
        list_tbl = bs.find_all('table')
        if (not list_tbl) or ( len(list_tbl)  < 2) :
            print(f"cannot read table for year {year}")
            return False
        scedule = list_tbl[1]
        rows = scedule.find_all('tr')
        wc_events = {}
        race_types = {}
        for row in rows[1:]:
            cells = row.find_all('td')
            for cell in cells:
                text = cell.get_text().replace(u'\xa0', u' ').strip()
                event_type = None
                race_type = 'Individual'
                if ('Sprint' in text ) or (' km' in text):
                    # тип гонки (спринт, преследование, скиатлон, масстарт или разделка по умолчанию)
                    races = ['Sprint', 'Pursuit', 'Skiathlon', 'Mass Start']
                    for race in races:
                        if race.lower() in text.lower():
                            race_type = race
                    if race_type not in race_types.keys():
                        race_types[race_type] = 1
                    else:
                        race_types[race_type] = race_types[race_type] + 1
                    # длина гонки
                    if ('Sprint' in text ):
                        event_type = 'Sprint'
                    elif ('Relay' in text):
                        event_type = 'Relay'
                    else:    
                        event_type = text.split(' ')[0]
                    if event_type:
                        if event_type not in wc_events.keys():
                            wc_events[event_type] = 1
                        else:     
                            wc_events[event_type] = wc_events[event_type] + 1
                        break
                    pass
                pass
            pass
        self.km_data[year] = wc_events 
        self.race_data[year] = race_types
        return True

    def save_km_data(self, filename):
        with open(filename, "w") as ofs:
            json.dump(self.km_data, ofs)
        pass

    def read_km_data(self, filename):
        try:
            with open(filename, "r") as ifs:
                self.km_data = json.load(ifs)
        except:
            print(f"cannot read data from {filename}")
        pass   

    def save_ev_data(self, filename):
        with open(filename, "w") as ofs:
            json.dump(self.race_data, ofs)
        pass

    def read_ev_data(self, filename):
        try:
            with open(filename, "r") as ifs:
                self.race_data = json.load(ifs)
        except:
            print(f"cannot read data from {filename}")
        pass   

    def show_km_plot(self):
        labels = []
        short_races, mid_races, long_races, marathons = [], [], [], []
        for year, data in self.km_data.items():
            labels.append(year)
            short_r, mid_r, long_r, marathon = 0, 0, 0, 0
            for race, count in data.items():
                if "Sprint" in race:
                    short_r = short_r + count
                else:
                    km = 0
                    try:
                        km = float(race)
                    except:
                        pass
                    if not km:
                        continue
                    if km <= 5:
                        short_r = short_r + count
                    elif km <= 15:
                        mid_r = mid_r + count
                    elif km <= 39:
                        long_r = long_r + count
                    else:
                        marathon = marathon + count
                pass
            short_races.append(short_r)
            mid_races.append(mid_r)
            long_races.append(long_r)
            marathons.append(marathon)
        print(labels)
        fig, ax = plt.subplots()
        ax.bar(labels, marathons, label='Марафоны', color='Navy', width=1.0, edgecolor='Black')
        ax.bar(labels, long_races, label='20-35 км', bottom=marathons, color='Green', width=1.0, edgecolor='Black')
        ax.bar(labels, mid_races, label='10-15 км', bottom=[ i + j for i, j in zip(marathons, long_races)], color='Orange', width=1.0, edgecolor='Black')
        ax.bar(labels, short_races, label='Спринт и короткие гонки', bottom= [ i + j + k for i, j, k in zip(marathons, long_races, mid_races) ], color='Red', width=1.0, edgecolor='Black')
        ax.set_ylabel('Количество этапов', fontsize=16)
        ax.set_title('Формат Кубка Мира по лыжным гонкам (муж)', fontsize=16)
        ax.legend(fontsize=16)
        xpos = range(len(labels))
        plt.xticks(xpos, labels, rotation=60)
        plt.show()


    def show_event_plot(self):
        labels = []
        individual, massstart, skiathlon, pursuit, sprint = [], [], [], [], []
        for year, data in self.race_data.items():
            labels.append(year)
            ind_r, mass_r, skitln_r, purs_r, sprint_r = 0, 0, 0, 0, 0
            for race, count in data.items():
                if "Individual" in race:
                    ind_r = ind_r + count
                elif "Mass Start" in race:
                    mass_r = mass_r + count
                elif "Pursuit" in race:
                    purs_r = purs_r + count
                elif "Skiathlon" in race:
                    skitln_r = skitln_r + count
                elif "Sprint" in race:
                    sprint_r = sprint_r + count
                else:
                    print(f"Unknown race {race}")
            individual.append(ind_r) 
            massstart.append(mass_r)
            skiathlon.append(skitln_r) 
            pursuit.append(purs_r) 
            sprint.append(sprint_r)
        pass
        print(labels)
        fig, ax = plt.subplots()
        ax.bar(labels, individual, label='Индивидуальная гонка', color='Navy', width=1.0, edgecolor='Black')
        ax.bar(labels, pursuit, label='Преследование', bottom=individual, color='Green', width=1.0, edgecolor='Black')
        ax.bar(labels, skiathlon, label='Скиатлон', bottom=[ i + j for i, j in zip(individual, pursuit)], color='Blue', width=1.0, edgecolor='Black')
        ax.bar(labels, massstart, label='Масс-старт', bottom= [ i + j + k for i, j, k in zip(individual, pursuit, skiathlon) ], color='Cyan', width=1.0, edgecolor='Black')
        ax.bar(labels, sprint, label='Спринт', bottom= [ i + j + k + t for i, j, k, t in zip(individual, pursuit, skiathlon, massstart) ], color='Red', width=1.0, edgecolor='Black')
        ax.set_ylabel('Количество этапов', fontsize=16)
        ax.set_title('Формат Кубка Мира по лыжным гонкам (муж)', fontsize=16)
        ax.legend(fontsize=16)
        xpos = range(len(labels))
        plt.xticks(xpos, labels, rotation=60)
        plt.show()

def main(args):
    m = xcwcup_parser()
    km_filename = "xc_cup_men_km.json"
    ev_filename = "xc_cup_men_ev.json"
    m.read_km_data(km_filename)
    m.read_ev_data(ev_filename)
    if not m.km_data or not m.race_data:
        m.process_data()
        m.save_km_data(km_filename)
        m.save_ev_data(ev_filename)
    m.show_km_plot()   
    m.show_event_plot()
    pass 
    
if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
