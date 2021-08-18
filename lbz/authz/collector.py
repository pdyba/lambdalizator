from lbz.misc import Singleton


class AuthCollector(metaclass=Singleton):
    # TODO: Add uni tests
    def __init__(self) -> None:
        self.possible_authz: list = []

    def add_authz(self, permission: str) -> None:
        self.possible_authz.append(permission)

    def dump_authz(self, resource: str, guest_permissions: dict) -> dict:
        return {resource: self.possible_authz, "guest_permissions": guest_permissions}


authz_collector = AuthCollector()
