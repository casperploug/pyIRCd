#!/usr/bin/env python
"""
	JOIN module for pyIRCd v0.1
"""
import re, sys
valid_mask = "^#[a-zA-Z0-9_\-]{3,40}"

# module
module_config = {
	"trigger":"JOIN",
	"handle":"handle_join_request",
	"include channels":True,
	"event_handle":"handle_event_join",
	"events":"registered"
}

def handle_join_request(client, channels, text):
	channel = join_helper(text)
	join_chan(client, channels, channel)

def join_chan(client, channels, channel):
	if channel is not None:
		if channel in client.channels:
			return
		# to do: ban/invite flag, not accounted for atm.
		if client.channel(channel) is None:
			channels[channel] = {"users":[{"client":client, "prefix":"o"}], "mode":"+nt"}
		else:
			client.channel(channel)["users"].append({"client":client, "prefix":""})
		client.channels[channel] = client.channel(channel)
		# get users on chan
		channel_nicks = []
		channel_info = client.channel(channel)
		if client in channel_info["users"]:
			return
		# return channel nicklist
		for users in channel_info["users"]:
			channel_nicks.append(usermode(users["prefix"])+users["client"].nick)
			try:
				users["client"].connection.send(":%s!%s@%s JOIN :%s\n" % (client.nick, client.ident, client.host, channel))
			except:
				pass

		for nick in channel_nicks:
			client.reply("RPL_NAMREPLY", "= %s :%s" % (channel, nick), None)
		client.reply("RPL_ENDOFNAMES", "%s :End of /NAMES list." % channel, None)
	else:
		error_msg = "disallowed channel.\n<channel> must be at least 3, and at most 40 chars\nallowed chars: a-z_- and 0-9.\n\nExample:\t/JOIN #herp.derp"
		client.connection.send(":%s %s %s :%s\n" % (client.vhost(), client.error_code("ERR_NEEDMOREPARAMS"), client.nick, error_msg))

def handle_event_join(event, client, channels):
	if event == "registered":
		error_msg = "Forcing you to join #blurk, muhaha!"
		client.connection.send(":%s %s %s :%s\n" % (client.vhost(), client.error_code("ERR_NEEDMOREPARAMS"), client.nick, error_msg))
		join_chan(client, channels, "#blurk")

def usermode(flag):
	if "q" in flag:
		return "~"
	elif "a" in flag:
		return "&"
	elif "o" in flag:
		return "@"
	elif "h" in flag:
		return "%"
	elif "v" in flag:
		return "+"
	else:
		return ""

def join_helper(text):
	channel_name = re.search("(%s)" % valid_mask, text)
	if channel_name is None:
		return None
	return channel_name.group(1)
