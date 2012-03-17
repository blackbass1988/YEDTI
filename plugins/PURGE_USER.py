    # -*- coding: utf-8
def init():
    return 1
def run(data):
    from MailIntegrator import MailIntegrator
    import re
    #retText = "PURGE USER"
    try:
	data = re.sub("\n|\r\n","",data)
	data = data.split(" ")
	username = data[0]
	#password = data[1]
        #print data
	mi = MailIntegrator()
	mi.deleteMailBox(username,physDelete=1)
	print mi.debugStack
        mi = False
	return "200 OK\n"
    except errorName:
	print errorName
	return "500 ERROR "+ errorName.toString() + "\n"
def ver():
    return "Функция полного удаления пользователя вместе с почтой.\nСинтаксис - username@domain"
    
    
#run("oleg@newmail.vvsu.ru")
