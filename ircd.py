#!/usr/bin/env python
import socket, string, sys, threading
from time import sleep
from datetime import timedelta, datetime, date
from random import choice
from OpenSSL import SSL
import ssl

class irc_client():
	def __init__(self, connection, nick="herpderp", user="", passwd="", host="127.0.0.1", port=22):
		self.nick = nick
		self.user = user
		self.passwd = passwd
		self.host = host
		self.port = port
		self.connection = connection
		self.registered = False
		ping_thread = threading.Thread(target=self.PING_chain)
		ping_thread.start()

	def PING_chain(self):
		valid_from = datetime.now() + timedelta(seconds=15)
		print "first ping req from us to client at", valid_from
		while (1):
			if datetime.now() >= valid_from:
				if self.PING(self.connection) is False:
					break
				valid_from = datetime.now() + timedelta(seconds=15)
			sleep(5)

	def PING(self, connection):
		try:
			ping_request = ''
			for i in range(8):
			  ping_request += choice(string.letters+string.digits)
			print "PING :%s" % ping_request
			connection.send("PING :%s\n" % ping_request)
			return True
		except:
			return False

	def motd(self, connection):
		connection.send(":%s %s %s :- %s Message of the day - \n" % (VHOST, RPL_MOTDSTART, self.nick, VHOST))
		for motd_line in MOTD_BODY:
			connection.send(":%s %s %s :- %s\n" % (VHOST, RPL_MOTD, self.nick, motd_line))
		connection.send(":%s %s %s :End of /MOTD command\n" % (VHOST, RPL_MOTDSTART, self.nick))

def accept_clients():
	while 1:
		try:
			conn, addr = s.accept()
			secure_connection = ssl.wrap_socket(conn, server_side=True, certfile=sys.argv[1], keyfile=sys.argv[2], ssl_version=ssl.PROTOCOL_SSLv23)
			client_handler = threading.Thread(target=irc_handler, args=[secure_connection, addr])
			client_handler.start()
		except:
			print "\nconnection failed, dropping"
			continue
		print 'connection from', addr
	s.close()

def irc_handler(conn, addr):
	client = irc_client(conn)
	while 1:
		try:
			conn.setblocking(1)
		except:
			break
		try:
			raw_data = conn.recv(1024)
		except:
			break
		conn.setblocking(0)
		if not raw_data:
			break
		if raw_data == "": continue
		for data_chunk in raw_data.split("\n"):
			data = data_chunk.rstrip()
			if len(data) is 0:
				continue
			print "received[",data,"]"
			if data[0:6] == "QUIT :":
				print "%s quit" % client.nick
				conn.close()
				break

			if data[0:5] == "PING ":
				print "got ping, replying PONG %s" % data[5:]
				conn.send("PONG %s\n" % data[5:])

			if data[0:5] == "PONG ":
				print "got pong %s" % data[5:]

			if data[0:4] == "NICK":
				try:
					oldnick = client.nick
					client.nick = data[5:]
					print "%s changes nick to %s" % (oldnick, client.nick)
					conn.send(":%s NICK %s\n" % (oldnick, client.nick))
				except:
					conn.send(":%s %s %s :No nickname given\n" % (VHOST, ERR_NONICKNAMEGIVEN, client.nick))

			if data[0:5] == "USER ":
				try:
					client.user = data[5:]
				except:
					conn.send(":%s %s %s :Not enough parameters\n" % (VHOST, ERR_NEEDMOREPARAMS, client.nick))

			if data[0:4] == "MODE":
				try:
					mode_chunks = data[5:].split()
					client.mode = mode_chunks[1]
					conn.send(":%s MODE %s :%s\n" % (client.nick, client.nick, client.mode))
					print "replied to MODE, with", ":%s MODE %s :%s" % (client.nick, client.nick, client.mode)
				except:
					conn.send(":%s %s %s :Unknown mode\n" % (VHOST, ERR_UNKNOWNMODE, client.nick))

			if data[0:8] == "USERHOST":
				try:
					conn.send(":%s %s %s :%s=+%s@%s\n" % (VHOST, RPL_USERHOST, client.nick, client.nick, "hidden", client.host))
				except:
					conn.send(":%s %s %s :Unknown command: %s\n" % (VHOST, ERR_UNKNOWNCOMMAND, client.nick, data))

			# welcome + motd
			if client.nick != "herpderp" and len(client.user) > 0 and client.registered is False:
				print "flagging %s@%s as registered..." % (client.nick, client.user)
				conn.send(":%s %s %s :Welcome to %s, %s\n" % (VHOST, "001", client.nick, NETWORK_NAME, client.nick))
				client.motd(conn)
#				conn.send(":%s MODE %s :+i\n" % (client.nick, client.nick))
				client.registered = True
				continue
			if client.registered is False:
				conn.send(":%s %s %s :You have not registered\n" % (VHOST, ERR_NOTREGISTERED, client.nick))

			if data[0:5] == "WHOIS":
				conn.send(":%s :End of /WHOIS list\n" % client.nick)
	conn.close()
	print "closed connection from", addr

# irc codes
RPL_USERHOST = 302
RPL_MOTDSTART = 375
RPL_MOTD = 372
RPL_ENDOFMOTD = 376
RPL_WHOISUSER = 311
RPL_WHOISSERVER = 312
RPL_WHOISOPERATOR = 313
RPL_WHOISIDLE = 317
RPL_ENDOFWHOIS = 318
RPL_WHOISCHANNELS = 319
ERR_NOSUCHNICK = 401
ERR_NOSUCHCHANNEL = 403
ERR_CANNOTSENDTOCHAN = 404
ERR_NOORIGIN = 409
ERR_NOTEXTTOSEND = 412
ERR_UNKNOWNCOMMAND = 421
ERR_NICKNAMEINUSE = 433
ERR_NONICKNAMEGIVEN = 431
ERR_NOTREGISTERED = 451
ERR_NEEDMOREPARAMS = 461

# irc settings
NETWORK_NAME = "blurk IRC Network"
HOST = "127.0.0.1"
VHOST = "irc.blurk.org"
PORT = 5005

MOTD_BODY = [
  "Standard IRC clients connect to port 6667*",
  "SSL IRC clients connect to port 7000",
  "",
  "",
  "*) temporarily enabled."
  ] 

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(5)
print 'herp derp ircd v0.1'
accept_thread = threading.Thread(target=accept_clients)
accept_thread.start()
sleep(1)
accept_thread.join()