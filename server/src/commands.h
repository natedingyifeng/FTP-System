#ifndef __COMMANDS_H__
#define __COMMANDS_H__

#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/stat.h>

#include <unistd.h>
#include <errno.h>

#include <ctype.h>
#include <string.h>
#include <memory.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <dirent.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include <arpa/inet.h>
#include "foundation.h"
#include "stringparse.h"

int LoggingIn(Command* command, Connection* connection);
int PortConnect(Command* command, Connection* connection);
int RetrFileTransport(Command* command, Connection* connection);
int PasvConnect(Command* command, Connection* connection);
int StorFileTransport(Command* command, Connection* connection);
int ChangeWoringDirectory(Command* command, Connection* connection, char root[]);
int CreateNewDirectory(Command* command, Connection* connection, char root[]);
int DeleteDirectory(Command* command, Connection* connection, char root[]);
int PrintWoringDirectory(Command* command, Connection* connection, char root[]);
int SendDirectoryContent(Command* command, Connection* connection, char root[]);
int RenameFile(Command* command, Connection* connection, char root[]);

#endif
