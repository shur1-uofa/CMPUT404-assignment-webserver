#  coding: utf-8 
import socketserver
# This just imports HTTP status code & text constants, so I don't have to write the enums myself
from http import HTTPStatus
from pathlib import Path

# Copyright 2023 Scott Hur
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 
#
# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

# Sets logging to console 
debug = True 
webPagesPath = Path('./www/')


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        log(f"Received data : \n{self.data}\n")

        if isInvalidHTTPSyntax( self.data ):
            log(f"Invalid HTTP Request\n")
            self.sendHttpResponse( HTTPStatus.BAD_REQUEST )
        else:
            log(f"Handling HTTP Request")
            self.handleHTTPRequest()
    
    
    def handleHTTPRequest(self):
        self.httpData = HTTPRequest.parsePayload( self.data.decode('utf-8') )
        log(f'Parsed HTTP Request : \n{self.httpData}\n')
        match self.httpData.method:
            case 'GET':
                self.handleGetRequest()
            case _:
                self.sendHttpResponse( HTTPStatus.METHOD_NOT_ALLOWED, { 
                    "Connection" : "close", 
                    "Allow" : "GET"     # No HEAD; outside of assignment spec
                })


    def handleGetRequest(self):
        if isFolder( self.httpData.contentURL ):
            self.sendHttpResponse( HTTPStatus.MOVED_PERMANENTLY, { 
                "Connection" : "close",
                "Location" : self.httpData.urlString + '/' 
            })
        elif not isExistingFile( self.httpData.contentURL ) or not isURLAllowed( self.httpData.contentURL ):
            body, length, contentType = getContent( Path('./404.html') )
            self.sendHttpResponse( HTTPStatus.NOT_FOUND, { 
                "Connection" : "close",
                "Content-Type" : contentType, 
                "Content-Length" : str( length )
            }, body)
        else:
            body, length, contentType = getContent( self.httpData.contentURL )
            self.sendHttpResponse( HTTPStatus.OK, {
                "Connection" : "close",
                "Content-Type" : contentType, 
                "Content-Length" : str( length )
            }, body)


    def sendHttpResponse(self, httpStatus, headers = {}, body = ""):
        log(f"Sending HTTP Response : {httpStatus.phrase}")

        httpResp = HTTPResponse( httpStatus, headers, body )
        self.request.sendall( httpResp.toPayload() )
        
        log(f"Sent HTTP Response : \n{ httpResp.toPayload() }\n")
        log('================================================\n\n')
    

class HTTPRequest:
    method : str
    urlString : str
    contentURL : Path
    headers : dict

    def __init__(self, payload : str): 
        if isInvalidHTTPSyntax( payload ):
            raise Exception("Given payload is not an HTTP message")
        # NOTE: Ignoring body & protocol; not part of assignment spec
        self.method, _, payload = payload.partition(" ")
        self.urlString, _, payload = payload.partition(" ")
        self.contentURL = webPagesPath / self.urlString.removeprefix('/')
        payload = payload.partition("\r\n")[2]

        if self.urlString.endswith('/'):
            self.contentURL = self.contentURL / 'index.html'
            
        self.headers = {}
        for line in payload.split("\r\n"):
            if line != "":
                header = line.split(':')
                self.headers[header[0]] = header[1].strip()
            else:
                break
    
    def __str__(self):
        return f"{self.method} {self.urlString}\n{self.contentURL}\n{self.headers}\n"

    @staticmethod
    def parsePayload(payload : str):
        return HTTPRequest(payload)
    

class HTTPResponse:
    statusCode : str
    statusText : str
    headers : dict
    body : str   

    def __init__(self, httpStatus, headers = {}, body = ''):
        self.statusCode = httpStatus.value
        self.statusText = httpStatus.phrase
        self.headers = headers
        self.body = body

    def toPayload(self):
        # This is quadratic time; MutableStringBuilder might be needed for larger strings
        res = f"HTTP/1.1 {self.statusCode} {self.statusText}\r\n"
        for header, value in self.headers.items():
            res += f'{header}: {value}\r\n'
        if len(self.body.strip()) > 0:
            res += f'\n{self.body}'
        return bytearray(res, 'utf-8')


def getContent(url : Path):
    data = '' 
    length = -1
    contentType = ''
    match url.suffix:
        case ".html":
            contentType = 'text/html'
        case ".css":
            contentType = 'text/css'
        case _:
            raise Exception("Unsupported content type")
      
    with url.open('r') as file:
        data = file.read()
    length = url.stat().st_size

    return (data, length, contentType)

# NOTE: Not part of requirements; Assumes valid HTTP thus returns False 
def isInvalidHTTPSyntax(payload : str):
    return False

def isFolder(url : Path):
    return Path.is_dir( url )

def isURLAllowed(url : Path):
    return webPagesPath.resolve() in url.resolve().parents

def isExistingFile(url : Path):
    return Path.is_file( url )

def log(str):
    if debug:
        print(str)



if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()