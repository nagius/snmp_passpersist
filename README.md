# SNMP-PassPersist

This module is a SNMP passpersist backend for Net-SNMP.

The snmp_passpersist.PassPersist class present a convenient way to creare a MIB subtree and expose it to snmp via it's passpersist protocol.
Two threads are used, one for talking with snmpd and a second that trigger the update process at a fixed interval.

The keyword 'DUMP' has been added to the protocol for testing purpose.


## Installation

The easiest way is using pip : 
```
pip install snmp_passpersist
```

If you're running Python 2.x and see this error : 
```
Traceback (most recent call last):
  File "test.py", line 3, in <module>
    import snmp_passpersist as snmp
  File "/root/snmp_passpersist/snmp_passpersist.py", line 32, in <module>
    from builtins import str
ImportError: No module named builtins
```

Install the `future` package to fix the issue: `pip install future`

## Example

Usage example: in a file /path/to/your/script.py :

```python
!/usr/bin/python -u

import snmp_passpersist as snmp

def update():
        pp.add_int('0.1', 123, "This is a label for this integer")
        pp.add_str('0.2', "A string")
        pp.add_oct('0.3', '01 00 1f 0b 00 0b') # MAC address as an octet string

pp=snmp.PassPersist(".1.3.6.1.3.53.8")
pp.start(update,30) # Every 30s
```

With the folowing line in snmpd.conf :

```
pass_persist    .1.3.6.1.3.53.8.0     /path/to/your/script.py
```

A Real-world example is available here: https://github.com/nagius/cxm/blob/master/misc/snmp_xen.py

## List of supported types and their helpers

| Type | Helper |
|------|--------|
|Counter32	|add_cnt_32bit
|Counter64	|add_cnt_64bit
|GAUGE		|add_gau
|INTEGER	|add_int
|IPADDRESS	|add_ip
|OBJECTID	|add_oid
|OCTET		|add_oct
|STRING		|add_str
|TIMETICKS	|add_tt


## Special helpers

### Labels

You can add a label with each entries, as an optional parameter to all add_*() helpers. 
This label is not used by Net-SNMP and is only useful for debugging with the DUMP keyword.


### add_oid()

This helper allow you to add a simple OID string and give it the proper type.  For example, calling this method with

```
pp.add_oid('.1.3.6.1.2.1.47','1.1.1.1.3.1','0.0')
```

where "0.0" represents `SNMPv2-SMI::zeroDotZero`.

This results in the following response when we walk this OID:

`ENTITY-MIB::entPhysicalVendorType.1 = OID: SNMPv2-SMI::zeroDotZero`

### Set an attribute

You can register a helper to allow the recording of value from Net-SNMP.

```
def my_setter(oid, type, value):
        print("Received %s with value %s for oid %s." % (type, value, oid))
        return True

pp.register_setter('.1.3.6.1.3.53.8.0.4', my_setter)
```

Example for debugging : 
```
$ /path/to/your/script.py
set
.1.3.6.1.3.53.8.0.4
INTEGER 987
Received INTEGER with value 987 for oid .1.3.6.1.3.53.8.0.4.
DONE
set
.1.3.6.1.3.53.8.0.1
STRING some-random-useless-string
not-writable
```

Another example that show the usage of the 'set' feature is available in the 'example/' directory.

## Debugging example

Run the previous script in a shell and type the commands :  

$ /path/to/your/script.py
PING
PONG
DUMP
{'0.1': {'type': 'INTEGER', 'value': '123'}}
get
.1.3.6.1.3.53.8
NONE
get
.1.3.6.1.3.53.8.0.1
.1.3.6.1.3.53.8.0.1
INTEGER
123
getnext
.1.3.6.1.3.53.8
.1.3.6.1.3.53.8.0.1
INTEGER
123

All commands are typed on two lines : get<ENTER>.1.3.6.1.3.53.8.0.1<ENTER>, except PING and DUMP.

## Credits

Many thanks to all contributors.


