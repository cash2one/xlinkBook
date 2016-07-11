#!/usr/bin/env python

import sys, os
from extensions.bas_extension import BaseExtension
from utils import Utils
from record import Record
from config import Config

class Delete(BaseExtension):


    def __init__(self):
        BaseExtension.__init__(self)


    def excute(self, form_dict):
        rID = form_dict['rID'].encode('utf8')
        user_name = form_dict['user_name'].encode('utf8')
        library = 'db/library/' + user_name + '-library'
        print library
        if os.path.exists(library):
            f = open(library, 'rU')
            all_lines = []
            for line in f.readlines():
                if rID != line[0 : line.find('|')].strip():
                    all_lines.append(line)
            f.close()
            f = open(library, 'w')
            if len(all_lines) > 0:
                for line in all_lines:
                    f.write(line)
            else:
                f.write('')
                f.close()
            return 'http://' + Config.ip_adress + '/?db=library/&key=' + user_name + '-library'
        return 'error'

    def check(self, form_dict):
        user_name = form_dict['user_name']
        return user_name != '' and form_dict.has_key('delete') and form_dict['delete'] and form_dict['rID'].startswith('loop') == False

    def needCache(self):
        return False
