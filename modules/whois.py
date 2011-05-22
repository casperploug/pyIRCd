#!/usr/bin/env python
"""
	WHOIS module for pyIRCd v0.1
"""
import re, sys, time

# module
module_config = {
	"trigger":"WHOIS",
	"handle":"handle_whois_request",
	"include channels":False
}

def handle_whois_request(client, text):
	if text != client.nick:
		client.reply("ERR_NEEDMOREPARAMS", "You can only look-up your own nick.")
		return
	try:
		client.reply("RPL_WHOISUSER", "%s %s %s * :%s" % (client.nick, client.ident, client.host, client.realname), None)
		if client.ircop is True:
			client.reply("RPL_WHOISOPERATOR", "is an IRC operator")
		client.reply("RPL_WHOISIDLE", "%s %s %s :seconds idle, signon time" % (client.nick, (int(time.time()) - client.last_action), client.signon), None)
		client.reply("RPL_ENDOFWHOIS", "End of /WHOIS list")
	except:
		client.reply("ERR_NEEDMOREPARAMS", "Usage: /WHOIS %s\nYou can only look-up your own nick." % client.nick)