# -*- coding:utf-8 -*-

'''@package settings.py

Recover settings from a standard ini/conf file
Author: Robert Oliveira <olivecoder@gmail.com>
'''
from future import standard_library
standard_library.install_aliases()
from builtins import object

###########################################################################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###########################################################################

import configparser
import tempfile
import os
import shutil


class Settings(object):
    '''Base class to read and write ini files

    define FNAME in child class
    '''

    FNAME = None

    def __init__(self):
        self.changed = False
        self.file_name = self.FNAME
        self.mtime = 0
        self.config = None
        self.read()

    def read(self):
        self.config = configparser.ConfigParser()
        self.config.read(self.file_name)

    def updateFromFile(self):
        current_mtime = os.path.getmtime(self.file_name)
        if current_mtime > self.mtime:
            self.read()
            self.mtime = current_mtime
            return True
        else:
            return False

    def set(self, section, option, value):
        self.changed = True
        self.config.set(section, option, value)

    def get(self, section, option):
        return self.config.get(section, option)

    def items(self, section):
        return self.config.items(section)

    def sections(self):
        return self.config.sections()

    def write(self):
        '''atomic writing'''
        tmp_file, tmp_fname = tempfile.mkstemp()
        os.close(tmp_file)
        shutil.copystat(self.file_name, tmp_fname)
        self.config.write(open(tmp_fname, 'w'))
        shutil.move(tmp_fname, self.file_name)

    def __enter__(self):
        return this

    def __exit__(self, *args):
        if self.changed:
            self.save()
