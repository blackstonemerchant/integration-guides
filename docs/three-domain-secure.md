# Blackstone 3DS Service Integration Guide

This guide provides instructions for integrating 3DS authentication into your Blackstone payment system. The 3DS implementation uses an external service (3DS Integrator) for the client-side authentication process, while Blackstone provides the initial authentication credentials and handles the final payment processing with the SecureData.

## Overview

The 3DS integration process involves:

1. **Blackstone-specific**: Obtain authentication credentials from Blackstone API
2. **External service**: Use 3DS Integrator for client-side authentication challenge
3. **Blackstone-specific**: Include the resulting SecureData in your payment requests

## Blackstone-Specific Integration

### Step 1: Obtain API Credentials from Blackstone

Make a request to the Blackstone API to obtain an ApiKey and a Token, which are necessary for the 3DS Integrator service. It is recommended to make this request from the server side for increased security.

**POST:** [https://services.bmspay.com/api/auth/tokenthreeds](https://services.bmspay.com/api/auth/tokenthreeds)

**Sample Body:**

```json
{
  "mid": 76074,
  "UserName": "nicolas",
  "Password": "password1",
  "AppType": 1,
  "AppKey": "12345",
  "cid": "1"
}
```

**Sample Response:**

```json
{
  "ApiKey": "7763ffac3f08a0eca618a0f9d77c67c5",
  "Token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiIzZHNpbnRlZ3JhdG9yX0F1dGhlbnRpY2F",
  "ResponseCode": 200,
  "Msg": [
    "Operation Successful"
  ],
  "verbiage": null
}
```

## 3DS Integrator Implementation

**Important**: Steps 2 and 3 use the external 3DS Integrator service. For complete implementation details, refer to the official [3DS Integrator Documentation](https://docs.3dsintegrator.com).

### Step 2: Client-Side 3DS Authentication

Using the ApiKey and Token obtained from Blackstone, implement the client-side 3DS challenge using 3DS Integrator:

1. **Import the 3DS Integrator JavaScript library:**

    ```html
    <script src="https://cdn.3dsintegrator.com/threeds.2.2.20231219.min.js"></script>
    ```

2. **Instantiate the ThreeDS object** with:
   - Payment form ID
   - ApiKey (from Blackstone)
   - Token (from Blackstone)
   - Options object with `showChallenge: true`
   - Callback function to receive challenge response

**For detailed implementation**: See [3DS Integrator Documentation](https://docs.3dsintegrator.com) for complete ThreeDS object configuration and callback handling.

### Step 3: Configure Form Attributes

Add 3DS attributes to your payment form inputs to enable automatic data collection:

```html
<!-- Required attributes -->
<input type="text" name="x_amount" value="00" data-threeds="amount" />
<input type="text" name="x_card_num" value="0000000000000000" data-threeds="pan" />
<input type="text" name="x_exp_month" value="00" data-threeds="month" />
<input type="text" name="x_exp_year" value="00" data-threeds="year" />
```

**For complete attribute documentation**: Refer to [3DS Library Documentation](https://docs.3dsintegrator.com) for all available attributes and configuration options.

## Blackstone Payment Processing

### Step 4: Include SecureData and SecureTransactionId in Payment Requests

After the 3DS challenge completes successfully (status: "Y" or "A"), the callback will provide an `authenticationValue` containing the SecureData. Include this SecureData in your Blackstone payment API requests. In addition, you must also send the `SecureTransactionId`, which corresponds to the 3DS transaction identifier exposed by the library as `threeDsTransactionId` on the ThreeDS instance.

The `threeDsTransactionId` property is initially `null` immediately after instantiating the ThreeDS object. Once the challenge flow completes and SecureData (`authenticationValue`) is available, `threeDsTransactionId` will be populated. Capture it at the same time you read the SecureData value.

Example (simplified):

```html
<script src="https://cdn.3dsintegrator.com/threeds.2.2.20231219.min.js"></script>
<script>
  var tds = new ThreeDS("billing-form", "<ApiKey>", "<Token>", { showChallenge: true }, function (result) {
    // result.authenticationValue => SecureData
    if (result && (result.status === 'Y' || result.status === 'A')) {
      const secureData = result.authenticationValue; // send to Blackstone
      const secureTransactionId = tds.threeDsTransactionId; // now populated
      // Include BOTH secureData and secureTransactionId in your payment API request body
      // e.g., { SecureData: secureData, SecureTransactionId: secureTransactionId, ... }
    }
  });
</script>
```

Sending `SecureTransactionId` allows Blackstone Portal users to later view detailed 3DS logs for that transaction (useful for dispute resolution, fraud analysis, or support investigations).

**Key Response Properties from 3DS Challenge:**

- **status**: "Y" (passed) or "A" (attempted; treated as successful), "N/C/U" (failed)
- **authenticationValue**: Contains SecureData (when successful)
- **threeDsTransactionId / SecureTransactionId**: 3DS transaction identifier set on the ThreeDS instance (`tds.threeDsTransactionId`) once challenge completes; send this value to enable log retrieval.

Note: If you encounter the message "No result found for transaction as yet", this is not a validation error. It is emitted by the 3DS library as part of its internal polling flow while awaiting a final outcome. You should ignore this specific message and continue processing normally.

### Step 5: Testing

Use the test cards provided in the [3DS Integrator Test Cards Documentation](https://docs.3dsintegrator.com) to verify your integration works correctly across different scenarios.

## Go-Live (Production Domains)

**Important**: Before going live, you must contact the Blackstone team to configure your production domains in the 3DS service. You must provide the complete domain name(s) where your checkout or payment form is hosted. Each hostname must be configured explicitly; providing only the base domain is not sufficient. Examples that must be configured individually:

- `example.com`
- `www.example.com`
- `app.example.com`

## Summary

**Blackstone responsibilities:**

- Provide 3DS authentication credentials (Step 1)
- Process payments with SecureData and SecureTransactionId (Step 4+)

**3DS Integrator responsibilities:**

- Client-side authentication challenge (Steps 2-3)
- Generate SecureData and populate threeDsTransactionId upon successful authentication

**External documentation**: For complete 3DS implementation details, including advanced configurations and troubleshooting, refer to [docs.3dsintegrator.com](https://docs.3dsintegrator.com).
