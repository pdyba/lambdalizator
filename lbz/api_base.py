from typing import Any


class APIBase:
    def react(self) -> Any:
        self.pre_handle()
        response = self.handle()
        self.post_handle()
        return response

    def handle(self) -> Any:
        pass

    def pre_handle(self) -> None:
        pass

    def post_handle(self) -> None:
        pass
