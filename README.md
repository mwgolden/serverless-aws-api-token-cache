# Serverless API Token Cache

Retrieve and cache api tokens in DynamoDB. 

# Lambda Functions
- GetAPIAccessToken - Retrieves and caches a authentication token for an api using client credentials
- QueryRestAPIFunction - Obtains authentication token from GetAPIAccessToken and calls the api endpoint

# DynamoDB Tables
- ApiConfig - Stores configuration for a bot

```json
{
  "bot_name": "partition_key",
  "config": {
    "auth_endpoint": "url",
    "client_id" : "name of parameter in ssm",
    "client_secret": "name of parameter in ssm",
    "grant_type": "client_credentials",
    "http_method": "GET",
    "requires_authentication": true,
    "scope": "*",
    "user_agent": "user-agent-name"
  }
}
```
- ApiTokenCache - Stores the cached access token. An item's TTL is set to when the cached token expires.  

```json
{
  "bot_name": "partition_key",
  "expires": "sort_key",
  "access_token": {
    "access_token": "",
    "expires_in": "num_seconds",
    "scope": "*",
    "token_type": "Bearer"
  }
}
```