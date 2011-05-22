#!/usr/bin/env python
"""
	SETHOST module for pyIRCd v0.1
"""
import re, sys
surfix = "blurk.org"
valid_mask = "[a-zA-Z0-9\.\-]{3,40}"

# module
module_config = {
	"trigger":"SETHOST",
	"handle":"handle_sethost_request",
	"include channels":True
}

def handle_sethost_request(client, channels, text):
	host = sethost_helper(text)
	if host is not None:
		# set host
		client.host = "%s.%s" % (host, surfix)
		client.reply("001", "mangled host set to %s@%s" % (client.nick, client.host)) # find better suited irc code
		# example of reaching other clients (should be threaded, but this is just a simple example, and threading can be chosen by the module author to his/her liking):
		#for other_client in clients:
		#	print other_client
		#	if other_client == client:
		#		print "this is the current user, don't spam to him"
		#	else:
		#		other_client.reply("001", "hey, this guy changed his host!")
	else:
		error_msg = "disallowed host.\nUsage:\n\t/SETHOST <host>[.blurk.org]\n\t\t<host> must be at least 3, and at most 40 chars\n\t\t<host> allowed chars: a-z.- and 0-9.\n\n\tExample:\t/SETHOST herp.derp\n\t\t\t/SETHOST user.blurk.org"
		client.connection.send(":%s %s %s :%s\n" % (VHOST, client.error_code("ERR_NEEDMOREPARAMS"), client.nick, error_msg))

def sethost_helper(text):
	capture = re.search("^(%s)" % valid_mask, text)
	if capture is None:
		return None
	output = capture.group(1)
	while output.find(surfix) > -1:
	  output = re.sub("(\.)?%s" % surfix.replace(".", "\.").replace("-", "\-"), "", output)
	if re.search(valid_mask, output) is None:
		return None
	return output