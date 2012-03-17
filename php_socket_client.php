<?php

class MailClient {
    //Конструктор. Коннектимся, убеждаемся, что работает сервер, посылаем ему свое приветствие
    function MailClient($address,$port){
	$this->address = $address;
	$this->port = $port;
	$this->workStatus = 0;
	if ($this->createSocket()){
	    $this->connectSocket($this->socket,$this->address,$this->port);
	    $returnText = $this->socketRead($this->socket);
	    // Ищем, что сервер готов для работы и посылаем, что мы свои
	    if (preg_match('/HELLO/',$returnText)){
		$this->socketWrite("EHLO");
		if ($this->checkStatus($this->socketRead())){
		    $this->workStatus = 1;
		}
	    }
	}
    }
    private function createSocket(){
	echo 'Create socket ... ';
	$this->socket = socket_create(AF_INET,SOCK_STREAM,SOL_TCP);
	if ($this->socket < 0 ) {
	    throw new Exception('socket_create() failed: '.socket_strerror(socket_last_error())."\n");
	}else{
	    echo "OK\n";
	    return true;
	}
    }
    
    private function connectSocket($socket,$address,$port){
	echo 'Connect socket ... ';
	$this->result = socket_connect($socket,$address,$port);
	if ($this->result === false){
	    throw new Exception('socket_connect() failed: '.socket_strerror(socket_last_error())."\n");
	}else{
	    echo "OK\n";
	    return true;
	}
	
    }
    private function socketRead(){
	return socket_read($this->socket,1024);
    }
    
    private function socketWrite($data){
	socket_write($this->socket,$data,strlen($data));
    }
    private function checkStatus($data){
	preg_match_all('/\S/i',$data,$dataArr);
	if ($dataArr[0]==200){
	    return array("status"=>true);
	}else{
	    return array("status"=>false,"error"=>$data);
	}
    }
    
    public function changeCommand($command){
	if (!$this->newCommand()){
	    die("Комманда не сменена. Сервер некорректно отвечает");
	}
	$this->socketWrite($command);
	if ($this->checkStatus($this->socketRead())) {
	    return true;
	}else{
	    return false;
	}
    }
    
    private function newCommand(){
	$this->socketWrite("NEW_COMMAND");
	if ($this->checkStatus($this->socketRead())){
	    return true;
	}
    }
    
    public function send($data){
	$this->socketWrite($data);
	if ($status = $this->checkStatus($this->socketRead())){
	    return true;
	}else{
	    return $status;
	}
    }
    
    
    function __destruct(){
	print "Close socket...";    
	$this->changeCommand("QUIT");
	socket_close($this->socket);
	unset($this->socket);
	print "OK\n";

    }
    
}
/*
$client = new MailClient("newmail.vvsu.ru","2003");
if ($client->changeCommand("ADD_USER"))
    $client->send("oleg@newmail.vvsu.ru");
if ($client->changeCommand("PURGE_USER"))
    $client->send("oleg@newmail.vvsu.ru");
*/
?>

