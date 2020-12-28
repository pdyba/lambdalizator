#!/usr/local/bin/python3.8
# coding=utf-8
"""
Dev Server.
"""
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
import json
import logging
import urllib.parse
from typing import Tuple, Union

from lbz.response import Response
from lbz.dev.misc import Event


class MyLambdaDevHandler(BaseHTTPRequestHandler):
    """
    Mimics AWS Lambda behavior.
    """

    cls = None
    done = False

    def _get_route_params(self, org_path: str) -> Tuple[Union[str, None], Union[dict, None]]:
        """
        Parses route and params.
        :param org_path:
        :return: standarised route, url params / None
        """
        router = self.cls._router
        if org_path in router:
            return org_path, None
        else:
            if org_path.find("?") != -1:
                org_path = org_path[: org_path.find("?")]
            path = org_path.split("/")
            path.remove("")
            for org_route in router:
                if org_route == "/":
                    continue
                route = org_route.split("/")
                route.remove("")
                if len(path) == len(route):
                    acc = 0
                    params = {}
                    for i, r in enumerate(route):
                        if r.startswith("{"):
                            acc += 1
                            param = path[i]
                            params[r.strip("{").strip("}")] = param
                        if r == path[i]:
                            acc += 1
                    if len(path) == acc:
                        return org_route, params
        return None, None  # to be raised

    def _send_json(self, code, obj, headers=None):
        # Make sure only one response is sent
        if self.done:
            return

        self.send_response(code, message=None)

        if headers:
            for key, value in headers.items():
                self.send_header(key, value)
        self.end_headers()

        self.done = True
        self.wfile.write(json.dumps(obj, indent=4, sort_keys=True).encode("utf-8"))

    def _error(self, code, message):
        content_type = "application/json;charset=UTF-8"
        self._send_json(code, {"error": message}, headers={"Content-Type": content_type})

    def handle_request(self):
        try:
            if self.path == "/favicon.ico":
                return
            self.done = False

            request_size = int(self.headers.get("Content-Length", 0))
            if request_size:
                request_body = self.rfile.read(request_size).decode(
                    encoding="utf_8", errors="strict"
                )
                request_obj = json.loads(request_body)
            else:
                request_obj = {}
            parsed_url = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_url.query, keep_blank_values=True)
            route, params = self._get_route_params(self.path)
            if route is None:
                return self._error(666, "Path not Found")
            resource = self.cls(
                Event(
                    resource_path=route,
                    method=self.command,
                    headers=self.headers,
                    path_params=params,
                    query_params=query_params,
                    body=request_obj,
                )
            )
            response = resource()
            code = response.status_code
            if isinstance(response, Response):
                response = response.to_dict()
                resp_headers = response.get("headers", {})
                if body := response.get("body"):
                    response = json.loads(body)
            else:
                logging.warning("Did not create a Response instance:")
                logging.warning(f"CLS: {self.cls} REQUEST: {request_obj} QParms: {query_params}")
                resp_headers = {}

            self._send_json(code, response, resp_headers)
        except Exception:
            logging.exception("Fail trying to send json")
        return self._error(500, "Server error")

    def do_GET(self):
        self.handle_request()

    def do_PATCH(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()

    def do_PUT(self):
        self.handle_request()

    def do_DELETE(self):
        self.handle_request()

    def do_OPTIONS(self):
        self.handle_request()


class MyDevServer:
    def __init__(self, acls=None, address="localhost", port=8000):
        class MyClassLambdaDevHandler(MyLambdaDevHandler):
            cls = acls

        self.my_handler = MyClassLambdaDevHandler
        self.address = address
        self.port = port
        self.server_address = (self.address, self.port)

    def run(self):
        print(f"serving on http://{self.server_address[0]}:{self.server_address[1]}")
        httpd = HTTPServer(self.server_address, self.my_handler)
        httpd.serve_forever()
