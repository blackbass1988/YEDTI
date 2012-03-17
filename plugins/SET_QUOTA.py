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
	try:
	    quota = data[1]
	except:
	    quota = ""
	if quota != "":
        #print data
	    mi = MailIntegrator()
	    mi.resizeBox(username,quota)
	    print mi.debugStack
    	    mi = False
	    return "200 OK\n"
	else:
	    return "500 ERROR QUOTA NOT SET\n"
    except errorName:
	print errorName
	return "500 ERROR "+ errorName.toString() + "\n"
def ver():
    return "Функция изменения размера ящика.\nСинтаксис - username@domain quota"
    
    
#run("oleg@newmail.vvsu.ru")
