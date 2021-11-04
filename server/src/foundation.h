#ifndef __FOUNDATION_H__
#define __FOUNDATION_H__

#include <sys/socket.h>
#include <netinet/in.h>

#include <unistd.h>
#include <errno.h>

#include <ctype.h>
#include <string.h>
#include <memory.h>
#include <stdio.h>
#include <stdlib.h>

typedef struct Command
{
    char name[5];
    char content[8192];
}Command;

typedef struct Connection
{
    int listenfd;
    int connfd;
    int transferfd;
    struct sockaddr_in addr;
    char username[20];
    int USER_ok;
    int login_ok;
    int rename_begin;
    int mode;
    char current_Dir[200];
}Connection;

#endif
