#include "commands.h"

int LoggingIn(Command* command, Connection* connection)
{
	char *username_list[] = {"anonymous"};
	int username_number=1;
	int flag=0;
	connection->USER_ok=0;
	for(int i=0;i<username_number;i++)
	{
		if(strcmp(command->content,username_list[i])==0)
		{
			flag=1;
			char USER_succeed[100] = "331 USER confirmed. Please enter your PASS.\r\n";
			connection->USER_ok=1;
			SendMessageToSocket(connection, USER_succeed, strlen(USER_succeed),0);
			return 0;
		}
	}
	if(flag==0)
	{
		char USER_fail[100] = "530 Wrong username!\r\n";
		SendMessageToSocket(connection, USER_fail, strlen(USER_fail),0);
	}
	return 0;
}

int PortConnect(Command* command, Connection* connection)
{
	int ip[4]={0,0,0,0};
	int port=21;
	char IP_Address[50];
	if(connection->login_ok==1)
	{
		connection->mode = 1;
		char delims[] = ",";
		ip[0]=atoi(strtok(command->content, delims));
		for(int i=1;i<4;i++)
		{
			ip[i]=atoi(strtok(NULL, delims));
		}
		port=atoi(strtok(NULL, delims))*256+atoi(strtok(NULL, delims));
		sprintf(IP_Address,"%d.%d.%d.%d",ip[0],ip[1],ip[2],ip[3]);
		connection->addr.sin_family = AF_INET;
		connection->addr.sin_port = htons(port);
		connection->addr.sin_addr.s_addr = htonl(INADDR_ANY);
		if ((connection->transferfd = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)) == -1) {
			printf("Error socket(): %s(%d)\n", strerror(errno), errno);
			char PORT_fail[100] = "425 PORT Failed.\r\n";
			SendMessageToSocket(connection, PORT_fail, strlen(PORT_fail),0);
			connection->mode = 0;
			return 1;
		}
		if (inet_pton(AF_INET, IP_Address, &connection->addr.sin_addr) <= 0) {
			printf("Error inet_pton(): %s(%d)\n", strerror(errno), errno);
			char PORT_fail[100] = "425 PORT Failed.\r\n";
			SendMessageToSocket(connection, PORT_fail, strlen(PORT_fail),0);
			connection->mode = 0;
			return 1;
		}
		char PORT_succeed[100] = "200 PORT command successful. Consider using PASV.\r\n";
		SendMessageToSocket(connection, PORT_succeed, strlen(PORT_succeed),0);
	}
	return 0;
}

int RetrFileTransport(Command* command, Connection* connection)
{
	if(connection->login_ok==1)
	{
		char sentence[8192];
		if(connection->mode == 1)
		{
			if (connect(connection->transferfd, (struct sockaddr*)&connection->addr, sizeof(connection->addr)) < 0) {
				printf("Error connect(): %s(%d)\n", strerror(errno), errno);
				char RETR_fail[100] = "426 The TCP connection was established but then broken by the client or by network failure.\r\n";
				SendMessageToSocket(connection, RETR_fail, strlen(RETR_fail),0);
				return 1;
			}
		}
		else if(connection->mode == 2)
		{
			if ((connection->transferfd = accept(connection->listenfd, NULL, NULL)) == -1) {
                printf("Error accept(): %s(%d)\n", strerror(errno), errno);
                return 1;
            }
		}
		else
		{
			char RETR_fail[100] = "425 No TCP connection was established.\r\n";
			SendMessageToSocket(connection, RETR_fail, strlen(RETR_fail),0);
			return 1;
		}
		char RETR_start[100] = "150 RETR start.\r\n";
		SendMessageToSocket(connection, RETR_start, strlen(RETR_start),0);
		char file_name[200];
		strncpy(file_name, connection->current_Dir, 150);
		strcat(file_name, "/");
		strcat(file_name, command->content);
		int fd = open(file_name, O_RDONLY);
		while (1) {
			int n = read(fd, sentence, 8191);
			if (n < 0) {
				printf("Error read(): %s(%d)\n", strerror(errno), errno);
				return 0;
			} else if (n == 0) {
				break;
			} else {
				SendMessageToSocket(connection, sentence, n, 1);
			}
		}
		close(fd);
        close(connection->transferfd);
        char RETR_succeed[100] = "226 transmission finished.\r\n";
		SendMessageToSocket(connection, RETR_succeed, strlen(RETR_succeed),0);
	}
	return 0;
}

int PasvConnect(Command* command, Connection* connection)
{
	if(connection->login_ok==1)
	{
		int ip[4]={0,0,0,0};
		int port_msg[2]={0,0};
		char host[100] = {0};
	    if (gethostname(host, sizeof(host)) < 0) {
	        return 0;
	    }
	    struct hostent *hp;
	    if ((hp = gethostbyname(host)) == NULL) {
	        return 0;
	    }
	    char* ip_home=inet_ntoa(*(struct in_addr*)hp->h_addr_list[0]);
		char IP_Address[50];
		char delims[] = ".";
		ip[0]=atoi(strtok(ip_home, delims));
		for(int i=1;i<4;i++)
		{
			ip[i]=atoi(strtok(NULL, delims));
		}
		// ip[0]=10;
		// ip[1]=211;
		// ip[2]=55;
		// ip[3]=3;
		sprintf(IP_Address,"%d.%d.%d.%d",ip[0],ip[1],ip[2],ip[3]);

		srand((unsigned)time(NULL));
	    int port = rand() % (65535 - 20000) + 20000;
	    if ((connection->listenfd = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)) == -1) {
	        printf("Error socket(): %s(%d)\n", strerror(errno), errno);
	        return 0;
	    }
	    while(1)
	    {
	    	memset(&connection->addr, 0, sizeof(connection->addr));
			connection->addr.sin_family = AF_INET;
			connection->addr.sin_port = htons(port);
			connection->addr.sin_addr.s_addr = htonl(INADDR_ANY);	
			if (bind(connection->listenfd, (struct sockaddr*)&connection->addr, sizeof(connection->addr)) == -1) 
			{
				port+=5;
				continue;
			}
			else
			{
		        break;
			}
	    }
	    port_msg[0]=port/256;
	    port_msg[1]=port%256;
		
		if (inet_pton(AF_INET, IP_Address, &connection->addr.sin_addr) <= 0) {			//转换ip地址:点分十进制-->二进制
			printf("Error inet_pton(): %s(%d)\n", strerror(errno), errno);
			return 1;
		}
		if (listen(connection->listenfd, 10) == -1) {
		    printf("Error listen(): %s(%d)\n", strerror(errno), errno);
	        return 0;
		}
		connection->mode = 2;
		char PASV_succeed[100];
	    sprintf(PASV_succeed,"227 (%d,%d,%d,%d,%d,%d)\r\n",ip[0], ip[1], ip[2], ip[3], port_msg[0], port_msg[1]);
		SendMessageToSocket(connection, PASV_succeed, strlen(PASV_succeed),0);
	}
	return 0;
}

int StorFileTransport(Command* command, Connection* connection)
{
	if(connection->login_ok==1)
	{
		char sentence[8192];
		if(connection->mode == 2)
		{
			if ((connection->transferfd = accept(connection->listenfd, NULL, NULL)) == -1) {
                printf("Error accept(): %s(%d)\n", strerror(errno), errno);
                return 0;
            }
		}
		else if(connection->mode == 1)
		{
			if (connect(connection->transferfd, (struct sockaddr*)&connection->addr, sizeof(connection->addr)) < 0) {
				printf("Error connect(): %s(%d)\n", strerror(errno), errno);
				char RETR_fail[100] = "426 The TCP connection was established but then broken by the client or by network failure.\r\n";
				SendMessageToSocket(connection, RETR_fail, strlen(RETR_fail),0);
				return 1;
			}
		}
		else
		{
			char STOR_fail[100] = "425 No TCP connection was established.\r\n";
			SendMessageToSocket(connection, STOR_fail, strlen(STOR_fail),0);
			return 1;
		}
		char STOR_start[100] = "150 STOR start.\r\n";
		SendMessageToSocket(connection, STOR_start, strlen(STOR_start),0);
		char file_name[200];
		strncpy(file_name, connection->current_Dir, 150);
		strcat(file_name, "/");
		strcat(file_name, command->content);
		int fd = open(file_name, O_WRONLY | O_CREAT | O_TRUNC, S_IRUSR);
		int p = 0;
		int len=8191;
		while (1) {
			int n = read(connection->transferfd, sentence + p, len - p);
			if (n < 0) {
				printf("Error read(): %s(%d)\n", strerror(errno), errno);
				return 0;
			} else if (n == 0) {
				break;
			}
			if(write(fd,sentence,n)==0)
			{
				break;
			}
		}
		close(fd);
		close(connection->transferfd);
        char STOR_succeed[100] = "226 transmission finished.\r\n";
		SendMessageToSocket(connection, STOR_succeed, strlen(STOR_succeed),0);
	}
	return 0;
}

int ChangeWoringDirectory(Command* command, Connection* connection, char root[])
{
	char CWD_path[300];
	memset(CWD_path,0 ,sizeof(char) * 300);
	printf("%s", command->content);
	strncpy(CWD_path,command->content,150);
	char current_Dir[300];
	memset(current_Dir, 0 ,sizeof(char) * 300);
	if(strcmp(CWD_path, "..")==0)
	{
		strncpy(current_Dir,connection->current_Dir, 150);
		int num=0;
		for(int i=0;i<strlen(current_Dir);i++)
		{
			if(current_Dir[i]=='/') num++;
		}
		if(num>2)
		{
			printf("%c", current_Dir[strlen(current_Dir)-1]);
			int temp=strlen(current_Dir)-2;
			current_Dir[strlen(current_Dir)-1]='\0';
			while(current_Dir[temp]!='/')
			{
				current_Dir[temp]='\0';
				temp--;
			}
			strncpy(connection->current_Dir, current_Dir, 150);
			char CWD_succeed[400] = "250 Directory successfully changed.\r\n";
			sprintf(CWD_succeed,"250 %s.\r\n", connection->current_Dir);
			SendMessageToSocket(connection, CWD_succeed, strlen(CWD_succeed),0);
			return 0;
		}
		else
		{
			char CWD_fail[100] = "550 Failed to change directory.\r\n";
			SendMessageToSocket(connection, CWD_fail, strlen(CWD_fail),0);
			return 0;
		}
	}
	else
	{
		if(CWD_path[strlen(CWD_path)-1]!='/')
		{
			strcat(CWD_path, "/");
		}
		printf("%s", CWD_path);
		if(CWD_path[0]!='/')
		{
			strncpy(current_Dir,connection->current_Dir, 150);
			strcat(current_Dir, CWD_path);
			if(access(current_Dir, F_OK)==0)
			{
				strncpy(connection->current_Dir, current_Dir, 150);
				char CWD_succeed[400] = "250 Directory successfully changed.\r\n";
				sprintf(CWD_succeed,"250 %s.\r\n", connection->current_Dir);
				SendMessageToSocket(connection, CWD_succeed, strlen(CWD_succeed),0);
				return 0;
			}
			else
			{
				char CWD_fail[100] = "550 Failed to change directory.\r\n";
				SendMessageToSocket(connection, CWD_fail, strlen(CWD_fail),0);
				return 0;
			}
		}
		else
		{
			strncpy(current_Dir, root, 150);
			if(current_Dir[strlen(current_Dir)-1]=='/')
			{
				current_Dir[strlen(current_Dir)-1]='\0';
			}
			strcat(current_Dir, CWD_path);
			if(access(current_Dir, F_OK)==0)
			{
				strncpy(connection->current_Dir, current_Dir, 150);
				char CWD_succeed[400] = "250 Directory successfully changed.\r\n";
				sprintf(CWD_succeed,"250 %s.\r\n", connection->current_Dir);
				SendMessageToSocket(connection, CWD_succeed, strlen(CWD_succeed),0);
				return 0;
			}
			else
			{
				char CWD_fail[100] = "550 Failed to change directory.\r\n";
				SendMessageToSocket(connection, CWD_fail, strlen(CWD_fail),0);
				return 0;
			}
		}
	}
	return 0;
}

int CreateNewDirectory(Command* command, Connection* connection, char root[])
{
	char MKD_path[200];
	memset(MKD_path,0 ,sizeof(char) * 200);
	strncpy(MKD_path,command->content, 150);
	char new_Dir[300];
	memset(new_Dir, 0 ,sizeof(char) * 200);
	if(MKD_path[strlen(MKD_path)-1]!='/')
	{
		strcat(MKD_path, "/");
	}
	if(MKD_path[0]!='/')
	{
		strncpy(new_Dir,connection->current_Dir, 150);
		strcat(new_Dir, MKD_path);
		if(mkdir(new_Dir, S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH)==0)
		{
			char MKD_succeed[300];
			sprintf(MKD_succeed,"257 \"%s\" created.\r\n", new_Dir);
			SendMessageToSocket(connection, MKD_succeed, strlen(MKD_succeed),0);
			return 0;
		}
		else
		{
			char MKD_fail[100] = "550 MKD failed\r\n";
			SendMessageToSocket(connection, MKD_fail, strlen(MKD_fail),0);
			return 0;
		}
	}
	else
	{
		strncpy(new_Dir, root, 150);
		if(new_Dir[strlen(new_Dir)-1]=='/')
		{
			new_Dir[strlen(new_Dir)-1]='\0';
		}
		strcat(new_Dir, MKD_path);
		if(mkdir(new_Dir, S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH)==0)
		{
			char MKD_succeed[300];
			sprintf(MKD_succeed,"257 \"%s\" created.\r\n", new_Dir);
			SendMessageToSocket(connection, MKD_succeed, strlen(MKD_succeed),0);
			return 0;
		}
		else
		{
			char MKD_fail[100] = "550 MKD failed\r\n";
			SendMessageToSocket(connection, MKD_fail, strlen(MKD_fail),0);
			return 0;
		}
	}
}

int DeleteDirectory(Command* command, Connection* connection, char root[])
{
	char RMD_path[200];
	memset(RMD_path,0 ,sizeof(char) * 200);
	strncpy(RMD_path,command->content, 150);
	char delete_Dir[200];
	memset(delete_Dir, 0 ,sizeof(char) * 200);
	int is_empty=1;
	if(RMD_path[strlen(RMD_path)-1]!='/')
	{
		strcat(RMD_path, "/");
	}
	if(RMD_path[0]!='/')
	{
		strncpy(delete_Dir,connection->current_Dir, 150);
		strcat(delete_Dir,RMD_path);
		is_empty = checkDirectoryEmpty(connection, delete_Dir);
		if(is_empty==1 && strcmp(delete_Dir, connection->current_Dir)!=0 && rmdir(delete_Dir)==0)
		{
			char RMD_succeed[100] = "250 Remove directory operation successful.\r\n";
			SendMessageToSocket(connection, RMD_succeed, strlen(RMD_succeed),0);
			return 0;
		}
		else
		{
			char RMD_fail[100] = "550 RMD failed\r\n";
			SendMessageToSocket(connection, RMD_fail, strlen(RMD_fail),0);
			return 0;
		}
	}
	else
	{
		strncpy(delete_Dir, root, 150);
		if(delete_Dir[strlen(delete_Dir)-1]=='/')
		{
			delete_Dir[strlen(delete_Dir)-1]='\0';
		}
		strcat(delete_Dir, RMD_path);
		is_empty = checkDirectoryEmpty(connection, delete_Dir);
		if(is_empty==1 && strcmp(delete_Dir, connection->current_Dir)!=0  && rmdir(delete_Dir)==0)
		{
			char RMD_succeed[100] = "250 Remove directory operation successful.\r\n";
			SendMessageToSocket(connection, RMD_succeed, strlen(RMD_succeed),0);
			return 0;
		}
		else
		{
			char RMD_fail[100] = "550 RMD failed\r\n";
			SendMessageToSocket(connection, RMD_fail, strlen(RMD_fail),0);
			return 0;
		}
	}
}

int PrintWoringDirectory(Command* command, Connection* connection, char root[])
{
	char tem[250];
	int p = strlen(root);
	for(int i=p;i<strlen(connection->current_Dir);i++)
	{
		tem[i-p] = connection->current_Dir[i];
	}
	tem[strlen(connection->current_Dir)-p] = '\0';
	char PWD_succeed[250];
	sprintf(PWD_succeed,"257 \"%s\"\r\n", tem);
	SendMessageToSocket(connection, PWD_succeed, strlen(PWD_succeed),0);
	return 0;
}

int SendDirectoryContent(Command* command, Connection* connection, char root[])
{
	char LIST_path[200];
	memset(LIST_path,0 ,sizeof(char) * 200);
	char LIST_Dir[200];
	memset(LIST_Dir, 0 ,sizeof(char) * 200);
	if(command->content==NULL)
	{
		strncpy(LIST_path,command->content, 150);
		if(LIST_path[strlen(LIST_path)-1]!='/')
		{
			strcat(LIST_path, "/");
		}
		if(LIST_path[0]!='/')
		{
			strncpy(LIST_Dir,connection->current_Dir, 150);
			strcat(LIST_Dir,LIST_path);
		}
		else
		{
			strncpy(LIST_Dir, root, 150);
			if(LIST_Dir[strlen(LIST_Dir)-1]=='/')
			{
				LIST_Dir[strlen(LIST_Dir)-1]='\0';
			}
			strcat(LIST_Dir, LIST_path);
		}
	}
	else
	{
		strncpy(LIST_Dir,connection->current_Dir, 150);
	}
	if(connection->login_ok==1)
	{
		char sentence[8192];
		if(connection->mode == 2)
		{
			if ((connection->transferfd = accept(connection->listenfd, NULL, NULL)) == -1) {
                printf("Error accept(): %s(%d)\n", strerror(errno), errno);
                return 0;
            }
		}
		else if(connection->mode == 1)
		{
			if ((connect(connection->transferfd, (struct sockaddr*)&connection->addr, sizeof(connection->addr))) < 0) {
				printf("Error connect(): %s(%d)\n", strerror(errno), errno);
				char LIST_fail[100] = "426 The TCP connection was established but then broken by the client or by network failure.\r\n";
				SendMessageToSocket(connection, LIST_fail, strlen(LIST_fail),0);
				return 1;
			}
		}
		else
		{
			char LIST_fail[100] = "425 No TCP connection was established.\r\n";
			SendMessageToSocket(connection, LIST_fail, strlen(LIST_fail),0);
			return 1;
		}
		char path[200];
		strncpy(path, "ls -al ", 150);
		strcat(path, LIST_Dir);
		char LIST_start[100] = "150 Here comes the directory listing.\r\n";
		SendMessageToSocket(connection, LIST_start, strlen(LIST_start),0);
		FILE* f = popen(path, "r");
		int len=8191;
		while (1) {
			int n = fread(sentence, 1, len, f);
			if (n < 0) {
				printf("Error read(): %s(%d)\n", strerror(errno), errno);
				return 0;
			} else if (n == 0) {
				break;
			} else {
				SendMessageToSocket(connection, sentence, n, 1);
			}
		}
		fclose(f);
        char LIST_succeed[100] = "226 Directory send OK.\r\n";
		SendMessageToSocket(connection, LIST_succeed, strlen(LIST_succeed),0);
		close(connection->transferfd);
	}
	return 0;
}

int RenameFile(Command* command, Connection* connection, char root[])
{
	connection->rename_begin = 0;
	char RNFR_path[200];
	memset(RNFR_path,0 ,sizeof(char) * 200);
	strncpy(RNFR_path,command->content, 150);
	char oldname_Dir[200];
	memset(oldname_Dir, 0 ,sizeof(char) * 200);
	if(RNFR_path[0]!='/')
	{
		strncpy(oldname_Dir,connection->current_Dir, 150);
		strcat(oldname_Dir, RNFR_path);
	}
	else
	{
		strncpy(oldname_Dir, root, 150);
		if(oldname_Dir[strlen(oldname_Dir)-1]=='/')
		{
			oldname_Dir[strlen(oldname_Dir)-1]='\0';
		}
		strcat(oldname_Dir, RNFR_path);
	}
	if(access(oldname_Dir,F_OK)!=-1)
	{
		connection->rename_begin = 1;
		char RNFR_succeed[100] = "350 Ready for RNTO.\r\n.\r\n";
		SendMessageToSocket(connection, RNFR_succeed, strlen(RNFR_succeed),0);
	}
	else
	{
		connection->rename_begin = 0;
		char RNFR_fail[100] = "450 The file is not ready.\r\n.\r\n";
		SendMessageToSocket(connection, RNFR_fail, strlen(RNFR_fail),0);
		return 0;
	}
	int len;
	char sentence[8192];
	while(1)
	{
		len = ReadMessageFromSocket(connection, sentence, 8191);
		Command *command=malloc(sizeof(Command));
		getCommand(sentence, command, len);
		if(strcmp(command->name, "RNTO")==0)
		{
			if(connection->rename_begin==1)
			{
				char RNTO_path[300];
				memset(RNTO_path,0 ,sizeof(char) * 300);
				strncpy(RNTO_path,command->content, 150);
				char newname_Dir[200];
				memset(newname_Dir, 0 ,sizeof(char) * 200);
				if(RNTO_path[0]!='/')
				{
					strncpy(newname_Dir,connection->current_Dir, 150);
					strcat(newname_Dir, RNTO_path);
				}
				else
				{
					strncpy(newname_Dir,connection->current_Dir, 150);
					if(newname_Dir[strlen(newname_Dir)-1] == '/')
					{
						newname_Dir[strlen(newname_Dir)-1] = '\0';
					}
					strcat(newname_Dir, RNTO_path);
				}
				if(rename(oldname_Dir,newname_Dir) == 0)
				{
					char RNTO_succeed[400] = "250 Rename successful.\r\n";
					SendMessageToSocket(connection, RNTO_succeed, strlen(RNTO_succeed),0);
					connection->rename_begin = 0;
					break;
				}
				else
				{
					char RNTO_fail[100] = "550 RNTO failed.\r\n";
					SendMessageToSocket(connection, RNTO_fail, strlen(RNTO_fail),0);
					connection->rename_begin = 0;
					break;
				}
			}
			else
			{
				char RNTO_fail[100] = "550 Need RNFR first!\r\n";
				SendMessageToSocket(connection, RNTO_fail, strlen(RNTO_fail),0);
				connection->rename_begin = 0;
				break;
			}
		}
		else
		{
			char RNTO_fail[100] = "450 Need RNTO now!\r\n";
			SendMessageToSocket(connection, RNTO_fail, strlen(RNTO_fail),0);
			connection->rename_begin = 0;
			break;
		}
	}
	return 0;
}
