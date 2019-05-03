#!/usr/bin/env python3

import selectors

sel = selectors.DefaultSelector()

def accept_wrapper(sock):
	conn, addr= sock.accept() #Should be ready to read
	print('accepted connection from', addr)
	conn.setblocking(False)
	data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
	events = selectors.EVENT_READ | selectors.EVENT_WRITE
	sel.register(conn, events, data=data)

def service_connection(key, mask):
	sock = key.fileobj
	data = key.data
	if mask & selectors.EVENT_READ:
		#Mask contains events that are ready.
		#EVENT_READ indicates availability for reading.
		recv_data = sock.recv(1024)
		#if data is received, append it to data.outb
		if recv_data:
			data.outb += recv_data
		#If not, unregister conn and then close.
		else: 
			print('closing connection to', data.addr)
			#Unreg so sock is no longer monitered by select().
			sel.unregister(sock)
			sock.close()			#Closes the server socket.
	if mask & selectors.EVENT_WRITE:
		#If mask is still open and available to be written to,
		#and outb is not an empty string, print out contents of outb.
		if data.outb:
			print('echoing', repr(data.outb), 'to', data.addr)
			#Sends contents of outb through socket to client.
			sent = sock.send(data.outb)
			#Deletes contents of outb.
			data.outb = data.outb[sent:]

host = '127.0.0.1'
port = 65432

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print('listening on', (host, port))
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

while True:
	events = sel.select(timeout=None)
	for key, mask in events:
		if key.data is None:
			accept_wrapper(key.fileobj)
		else:
			service_connection(key, mask)