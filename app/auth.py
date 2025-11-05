import requests
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose.jwt import decode, get_unverified_header

from app.config import settings

security = HTTPBearer()


def get_keycloak_jwks():
    """Retrieve JSON Web Key Set (JWKS) from Keycloak OIDC provider.

    Fetches the well-known OIDC configuration from the configured URL
    and retrieves the JWKS containing public keys for JWT validation.

    Returns:
        list: List of JSON Web Keys from the OIDC provider.

    Raises:
        HTTPException: If OIDC_CONFIG_URL is not configured or request fails.
    """
    keycloak_well_known_url = settings.OIDC_CONFIG_URL

    if not keycloak_well_known_url:
        raise HTTPException(
            status_code=500,
            detail="OIDC_CONFIG_URL is not configured",
        )

    try:
        response = requests.get(keycloak_well_known_url, timeout=5)
        response.raise_for_status()
        well_known_config = response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch OIDC configuration: {e!s}",
        ) from e
    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid JSON response from OIDC provider: {e!s}",
        ) from e

    try:
        jwks_url = well_known_config["jwks_uri"]
        jwks_response = requests.get(jwks_url, timeout=5)
        jwks_response.raise_for_status()
        jwks = jwks_response.json()
        return jwks["keys"]
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch JWKS: {e!s}",
        ) from e
    except (ValueError, KeyError) as e:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid JWKS response: {e!s}",
        ) from e


def validate_jwt(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Validate a JSON Web Token (JWT) using JWKS from the OIDC provider.

    Extracts the key ID from the JWT header, finds the matching RSA key
    in the JWKS, and decodes/validates the token.

    Args:
        credentials: HTTP Authorization credentials containing the JWT token.

    Returns:
        dict: Decoded JWT payload containing user claims.

    Raises:
        HTTPException: If RSA key is not found (401) or JWT is invalid (401).
    """
    token = credentials.credentials

    try:
        header = get_unverified_header(token)
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid JWT token format: {e!s}",
        ) from e

    jwks = get_keycloak_jwks()

    # Find the RSA key with the matching kid in the JWKS
    rsa_key = None
    for key in jwks:
        if key.get("kid") == header.get("kid"):
            rsa_key = {
                "kty": key.get("kty"),
                "kid": key.get("kid"),
                "use": key.get("use"),
                "n": key.get("n"),
                "e": key.get("e"),
            }
            break

    if rsa_key is None:
        # Provide helpful debugging information
        available_kids = [key.get("kid") for key in jwks]
        token_kid = header.get("kid")
        raise HTTPException(
            status_code=401,
            detail=(
                f"RSA Key not found in JWKS. Token kid: {token_kid}, "
                f"Available kids: {available_kids}"
            ),
        )

    try:
        payload = decode(token, rsa_key, algorithms=[header["alg"]])
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid JWT token: {e!s}",
        ) from e

    return payload
