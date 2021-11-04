#ifndef __SERVER_H__
#define __SERVER_H__

#include <sys/socket.h>
#include <netinet/in.h>

#include <unistd.h>
#include <errno.h>

#include <ctype.h>
#include <string.h>
#include <memory.h>
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include "foundation.h"
#include "stringparse.h"
#include "commands.h"

char server_root[200] = "/tmp";

int ServerInit(int argc, char **argv);
Connection* ConnectionInit(int port, int listenfd);
void LoginProcessing(Connection *connection);
void CommandsProcessing(Connection *connection);
int main(int argc, char **argv);

#endif
