#!/usr/bin/python
# -*- encoding: utf-8 -*-

import xml.dom.minidom
import sys
import os

def printagsData (dom, prepr, tags, strict):
	_s = {}
	for p in dom.childNodes:
		if not 'tagName' in dir (p):
			continue
		if p.tagName in tags and not p.tagName in _s:
			for q in p.childNodes:
				if not 'data' in dir (q):
					continue
				else:
					if not p.tagName in _s:
						_s[p.tagName] = ""
					try:
						_s[p.tagName] += q.data
					except: pass
	line = ""
	for q in tags:
		if q in _s:
			line += '|' + _s[q]
		else:
			line += '|'
			if strict:
				if q in strict:
					return
	sys.stdout.write (prepr + line + '\n')

def printlshw (xmlfd):
	x = xml.dom.minidom.parse (xmlfd)
	for xx in x.getElementsByTagName ('node'):
		handlen = xx.getAttribute ('handle')
		if not handlen:
			continue
		idn = xx.getAttribute ('id').split (':', 1)[0]
		match = { # список: { 'узел': (['замена на тег', 'столбец1', 'столбец2', 'столбецn'], ['обязательный столбец1', 'обязательный столбец2']) }
				'core': (['board', 'vendor', 'product', 'serial'], []),
				'cpu': ([None, 'product', 'serial', 'slot'], ['slot']),
				'disk': ([None, 'product', 'serial', 'size'], ['product', 'serial']),
				'bank': (['mem', 'description', 'size'], ['size']),
				'network': (['net', 'product', 'serial'], ['serial']),
				}
		# ***
		if not idn in match.keys ():
			continue
		printagsData (xx, match[idn][0][0] or idn, tuple (match[idn][0][1:]), tuple (match[idn][1]))

if __name__ == '__main__':
	try:
		if os.path.exists ('/etc/vlintid'):
			sys.stdout.write ('id|' + open ('/etc/vlintid').read ().split ('\n')[0].strip ()[1:40] + '\n')
	except: pass
	# hw
	fd = os.popen ('lshw -xml 2>/dev/null | grep -v lastmountpoint')
	printlshw (fd)
	del fd
	# host
	uname = os.uname ()
	sys.stdout.write ('host|' + uname[1] + '|' + uname[0] + ' ' + uname[2] + '|' + uname[4] + '\n')
	# display
	fd = os.popen ("ddccontrol -pfc 2>/dev/null | sed -e 's/.*Plug and Play ID: \\([^\[]*\\).*\\|.*/\\1/' -e '/^$/d'")
	for q in fd.read ().split ('\n'):
		q = q.strip ()
		if (q):
			sys.stdout.write ('face|' + q + "\n")
	del fd
	# ip
	fd = os.popen ("ip addr show | sed -e 's/.*inet \\(\\([0-9]\\{1,3\\}[\\.]\\?\\)\\{4\\}\\).*\\|.*/\\1/' -e '/^$/d' | grep -v '127.0.0.1'")
	for q in fd.read ().split ('\n'):
		q = q.strip ()
		if (q):
			sys.stdout.write ('ipv4|' + q + "\n")
