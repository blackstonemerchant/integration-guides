# Apple Pay iOS Integration

## Overview

This guide describes how to integrate Apple Pay with the Bpayd API for **iOS** using PassKit. It covers the merchant ID setup, front-end implementation, and the backend payment flow.

The integration involves two main components:

1. **Front-end (iOS)**: Collecting the Apple Pay payment token using PassKit
2. **Back-end**: Sending the Apple Pay token to the Bpayd API for payment processing

There is no domain verification or merchant validation step for iOS — you go directly to payment authorization.

## Prerequisites

Before you begin, make sure you have:

- **Bpayd API Credentials**: Provided by Bpayd/Blackstone for your integration:
  - `AppKey`: Application Key that uniquely identifies your application
  - `AppType`: Application Type identifier
  - `UserName`: API username
  - `Password`: API password
  - `mid`: Merchant ID
  - `cid`: Cashier ID
- **Apple Pay enablement from Bpayd**: Apple Pay is enabled for your merchant in Bpayd.
- **Apple Developer Program account** with Apple Pay capability enabled in Xcode.
- **Your own Apple Pay Merchant ID** registered in your Apple Developer account (see [Merchant ID Setup](#merchant-id-setup) below).
- **Payment Processing Certificate** created using the Bpayd CSR (see [Merchant ID Setup](#merchant-id-setup) below).
- **Test device** with Apple Pay set up (or Apple Pay sandbox test cards).
- Official iOS documentation:
  - Setting up Apple Pay: <https://developer.apple.com/documentation/passkit/setting-up-apple-pay>
  - Offering Apple Pay in your app: <https://developer.apple.com/documentation/passkit/offering-apple-pay-in-your-app>

## Integration Flow

The complete Apple Pay in-app flow consists of these steps:

1. The customer taps the Apple Pay button in your iOS app.
2. Your app builds a `PKPaymentRequest` and presents a `PKPaymentAuthorizationController`.
3. The customer authorizes the payment with Face ID, Touch ID, or passcode.
4. iOS returns a payment token (`payment.token.paymentData`).
5. Your app sends the payment token to your back-end.
6. Your back-end Base64-encodes the token and calls the Bpayd API `SaleWithApplePay` endpoint with your `MerchantIdentifier`.
7. Bpayd processes the payment and returns the result.
8. Your app displays the payment result to the customer.

## Responsibilities

### Bpayd provides

- Bpayd API credentials (`AppKey`, `AppType`, `UserName`, `Password`, `mid`, `cid`).
- CSR (Certificate Signing Request) for creating your Payment Processing Certificate.
- API endpoint for `SaleWithApplePay` (Apple Pay sale processing).

### Your application is responsible for

- Creating your own Apple Pay Merchant ID and Payment Processing Certificate using the Bpayd CSR (see [Merchant ID Setup](#merchant-id-setup)).
- Enabling Apple Pay capability and adding your merchant identifier in Xcode.
- Building the Apple Pay in-app flow with PassKit (`PKPaymentRequest`, `PKPaymentAuthorizationController`).
- Forwarding the Apple Pay token (`payment.token.paymentData`) to your back-end exactly as received from Apple.
- Base64-encoding the token on the back-end before sending it to Bpayd.
- Including `MerchantIdentifier` (your own merchant ID) in the `SaleWithApplePay` request.
- Generating a unique `UserTransactionNumber` for each transaction.

## Merchant ID Setup

For in-app Apple Pay, you must use your own Apple Pay Merchant ID registered in your Apple Developer account. This is required because Apple ties the merchant identifier to your app's code signing entitlements, which must belong to your own Apple Developer Team.

### 1. Download the Bpayd CSR

Download the Bpayd Certificate Signing Request (CSR) file. You will use this when creating your Payment Processing Certificate in Apple's developer portal.

**Download**: [bpayd-apple-pay.csr](downloads/bpayd-apple-pay.csr)

### 2. Create a Merchant ID in Apple Developer

1. Sign in to your [Apple Developer account](https://developer.apple.com/account/).
2. Go to **Certificates, Identifiers & Profiles** > **Identifiers**.
3. Click the **+** button and select **Merchant IDs**.
4. Enter a description (e.g., "My App Apple Pay") and an identifier (e.g., `merchant.com.yourcompany.yourapp`).
5. Click **Continue** and then **Register**.

### 3. Create the Payment Processing Certificate

1. In **Certificates, Identifiers & Profiles** > **Identifiers**, select your newly created Merchant ID.
2. Under **Apple Pay Payment Processing Certificate**, click **Create Certificate**.
3. When prompted, answer **No** to the question "Will payments associated with this Merchant ID be processed exclusively in China mainland?".
4. Upload the **Bpayd CSR file** you downloaded in step 1 (do **not** generate your own CSR).
5. Click **Continue** and then **Download** the certificate.

You do not need to install or use this certificate yourself. It is only needed so that Apple can encrypt payment tokens in a way that Bpayd can decrypt.

### 4. Configure your app

Add the Apple Pay capability in Xcode and select your Merchant ID (the one you just created).

In your entitlements (or via Xcode > Signing & Capabilities > Apple Pay):

```xml
<key>com.apple.developer.in-app-payments</key>
<array>
    <string>merchant.com.yourcompany.yourapp</string>
</array>
```

## Front-End Implementation

> [!NOTE]
> **Disclaimer**: The following iOS implementation is provided as a **reference guide**. Your actual implementation may vary depending on your app architecture. You should adapt these examples to fit your needs rather than copying them verbatim.

On iOS, you integrate Apple Pay using PassKit (`PKPaymentRequest` and `PKPaymentAuthorizationController`).

### 1. Configure the Apple Pay capability

- In Xcode, add the Apple Pay capability and include your own merchant identifier.
- Confirm that your supported networks and merchant capabilities match your Bpayd configuration.

### 2. Create and present the payment sheet

At a high level:

1. Check `PKPaymentAuthorizationController.canMakePayments(usingNetworks:)`.
2. Build a `PKPaymentRequest` with total, currency, country, supported networks, and merchant capabilities.
3. Present a `PKPaymentAuthorizationController`.
4. When authorized, send `payment.token.paymentData` to your backend as a JSON string.

### Minimal Swift example

```swift
import PassKit

final class CheckoutViewController: UIViewController, PKPaymentAuthorizationControllerDelegate {
    func beginApplePay() {
        let networks: [PKPaymentNetwork] = [.visa, .masterCard, .amex, .discover]
        guard PKPaymentAuthorizationController.canMakePayments(usingNetworks: networks) else {
            return
        }

        let request = PKPaymentRequest()
        request.merchantIdentifier = "merchant.com.yourcompany.yourapp" // Your own merchant ID
        request.countryCode = "US"
        request.currencyCode = "USD"
        request.supportedNetworks = networks
        request.merchantCapabilities = [.threeDS]
        request.paymentSummaryItems = [
            PKPaymentSummaryItem(
                label: "Your Business Name", amount: NSDecimalNumber(string: "10.50"))
        ]

        let controller = PKPaymentAuthorizationController(paymentRequest: request)
        controller.delegate = self
        controller.present(completion: nil)
    }

    func paymentAuthorizationController(
        _ controller: PKPaymentAuthorizationController, didAuthorizePayment payment: PKPayment,
        handler completion: @escaping (PKPaymentAuthorizationResult) -> Void
    ) {
        guard let tokenString = String(data: payment.token.paymentData, encoding: .utf8) else {
            completion(PKPaymentAuthorizationResult(status: .failure, errors: nil))
            return
        }

        // Send tokenString to your backend and call completion based on the result.
        completion(PKPaymentAuthorizationResult(status: .success, errors: nil))
    }

    func paymentAuthorizationControllerDidFinish(_ controller: PKPaymentAuthorizationController) {
        controller.dismiss(completion: nil)
    }
}
```

## Back-End Implementation

### Apple Pay sale endpoint

To process an Apple Pay payment, your back-end must call the Bpayd API Apple Pay sale endpoint.

**URL**: `https://services.bmspay.com/api/Transactions/SaleWithApplePay`
**Method**: `POST`
**Content-Type**: `application/json`

#### Required fields

At a minimum, your request must include:

- **Authentication fields**: `AppKey`, `AppType`, `UserName`, `Password`, `mid`, `cid`
- **Transaction fields**: `Amount`, `Token`, `UserTransactionNumber`
- **In-app required**: `MerchantIdentifier` — your own Apple Pay merchant identifier (e.g., `merchant.com.yourcompany.yourapp`)

`UserTransactionNumber` must be **unique per transaction** and is used by Bpayd for transaction tracking and idempotency.

For the full list of supported fields and detailed schema for `SaleWithApplePay`, refer to the official Bpayd API documentation at [documentation.bmspay.com](https://documentation.bmspay.com/).

### Important: Token encoding

The Apple Pay token you receive from PassKit is a JSON payload (`payment.token.paymentData`). **Before sending it to the Bpayd API, you must Base64-encode it** and place the result in the `Token` field of the request.

The typical sequence is:

1. On the front end, obtain the Apple Pay token and convert it to a UTF-8 string from `payment.token.paymentData`.
2. Send that JSON string to your back-end.
3. On the back-end, Base64-encode the JSON string and assign the result to the `Token` field in the `SaleWithApplePay` request body.

### Sample request body

```json
{
    "AppKey": "YOUR_APP_KEY",
    "AppType": 1,
    "UserName": "YOUR_USERNAME",
    "Password": "YOUR_PASSWORD",
    "mid": 12345,
    "cid": 1,

    "Amount": 10.50,
    "Token": "<BASE64_ENCODED_APPLE_PAY_TOKEN>",
    "UserTransactionNumber": "UNIQUE_TXN_123456",

    "MerchantIdentifier": "merchant.com.yourcompany.yourapp",

    "IsTest": true
}
```

For the full list of supported fields, refer to the official Bpayd API documentation at [documentation.bmspay.com](https://documentation.bmspay.com/).

## Testing

Use the **Apple Pay sandbox** when testing your integration, and set `IsTest: true` in your requests to Bpayd. Follow Apple's official guidance for configuring test cards and devices:

- Apple Pay in-app setup/testing: <https://developer.apple.com/documentation/passkit/setting-up-apple-pay>

## Summary

Integrating Apple Pay on iOS with Bpayd API involves:

1. **Merchant ID setup**: Create your own Apple Pay Merchant ID and Payment Processing Certificate using the Bpayd CSR.
2. **Front-end**: Implement Apple Pay using PassKit and obtain the Apple Pay token payload.
3. **Back-end**: Call `SaleWithApplePay` with your `MerchantIdentifier`, Base64-encoding the Apple Pay token before sending it to Bpayd.
4. **Handle response**: Process the result and update your application accordingly.

If you also need to support Google Pay, see the [Google Pay Integration Guide](google-pay-integration.md).
