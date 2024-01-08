from lbz.collector import AuthzCollector


class TestAuthzCollector:
    def test__singleton_only_one_exists(self) -> None:
        azc = AuthzCollector()
        az_2 = AuthzCollector()

        assert azc == az_2

    def test__init__(self) -> None:
        azc = AuthzCollector()
        assert azc.possible_permissions == {}
        assert azc.resource_name == ""
        assert azc.guest_permissions == {}

    def test_set_resource(self) -> None:
        azc = AuthzCollector()
        test_resource = "test_resource"
        azc.set_resource(test_resource)

        assert azc.resource_name == test_resource

    def test_set_guest_permissions(self) -> None:
        azc = AuthzCollector()
        guest_permissions = {"allow": "*"}
        azc.set_guest_permissions(guest_permissions)

        assert azc.guest_permissions == guest_permissions

    def test_add_authz(self) -> None:
        azc = AuthzCollector()
        some_permission = "some_permission"
        azc.add_authz(some_permission)

        assert azc.possible_permissions == {some_permission: None}

    def test_dump(self) -> None:
        azc = AuthzCollector()
        test_resource = "x_resource"
        azc.set_resource(test_resource)
        guest_permissions = {"allow": "*", "deny": "root"}
        azc.set_guest_permissions(guest_permissions)
        some_permission = "x_permission"
        azc.add_authz(some_permission)

        assert azc.dump() == {
            test_resource: {
                "possible_permissions": {some_permission: None},
                "guest_permissions": guest_permissions,
            }
        }

    def test_clean(self) -> None:
        azc = AuthzCollector()
        guest_permissions = {"allow": "*"}
        azc.set_guest_permissions(guest_permissions)
        test_resource = "test_resource"
        azc.set_resource(test_resource)
        some_permission = "some_permission"
        azc.add_authz(some_permission)

        assert azc.possible_permissions == {some_permission: None}
        assert azc.resource_name == test_resource
        assert azc.guest_permissions == guest_permissions

        azc.clean()

        assert azc.possible_permissions == {}
        assert azc.resource_name == ""
        assert azc.guest_permissions == {}
