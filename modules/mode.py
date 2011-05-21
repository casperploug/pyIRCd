#!/usr/bin/env python
"""
	MODE module for pyIRCd v0.1
"""
import re, sys, time

# module
module_config = {
	"trigger":"MODE",
	"handle":"handle_mode_request",
	"all_clients":True
}

supported_modes = "ntmib"

def handle_mode_request(client, clients, text):
	try:
		mode_chunks = text.split()
		target = mode_chunks[0]
		modes = mode_chunks[1]
		set_modes = []
		
		for mode in re.finditer("([\+\-])([a-z])", modes):
			if mode.group(2) in supported_modes:
				set_modes.append(mode.group(1)+mode.group(2))
			else:
				client.reply("ERR_UNKNOWNMODE", "Mode %s is not supported." % mode.group(2))
		
		if target == client.nick:
			client.mode = ''.join(set_modes)
			client.connection.send(":%s MODE %s :%s\n" % (client.nick, target, client.mode))
		elif '@'+target in client.channels:
			pass
			# channel.mode = ''.join(set_modes)
			# for other_client in clients:
			# 	other_client.reply(":%s MODE %s :%s" % (other_client.nick, target, channel.mode))
		else:
			client.reply("ERR_UNKNOWNMODE", "You're not allowed to set mode for %s" % target)
	except:
		client.reply("ERR_UNKNOWNMODE", "Unknown mode")