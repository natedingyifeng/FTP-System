#ifndef __STRINGPARSE_H__
#define __STRINGPARSE_H__

#include <sys/socket.h>
#include <netinet/in.h>

#include <unistd.h>
#include <errno.h>

#include <ctype.h>
#include <string.h>
#include <memory.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <dirent.h>
#include "foundation.h"

int getCommand(char* sentence, Command* command, int len);
int SendMessageToSocket(Connection *connection, char* sentence, int len, int type);
int ReadMessageFromSocket(Connection *connection, char* sentence, int len);
int getRandomPort(Connection *connection);
int checkDirectoryEmpty(Connection *connection, char* delete_path);

#endif
