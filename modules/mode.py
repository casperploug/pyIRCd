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

DEL = "-"
ADD = "+"

valid_mask = "^#[a-zA-Z0-9_\-]{3,40}"
supported_modes = "oqahvs"

def handle_mode_request(client, text):
	try:
		# MODE #chan +-x[x] user1 [user2]
		modes = re.search("(#[a-zA-Z0-9_\-]{3,40}) (.+)", text)
		mode_no = 0
		if modes is not None:
			target = modes.group(1)
			set_modes = modes.group(2).lower()

			modes_m = re.search("([\-\+a-z]+)(?: (.+))?", set_modes)
			mode_list = modes_m.group(1)
			nicks = modes_m.group(2).split()
			sign = None
			for mode in mode_list:
				if mode not in supported_modes:
					client.reply("ERR_UNKNOWNMODE", "Mode %s not supported." % mode)
					continue
				if mode == '+':
					sign = ADD
					continue
				elif mode == '-':
					sign = DEL
					continue
				elif mode == ' '
					break
				if mode in ["q", "a", "o", "h", "v"]:
					allowed = False
					for user in client.channel(target)["users"]:
						# q: ~owner a: &protected  o: @op h: %halfop v: +voice
						if user["client"] == client and len(set(["q", "a", "o", "h"]).intersection(list(user["prefix"]))) > 0:
							allowed = True
							break
					if allowed is not True:
						client.reply("ERR_UNKNOWNMODE", "You're not allowed to set mode %s for %s." % (mode, target))
						continue
				mode_string = sign + mode
				if nicks[i] is not None:
					mode_string += " " + nicks[i]
				for user in client.channel(target)["users"]:
					user["client"].connection.send(":%s MODE %s %s\n" % (client.nick, target, mode_string))
					if user["client"].nick in set_modes:
						if sign == ADD:
							if mode not in user["prefix"]:
								user["prefix"] += set_modes[1:].replace(user["client"].nick, "")
						elif sign == DEL:
							for mode in list(set_modes):
								user["prefix"] = user["prefix"].replace(mode, "")
						print "user's flags changed to:", user["prefix"]
				i += 1 # only if mode isn't +/1 or ' '
		else:
			# MODE #channel
			if re.search("^#[a-zA-Z0-9_\-]{3,40}$", text) is not None and text in client.channels:
				channel_info = client.channels[text]
				client.reply("RPL_CHANNELMODEIS", "%s %s" % (text, channel_info["mode"]), None) # results in: client.nick sets mode: +nt - wrong text format?
				client.reply("329", "%s %i" % (text, int(time.time())), None) # created (now)
			else:
				client.reply("ERR_UNKNOWNMODE", "You're not on %s" % text)
	except:
		client.reply("ERR_UNKNOWNMODE", "Unknown mode")