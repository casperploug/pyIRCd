#!/usr/bin/env python
"""
	Quit module for pyIRCd v0.1
"""
import sys

# module
module_config = {
	"event_handle":"handle_event_quit",
	"events":"quit",
	"include channels":True
}

def handle_event_quit(event, client, channels):
	if event == "quit":
		notified_users = []
		for channel in client.channels:
			for user in client.channel(channel)["users"]:
				if user["client"] == client or user in notified_users:
					continue
				user["client"].connection.send(":%s!%s@%s QUIT :Bye!\n" % (client.nick, client.ident, client.host))
				notified_users.append(user)
		notified_users = None