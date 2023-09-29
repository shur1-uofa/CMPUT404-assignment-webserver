#  coding: utf-8 
import socketserver

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
debug = False 
webPageFolder = 'www'
webPagesPath = './www/'


class HTTPStatus:
    def __init__(self, value, phrase):
        self.value = value 
        self.phrase = phrase 

HTTP_OK = HTTPStatus(value = '200', phrase = 'OK')
HTTP_MOVED_PERMANENTLY = HTTPStatus(value = '301', phrase = 'Moved Permanently')
HTTP_BAD_REQUEST = HTTPStatus(value = '400', phrase = 'Bad Request')
HTTP_NOT_FOUND = HTTPStatus(value = '404', phrase = 'Not Found')
HTTP_METHOD_NOT_ALLOWED = HTTPStatus(value = '405', phrase = 'Method Not Allowed')


# ASSUMPTIONS:
# Valid HTTP request is sent
# Given URLs have valid syntax 


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        log(f"Received data : \n{self.data}\n")

        log(f"Handling HTTP Request")
        self.handleHTTPRequest()
    
    
    def handleHTTPRequest(self):
        self.httpData = HTTPRequest.parsePayload( self.data.decode('utf-8') )
        log(f'Parsed HTTP Request : \n{self.httpData}\n')
        match self.httpData.method:
            case 'GET':
                self.handleGetRequest()
            case _:
                self.sendHttpResponse( HTTP_METHOD_NOT_ALLOWED, { 
                    "Connection" : "close", 
                    "Allow" : "GET"     # No HEAD; outside of assignment spec
                })


    def handleGetRequest(self):
        if not isURLWithinWebDomain( self.httpData.contentURL ):
            self.sendNotFoundHTTPResponse()
            return 

        try:
            with open( self.httpData.contentURL ) as f:
                body, length, contentType = getContent( self.httpData.contentURL, f )
                self.sendHttpResponse( HTTP_OK, {
                    "Connection" : "close",
                    "Content-Type" : contentType, 
                    "Content-Length" : str( length )
                }, body)
        except IsADirectoryError:
            self.sendFolderRedirectResponse()
        except FileNotFoundError:
            self.sendNotFoundHTTPResponse()

    def sendFolderRedirectResponse(self):
        self.sendHttpResponse( HTTP_MOVED_PERMANENTLY, { 
            "Connection" : "close",
            "Location" : self.httpData.urlString + '/' 
        })

    def sendNotFoundHTTPResponse(self):
        body, length, contentType = getContent( './404.html' )
        self.sendHttpResponse( HTTP_NOT_FOUND, { 
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
    contentURL : str
    headers : dict

    def __init__(self, payload : str): 
        # NOTE: Ignoring body & protocol; not part of assignment spec
        self.method, _, payload = payload.partition(" ")
        self.urlString, _, payload = payload.partition(" ")
        self.contentURL = webPagesPath + self.urlString.removeprefix('/')
        payload = payload.partition("\r\n")[2]

        if self.urlString.endswith('/'):
            self.contentURL = self.contentURL + 'index.html'
            
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


def getContent(url : str, file = None):
    data = '' 
    length = -1
    contentType = ''
    if hasHtmlSuffix(url):
        contentType = 'text/html'
    elif hasCssSuffix(url):
        contentType = 'text/css'
    else:
        raise Exception("Unsupported content type")
    
    if file is None:
        with open(url, 'r') as file:
            data = file.read()
    else:
        data = file.read()
    # Not efficient way of doing it but I'm scared of using other libraries because apparently pathlib.Path isn't allowed. 
    length = len( data.encode('utf-8') )

    return (data, length, contentType)

def hasHtmlSuffix(url : str):
    return url.endswith('.html')

def hasCssSuffix(url : str):
    return url.endswith('.css')

# Assumes it is in form "./www{url}"
def isURLWithinWebDomain(url : str):
    # One consideration : should reject all URLs that nest outside ./www/ folder certain number of paths. (possibly even just once)
    # For example : if ./www/../../../app/group/content/www/content.html is accepted, then clients could possibly peek at the file structure of the web app
    
    # Or any ../ outside the ./www/ should be interpreted as a void operation. so ./www/../../../../../base.css maps to ./www/base.css
    

    # For my case, access to any folder that is not in ./www/ will be rejected
    # So any path deeper than './www' will be rejected since going back to the ./www directory 
    # would imply knowing the file structure outside the ./www directory 
    # It also makes this algorithm simpler to implement. 

    step, _, traversal = url.partition('./www')     # Remove './'
    depth = 0       # how deep into/away from ./www directory; negative for away, positive for in
    while '/' in traversal and depth >= -1:
        step, _, traversal = traversal.partition('/')
        
        if step == '..':
            depth -= 1
        else:
            # Allows edge case : ./www/../www. I don't think it should, but I don't know what the test cases are like
            if depth == -1 and step != 'www':
                break 
            depth += 1
        
    return depth >= 0

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