# -*- coding: utf-8

import asyncore, socket, logging, time
logging.basicConfig(level=logging.DEBUG, format="%(created)-15s %(msecs)d %(levelname)8s %(thread)d %(name)s %(message)s")
log                     = logging.getLogger(__name__)

class MailSyncHandler(asyncore.dispatcher_with_send):
    ehlo = False
    current_command = ""
    def loadPlugins(self):
	import os
	commands = []
	for fname in os.listdir('plugins/'):
	    if fname.endswith('.py'):
		plugin_name = fname[:-3]
		if plugin_name != '__init__':
		    plugins = __import__('plugins.'+plugin_name)
		    plugin = getattr(plugins,plugin_name)
		    commands.append(plugin_name)
	return {'plugins':plugins, 'commands':commands}
    def handle_write(self):
	sent = self.send(send.buffer)
	self.buffer = self.buffer[sent:]
    def handle_close(self):
	self.close()
    def handle_read(self):
	self.plugins=self.loadPlugins()
	print self.current_command
	#print self.plugins
        data = self.recv(8192)
        if data:
    	    command = data[0:20].strip()
    	    if command=="EHLO":
    		self.send("Hello! Client\n200 OK\n")
    		log.debug("Клиент одобрен")
    		self.ehlo = True
    	    if command=="QUIT":
    		self.send("Bye Bye!\n")
    		log.debug("Сессия закрыта")
    		self.close()
	    if self.ehlo == False:
		self.send("Go on, Bad User\n")
		self.close()
	    try:
		changed=False
		if self.current_command=="":
		    if hasattr(self.plugins['plugins'],command):
			log.debug("Переход в режим " + command)
			self.current_command = getattr(self.plugins['plugins'],command)
			changed=True
			self.send("200 OK\n")
		if command == "NEW_COMMAND":
		    self.send("200 OK\n")
		    self.current_command = ""
		    pass
		if self.current_command != "" and not changed:
		    ret = self.current_command.run(data)
		    self.send(ret)
	    except NameError:
		print NameError


class MailSyncServer(asyncore.dispatcher):

    def __init__(self, host, port):
	self.logger("Начало работы сокет сервера")
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)


    def logger(self,msg):
	curTime = str(time.strftime("%Y:%m:%d %H:%M:%S"))
	log.debug(curTime + ": " + msg)
    def handle_accept(self):
        pair = self.accept()
        if pair is None:
            pass
        else:
            sock, addr = pair
            self.logger('Входящее соединение %s' % repr(addr))

            handler = MailSyncHandler(sock)
            handler.send("MailSyncServer ready\nHELLO\n")            
    def __del__(self):
	self.logger("Сервер выключен. Все соединения сброшены")
server = MailSyncServer('',2003)
asyncore.loop()

