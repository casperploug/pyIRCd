#!/usr/bin/env python
"""
	Allowed user/ip filtering module for pyIRCd v0.1
"""
import re, sys
valid_mask = "^#[a-zA-Z0-9_\-]{3,40}"

# module
module_config = {
	"event_handle":"handle_event_connect",
	"events":"connect"
}

def handle_event_connect(event, client):
	ip = client.ip[0]
	if "192.168.0." in ip:
		print ip, "allowed"
		return # ok
	else:
		print ip, "not allowed, closing"
		client.connection.close() # not ok