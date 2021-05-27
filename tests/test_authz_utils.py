import pytest

from lbz.authz import Authorizer, has_permission, ALL, LIMITED_ALLOW
from lbz.dev.test import Event
from lbz.resource import Resource
from tests import sample_private_key


class SampleResource(Resource):
    _name = "sample_resource"


class TestAuthorizationUtils:
    @pytest.mark.parametrize(
        "acl, expected_result",
        [
            (
                {"allow": {ALL: ALL}, "deny": {}},
                True,
            ),
            (
                {
                    "allow": {"sample_resource": {"sample_function": {"allow": LIMITED_ALLOW}}},
                    "deny": {},
                },
                True,
            ),
            (
                {
                    "allow": {ALL: ALL},
                    "deny": {"sample_resource": {"sample_function": {"deny": ALL}}},
                },
                False,
            ),
            (
                {
                    "allow": {"unknown_function": ALL},
                },
                False,
            ),
        ],
    )
    def test__has_permission__informs_if_request_user_has_access_to_permission(
        self, sample_event: Event, acl: dict, expected_result: bool
    ):

        authorization = Authorizer.sign_authz(acl, sample_private_key)
        sample_event["headers"]["authorization"] = authorization

        assert has_permission(SampleResource(sample_event), "sample_function") is expected_result
