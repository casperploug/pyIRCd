#!/usr/bin/env python
"""
	MODE module for pyIRCd v0.1
"""
import re, sys, time

# module
module_config = {
	"trigger":"MODE",
	"handle":"handle_mode_request",
	"all_clients":False
}

def handle_mode_request(client, text):
	try:
		mode_chunks = text.split()
		target = mode_chunks[0]
		mode = mode_chunks[1]
		if target == client.nick or '@'+target in client.channels:
			client.mode = mode
			client.connection.send(":%s MODE %s :%s\n" % (client.nick, target, client.mode))
		else:
			client.reply("ERR_UNKNOWNMODE", "You're not allowed to set mode for %s" % target)
	except:
		client.reply("ERR_UNKNOWNMODE", "Unknown mode")