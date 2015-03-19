#    Copyright 2015 Mirantis, Inc
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


class BaseHTTPException(Exception):

    def __init__(self, message=None,
                 http_code=400, **kwargs):
        self.message = (message % kwargs
                        if message else self.message)
        self.http_code = http_code
        self.reason = "HTTP Code: %d." % http_code
        super(BaseHTTPException, self).__init__(self.message + self.reason)


class BadRequest(BaseHTTPException):
    http_code = 400
    message = "Bad request. "


class NotFound(BaseHTTPException):
    http_code = 404
    message = "Not Found. "


class ConnectionRefused(BaseHTTPException):
    http_code = 111
    message = "Server shutdowned. "

exception_mapping = {
    111: ConnectionRefused,
    404: NotFound,
    400: BadRequest
}
