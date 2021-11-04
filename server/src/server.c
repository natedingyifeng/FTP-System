#include "server.h"

int ServerInit(int argc, char **argv)
{
	int listenfd;
	struct sockaddr_in addr;

	int server_port = 21;

	for(int i=1; i<argc; i++)
	{
		if(strcmp(argv[i],"-root")==0)
		{
			strcpy(server_root, argv[i+1]);
		}
		if(strcmp(argv[i],"-port")==0)
		{
			server_port = atoi(argv[i+1]);
		}
	}

	if ((listenfd = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)) == -1) {
		printf("Error socket(): %s(%d)\n", strerror(errno), errno);
		return 1;
	}

	memset(&addr, 0, sizeof(addr));
	addr.sin_family = AF_INET;
	addr.sin_port = htons(server_port);
	addr.sin_addr.s_addr = htonl(INADDR_ANY);

	if (bind(listenfd, (struct sockaddr*)&addr, sizeof(addr)) == -1) {
		printf("Error bind(): %s(%d)\n", strerror(errno), errno);
		return 1;
	}

	if (listen(listenfd, 10) == -1) {
		printf("Error listen(): %s(%d)\n", strerror(errno), errno);
		return 1;
	}
	// if ((connection->connfd = accept(listenfd, NULL, NULL)) == -1) {
	// 	printf("Error accept(): %s(%d)\n", strerror(errno), errno);
	// }
	// else
	// {
	// 	char initial_message[100] = "220 Anonymous FTP server ready.\r\n";
	// 	SendMessageToSocket(connection,initial_message,strlen(initial_message),0);
	// }


	while (1) {
		Connection *connection = ConnectionInit(server_port, listenfd);
		pthread_t thread;
		pthread_create(&thread, NULL, (void*)CommandsProcessing, connection);
		pthread_detach(thread);
		// else
		// {
		// 	char USER_No[100] = "530 Not USER!\r\n";
		// 	SendMessageToSocket(connection, USER_No, strlen(USER_No),0);
		// }

 		// SendMessageToSocket(connection,sentence,len);

		// close(connection->connfd);
	}
	// close(connection->connfd);
	close(listenfd);
	return 0;
}

Connection* ConnectionInit(int port, int listenfd)
{
	Connection *connection=malloc(sizeof(Connection));
	memset(&connection->current_Dir, 0, sizeof(connection->current_Dir));
	strcpy(connection->current_Dir, server_root);
	if(connection->current_Dir[strlen(connection->current_Dir)-1]!='/')
	{
		strcat(connection->current_Dir, "/");
	}
	memset(&connection->addr, 0, sizeof(connection->addr));
	connection->addr.sin_family = AF_INET;
	connection->addr.sin_port = htons(port);
	connection->addr.sin_addr.s_addr = htonl(INADDR_ANY);	
	if ((connection->connfd = accept(listenfd, NULL, NULL)) == -1) {
		printf("Error accept(): %s(%d)\n", strerror(errno), errno);
	}
	else
	{
		char initial_message[100] = "220 Anonymous FTP server ready.\r\n";
	    SendMessageToSocket(connection,initial_message,strlen(initial_message), 0);
	}
	return connection;
}

void LoginProcessing(Connection *connection)
{
	int len;
	char sentence[8192];
	while(1)
	{
		len = ReadMessageFromSocket(connection, sentence, 8191);
		Command *command=malloc(sizeof(Command));
		getCommand(sentence, command, len);
		if(strcmp(command->name, "USER")==0)
		{
			LoggingIn(command,connection);
			if(connection->USER_ok == 1) break;
			else continue;
		}
		else
		{
			char USER_fail[100] = "530 USER is needed!\r\n";
			SendMessageToSocket(connection, USER_fail, strlen(USER_fail),0);
			continue;
		}
	}
	while(1)
	{
		len = ReadMessageFromSocket(connection, sentence, 8191);
		Command *command=malloc(sizeof(Command));
		getCommand(sentence, command, len);
		if(strcmp(command->name, "PASS")==0)
		{
			if(connection->USER_ok==1)
			{
				connection->login_ok=1;
				char PASS_succeed[100] = "230 PASS succeed.\r\n";
				SendMessageToSocket(connection, PASS_succeed, strlen(PASS_succeed),0);
				break;
			}
			else
			{
				connection->login_ok=0;
				char PASS_fail[100] = "503 Need USER first!\r\n";
				SendMessageToSocket(connection, PASS_fail, strlen(PASS_fail),0);
				continue;
			}
		}
	}
}

void CommandsProcessing(Connection *connection)
{
	LoginProcessing(connection);
	while(1)
	{
		int len;
		char sentence[8192];
		len = ReadMessageFromSocket(connection, sentence, 8191);
		Command *command=malloc(sizeof(Command));
		getCommand(sentence, command, len);
		if(strcmp(command->name, "SYST")==0)
		{
			char SYST_succeed[100] = "215 UNIX Type: L8\r\n";
			SendMessageToSocket(connection, SYST_succeed, strlen(SYST_succeed),0);
		}
		else if(strcmp(command->name, "TYPE")==0)
		{
			if(strcmp(command->content, "I")==0)
			{
				char TYPE_succeed[100] = "200 Type set to I.\r\n";
				SendMessageToSocket(connection, TYPE_succeed, strlen(TYPE_succeed),0);
			}
			else
			{
				char TYPE_fail[100] = "Invalid TYPE!\r\n";
				SendMessageToSocket(connection, TYPE_fail, strlen(TYPE_fail),0);
			}
		}
		else if(strcmp(command->name, "PORT")==0)
		{
			PortConnect(command,connection);
		}
		else if(strcmp(command->name, "RETR")==0)
		{
			RetrFileTransport(command,connection);
		}
		else if(strcmp(command->name, "PASV")==0)
		{
			PasvConnect(command,connection);
		}
		else if(strcmp(command->name, "STOR")==0)
		{
			StorFileTransport(command,connection);
		}
		else if(strcmp(command->name, "CWD")==0)
		{
			ChangeWoringDirectory(command, connection, server_root);
		}
		else if(strcmp(command->name, "MKD")==0)
		{
			CreateNewDirectory(command, connection, server_root);
		}
		else if(strcmp(command->name, "RMD")==0)
		{
			DeleteDirectory(command, connection, server_root);
		}
		else if(strcmp(command->name, "PWD")==0)
		{
			PrintWoringDirectory(command, connection, server_root);
		}
		else if(strcmp(command->name, "LIST")==0)
		{
			SendDirectoryContent(command, connection, server_root);
		}
		else if(strcmp(command->name, "RNFR")==0)
		{
			RenameFile(command, connection, server_root);
		}
		else if(strcmp(command->name, "QUIT")==0)
		{
			char QUIT_succeed[100] = "221 Goodbye.\r\n";
			SendMessageToSocket(connection, QUIT_succeed, strlen(QUIT_succeed),0);
			close(connection->connfd);
		}
		else
		{
			char unknown[100] = "Command Unknown!\r\n";
			SendMessageToSocket(connection, unknown, strlen(unknown),0);
		}
		free(command);
	}
}

int main(int argc, char **argv) {
	ServerInit(argc, argv);
	return 0;
}
