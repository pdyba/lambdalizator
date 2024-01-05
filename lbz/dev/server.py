from __future__ import annotations

import json
import logging
import urllib.parse
from abc import ABCMeta, abstractmethod
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from os import environ
from threading import Thread

from lbz.dev.misc import APIGatewayEvent
from lbz.resource import Resource

if environ.get("LBZ_DEBUG_MODE") is None:
    environ["LBZ_DEBUG_MODE"] = "true"


class MyLambdaDevHandler(BaseHTTPRequestHandler, metaclass=ABCMeta):
    """Mimics AWS Lambda behavior."""

    done: bool = False  # TODO: if possible move to __init__

    @property
    @abstractmethod
    def cls(self) -> type[Resource]:
        pass

    def _get_route_params(self, org_path: str) -> tuple[str | None, dict | None]:  # noqa:C901
        """Parses route and params.

        :param org_path:
        :return: standardised route, url params / None
        """
        router = self.cls._router  # pylint: disable=protected-access
        if org_path in router:
            return org_path, None
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
                for i, route_part in enumerate(route):
                    if route_part.startswith("{"):
                        acc += 1
                        param = path[i]
                        params[route_part.strip("{").strip("}")] = param
                    if route_part == path[i]:
                        acc += 1
                if len(path) == acc:
                    return org_route, params
        return None, None

    def _send_json(self, code: int, obj: dict, headers: dict | None = None) -> None:
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

    def _error(self, code: int, message: str) -> None:
        content_type = "application/json;charset=UTF-8"
        self._send_json(code, {"error": message}, headers={"Content-Type": content_type})

    def handle_request(self) -> None:
        """Main method for handling all incoming requests."""
        try:
            if self.path == "/favicon.ico":
                return
            self.done = False

            if request_size := int(self.headers.get("Content-Length", 0)):
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
                self._error(666, "Path not Found")
                return
            resource = self.cls(
                APIGatewayEvent(
                    resource_path=route,
                    method=self.command,
                    headers=self.headers,  # type: ignore
                    path_params=params,
                    query_params=query_params,
                    body=request_obj,
                )
            )
            response = resource()
            code = response.status_code
            response_as_dict = response.to_dict()
            resp_headers = response_as_dict.get("headers", {})
            if body := response_as_dict.get("body"):
                response_as_dict = json.loads(body)
            else:
                response_as_dict = {}
            self._send_json(code, response_as_dict, resp_headers)
        except Exception:  # pylint: disable=broad-except
            logging.exception("Fail trying to send json")
        self._error(500, "Server error")

    def do_GET(self) -> None:  # pylint: disable=invalid-name
        self.handle_request()

    def do_PATCH(self) -> None:  # pylint: disable=invalid-name
        self.handle_request()

    def do_POST(self) -> None:  # pylint: disable=invalid-name
        self.handle_request()

    def do_PUT(self) -> None:  # pylint: disable=invalid-name
        self.handle_request()

    def do_DELETE(self) -> None:  # pylint: disable=invalid-name
        self.handle_request()

    def do_OPTIONS(self) -> None:  # pylint: disable=invalid-name
        self.handle_request()


class MyDevServer(Thread):
    def __init__(
        self,
        acls: type[Resource],
        address: str = "localhost",
        port: int = 8000,
    ) -> None:
        class MyClassLambdaDevHandler(MyLambdaDevHandler):
            cls: type[Resource] = acls

        super().__init__()
        self.my_handler = MyClassLambdaDevHandler
        self.address = address
        self.port = port
        self.server_address = (self.address, self.port)
        self.httpd = ThreadingHTTPServer(self.server_address, self.my_handler)
        print(f"server bound to port: {self.port}")

    def run(self) -> None:
        """Start the server in the foreground."""
        print(f"serving on http://{self.address}:{self.port}")
        self.httpd.serve_forever()

    def stop(self) -> None:
        self.httpd.shutdown()
        self.httpd.server_close()
        print(f"Server stopped and port {self.port} released")

    def start(self) -> None:  # pylint: disable=useless-super-delegation
        """Start the server in the background"""
        super().start()
