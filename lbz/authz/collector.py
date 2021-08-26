from lbz.misc import Singleton


class AuthzCollector(metaclass=Singleton):
    def __init__(self) -> None:
        self.possible_permissions: dict = {}
        self.resource_name = ""
        self.guest_permissions: dict = {}

    def set_resource(self, resource_name: str) -> None:
        self.resource_name = resource_name

    def set_guest_permissions(self, guest_permissions: dict) -> None:
        self.guest_permissions = guest_permissions

    def add_authz(self, permission_name: str) -> None:
        self.possible_permissions[permission_name] = None

    def dump(self) -> dict:
        return {
            self.resource_name: {
                "possible_permissions": self.possible_permissions,
                "guest_permissions": self.guest_permissions,
            }
        }


authz_collector = AuthzCollector()
