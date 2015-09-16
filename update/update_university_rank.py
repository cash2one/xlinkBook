#!/usr/bin/env python

from spider import *
import time

class UniversityRankSpider(Spider):

    def __init__(self):
        Spider.__init__(self)
        self.subject = 'rank'

    def processQSData(self):
        self.school = 'QS'
        base_url = 'http://www.topuniversities.com'
        r = requests.get(base_url + '/subject-rankings')
        soup = BeautifulSoup(r.text)
        for div in soup.find_all('div', class_='link'):
            sp = BeautifulSoup(div.prettify())
            for li in sp.find_all('li'):
                print li.text.strip() + " " + li.a['href']
                url = li.a['href']
                if url.startswith('http') == False:
                    url = base_url + url
                r = requests.get(url)
                if r.text.find('flat_file') != -1:
                    sub = li.a['href'].strip()
                    while sub.find('/') != -1:
                        sub = sub[sub.find('/') + 1 :]

                    file_name = self.get_file_name(self.subject + '/' + self.school + '/' + sub, self.school)
                    file_lines = self.countFileLineNum(file_name)
                    f = self.open_db(file_name + ".tmp")
                    self.count = 0

                    pos = r.text.find('flat_file')
                    data_url = r.text[r.text.find('http', pos) : r.text.find('",', pos)].replace('\\', '')
                    sub = data_url
                    while sub.find('/') != -1:
                        sub = sub[sub.find('/') + 1 :]
                    sub = sub[0 : sub.find('.txt')]
                    r = requests.get(data_url)
                    jobj = json.loads(r.text)
                    for obj in jobj:
                        print obj['rank'] + ' ' + obj['title']
                        self.count += 1
                        self.write_db(f, self.school.lower() + '-' + sub + '-' + obj['rank'], obj['title'], '')

                    self.close_db(f)
                    if file_lines != self.count and self.count > 0:
                        self.do_upgrade_db(file_name)
                        print "before lines: " + str(file_lines) + " after update: " + str(self.count) + " \n\n"
                    else:
                        self.cancel_upgrade(file_name)
                        print "no need upgrade\n"

    def processTimesHigherEducationData(self):
        self.school = 'TimesHigherEducation'
        r = requests.get('https://www.timeshighereducation.co.uk/world-university-rankings/')
        soup = BeautifulSoup(r.text)
        for li in soup.find_all('li'):
            if li.h3 != None:
                subject = li.h3.a.text.lower().strip().replace(' ', '-')
                r = requests.get(li.a['href'])
                sp = BeautifulSoup(r.text)

                file_name = self.get_file_name(self.subject + '/' + self.school + '/' + subject, self.school)
                file_lines = self.countFileLineNum(file_name)
                f = self.open_db(file_name + ".tmp")
                self.count = 0

                for a in sp.find_all('a', class_='wur-table-link'):
                    if a.span != None and a.div != None:
                        print a.span.text
                        self.count += 1
                        self.write_db(f, 'the-' + subject + str(self.count), a.span.text, 'https://www.timeshighereducation.co.uk' + a['href'])

                self.close_db(f)
                if file_lines != self.count and self.count > 0:
                    self.do_upgrade_db(file_name)
                    print "before lines: " + str(file_lines) + " after update: " + str(self.count) + " \n\n"
                else:
                    self.cancel_upgrade(file_name)
                    print "no need upgrade\n"



    def processARWUData(self):
        self.school = 'arwu'
        r = requests.get('http://www.shanghairanking.com/index.html')
        soup = BeautifulSoup(r.text)
        sub = {}
        sublist = []
        for div in soup.find_all('div', class_='sublist'):
            sp = BeautifulSoup(div.prettify())
            data = []
            for li in sp.find_all('li'):
                data.append(li.text)
            sublist.append(data)

        count = 0
        for ul in soup.find_all('ul', class_='tabbtn'):
            for line in ul.text.strip().split('\n'):
                sub[line.strip()] = sublist[count]
                count += 1
            
        for s in sub.keys():
            print s
            file_name = self.get_file_name(self.subject + '/' + self.school + '/' + s, self.school)
            file_lines = self.countFileLineNum(file_name)
            f = self.open_db(file_name + ".tmp")
            self.count = 0

            for item in sub[s]:
                title = item.strip().replace('\n', '')
                title = title[title.find(' ') :].strip()
                self.count += 1
                print title
                self.write_db(f, self.school + '-' + s + '-' + str(self.count), title, '')

            self.close_db(f)
            if self.count > 0:
                self.do_upgrade_db(file_name)
                print "before lines: " + str(file_lines) + " after update: " + str(self.count) + " \n\n"
            else:
                self.cancel_upgrade(file_name)
                print "no need upgrade\n"

    def processUsnewsData(self):
        self.school = 'usnews'
        sub_list = ['biology-biochemistry', 'computer-science', 'economics-business', 'engineering', 'mathematics', 'neuroscience-behavior',\
                    'physics', 'psychiatry-psychology']
        for sub in sub_list:
            r = requests.get('http://www.usnews.com/education/best-global-universities/search?region=&subject=' + sub + '&name=')
            soup = BeautifulSoup(r.text)
            file_name = self.get_file_name(self.subject + '/' + self.school + '/' + sub, self.school)
            file_lines = self.countFileLineNum(file_name)
            f = self.open_db(file_name + ".tmp")
            self.count = 0
            print 'processing ' + sub
            for h2 in soup.find_all('h2', class_='h-taut'):
               print h2.a.text
               self.count += 1
               self.write_db(f, self.school + '-' + sub + '-' + str(self.count), h2.a.text, h2.a['href'])

            self.close_db(f)
            if self.count > 0:
                self.do_upgrade_db(file_name)
                print "before lines: " + str(file_lines) + " after update: " + str(self.count) + " \n\n"
            else:
                self.cancel_upgrade(file_name)
                print "no need upgrade\n"

    def doWork(self):
        self.processQSData()
        self.processTimesHigherEducationData()
        self.processARWUData()
        self.processUsnewsData()


start = UniversityRankSpider()
start.doWork()
