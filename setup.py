#!/usr/bin/env python

import os
from setuptools import setup

# Utility function to read the README file.
def read(fname):
	return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
	name='snmp_passpersist',
	version='1.2.3',
	license='GPLv3',
	description="""SNMP passpersist backend for Net-SNMP""",
	long_description=read('README'),
	keywords="snmp net-snmp",
	author='Nicolas Agius',
	author_email='nicolas.agius@lps-it.fr',
	url='http://github.com/nagius/snmp_passpersist',
	py_modules=['snmp_passpersist'],
	classifiers=[
		'Intended Audience :: Developers',
		'License :: OSI Approved :: GNU General Public License (GPL)',
		'Development Status :: 5 - Production/Stable',
		'Operating System :: POSIX :: Linux',
		'Topic :: System :: Monitoring',
	],
)

# vim: ts=4:sw=4:ai
