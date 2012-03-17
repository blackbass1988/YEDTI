# -*- coding: utf-8
def init():
    return 1
def run(data):
    from MailIntegrator import MailIntegrator
    import re
    #retText = "ADDING NEW USER"
    data = re.sub("\n|\r\n","",data)
    data = data.split(" ")
    username = data[0]
    mi = MailIntegrator()
    try:
        password = data[1]
        status = mi.createMailBox(username,password)
    except:
        status = mi.createMailBox(username)	    
    print mi.debugStack
    mi = False
    if status:
	return "200 OK\n"
    else:
	return "500 ERROR Mailbox already exists\n"
    #except errorName:
#	print errorName
#	return "500 ERROR "+ errorName + "\n"
def ver():
    return "Функция создания нового пользователя.\nСинтаксис - username@domain password"