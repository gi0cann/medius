import socket
import struct


class dnsRequest(object):
    """Representation of a dnsRequest"""
    
    def __init__(self, data=None):
        if data:
            self.raw_data = data
            self.transaction_id = data[0:2]
            self.flags = data[2:4]
            self.questions = data[4:6]
            self.answer_rr = data[6:8]
            self.authority_rr = data[8:10]
            self.additional_rr = data[10:12]
            self.queries_raw = data[12:]
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
        self.name_terminator_index = current_index + 1
        return b".".join(hostname)

    def getHostname(self):
        return self.queries["Name"]
    
    def getType(self):
        return self.queries["Type"]

    def printHex(self):
        for i in self.raw_data:
            print(hex(ord(i)))


class dnsResponse(object):
    """Representation of a dnsResponse"""

    def __init__(self, data=None, transaction_id=None, flags=None, questions=None, answer_rr=None, authority_rr=None, additional_rr=None, queries=dict(), answers=dict()):
        if data:
            self.raw_data = data
            self.transaction_id = data[0:2]
            self.flags = data[2:4]
            self.questions = data[4:6]
            self.answer_rr = data[6:8]
            self.authority_rr = data[8:10]
            self.additional_rr = data[10:12]
            self.queries_raw = data[12:]
            self.queries = dict()
            self.name_terminator_index = data[12:].find(b"\x00")+12
            self.queries["Name"] = self.setHostname()
            self.queries["Type"] = data[self.name_terminator_index:self.name_terminator_index+2]
            self.queries["Class"] = data[self.name_terminator_index+2:self.name_terminator_index+4]
        else:
            self.transaction_id = transaction_id
            self.flags = flags
            self.questions = questions
            self.answer_rr = answer_rr
            self.authority_rr = authority_rr
            self.additional_rr = additional_rr
            self.queries = queries
            self.answers = answers
    
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

    def setAddress(self, ip_address):
        self.answers["Address"] = struct.pack(">BBBB", *[int(i) for i in ip_address.split(".")])
    
    def getResponsedata(self):
        self.raw_data = b""
        self.raw_data += self.transaction_id
        self.raw_data += self.flags
        self.raw_data += self.questions
        self.raw_data += self.answer_rr
        self.raw_data += self.authority_rr
        self.raw_data += self.additional_rr
        self.raw_data += self.queries_raw
        self.raw_data += self.answers["Name"]
        self.raw_data += self.answers["Type"]
        self.raw_data += self.answers["Class"]
        self.raw_data += self.answers["TTL"]
        self.raw_data += self.answers["Data_length"]
        self.raw_data += self.answers["Address"]
        return self.raw_data

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
    hosts = [b"pbanner.gi0cann.io"]

    udpserver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpserver.bind((HOST, UDP_PORT))

    while True:
        data, address = udpserver.recvfrom(1024)
        if address:
            print("Start request: ", address)
        if data:
            request = dnsRequest(data)
            hostname = request.getHostname()
            resolved_address = "10.0.0.141"
            print("Transaction ID: ", request.transaction_id)
            print("Flags: ", request.flags)
            print("Name: ", hostname)
            print("Type: ", request.getType())
            print("End request: ", address)
            print("Start response: ", address)
            if hostname not in hosts:
                resolved_address = socket.gethostbyname(hostname)
            print("Resolved Address: ", resolved_address)
            response = dnsResponse()
            response.transaction_id = request.transaction_id
            response.flags = struct.unpack(">H", request.flags)[0] + 0x8080
            response.flags = struct.pack(">H", response.flags)
            print("Response flags: ", response.flags)
            response.questions = request.questions
            response.answer_rr = struct.pack(">H", 0x0001)
            response.authority_rr = request.authority_rr
            response.additional_rr = request.additional_rr
            response.queries_raw = request.queries_raw
            response.queries = request.queries
            response.answers["Name"] = struct.pack(">H", 0xc00c)
            response.answers["Type"] = request.queries["Type"]
            response.answers["Class"] = struct.pack(">H", 0x0001)
            response.answers["TTL"] = struct.pack(">I", 0x000000ee)
            response.answers["Data_length"] = struct.pack(">H", 0x0004)
            response.setAddress(resolved_address)
            response_data = response.getResponsedata()
            sent = udpserver.sendto(response_data, address)
            print("End response: ", address)

