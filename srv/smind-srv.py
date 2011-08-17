#!/usr/bin/python
# -*- encoding: utf-8 -*-

import time
mport MySQLdb
import os
import sys
import select
import socket
import traceback

def dprint (st):
	sys.stderr.write (str (st) + "\n")

class Main:
	socket_famy = socket.AF_UNIX
	socket_addr = ("/tmp/sock_smind-srv")
	mysql_addr = None
	mysql_user = None
	mysql_pass = None
	mysql_db = None
	timeout = 30
	nnames = {"cpu": ['string', 'serial', 'slot'],
			"face": ['string'],
			"net": ['string', 'hwaddr'],
			"ipv4": ['addr'],
			"board": ['vendor', 'string', 'serial'],
			"disk": ['string', 'serial', 'size'],
			"mem": ['string', 'size'],
			"host": ['hostname', 'string', 'arch']
			}
	_db = None
	_s = None
	_c = {} # { sockfd: [lasttime, "data"] }
	_l = [] # queue for remove sockets
	_d = [] # data queue
	def __init__ (self):
		for line in open ('/etc/shadowmind').read ().split ('\n'):
			line = line.split ('=', 1)
			if not len (line) == 2:
				continue
			line[0] = line[0].strip ()
			line[1] = line[1].strip ()
			if line[0] == 'mysql_addr':
				self.mysql_addr = line[1]
			elif line[0] == 'mysql_user':
				self.mysql_user = line[1]
			elif line[0] == 'mysql_pass':
				self.mysql_pass = line[1]
			elif line[0] == 'mysql_db':
				self.mysql_db = line[1]
			elif line[0] == 'timeout':
				try: self.timeout = int (line[1])
				except: pass
			elif line[0] == 'socket_addr':
				self.socket_addr = (line[1])
		# open mysql
		self._db = MySQLdb.connect (host = self.mysql_addr,
				user = self.mysql_user,
				passwd = self.mysql_pass,
				db = self.mysql_db)
	def lis (self):
		# set listen
		self._s = socket.socket (self.socket_famy, socket.SOCK_STREAM, 0)
		self._s.bind (self.socket_addr)
		self._s.listen (10)
		if self.socket_famy == socket.AF_UNIX:
			os.chmod (self.socket_addr, 0770)
	def clo (self):
		""" закрытие сервера """
		if self._s:
			self._s.close ()
		for s in list (self._c):
			if s:
				s.close ()
		self._c = type (self._c) ()
		self._s = None
		self._db.close ()
		self._db = None
		if self.socket_famy == socket.AF_UNIX:
			os.remove (self.socket_addr)
	def cle (self):
		""" чистка очереди на удаление """
		for s in self._l:
			if s in self._c:
				dprint ("cle '%s'" %(s))
				del self._c[s]
			try: s.close ()
			except: pass
		self._l = type (self._l) ()
	def parse (self, noparse = False):
		""" обрабатываем очередь данных """
		if not noparse:
			for q in self._d:
				dprint ("parse '%s'" %(q))
				self._parse_query (q.split ('\n'))
		self._d = type (self._d) ()
	def proc (self, tm):
		""" обрабатываем список сокетов """
		for s in select.select ([self._s] + list (self._c), [], [], tm)[0]:
			if s == self._s:
				""" если это серверный сокет, то обновляем добавлеям полученный сокет на обработку """
				self._c[s.accept ()[0]] = [time.time (), None]
				dprint ("append client")
			elif s in self._c:
				""" сокет клиентский """
				dprint ("client recv '%s'" %(s))
				dt = s.recv (1024)
				""" если данные не проинициализированны - делаем это """
				if not self._c[s][1]:
					self._c[s][1] = dt
				else:
					""" иначе складываем строки """
					self._c[s][1] += dt
				""" если длина dt нулевая - значит добрались до конца файла """
				if not len (dt):
					""" добавляем сокет в очередь на удаление """
					dprint ("append to cle '%s'" %(s))
					self._l.append (s)
					""" если есть завершённый файл в буфере - добавляем в очередь на обработку """
					if len (self._c[s][1]):
						dprint ("append to parse '%s'" %self._c[s][1])
						self._d.append (self._c[s][1])
				else:
					""" если это не конец - обновляем время """
					self._c[s][0] = time.time ()
			else:
				""" если эть какая-то левая чухня, то пытаемся закрыть её """
				try: s.close ()
				except: pass
		""" test socket's time """
		tt = time.time ()
		for s in self._c:
			if tt - self._c[s][0] > self.timeout and not s in self._l:
				self._l.append (s)
	def _parse_query (self, data):
		machine_id = None
		nodes = [] # [(current-id, gadget-id, gadget-type, "type|info|rma|tion"), ...]
		data = list (data)
		for q in range (0, len (data)):
			data[q] = data[q].strip ()
		# получаем sha1-ключ машины
		for line in data:
			i = line.split ('|')
			if i[0] == 'id' and len (i) == 2:
				machine_id = i[1].strip ()
				break
		# если ключ не указан - уходим
		if not machine_id:
			dprint ("KEY NOT SET")
			return
		# проверяем, есть ли она в базе
		c = self._db.cursor ()
		if c.execute ("SELECT * FROM `main` WHERE `machine_id`=%s", [machine_id]):
			# уже есть в списке, используем её id
			machine_id = c.fetchone ()[0]
			# и обновляем время доступа
			c.execute ("UPDATE `main` SET `update_time`=NOW() WHERE `id`=%s;", [machine_id])
		else:
			# нужно добавить наш тазик
			c.execute ("INSERT INTO `main` (`machine_id`, `update_time`) VALUES (%s, NOW());", [machine_id])
			machine_id = c.lastrowid
		# получаем список узлов
		if c.execute ("SELECT * FROM `current` WHERE `main_id`=%s AND `status`='1' AND `historical`!='1'", [machine_id]):
			for sline in list (c.fetchall ()):
				if c.execute ("SELECT * FROM `_" + sline[2] + "` WHERE `id`=%s", [sline[3]]):
					e = list (c.fetchone ())
					# предупреждаем появление ошибок из-за того, что тип не соответсвует строке (типа None)
					for q in range (0, len (e)):
						if not e[q]:
							e[q] = ''
						else:
							e[q] = str (e[q])
					# кладём строку в массив
					nodes.append ((sline[0], e[0], sline[2], "|".join (e[1:])))
		# сравниваем списки узлов
		#  ищем для удаления
		for q in nodes:
			dprint ("remove: %s" %str(q))
			ll = "|".join ((q[2], q[3]))
			if not ll  in data:
				# нашли, помечаем его как удалённый
				c.execute ("UPDATE `current` SET `historical`='1' WHERE `id`=%s", [q[0]])
				c.execute ("INSERT INTO `current` (`main_id`, `gadget_type`, `gadget_id`, `status_time`, `status`, `historical` )\
							VALUES (%s, %s, %s, NOW(), '0', '1')", [machine_id, q[2], q[1]])
			else:
				data.remove (ll)
		# всё что осталось - новое
		dprint ("data: %s" %(data))
		for q in data:
			q = q.split ('|')
			# сверяем наличие типа узла в списке и соотвествие количества аргументов с требуемым
			if q[0] in list (self.nnames) and len(q[1:]) == len (self.nnames[q[0]]):
				# подготавливаем запрос
				sql = "SELECT * FROM `_" + q[0] + "` WHERE "
				for i in range (0, len (self.nnames[q[0]])):
					if i != 0:
						sql += 'AND'
					sql = sql + " `" + self.nnames[q[0]][i] + "`='" + self._db.escape_string (q[1 + i]) + "' "
				i = None
				if c.execute (sql):
					# используем id шник из базы
					i = c.fetchone ()[0]
				else:
					# нужно добавить новую железку
					sql = "INSERT INTO `_" + q[0] + "` (" + "`" + "`, `".join (self.nnames[q[0]]) + "`" + ") VALUES ("
					for n in range (1, len (q)):
						if n != 1:
							sql += ', '
						sql += "'" + self._db.escape_string (q[n]) + "'"
					sql = sql + ");"
					if c.execute (sql):
						i = c.lastrowid
				# обновляем список текущих щелезак, если известен id
				if not i == None:
					c.execute ("INSERT INTO `current` (`main_id`, `gadget_type`, `gadget_id`, `status_time`, `status`, `historical` )\
								VALUES (%s, %s, %s, NOW(), '1', '0');", [machine_id, q[0], i])
			else:
				dprint ("!! %s" %(q))
				if not q[0] in list (self.nnames):
					dprint ("## not in self.nnames")
				else:
					if not len (q[1:]) == len (self.nnames[q[0]]):
						dprint ("## not eq len (%s:%s)" %(len (q[1:]), len (self.nnames[q[0]])))
						dprint ("@@ %s" %str (self.nnames[q[0]]))


						
if __name__ == '__main__':
	inst = Main ()
	inst.lis ()
	while True:
		try:
			try:
				inst.proc (1)
				inst.cle ()
				try: inst.parse ()
				except:
					e = sys.exc_info ()
					traceback.print_tb (e[2])
					print (e[1])
					print ("try continue")
					inst.parse (True)
					try:
						inst.parse
					except:
						break
			except KeyboardInterrupt:
				dprint ("@ shutdown")
				break
		except:
			e = sys.exc_info ()
			traceback.print_tb (e[2])
			print (e[1])
	inst.clo ()

