#include "stringparse.h"

int SendMessageToSocket(Connection *connection, char* sentence, int len, int type)
{
	int p = 0;
	int fd=0;
	if(type==0) fd=connection->connfd;
	else if(type==1) fd=connection->transferfd;
	while (p < len) {
		int n = write(fd, sentence + p, len - p);
		if (n < 0) {
			printf("Error write(): %s(%d)\n", strerror(errno), errno);
			return 0;
	 	} else {
			p += n;
		}			
	}
	return 1;
}

int ReadMessageFromSocket(Connection *connection, char* sentence, int len)
{
	int p = 0;
	while (1) {
		int n = read(connection->connfd, sentence + p, len - p);
		if (n < 0) {
			printf("Error read(): %s(%d)\n", strerror(errno), errno);
			close(connection->connfd);
			continue;
		} else if (n == 0) {
			break;
		} else {
			p += n;
			if (sentence[p - 1] == '\n') {
				break;
			}
		}
	}
	sentence[p] = '\0';
	int sentence_length = p-1;
	return sentence_length;
}

int getCommand(char* sentence, Command* command, int len)
{
	sscanf(sentence,"%s %s",command->name,command->content);
	return 0;
}

int checkDirectoryEmpty(Connection *connection, char* delete_path)
{
	int is_empty = 1;
	DIR *pointer = NULL;
    struct dirent *reader;
    pointer = opendir(delete_path);
    if(pointer==NULL){
        char RMD_fail[100] = "550 MKD failed\r\n";
		SendMessageToSocket(connection, RMD_fail, strlen(RMD_fail),0);
		return -1;
    }
    while((reader=readdir(pointer))){
        if(strcmp(reader->d_name,".")!=0&&strcmp(reader->d_name,"..")!=0)
        {
        	is_empty=0;
        	break;
        }
    }
    return is_empty;
}
