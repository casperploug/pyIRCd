#!/usr/bin/env python
"""
	MODE module for pyIRCd v0.1
"""
import re, sys, time

# module
module_config = {
	"trigger":"MODE",
	"handle":"handle_mode_request",
}

valid_mask = "^#[a-zA-Z0-9_\-]{3,40}"
supported_modes = "oqahvnt" # not enforced atm.

def handle_mode_request(client, text):
#	try:
		# MODE #chan +-x[x] user1 [user2]
		modes = re.search("(#[a-zA-Z0-9_\-]{3,40}) (.+)", text)
		if modes is not None:
			target = modes.group(1)
			set_modes = modes.group(2)
			allowed = False
			for user in client.channel(target)["users"]:
				# q: ~owner a: &protected  o: @op h: %halfop v: +voice
				if user["client"] == client and len(set(["q", "a", "o", "h"]).intersection(list(user["prefix"]))) > 0:
					allowed = True
					break
			if allowed is True:
				for user in client.channel(target)["users"]:
					user["client"].connection.send(":%s MODE %s %s\n" % (client.nick, target, set_modes))
					if user["client"].nick in set_modes:
						if set_modes[0] == "+":
							user["prefix"] += set_modes[1:].replace(user["client"].nick, "")
						elif set_modes[0] == "-":
							for mode in list(set_modes):
								user["prefix"] = user["prefix"].replace(mode, "")
						print "user's flags changed to:", user["prefix"]
			else:
				client.reply("ERR_UNKNOWNMODE", "You're not allowed to set mode for %s" % target)
				return
		else:
			# MODE #channel
			if re.search("^#[a-zA-Z0-9_\-]{3,40}$", text) is not None and text in client.channels:
				channel_info = client.channels[text]
				client.reply("RPL_CHANNELMODEIS", "%s %s" % (text, channel_info["mode"]), None) # results in: client.nick sets mode: +nt - wrong text format?
				client.reply("329", "%s %i" % (text, int(time.time())), None) # created (now)
			else:
				client.reply("ERR_UNKNOWNMODE", "You're not on %s" % text)
#	except:
#		client.reply("ERR_UNKNOWNMODE", "Unknown mode")