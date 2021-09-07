from lbz.collector import AuthzCollector


class TestAuthzCollector:
    def setup_method(self) -> None:
        self.azc = AuthzCollector()  # pylint: disable=attribute-defined-outside-init

    def teardown_method(self) -> None:
        self.azc._del()  # pylint: disable=protected-access

    def test__singleton_only_one_exists(self) -> None:
        az_2 = AuthzCollector()

        assert self.azc == az_2

    def test__init__(self) -> None:
        assert self.azc.possible_permissions == {}
        assert self.azc.resource_name == ""
        assert self.azc.guest_permissions == {}

    def test_set_resource(self) -> None:
        test_resource = "test_resource"
        self.azc.set_resource(test_resource)

        assert self.azc.resource_name == test_resource

    def test_set_guest_permissions(self) -> None:
        guest_permissions = {"allow": "*"}
        self.azc.set_guest_permissions(guest_permissions)

        assert self.azc.guest_permissions == guest_permissions

    def test_add_authz(self) -> None:
        some_permission = "some_permission"
        self.azc.add_authz(some_permission)

        assert self.azc.possible_permissions == {some_permission: None}

    def test_dump(self) -> None:
        test_resource = "x_resource"
        self.azc.set_resource(test_resource)
        guest_permissions = {"allow": "*", "deny": "root"}
        self.azc.set_guest_permissions(guest_permissions)
        some_permission = "x_permission"
        self.azc.add_authz(some_permission)

        assert self.azc.dump() == {
            test_resource: {
                "possible_permissions": {some_permission: None},
                "guest_permissions": guest_permissions,
            }
        }
