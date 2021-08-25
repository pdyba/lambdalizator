from lbz.misc import Singleton


class AuthzCollector(metaclass=Singleton):
    # TODO: Add uni tests
    def __init__(
        self,
    ) -> None:
        self.possible_permissions: list = []
        self.resource = ""
        self.guest_permissions: dict = {}

    def set_resource(self, resource_name: str) -> None:
        self.resource = resource_name

    def set_guest_permissions(self, guest_permissions: dict) -> None:
        self.guest_permissions = guest_permissions

    def add_authz(self, permission: str) -> None:
        self.possible_permissions.append(permission)

    def dump(self) -> dict:
        return {
            self.resource: {
                "possible_permissions": self.possible_permissions,
                "guest_permissions": self.guest_permissions,
            }
        }
