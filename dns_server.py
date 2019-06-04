import socket


class dnsRequest(object):
    """Representation of a dnsRequest"""
    
    def __init__(self, data):
        self.raw_data = data
        #self.transaction_id = [hex(ord(i)) for i in data[0:2]]
        self.transaction_id = data[0:2]
        self.flags = data[2:4]
        self.questions = data[4:6]
        self.answer_rr = data[6:8]
        self.authority_rr = data[8:10]
        self.additional_rr = data[10:12]
        self.queries = dict()
        self.name_terminator_index = data[12:].find(b"\x00")+12
        self.queries["Name"] = self.setHostname()
        self.queries["Type"] = data[self.name_terminator_index:self.name_terminator_index+2]
        self.queries["Class"] = data[self.name_terminator_index+2:self.name_terminator_index+4]

    def setHostname(self):
        current_index = 12
        current_length = self.raw_data[current_index]
        hostname = list()
        while current_length != 0:
            print(type(current_index))
            print(type(current_length))
            print(current_length)
            print(hostname)
            hostname.append(self.raw_data[current_index+1:current_index+current_length+1])
            current_index += current_length + 1
            current_length = self.raw_data[current_index]
        print(current_index)
        self.name_terminator_index = current_index
        return b".".join(hostname)

    def getHostname(self):
        return self.queries["Name"]
    
    def getType(self):
        return self.queries["Type"]

    def printHex(self):
        for i in self.raw_data:
            print(hex(ord(i)))

if __name__ == '__main__':
    HOST = ''
    TCP_PORT = 53
    UDP_PORT = 53

    udpserver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpserver.bind((HOST, UDP_PORT))

    while True:
        data, address = udpserver.recvfrom(1024)
        if address:
            print("Start request: ", address)
        if data:
            request = dnsRequest(data)
            print("Transaction ID: ", request.transaction_id)
            print("Flags: ", request.flags)
            print("Name: ", request.getHostname())
            print("Type: ", request.getType())
            #sent = udpserver.sendto(data, address)
            print("End request: ", address)

