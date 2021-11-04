server: server.o stringparse.o commands.o
	gcc -pthread server.o stringparse.o commands.o -o server -Wall

server.o: server.c server.h foundation.h
	cc -c server.c -Wall

stringparse.o: stringparse.c stringparse.h
	cc -c stringparse.c -Wall

commands.o: commands.c commands.h
	cc -c commands.c -Wall

clean:
	rm -rf *.o
	rm -rf server