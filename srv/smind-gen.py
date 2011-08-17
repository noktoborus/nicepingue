#!/usr/bin/python
# -*- encoding: utf-8 -*-

import os
import sys
import time

sys.path.insert (0, '.')
smind = __import__ ('smind-srv')

class Main (smind.Main):
	def __init__ (self):
		smind.Main.__init__ (self)
	def gen (self):
		macj = {}
		ha = {}
		c = self._db.cursor ()
		if not c.execute ("SELECT * FROM `main`"):
			return
		for mac in c.fetchall ():
			c.execute ("SELECT * FROM `current` WHERE `main_id`='" + str (mac[0]) + "' AND `status`='1' AND `historical`='0'")
			for node in c.fetchall ():
				if not mac[1] in macj:
					# if not machine in list
					macj[mac[1]] = {'__time': mac[2]}
				if not node[2] in macj[mac[1]]:
					# if not gadget_type in list
					macj[mac[1]][node[2]] = []
				if not c.execute ("SELECT * FROM `_" + str (node[2]) + "` WHERE `id`='" + str (node[3]) + "'"):
					continue
				macj[mac[1]][node[2]].append (list (c.fetchone ()[1:]) + [node[4]])
				if not node[2] in ha:
					ha[node[2]] = 0
				if ha[node[2]] < len (macj[mac[1]][node[2]]):
					ha[node[2]] = len (macj[mac[1]][node[2]])
		#print (macj)
		print ("""<html>
		<head>
			<meta http-equiv="content-type" content="text/html; charset=utf-8">
			<title>nicepingue :: """ + time.ctime () +  """</title>
			<style type='text/css'>
				th, td
				{
					border: 1px solid black;
					padding: 3px;
				}
			</style>
		</head>
		<body>
		""")
		print ("<table cellpadding='0' cellspacing='0'>")
		print ("\t" * 1 + "<thead>")
		print ("\t" * 2 + "<tr>")
		print ("\t" * 3 + "<th>#</th>")
		print ("\t" * 3 + "<th>time</th>")
		for ty in self.nnames:
			if not ty in ha or not ha[ty]:
				continue
			print ("\t" * 3 + "<th colspan='" + str (ha[ty] * (len (self.nnames[ty]) + 1)) + "'>" + ty + "</th>")
		print ("\t" * 2 + "</tr>")
		print ("\t" * 2 + "<tr>")
		print ("\t" * 3 + "<th>last query's time</th>")
		for ty in self.nnames:
			if not ty in ha or not ha[ty]:
				continue
			for n in range (0, ha[ty]):
				for tty in self.nnames[ty]:
					print ("\t" * 3 + "<th>" + tty + "</th>")
				print ("\t" * 3 + "<th>#</th>")
				print ("\t" * 3 + "<th>time</th>")
		print ("\t" * 2 + "</tr>")
		print ("\t" * 1 + "</thead>")
		print ("\t" * 1 + "<tbody>")
		_i = 0
		for node in macj:
			print ("\t" * 2 + "<tr>")
			print ("\t" * 3 + "<td>" + str (i) + "</td>")
			print ("\t" * 3 + "<td>" + str (macj[node]['__time']) + "</td>")
			for ty in self.nnames:
				if not ty in ha:
					continue
				n = 0
				if ty in macj[node]:
					n = len (macj[node][ty])
				if n < ha[ty]:
					for x in range (0, (ha[ty] - n) * (len (self.nnames[ty]) + 1)):
						print ("\t" * 3 + "<td></td>")
					continue
				for x in macj[node][ty]:
					for xx in x:
						print ("\t" * 3 + "<td>" + str (xx) + "</td>")
			print ("\t" * 2 + "</tr>")
		print ("\t" * 1 + "</tbody>")
		print ("</table>")
		print ("""</body>
				</html>""")


if __name__ == '__main__':
	s = Main ()
	s.gen ()

