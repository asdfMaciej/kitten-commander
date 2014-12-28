import socket
import time
import sys


class Command:
	def __init__(self, you):
		self.you = you
		self.name = ""
	
	def run(self, arguments):
		pass

class cAuthorize(Command):
	def __init__(self, you):
		Command.__init__(self, you)
		self.name = "authorize"
	
	def run(self, arguments):
		if len(arguments) > 1: # first one - always nick
			if arguments[1] == self.you.password:
				accept_msg = "Correct! "+arguments[0]+" was added to "
				accept_msg += "authorized list. "
				self.you.authorized.append(arguments[0])
				self.you.functions.privmsg(self.you.channel, accept_msg)
			else:
				self.you.functions.privmsg(self.you.channel, "Wrong pass!")

class cQuit(Command):
	def __init__(self, you):
		Command.__init__(self, you)
		self.name = "quit"
	
	def run(self, arguments):
		if arguments[0] in self.you.authorized:
			self.you.functions.privmsg(self.you.channel, "Goodbye.")
			sys.exit(1)
		else:
			self.you.functions.privmsg(self.you.channel, "Not authorized!")


class IrcParser:
	def __init__(self, you):
		self.you = you
	
	def parse_raw_data(self, line):
		lines_split = line.split(" ") # split by spaces
		if lines_split[0] == "PING":
			self.you.functions.pong(lines_split[1])
			print "[*] Pong!"
			return ("", "PING", "", lines_split[1])				
		try:
			user_sending = lines_split[0]
			command = lines_split[1]
			user_receiving = lines_split[2]
			main_data = " ".join(lines_split[3:])
		
			return (user_sending, command, user_receiving, main_data)
 		except:
			print "[!] Error in parser: " + line
			return ("", "", "", "")
	
	def parse_user(self, user):
		username = (user.split("!")[0])[1:]
		ident = user.split("@")[0].split("!")[1]
		hostname = user.split("@")[1]
		
		return (username, ident, hostname)

	def parse_privmsg(self, line_parsed):
		username, ident, hostname = self.parse_user(line_parsed[0])
		channel = line_parsed[2]
		message = line_parsed[3][1:] # removes : before msg
		message_split = message.split(" ")
		prefix = message[0]  # first char of message
		
		owner_message = (username in self.you.authorized)
		command = (prefix == "#")
		if channel == self.you.channel:
			self.you.print_d("<"+username+"> "+message)
		else:
			self.you.print_d("<"+username+"@PRIV> "+message)

		if command:
			command_name = message_split[0][1:]
			if command_name in self.you.commands:
				self.you.exec_command(command_name, [username]+message_split[1:])		
class IrcFunctions:
	def __init__(self, you):
		self.you = you
	
	def join_channel(self, channel):
		self.you.socket_send(self.you.socket, "JOIN "+channel)
	
	def pong(self, msg):
		self.you.socket_send(self.you.socket, "PONG "+msg)
	
	def privmsg(self, channel, msg):
		self.you.socket_send(self.you.socket, "PRIVMSG "+channel+" :"+msg)

class IrcBot:
	def __init__(self):
		self.ip = "irc.rizon.net"
		self.port = 6667
		self.nickname = "RenkoSux"
		self.channel = "#polish"
		self.functions = IrcFunctions(self)
		self.parser = IrcParser(self)
		self.authorized = []
		self.password = "cyprianz5"
		self.commands = {}
	
	def add_command(self, command):
		self.commands[command.name] = command
	
	def exec_command(self, name, arguments):
		self.commands[name].run(arguments)

	def socket_send(self, socket, msg):
		socket.send(msg + "\n")
	
	def connect(self, socket, channel):
		n = self.nickname
		socket.connect((self.ip, self.port))
		self.socket_send(socket, "USER "+n+" "+n+" "+n+" :Jestem bogiem irc")
		self.socket_send(socket, "NICK "+n)
		time.sleep(10) # otherwise, it tends to not join the channel

		self.functions.join_channel(self.channel)
	
	def receive(self):
		message = self.socket.recv(2048)
		message = message.strip('\n\r')
		for line in message.split('\n'):
			
			line_parsed = self.parser.parse_raw_data(line)
			if line_parsed != ("", "", "", ""):
				if line_parsed[1] == "PRIVMSG": 
					self.parser.parse_privmsg(line_parsed)

	def run(self):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connect(self.socket, self.channel)
		while True:
			self.receive()
	
	def print_d(self, msg):
		print time.strftime("%H:%M:%S "+msg)

lil_bot = IrcBot()
lil_bot.add_command(cAuthorize(lil_bot))
lil_bot.add_command(cQuit(lil_bot))
lil_bot.run()
