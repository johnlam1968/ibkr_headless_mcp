# IBKR Headless MCP Server

This project provides an MCP (Model Context Protocol) server and tools for Interactive Brokers (IBKR) via ibind library.

Using ibind's oauth feature, this headless application runs independent of a IBKR TWS/gateway or helper java program.

## Features

Instead of wrapping on ibind's method, now an endpoint mcp server is available: a LLM agent parses the documentation and uses the get method to retrieve information for an end user.

## Prerequisites
1. **IBKR Account**: Paper/live trading account with API access enabled.
3. **oauth files stored in local folder. Refer to https://github.com/Voyz/ibind/wiki/OAuth-1.0a

## Quick Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Create .env with following lines
IBIND_USE_OAUTH=True
IBIND_OAUTH1A_CONSUMER_KEY=""
IBIND_OAUTH1A_ENCRYPTION_KEY_FP="path-to/private_encryption.pem"
IBIND_OAUTH1A_SIGNATURE_KEY_FP="path-to/private_signature.pem"
IBIND_OAUTH1A_ACCESS_TOKEN=""
IBIND_OAUTH1A_ACCESS_TOKEN_SECRET=""
IBIND_OAUTH1A_DH_PRIME='prime_hex'

## Reference
https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#endpoints
