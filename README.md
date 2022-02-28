# CODAPI Wrapper Written in Python

### Initial Setup
```
from codapi_py import CODAPI

# Initialize
codapi = CODAPI(sso_token="",cookies={},headers={},proxies=[])

## Example Endpoints
# WZ Profile
data=codapi.MWwz(gamertag,platform)

# WZ Matches
data=codapi.MWcombatwz(gamertag,platform)
```
