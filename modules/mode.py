#!/usr/bin/env python
"""
	MODE module for pyIRCd v0.1
"""
import re, sys, time

# module
module_config = {
	"trigger":"MODE",
	"handle":"handle_mode_request",
	"include channels":True
}

supported_modes = "ovnt"

def handle_mode_request(client, channels, text):
#	try:
#		mode_chunks = re.search("", text)
		
		mode_chunks = text.split()
		target = mode_chunks[0]
		try:
			modes = mode_chunks[1]
			try:
				modes += " "+mode_chunks[2]
			except:
				pass
		except:
			modes = None
		if modes is not None:
			set_modes = []
			print modes,"!!!!"
			for mode in re.finditer("([\+\-])([a-z])(?: (?P<param>[a-zA-Z0-9]+))?", modes):
				if mode.group(2) in supported_modes:
					set_modes.append(mode.group(1)+mode.group(2))
				else:
					client.reply("ERR_UNKNOWNMODE", "Mode %s is not supported." % mode.group(2))
			if len(set_modes) is 0:
				return
			if target == client.nick:
				client.mode = ''.join(set_modes)
				pass
			else:
				for user in client.channels[target]["users"]:
					if user["client"] == client and user["prefix"] not in "~&@":
						client.reply("ERR_UNKNOWNMODE", "You're not allowed to set mode for %s" % target)
						return
			for user in client.channels[target]["users"]:
				if mode.group("param") is not None:
					for set_mode in set_modes:
						user["client"].connection.send(":%s MODE %s :%s %s\n" % (client.nick, target, set_mode, mode.group("param")))
				else:
					for set_mode in set_modes:
						user["client"].connection.send(":%s MODE %s :%s %s\n" % (client.nick, target, set_mode, mode.group("param")))
		else:
			if re.search("^#[a-zA-Z0-9_\-]{3,40}", target) is not None and target in client.channels:
				channel_info = client.channels[target]
				for user in channel_info["users"]:
					user["client"].reply("RPL_CHANNELMODEIS", "%s %s" % (target, channel_info["mode"]), None) # results in: client.nick sets mode: +nt - wrong text format?
					user["client"].reply("329", "%s %i" % (target, int(time.time())), None) # created (now)
			else:
				client.reply("ERR_UNKNOWNMODE", "You're not on %s" % target)
#	except:
#		client.reply("ERR_UNKNOWNMODE", "Unknown mode")