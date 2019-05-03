#!/usr/bin/env python3

import socket, selectors

message = [b'Houston, we have liftoff.' , b'One small step for man.']

def service_connection(key, mask):
	sock = key.fileobj
	data = key.data
	if mask & selectors.EVENT_READ:
		recv_data = sock.recv(1024)
		if recv_data:
			print('received', repr(recv_data), 'from connection', data.connid)
			#Only difference from server.
			#Keeps track of num of bytes received from server so it can close
			#it's side of connection.  Server closes as well upon detection.
			data.recv_total += len(recv_data)
		if not recv_data or data.recv_total == data.msg_total:
			print('closing connection', data.connid)
			sel.unregister(sock)
			sock.close()
	if mask & selectors.EVENT_WRITE:
		if not data.outb and data.message:
			data.outb = data.message.pop(0)
		if data.outb:
			print('sending', repr(data.outb), 'to connection', data.connid)
			sent = sock.send(data.outb)
			data.outb = data.outb[sent:]