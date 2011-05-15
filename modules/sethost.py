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
	"handle":"handle_userhost_request"
}

def handle_userhost_request(client, text):
	host = user_host_helper(text)
	if host is not None:
		# set host
		print client
		client.host = "%s.%s" % (host, surfix)
		print client.host
		client.reply(RPL_USERHOST, "%s=+%s@%s" % (client.nick, "hidden", client.host))
	else:
		error_msg = "disallowed host.\nUsage:\n\t/SETHOST <host>[.blurk.org]\n\t\t<host> must be at least 3, and at most 40 chars\n\t\t<host> allowed chars: a-z.- and 0-9.\n\n\tExample:\t/SETHOST herp.derp\n\t\t\t/SETHOST user.blurk.org"
		self.connection.send(":%s %s %s :%s\n" % (VHOST, ERR_NEEDMOREPARAMS, self.nick, error_msg))
		print errormsg # debug version

def user_host_helper(text):
	capture = re.search("^(%s)" % valid_mask, text)
	if capture is None:
		return None
	output = capture.group(1)
	while output.find(surfix) > -1:
	  output = re.sub("(\.)?%s" % surfix.replace(".", "\.").replace("-", "\-"), "", output)
	if re.search(valid_mask, output) is None:
		return None
	return output

#handle_userhost_request(sys.argv[1])