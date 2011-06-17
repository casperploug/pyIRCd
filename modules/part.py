#!/usr/bin/env python
"""
	Part module for pyIRCd v0.1
"""
import re, sys

# module
module_config = {
	"trigger":"PART",
	"handle":"handle_part_request",
}

# to do, add part text
valid_mask = "^(#[a-zA-Z0-9_\-]{3,40})(?: )?(.+)?"

def handle_part_request(client, text):
	channel = part_helper(text)
	for user in client.channel(channel[0])["users"]:
		if user["client"] == client:
			continue
		try:
			user["client"].connection.send(":%s!%s@%s PART %s\n" % (client.nick, client.ident, client.host, channel[0]))
		except:
			pass

def part_helper(text):
	channel_name = re.search("(%s)" % valid_mask, text)
	if channel_name is None:
		return None
	return (channel_name.group(2), channel_name.group(3))