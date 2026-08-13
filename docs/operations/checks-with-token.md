---
title: Check Payments with Token
---

## Overview

This guide explains how to process check payments using a reusable token. The flow is:

1) Process a regular check and request to save a token.
2) Use the returned token to process future check payments without sending sensitive bank details again.

> Tokens are merchant-scoped and should be stored securely on your side for reuse.

## Step 1: Process a check and request token creation

- Endpoint: POST /CheckProcessor/ProcessCheck
- Purpose: Authorize a check using account details and request token creation by setting `SaveToken = true`.

### Request body

```json
{
  "AppKey": "your-app-key",
  "UserName": "api-user",
  "Password": "api-pass",
  "mid": 123456,
  "PacketIdentifier": "R",
  "Method": 0,
  "ROUTING_NUMBER": "011000015",
  "ACCOUNT_NUMBER": "000123456789",
  "CHECK_NUMBER": "1001",
  "CHECK_AMOUNT": "25.50",
  "FIRST_NAME": "John",
  "LAST_NAME": "Doe",
  "ADDRESS1": "123 Main St",
  "CITY": "Miami",
  "STATE": "FL",
  "ZIP": "33101",
  "PHONE_NUMBER": "3055550000",
  "SaveToken": true
}
```

### Successful response example

```json
{
  "ResponseCode": 200,
  "Message": "APPROVED",
  "Code": "ABC123",
  "Token": "3b6a1b37-6d3c-4b9c-8df9-84a8f9a4d2ab",
  "TransactionInfo": {
    "ServiceTransactionNumber": "..."
  }
}
```

- Notes
  - `Token` is returned only when the transaction is approved and token creation succeeds.
  - `CHECK_AMOUNT` must be a string with a valid decimal (e.g., "10.00").

## Step 2: Process a check using a token

- Endpoint: POST /CheckProcessor/ProcessToken
- Purpose: Charge a check payment using a previously saved token. Only `Token` and `CHECK_AMOUNT` are required; `CHECK_NUMBER` is optional.

### Request body

```json
{
  "AppKey": "your-app-key",
  "UserName": "api-user",
  "Password": "api-pass",
  "mid": 123456,
  "Token": "3b6a1b37-6d3c-4b9c-8df9-84a8f9a4d2ab",
  "CHECK_AMOUNT": "25.50",
  "CHECK_NUMBER": "1002"
}
```

### Successful response

The response structure matches the regular check response (e.g., `ResponseCode = 200` on success).

## Error handling

- `ResponseCode = 1`: Invalid credentials
- `ResponseCode = 11`: Merchant not authorized for this operation
- `ResponseCode = 14`: Invalid/expired/inactive token
- `ResponseCode = 19`: Incorrect data type for `CHECK_AMOUNT`

## Best practices

- Store tokens securely and associate them with your customer profiles.
- Log the `ServiceTransactionNumber` from `TransactionInfo` for reconciliation.
- Do not log or store routing/account numbers if you plan to reuse a token.
