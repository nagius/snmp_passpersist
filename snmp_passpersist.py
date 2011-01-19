#!/usr/bin/python -u

# snmp_passpersist.py - SNMP passPersist bakend for Net-SNMP
# Copyleft 2010 - Nicolas AGIUS <nagius@astek.fr>

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

"""
This 'snmp_passpersist' module is a python backend for snmp's "pass_persist" function. 

It is critical that the python interpreter be invoked with unbuffered STDIN and 
STDOUT by use of the -u switch in the shebang line.

All the methods are in the PassPersist class.
"""

import sys, time, threading

__all__ = [ "encode", "start", "add_oid_entry", "add_int", "add_str", "add_cnt" ]

__author__ = "Nicolas Agius"
__license__ = "GPL"
__version__ = "1.0.1"
__email__ = "nagius@astek.fr"
__status__ = "Production"


class PassPersist:
	"""
	This class present a convenient way to creare a MIB subtree and expose it to snmp via it's passpersist protocol.
	Two thread are used, one for talking with snmpd and a second that trigger the update process at a fixed interval.

	The keyword 'DUMP' has been added to the protocol for testing purpose.

	Usage example: in a file /path/to/your/script.py :

	> #!/usr/bin/python -u
	> import snmp_passpersist as snmp
	>
	> def update():
	> 	pp.add_int('0.1',123)
	>
	> pp=snmp.PassPersist(".1.3.6.1.3.53.8")
	> pp.start(update,30) # Every 30s

	With the folowing line in snmpd.conf : 

	pass_persist    .1.3.6.1.3.53.8.0     /path/to/your/script.py

	"""

	@staticmethod	
	def encode(string):
		"""
		Encode the given string as an OID.

		>>> import snmp_passpersist as snmp
		>>> snmp.PassPersist.encode("hello")
		'5.104.101.108.108.111'
		>>> 
		"""

		result=".".join([ str(ord(s)) for s in string ])
		return  "%s." % (len(string)) + result

	def __init__(self, base_oid):
		"""
		Initialize internals structures.
		base_oid is the OID prefix used for all entry (the root of the MIB tree).
		"""

		self.data=dict()
		self.data_idx=list()
		if not base_oid.endswith("."):
			base_oid += "."
		self.base_oid=base_oid

		# The data structure is a dict that hold the unsorted MIB tree like this :
		# data = { 
		#	'1.1': { 'type':'INTEGER', 'value':4 },
		#	'1.3.2.1':{ 'type':'STRING', 'value':'vm1' }
		#	}

	def get(self,oid):
		"""Return snmp value for the given OID."""
		if oid not in self.data:
			return "NONE"
		else:
			return self.base_oid + oid + '\n' + self.data[oid]['type'] + '\n' +	str(self.data[oid]['value'])

	def get_next(self,oid):
		"""Return snmp value for the next OID."""
		try:
			return self.get(self.data_idx[self.data_idx.index(oid)+1])
		except ValueError:
			# Not found: try to match partial oid
			for real_oid in self.data_idx:
				if real_oid.startswith(oid):
					return self.get(real_oid)
			return "NONE" # Unknown OID
		except IndexError:
			return "NONE" # End of MIB

	def get_first(self):
		"""Return snmp value for the first OID."""
		try:
			return self.get(self.data_idx[0])
		except (IndexError, ValueError):
			return "NONE"

	def cut_oid(self,full_oid):
		"""
		Remove the base OID from the given string.

		>>> import snmp_passpersist as snmp
		>>> pp=snmp.PassPersist(".1.3.6.1.3.53.8")
		>>> pp.cut_oid(".1.3.6.1.3.53.8.28.12")
		'28.12'
		"""
		if not full_oid.startswith(self.base_oid.rstrip('.')):
			return None 
		else:
			return full_oid[len(self.base_oid):]

	def add_oid_entry(self, oid, type, value):
		"""General function to add an oid entry to the MIB subtree."""
		self.data[oid]={'type': str(type), 'value': str(value)}

	def add_int(self,oid,value):
		"""Short helper to add an integer value to the MIB subtree."""
		self.add_oid_entry(oid,'INTEGER',value)

	def add_str(self,oid,value):
		"""Short helper to add a string value to the MIB subtree."""
		self.add_oid_entry(oid,'STRING',value)

	def add_cnt(self,oid,value):
		"""Short helper to add a counter value to the MIB subtree."""
		self.add_oid_entry(oid,'Counter32',value)

	def add_gau(self,oid,value):
		"""Short helper to add a gauge value to the MIB subtree."""
		self.add_oid_entry(oid,'GAUGE',value)

	def main_passpersist(self):
		"""
		Main function that handle SNMP's pass_persist protocol, called by 
		the start method.
		Direct call is unnecessary.
		"""
		line = sys.stdin.readline().strip()

		if 'PING' in line:
			print "PONG"
		elif 'getnext' in line:
			oid = self.cut_oid(sys.stdin.readline().strip())
			if oid is None:
				print "NONE"
			elif oid == "":
				# Fallback to the first entry
				print self.get_first()
			else:
				print self.get_next(oid)
		elif 'get' in line:
			oid = self.cut_oid(sys.stdin.readline().strip())
			if oid is None:
				print "NONE"
			else:
				print self.get(oid)
		elif 'set' in line:
			oid = sys.stdin.readline()
			typevalue = sys.stdin.readline()
			print "not-writable"
		elif 'DUMP' in line: # Just for debbuging
			from pprint import pprint
			pprint(self.data)
		else:
			print "NONE"

	def main_update(self):
		"""
		Main function called by the updater thread.
		Direct call is unnecessary.
		"""

		try:
			while True:
				time.sleep(self.refresh)

				# Update data with user's defined function
				self.update()

				# Generate index 
				self.data_idx = sorted(self.data.keys())

		except Exception,e:
			self.error=e
			raise

	def start(self, user_func, refresh):
		"""
		Start the SNMP's protocol handler and the updater thread
		user_func is a reference to an update function, ran every 'refresh' seconds.
		"""
		self.update=user_func
		self.refresh=refresh
		self.error=None

		# First load
		self.update()
		self.data_idx = sorted(self.data.keys())

		# Start updater thread
		up = threading.Thread(None,self.main_update,"Updater")
		up.start()

		# Main loop
		while up.isAlive(): # Do not serve data if the Updater thread has died
			try:
				self.main_passpersist()
			except:
				up._Thread__stop()
				raise

# vim: ts=4:sw=4:ai
