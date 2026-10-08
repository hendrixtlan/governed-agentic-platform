from typing import Annotated

from fastapi import Header

from agentic_platform.auth.context import Principal


async def authenticate_demo(
    x_user_id: Annotated[str, Header(alias="X-User-Id")] = "demo-user",
    x_tenant_id: Annotated[str, Header(alias="X-Tenant-Id")] = "ACME",
    x_roles: Annotated[str, Header(alias="X-Roles")] = "analyst,ops_manager",
) -> Principal:
    """Development-only identity provider.

    Production: validate OIDC/JWT and resolve tenant/roles from trusted claims
    or an enterprise authorization service.
    """
    roles = tuple(role.strip() for role in x_roles.split(",") if role.strip())
    return Principal(user_id=x_user_id, tenant_id=x_tenant_id, roles=roles)
