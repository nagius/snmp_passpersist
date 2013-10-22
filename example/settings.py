'''
settings.py
Recover settings from a standard ini file
'''

import ConfigParser
import tempfile
import os
import shutil


class Settings():
    FNAME = None

    def __init__(self):
        self.changed = False
        self.file_name = self.FNAME
        self.mtime = 0
        self.config = None
        self.read()

    def read(self):
        self.config = ConfigParser.ConfigParser()
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
