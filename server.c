#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <netdb.h>
#include <errno.h>
#include <time.h>
#include <unistd.h>

int main() {
    int server_socket;
    char *local_host = "127.0.0.1";
    char *local_port = "80";
    char *remote_host = "example";
    char *remote_port = "80";
    struct addrinfo hints;
    struct addrinfo *bind_address, *remote_address;
    struct sockaddr_storage client_address;
    socklen_t client_len;
    char request_buf[1024];
    char response_buf[1024];
    int request_length, response_length;
    int request_buf_length = 1024;
    int response_buf_length = 1024;
    int client_socket, remote_socket;

    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_flags = AI_PASSIVE;

    getaddrinfo(local_host, local_port, &hints, &bind_address);

    server_socket = socket(bind_address->ai_family, bind_address->ai_socktype, bind_address->ai_protocol);
    if (server_socket < 0) {
        fprintf(stderr, "socket() failed. (%d)\n", errno);
        return 1;
    }

    printf("Binding socket to local address...\n");
    if (bind(server_socket, bind_address->ai_addr, bind_address->ai_addrlen)) {
        fprintf(stderr, "bind() failed. (%d)\n", errno);
    }
    freeaddrinfo(bind_address);

    printf("Listening on %s:%s\n", local_host, local_port);
    if (listen(server_socket, 10) < 0) {
        fprintf(stderr, "listen() failed. (%d)\n", errno);
        return 1;
    }
    
    printf("Waiting for connection...\n");
    while (1) {
        client_len = sizeof(client_address);
        client_socket = accept(server_socket, (struct sockaddr*) &client_address, &client_len);

        if (client_socket < 0) {
            fprintf(stderr, "accept() failed. (%d)\n", errno);
            return 1;
        }

        request_length = recv(client_socket, request_buf, request_buf_length, 0);
        printf("Request: %s\n", request_buf);

        getaddrinfo(remote_host, remote_port, &hints, &remote_address);
        remote_socket = socket(remote_address->ai_family, remote_address->ai_socktype, remote_address->ai_protocol);
        if (remote_socket < 0) {
            fprintf(stderr, "socket() failed. (%d)\n", errno);
            return 1;
        }

        if (connect(remote_socket, (struct sockaddr *)&remote_address, sizeof(remote_address)) < 0) {
            fprintf(stderr, "connect() failed. (%d)\n", errno);
            return 1;
        }

        int result = send(remote_socket, request_buf, strlen(request_buf), 0);

        if (result == -1) {
            fprintf(stderr, "remote send() failed: (%d)\n", errno);
            return 1;
        }

        request_length = recv(remote_socket, response_buf, response_buf_length, 0);
        printf("Response: %s\n", response_buf);

        result = send(client_socket, response_buf, response_buf_length, 0);
        if (result == -1) {
            fprintf(stderr, "client send() failed: (%d)\n", errno);
            return 1;
        }

        close(remote_socket);
        close(client_socket);
    }

    printf("Closing connection...\n");
    close(server_socket);

    printf("Finished.\n");

    return 0;
}