# coding=utf-8
from http import HTTPStatus
from unittest.mock import patch, MagicMock

import pytest

from lbz.authz.decorators import authorization
from lbz.resource import Resource


class TestAuthorizationDecorator:
    @patch("lbz.authz.decorators.authz_collector")
    def test_authz_collectore_called(self, mocked_authzc_ollector: MagicMock) -> None:
        class XResource(Resource):  # pylint: disable=unused-variable
            _name = "test_res"

            @authorization("perm-name")
            def handler(self, restrictions) -> None:
                pass

        mocked_authzc_ollector.add_authz.assert_called_once()

    def test_root_permissions_success(
        self, sample_resoruce_with_authorization, sample_event_with_full_access_auth_header
    ) -> None:
        res_instance = sample_resoruce_with_authorization(
            sample_event_with_full_access_auth_header
        )
        assert res_instance().status_code == HTTPStatus.OK

    @pytest.mark.parametrize(
        "sample_event_with_limited_access_auth_header",
        [{"path": "/"}],
        indirect=True,
    )
    def test_limited_permissions_success(
        self, sample_event_with_limited_access_auth_header, sample_resoruce_with_authorization
    ) -> None:
        res_instance = sample_resoruce_with_authorization(
            sample_event_with_limited_access_auth_header
        )
        assert res_instance().status_code == HTTPStatus.OK

    @pytest.mark.parametrize(
        "sample_event_with_limited_access_auth_header",
        [{"path": "/garbage"}],
        indirect=True,
    )
    def test_limited_permissions_failed(
        self, sample_event_with_limited_access_auth_header, sample_resoruce_with_authorization
    ) -> None:
        res_instance = sample_resoruce_with_authorization(
            sample_event_with_limited_access_auth_header
        )
        assert res_instance().status_code == HTTPStatus.FORBIDDEN
