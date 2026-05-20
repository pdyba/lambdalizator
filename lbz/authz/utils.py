from lbz.authz.authorizer import Authorizer
from lbz.exceptions import PermissionDenied, Unauthorized
from lbz.resource import Resource


# TODO: Raise an Unauthorized exception when Auth tokens are missing but marked as required
def check_permission(resource: Resource, permission_name: str) -> dict:
    """Check if requester has sufficient permissions to do something on specific resource.

    Raises if not.
    """
    authorizer = Authorizer(
        # TODO: Cook the policy in the Resource (once) and use it as many times as needed
        #  (consider keeping the policy very close to the User who is under verification)
        # TODO: Do not allow using the Authorization header alone (without Authentication)
        auth_jwt=resource.request.headers.get("Authorization"),
        resource_name=resource.get_name(),
        permission_name=permission_name,
        base_permission_policy=resource.get_guest_authorization(),
    )
    authorizer.check_access()
    return authorizer.restrictions


def has_permission(resource: Resource, permission_name: str) -> bool:
    """Safe Check if requester has sufficient permissions to do something on specific resource.

    Does not raise.
    """
    try:
        check_permission(resource, permission_name)
    except (Unauthorized, PermissionDenied):
        return False
    return True
