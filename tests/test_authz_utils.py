# coding=utf-8

import pytest

from lbz.authz.authorizer import ALL, LIMITED_ALLOW
from lbz.authz.decorators import has_permission
from lbz.dev.test import Event
from lbz.resource import Resource
from unittest.mock import patch

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
        self,
        sample_event: Event,
        acl: dict,
        expected_result: bool,
        base_auth_payload,
    ):
        sample_event["headers"]["authorization"] = "dont_care"

        with patch("lbz.authz.authorizer.decode_jwt", lambda _: {**base_auth_payload, **acl}):
            assert has_permission(SampleResource(sample_event), "sample_function") is expected_result
