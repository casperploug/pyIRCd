#!/usr/bin/env python
import re, socket, string, sys, threading, time
from time import sleep
from datetime import timedelta, datetime, date
from random import choice
from OpenSSL import SSL
import ssl

sys.path.append("core")
sys.path.append("modules")

from irc_codes import *
MODULES = []

class irc_client():
	def __init__(self, connection, nick="herpderp", user="", passwd="", host="127.0.0.1", port=22):
		self.nick = nick
		self.user = user
		self.ident = None
		self.ip = None
		self.realname = None
		self.passwd = passwd
		self.host = host
		self.port = port
		self.connection = connection
		self.registered = False
		self.ircop = False
		self.last_action = None
		self.signon = None
		ping_thread = threading.Thread(target=self.PING_chain)
		ping_thread.start()
		
	def reply(self, code, text, prefix=":"):
		if prefix is None:
			prefix = ''
		if text[-1] != '\n':
			text += '\n'
		self.connection.send(":%s %s %s %s%s" % (config["VHOST"], self.error_code(code), self.nick, prefix, text))

	def error_code(self, error):
		try:
			return IRC_CODES[error]
		except:
			if re.search("[0-9]{3}", error) is not None:
				return error
			else:
				return None

	def PING_chain(self):
		valid_from = datetime.now() + timedelta(seconds=60)
		print "first ping req from us to client at", valid_from
		while (1):
			if datetime.now() >= valid_from:
				if self.PING() is False:
					break
				valid_from = datetime.now() + timedelta(seconds=60)
			sleep(5)

	def PING(self):
		try:
			ping_request = ''
			for i in range(8):
			  ping_request += choice(string.letters+string.digits)
			print "PING :%s" % ping_request
			self.connection.send("PING :%s\n" % ping_request)
			return True
		except:
			return False

	def display_motd(self):
		self.reply("RPL_MOTDSTART", "- %s Message of the day - " % config["VHOST"])
		try:
			motd_fp = open(MOTD_FILE)
			for motd_line in motd_fp:
				self.reply("RPL_MOTD", "- %s" % motd_line)
		except:
			pass
		self.reply("RPL_ENDOFMOTD", "End of /MOTD command")

clients = []

def accept_clients():
	while 1:
		try:
			conn, addr = s.accept()
			secure_connection = ssl.wrap_socket(conn, server_side=True, certfile=config["SSL_CERT"], keyfile=config["SSL_KEY"], ssl_version=ssl.PROTOCOL_SSLv23)
			client_handler = threading.Thread(target=irc_handler, args=[secure_connection, addr])
			client_handler.start()
		except:
			print "\nconnection failed, dropping"
			continue
		print "connection from", addr
	s.close()

def irc_handler(conn, addr):
	client = irc_client(conn)
	clients.append(client)
	client.signon = int(time.time())
	while 1:
		client.last_action = int(time.time())
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
				clients.remove(client)
				conn.close()
				break

			if data[0:5] == "PING ":
				print "got ping, replying PONG %s" % data[5:]
				conn.send("PONG %s\n" % data[5:])
				continue

			if data[0:5] == "PONG ":
				print "got pong %s" % data[5:]
				continue

			if data[0:4] == "NICK":
				try:
					oldnick = client.nick
					client.nick = data[5:]
					print "%s changes nick to %s" % (oldnick, client.nick)
					conn.send(":%s NICK %s\n" % (oldnick, client.nick))
				except:
					client.reply("ERR_NONICKNAMEGIVEN", "No nickname given")
				continue

			if data[0:5] == "USER ":
				try:
					client.user = data[5:]
					parse_user = re.search("^(?P<ident>[^ ]+) \"(?P<mail>[^\"]+)?\" \"(?P<ip>[^\"]+)\" :(?P<realname>.+)$", client.user)
					client.ident = parse_user.group("ident")
					client.ip = parse_user.group("ip")
					client.realname = parse_user.group("realname")
				except:
					client.reply("ERR_NEEDMOREPARAMS", "Not enough parameters")

			# welcome + motd
			if client.nick != "herpderp" and len(client.user) > 0 and client.registered is False:
				client.host = "user.%s" % config["VHOST"]
				print "flagging %s!%s@%s as registered..." % (client.nick, client.ident, client.host)
				client.reply("001", "Welcome to %s, %s" % (config["NETWORK_NAME"], client.nick))
				client.reply("002", "mangled host set to %s" % client.host)
				client.display_motd()
				client.registered = True
				continue
				if client.registered is False:
					client.reply("ERR_NOTREGISTERED", "You have not registered")

			if client.registered is False:
				# only allow the following commands to registered clients.
				continue

			if data[0:4] == "MODE":
				try:
					mode_chunks = data[5:].split()
					client.mode = mode_chunks[1]
					conn.send(":%s MODE %s :%s\n" % (client.nick, client.nick, client.mode))
				except:
					client.reply("ERR_UNKNOWNMODE", "Unknown mode")

			for module in MODULES:
				if data[0:len(module.module_config["trigger"])+1] == module.module_config["trigger"]+" ":
					try:
						print "sending data", data[len(module.module_config["trigger"])+1:], "to function named:", module.module_config["handle"]
						if module.module_config["all_clients"] is True:
							getattr(module, module.module_config["handle"])(client, clients, data[len(module.module_config["trigger"])+1:])
						else:
							getattr(module, module.module_config["handle"])(client, data[len(module.module_config["trigger"])+1:])
					except:
						print "External module error"
						client.reply("ERR_NEEDMOREPARAMS", "An error occurred. Please report to an IRCOP.")
	conn.close()
	try:
		clients.remove(client)
	except:
		pass
	print "closed connection from", addr

# irc settings. define in pyircd.conf
config = {
	"NETWORK_NAME" : None,
	"BIND_ADDRESS" : None,
	"PORT" : None,
	"VHOST" : None,
	"SSL_CERT" : None,
	"SSL_KEY" : None,
	"MOTD_FILE" : None
}
config_path = None
try:
	config_path = sys.argv[1]
except:
	config_path = "pyircd.conf"

def load_config(config_file):
	try:
		config_fp = open(config_file)
		config_content = config_fp.read()
		for network_name_setting in re.finditer("NETWORK_NAME[^\w]+([^\n\";]+)", config_content):
			config["NETWORK_NAME"] = network_name_setting.group(1)
		for bind_address_setting in re.finditer("BIND_ADDRESS[^\w]+([^\n\";]+)", config_content):
			config["BIND_ADDRESS"] = bind_address_setting.group(1)
		for port_setting in re.finditer("PORT[^\w]+([^\n\";]+)", config_content):
			config["PORT"] = int(port_setting.group(1))
		for vhost_setting in re.finditer("VHOST[^\w]+([^\n\";]+)", config_content):
			config["VHOST"] = vhost_setting.group(1)
		for ssl_cert_setting in re.finditer("SSL_CERT[^\w]+([^\n\";]+)", config_content):
			config["SSL_CERT"] = ssl_cert_setting.group(1)
		for ssl_key_setting in re.finditer("SSL_KEY[^\w]+([^\n\";]+)", config_content):
			config["SSL_KEY"] = ssl_key_setting.group(1)
		for motd_setting in re.finditer("MOTD_FILE[^\w]+([^\n\";]+)", config_content):
			config["MOTD_FILE"] = motd_setting.group(1)
		module_region = re.search("MODULES[^\w]+\[([^\]]+)]", config_content)
		if module_region is not None:
			for load_module in re.finditer("(?:\")(?P<module_name>[^,\"]+)(?:\")", module_region.group(1)):
				MODULES.append(__import__(load_module.group("module_name"), globals(), locals()))
				print "Loaded module: %s" % load_module.group("module_name")
		config_fp.close()
		if config["NETWORK_NAME"] is None or config["BIND_ADDRESS"] is None or config["PORT"] is None or config["VHOST"] is None or config["SSL_CERT"] is None or config["SSL_KEY"] is None:
			return False
		return True
	except:
		return False

if load_config(config_path) is False:
	print "config error."
	exit(0)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
	s.bind((config["BIND_ADDRESS"], config["PORT"]))
except Exception, e:
	print type(e)
print "Listening on %s:%s" % (config["BIND_ADDRESS"], str(config["PORT"]))
s.listen(5)
print 'pyIRCd v0.1'
accept_thread = threading.Thread(target=accept_clients)
accept_thread.start()
sleep(1)
accept_thread.join()