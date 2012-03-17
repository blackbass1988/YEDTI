# -*- coding: utf-8
import time,os, pymssql, MySQLdb
class MailIntegrator:     
    debugStack = ""
    timeStart = str(time.strftime("%Y:%m:%d %H:%M:%S"))
    
    # фукнция логирования. 
    def logger(self,log):
	self.debugStack+= str(time.strftime("%Y:%m:%d %H:%M:%S")) + " : " + log + "\n"
    
    
    # Парсит ящик на имя пользователя и его домен. возвращает объект из трех элементов: полное название, имя ящика и его домен
    def parseMailBox(self,mailbox):
	import re
	pregExp = re.compile('(.*)\@(.*)')
	match = pregExp.match(mailbox)
	matches = match.groups()
	name = matches[0]
	domain = matches[1]
	return {"username":mailbox,"name":name,"domain":domain}
    
    
    #Генерация пароля возвращает пароль в base64
    def generatePassword(self,passwd):
	import hashlib,base64
	passwd = hashlib.sha1(passwd)
	return "{SHA}" + base64.b64encode(passwd.digest())
    
    #Функция загрузки конфигурации из файла config.ini. Затем можно обратиться к любому элементу конфига через self.config.get('секиця','параметр')
    def loadConfig(self):
	self.logger("Вход в функцию loadConfig()")
	import ConfigParser
	config = ConfigParser.ConfigParser()
	config.read("config.ini")
	self.logger("Выход из функции. Параметры загружены успешно.")
	return config
    
    def __init__(self): 
    	self.logger("Класс инициализирован")
    	self.config = self.loadConfig()
    	self.ms_host=self.config.get('mssql','host') 
    	self.ms_login=self.config.get('mssql','login')
    	self.ms_password=self.config.get('mssql','password')
    	self.ms_database=self.config.get('mssql','database')
    	
    	self.my_host=self.config.get('mysql','host')
    	self.my_login=self.config.get('mysql','login')
    	self.my_password=self.config.get('mysql','password')
    	self.my_database=self.config.get('mysql','database')
    	#try:
    	self.connect()

    	#except:
    	#print "SQL CONNETION ERROR: "
    	
    def connect(self):
	try:
	    self.ms_connection = pymssql.connect(host=self.ms_host,user=self.ms_login,password=self.ms_password, database=self.ms_database)
	    self.ms_cursor = self.ms_connection.cursor()
	    self.my_connection = MySQLdb.connect(host=self.my_host,user=self.my_login,passwd=self.my_password, db=self.my_database)
	    self.my_cursor = self.my_connection.cursor()
	    self.logger("Соединение с базами установлено")
	except:
	    print "Connect() function exception"
    
    def getMsCursor(self):
	return self.ms_cursor
    
    def msQuery(self,sql):
	self.ms_cursor.execute(sql)
	return self.getMsCursor()
    
    def getMyCursor(self):
	return self.my_cursor
    
    def myQuery(self,sql):
	self.my_cursor.execute(sql)
	return self.getMyCursor()
    
    def createAlias(self,alias,goto,isbox=0):
	self.logger("Вход в функцию createAlias("+alias+","+goto+")")
	if self.checkExistanceBox(box=alias) or isbox==1:
	    active = "1"
	    mb = self.parseMailBox(alias)
	    domain = mb['domain']
	    query = "insert into alias(address,goto,domain,active) values ('"+alias+"','"+goto+"','"+domain+"','"+active+"')"
	    self.myQuery(query)
	    self.logger("Выход из функции. Алиас создан")
	else:
	    self.logger("Выход из фукнции. Алиас не создан")
	    return 0
    #хм
    def getAllAliases(self):
	return 1
    
    
    def deleteMailBox(self,box,physDelete=0):
	self.logger("Вход в функцию deleteMailBox("+box+")")
	if self.checkExistanceBox(box):
	    if physDelete==1:
		self.realDeleteMailBox(box)
	    sql = "delete from mailbox where username='"+box+"'"
	    self.myQuery(sql)
	    self.deleteAlias(box)
	    self.logger("Выход из функции. Почтовый ящик удален")
	    return 1
	else:
	    self.logger("Выход из функции. Почтовый ящик не найден")
	    return 0
	
    
    def deleteAlias(self,alias):
	self.logger("Вход в функцию deleteAlias("+alias+")")
	if self.checkExistanceAlias(alias):
	    sql = "delete from alias where address='"+alias+"'"
	    self.myQuery(sql)
	    self.logger("Выход из функции. Алиас удален")
	    return 1
	else:
	    self.logger("Выход из функции. Алиас не найден")
	    return 0
    #
    def getAlias(self):
	return 1
    
    def getDefaultSize(self):
	sql = "select value from config where name='DefaultSize'"
	cur = self.myQuery(sql)
	size = 104857600
	for row in cur:
	    size = row[0]
	return size
    
    def checkExistanceAlias(self,alias):
	sql = "select count(*) from alias where address='"+alias+"'"
	cur = self.myQuery(sql)
	result = cur.fetchone()
	if result[0]>0:
	    return 1
	else:
	    return 0
    
    def checkExistanceBox(self,box):
	self.logger("Вход в функцию checkExistanceBox("+box+")")
	if self.checkExistanceAlias(box):
	    sql = "select count(*) from mailbox where username='"+box+"'"
	    cur = self.myQuery(sql)
	    result = cur.fetchone()
	    if result[0]>0:
		self.logger("Ящик существует. Выход из функции")
		return 1
	    else:
		self.logger("Ящика не существует. Выход из функции")
		return 0
	else:
	    return 0
    
    #Нужно ли?
    def checkExistanceBoxAll(self):
	return 1
    
    def resizeBox(self,box,newQuota):
	self.logger( "Вход в функцию resizeBox("+box+","+str(newQuota)+")")
	if self.checkExistanceBox(box):
	    sql = "update mailbox set quota = '"+str(newQuota)+"' where username = '"+box+"'"
	    cur = self.myQuery(sql)
	    self.logger("Размер ящика успешно изменен. Выход из функции")
	    return 1
	else:
	    self.logger("Ящика не существует. Выход из функции")
	    return 0
    
    #Создание нового ящика. создает ящик и алиас на него.
    def createMailBox(self,box,passwd=str(time.time()),quota=0):
	self.logger("Вход в фукнцию createMailBox("+box+","+self.generatePassword(passwd)+","+str(quota)+")")
	if self.checkExistanceBox(box)<>1:
	    active = "1"
	    mb = self.parseMailBox(box)
	    passwd = self.generatePassword(passwd)
	    maildir = self.getMailDir(mb)
	    if quota==0:
		quota=self.getDefaultSize()
	    sql = "insert into mailbox(username,password,name,maildir,quota,local_part,domain,active) values ('"+box+"','"+passwd+"','"+mb['name']+"','"+maildir+"','"+str(quota)+"','"+mb['name']+"','"+mb['domain']+"','"+active+"')"
	    #print sql
	    self.myQuery(sql)
	    if self.createAlias(box,box,isbox=1):
		self.logger("Выход из фукнции. Ящик успешно добавлен")
	    return 1
	else:
	    self.logger("Выход из фукнции. Ящик уже существует")
	    return 0
    
    #Смена пароля для доступа к почтовому ящику
    def changePassword(self,box,passwd=str(time.time())):
	self.logger("Вход в фукнцию changePassword("+box+","+self.generatePassword(passwd)+")")
	if self.checkExistanceBox(box):
	    sql = "update mailbox set password = '"+self.generatePassword(passwd)+"' where username='"+box+"'"
	    self.logger("Выход из фукнции. Пароль изменен")
	    self.myQuery(sql)
	    return 1
	else:
	    self.logger("Выход из фукнции. Ящика не существует")
	    return 0



    def isExist(self):
	return 1
    
    def isDir(self):
	return 1
    
    #Генерируем имя директории для хранения почты.
    def getMailDir(self,mailboxObj):
	maildirpath=self.config.get('common','maildirprefix')
	if len(maildirpath)>0 and maildirpath[0:-1]<>"/":
	    maildirpath+="/"
	maildirpath += mailboxObj['domain'] + "/" + mailboxObj['name'][0:1] +"/" + mailboxObj['name'] + "/"
	return maildirpath
	
    #Взять имя директории почты из базы	
    def getDBMailDir(self,box):
	maildirpath=self.config.get('common','maildirprefix')
	if len(maildirpath)>0 and maildirpath[0:-1]<>"/":
	    maildirpath+="/"
    
	sql = "select maildir from mailbox where username = '"+box+"'"
	cur = self.myQuery(sql)
	result = cur.fetchone()
	maildir = result[0]
	if maildir[0:1]<>"/":
	    maildir=maildirpath+maildir
	    if maildir[0:1]<>"/":
		maildir="/var/vmail/" + maildir
	return maildir

    def checkDir(self):
	return 1

    
    def deleteFiles(self,dirList, dirPath):
	for file in dirList:
	    self.logger("Удаляю " + file)
    	    os.remove(dirPath + "/" + file)
    def removeDirectory(self,dirEntry):
    	    self.logger("Удаляю файлы в каталоге" + dirEntry[0])
            self.deleteFiles(dirEntry[2], dirEntry[0])
            self.emptyDirs.insert(0, dirEntry[0])
    
    #Функция удаления файлов и директорий на диске по пути
    def purgeBox(self,path):
	self.logger("Вход в функцию purgeBox("+path+")")
	self.emptyDirs = []
	tree = os.walk(path)
	for directory in tree:
	    self.removeDirectory(directory)
	for dir in self.emptyDirs:
	    os.rmdir(dir)
	self.logger("Выход из фукнции. Удаление прошло успешно")
	return 1

    #Фукнция физчического удаления почтовика
    def realDeleteMailBox(self,box):
	self.logger("Вход в функцию realDeleteMailBox("+box+")")
	physPath = self.getDBMailDir(box)
	if self.purgeBox(physPath):
	    self.logger("Выход из фукнции. Удаление прошло успешно")
	    return 1
	else:
	    self.logger("Выход из фукнции. Удаление не удалось")

    def blockMailBox(self,box):
	self.logger("Вход в функцию blockMailBox("+box+")")
	if self.checkExistanceBox():
	    sql="update mailbox set active=0 where username='"+box+"'"
	    self.myQuery(sql)
	    sql="update alias set active=0 where address='"+box+"'"
	    self.myQuery(sql)	    
	    self.logger("Выход из фукнции. Ящик заблокирован")
	    return 1
	else:
	    self.logger("Выход из фукнции. Ящика не существует")
	    return 0
	    

    def activateMailBox(self,box):
	self.logger("Вход в функцию activateMailBox("+box+")")
	if self.checkExistanceBox():
	    sql="update mailbox set active=1 where username='"+box+"'"
	    self.myQuery(sql)
	    sql="update alias set active=1 where address='"+box+"'"
	    self.myQuery(sql)	    
	    self.logger("Выход из фукнции. Ящик разблокирован")
	    return 1
	else:
	    self.logger("Выход из фукнции. Ящика не существует")
	    return 0

    # Отправить сообщение от постмастера
    def notificate(self,box,message):
	from Mailing import Mailing
	magent = Mailing()
	magent.send(rcpt=box,msg=message)
	
	return 1

    # Оновление алиаса 
    def updateAlias(self,alias,goto,domain):
	self.logger("Вход в функцию updateAlias('"+alias+"','"+goto+"','"+domain+"')")
	if self.checkExistanceAlias(alias):
	    self.logger("Обновление существующего алиаса " + alias)
	    sql="update alias set goto='"+goto+"',active='1',is_imported=1,synced=1 where address='"+alias+"'"
	    print sql
	    self.myQuery(sql)
	else:
	    self.logger("Создание нового алиаса " + alias)
	    sql="insert alias (address,goto,domain,active,is_imported,synced) values('"+alias+"','"+goto+"','"+domain+"','1',1,1)"
	    print sql
	    self.myQuery(sql)
	self.logger("Выход из функции. Алиас обновлен успешно")
	return 1
    
    #Обновление всех алиасов
    def updateAliases(self):
	self.logger("Вход в функцию updateAlias")
	self.logger("Запуск обновления алиасов")
	sql = "update alias set synced=0 where is_imported=1"
	self.myQuery(sql)
	mssql = "select alias,[goto],domain from inet..mail_aliases_goto"
	print mssql
	result = self.msQuery(mssql)
	for row in result:
	    self.updateAlias(alias=row[0],goto=row[1],domain=row[2] )
	self.logger("Удаление неиспользуемых алиасов")
	sql = "delete from alias where is_imported=1 and synced=0"
	self.myQuery(sql)
	self.logger("Выход из функции. Все алиасы обновлены")
	return 1
    
    def renameBox(self,username,newusername):
        self.logger("Вход в функцию renameBox("+username+","+newusername+")")
        mb = self.parseMailBox(newusername)
        sql = "update mailbox set username='"+newusername+"', domain = '"+mb['domain']+"', local_part='"+mb['name']+"' where username = '"+username+"'"
        self.myQuery(sql)
        sql = "update alias set address='"+newusername+"', goto='"+newusername+"', domain ='"+mb['domain']+"' where address='"+username+"'"
        self.myQuery(sql)
        self.logger("Выход из функции. Ящик изменен")
	return 1
    
    
    #Функция обновления ящика пользователя.
    def updateBox(self,username,newusername=0,passwd=0,quota=0):
	self.logger("Вход в функцию updateBox("+username+","+self.generatePassword(str(passwd))+")")
	if self.checkExistanceBox(username):
	    if passwd != 0:
		self.changePassword(username,passwd)
	    if quota !=  0:
		self.resizeBox(username,quota)
	    if newusername != 0:
		self.renameBox(username,newusername)
    	    self.logger("Выход из функции. Учетная запись обновлена")
	    return 1
	else:
	    self.logger("Выход из функции. Учетной записи не существует")
	    return 0
    def __del__(self):
	self.ms_connection.close()
	self.my_connection.close()
	print 'Работа класса прекращена'