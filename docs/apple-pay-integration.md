# Apple Pay Integration Guide

## Overview

This guide describes how to integrate Apple Pay with the Bpayd API for **web** (Apple Pay JS), **iOS** (PassKit), and **Flutter** (using the Flutter team official `pay` package on iOS). It covers the shared backend payment flow and the platform-specific front-end steps.

The integration involves two main components:

1. **Front-end (Web, iOS, or Flutter)**: Collecting the Apple Pay payment token
2. **Back-end (Shared)**: Sending the Apple Pay token to the Bpayd API for payment processing

Web integrations require domain verification and merchant validation. iOS and Flutter integrations skip those steps and go directly to payment authorization.

## Prerequisites

Before you begin, make sure you have:

### General prerequisites (Web + iOS)

- **Bpayd API Credentials**: Provided by Bpayd/Blackstone for your integration:
  - `AppKey`: Application Key that uniquely identifies your application  
  - `AppType`: Application Type identifier  
  - `UserName`: API username  
  - `Password`: API password  
  - `mid`: Merchant ID  
  - `cid`: Cashier ID  
- **Apple Pay enablement from Bpayd**:
  - Apple Pay is enabled for your merchant in Bpayd.
  - Bpayd manages the Apple Pay merchant identifier, certificates, and communication with Apple's servers on your behalf.

### Web prerequisites (Apple Pay JS)

- **Apple Pay domains**:
  - A list of all domains where you will show the Apple Pay button (see **Web Domain Configuration for Bpayd** below).
  - Each domain must be available over HTTPS in production.
- **Supported devices and browsers**:
  - **iPhone (iOS 16+)**: Apple Pay works natively in **all browsers** (Safari, Chrome, Edge, Firefox, etc.).
  - **Mac (macOS)**: Native Apple Pay is available only in **Safari**.
  - **Other environments**: On macOS with other browsers (Chrome, Firefox) or on Windows/Linux, the user will see a **QR Code** which they must scan with their iPhone to complete the payment.
- Official web documentation:
  - Apple Pay on the Web overview: <https://developer.apple.com/documentation/apple_pay_on_the_web/>
  - Apple Pay JS API reference: <https://developer.apple.com/documentation/apple_pay_on_the_web/applepaysession>

### iOS prerequisites (PassKit)

- **Apple Developer Program account** with Apple Pay capability enabled in Xcode.
- **Test device** with Apple Pay set up (or Apple Pay sandbox test cards).
- Official iOS documentation:
  - Setting up Apple Pay: <https://developer.apple.com/documentation/passkit/setting-up-apple-pay>
  - Offering Apple Pay in your app: <https://developer.apple.com/documentation/passkit/offering-apple-pay-in-your-app>

### Flutter prerequisites (pay package)

- **Flutter app with iOS target enabled** (Apple Pay works on iOS only).
- **`pay` package** added to `pubspec.yaml`.
- **Apple Pay configuration JSON** file (for example, `assets/apple_pay.json`) registered in `pubspec.yaml`.
- **Apple Pay capability** enabled in the iOS Runner target with the Bpayd merchant identifier.
- Official Flutter resources:
  - `pay` package: <https://pub.dev/packages/pay>
  - Example payment configuration: <https://github.com/google-pay/flutter-plugin/blob/main/pay/example/lib/payment_configurations.dart>

## Integration Flow

### Web (Apple Pay JS)

The complete Apple Pay on the web flow consists of these steps:

1. The customer clicks the Apple Pay button on your site (on a compatible Apple device and browser).
2. Your front-end creates an `ApplePaySession` with a payment request (amount, currency, supported networks, capabilities).
3. During the session, Apple calls your front-end’s `onvalidatemerchant` handler with a `validationURL`.
4. Your front-end sends this `validationURL` to your back-end.
5. Your back-end calls the Bpayd API `ValidateApplePayMerchant` endpoint, which talks to Apple and returns a merchant session object.
6. Your front-end completes merchant validation using that merchant session.
7. When the customer authorizes the payment, Apple Pay returns a payment token to your front-end.
8. Your front-end sends the Apple Pay token to your back-end.
9. Your back-end Base64-encodes the token and calls the Bpayd API `SaleWithApplePay` endpoint.
10. Bpayd processes the payment and returns the result.
11. Your application displays the payment result to the customer.

### iOS (PassKit)

The complete Apple Pay in-app flow consists of these steps:

1. The customer taps the Apple Pay button in your iOS app.
2. Your app builds a `PKPaymentRequest` and presents a `PKPaymentAuthorizationController`.
3. The customer authorizes the payment with Face ID, Touch ID, or passcode.
4. iOS returns a payment token (`payment.token.paymentData`).
5. Your app sends the payment token to your back-end.
6. Your back-end Base64-encodes the token and calls the Bpayd API `SaleWithApplePay` endpoint.
7. Bpayd processes the payment and returns the result.
8. Your app displays the payment result to the customer.

### Flutter (pay package)

Flutter uses the iOS Apple Pay flow under the hood. The steps are:

1. The customer taps the Apple Pay button rendered by the `pay` package.
2. The package presents the Apple Pay sheet and collects authorization.
3. `onPaymentResult` returns the Apple Pay token payload.
4. Your app sends the token payload to your back-end.
5. Your back-end Base64-encodes the token and calls the Bpayd API `SaleWithApplePay` endpoint.
6. Bpayd processes the payment and returns the result.
7. Your app displays the payment result to the customer.

## Responsibilities

At a high level, responsibilities are split as follows:

### Bpayd provides (shared)

- Bpayd API credentials (`AppKey`, `AppType`, `UserName`, `Password`, `mid`, `cid`).
- Apple Pay merchant configuration (merchant identifier, certificates, and processing keys).
- API endpoints for:
  - `SaleWithApplePay` (Apple Pay sale processing).
  - `ValidateApplePayMerchant` (merchant session validation with Apple, web only).
- Domain verification files and instructions for each domain where you will use Apple Pay (web only).

### Your application is responsible for (Web)

- Providing Bpayd with **all domains** where Apple Pay will be used (see below).
- Hosting the Apple Pay domain verification file(s) at the exact URLs specified by Bpayd for each domain.
- Building the Apple Pay front-end integration (`ApplePaySession`, merchant validation, payment authorization).
- Forwarding the Apple Pay token to your back-end exactly as received from Apple (without modification).
- Base64-encoding the token on the back-end before sending it to Bpayd.
- Generating a unique `UserTransactionNumber` for each transaction.

### Your application is responsible for (Flutter)

- Enabling Apple Pay capability in the iOS Runner target and adding the Bpayd merchant identifier.
- Defining the Apple Pay payment configuration JSON and loading it with `PaymentConfiguration.fromAsset`.
- Presenting an `ApplePayButton` (or `PayButton`) and handling `onPaymentResult`.
- Forwarding the Apple Pay token payload to your back-end exactly as received.
- Base64-encoding the token on the back-end before sending it to Bpayd.
- Generating a unique `UserTransactionNumber` for each transaction.

### Your application is responsible for (iOS)

- Enabling Apple Pay capability and adding the Bpayd merchant identifier in Xcode.
- Building the Apple Pay in-app flow with PassKit (`PKPaymentRequest`, `PKPaymentAuthorizationController`).
- Forwarding the Apple Pay token (`payment.token.paymentData`) to your back-end exactly as received from Apple.
- Base64-encoding the token on the back-end before sending it to Bpayd.
- Generating a unique `UserTransactionNumber` for each transaction.

## Web Front-End Implementation (Apple Pay JS)

> [!NOTE]
> **Disclaimer**: The following web front-end implementation is provided as a **reference guide**. Your actual implementation may vary depending on your technology stack (e.g., React, Vue, Angular) and specific application architecture. You should adapt these examples to fit your needs rather than copying them verbatim.

On the web, you integrate Apple Pay using Apple's JavaScript API (`ApplePaySession`).

### 1. Import the Apple Pay SDK

You must include the Apple Pay JS SDK in your page. Add the following script tag to your HTML:

```html
<script src="https://applepay.cdn-apple.com/jsapi/1.latest/apple-pay-sdk.js"></script>
```

### 2. Implementation Steps

At a high level:

1. **Check for Secure Context**: Apple Pay requires HTTPS (or localhost).
2. **Wait for API Availability**: The `ApplePaySession` object might load asynchronously.
3. **Check Payment Capability**: Use `canMakePayments()` to check if the device and browser support Apple Pay.
4. **Show the Button**: If supported, display the Apple Pay button.
5. **Handle Session**: Create the session, handle merchant validation, and process the payment.

For full implementation details, follow Apple’s official documentation:

- Apple Pay on the Web overview: <https://developer.apple.com/documentation/apple_pay_on_the_web/>
- Apple Pay JS API reference: <https://developer.apple.com/documentation/apple_pay_on_the_web/applepaysession>

### Web configuration for Bpayd

When integrating Apple Pay with Bpayd, your front-end code should:

- Use a **payment request** that matches Bpayd’s configuration.
- Implement **merchant validation** by sending Apple’s `validationURL` to your back-end so it can call Bpayd’s `ValidateApplePayMerchant`.
- Implement **payment authorization** by forwarding the Apple Pay token to your back-end, unchanged.

### Robust JavaScript Example

Below is a robust JavaScript example that handles cross-browser support, async loading, and secure context checks.

```javascript
// 1. Helper: Check if the context is secure (HTTPS or localhost)
function isSecureApplePayContext() {
    return location.protocol === 'https:' || location.hostname === 'localhost';
}

// 2. Helper: Wait for ApplePaySession to be available (it may load asynchronously)
function waitForApplePaySession(maxAttempts = 10, delayMs = 300) {
    return new Promise(resolve => {
        const attempt = (count) => {
            if (window.ApplePaySession) {
                return resolve(true);
            }
            if (count >= maxAttempts) {
                return resolve(false);
            }
            setTimeout(() => attempt(count + 1), delayMs);
        };
        attempt(0);
    });
}

// 3. Helper: Resolve the supported Apple Pay version
function resolveApplePayVersion() {
    if (!window.ApplePaySession) {
        return null;
    }
    if (typeof ApplePaySession.supportsVersion !== 'function') {
        return 1; // Default to version 1 if supportsVersion is missing
    }
    // Check for versions in descending order
    const versions = [3, 2, 1];
    for (let i = 0; i < versions.length; i++) {
        if (ApplePaySession.supportsVersion(versions[i])) {
            return versions[i];
        }
    }
    return null;
}

// 4. Main Initialization Function
async function initializeApplePay() {
    // Security check
    if (!isSecureApplePayContext()) {
        console.warn('Apple Pay requires a secure (HTTPS) connection.');
        return;
    }

    // Wait for the SDK to load
    const sessionReady = await waitForApplePaySession();
    if (!sessionReady) {
        console.warn('Apple Pay SDK not loaded or not supported in this browser.');
        return;
    }

    // Check availability
    try {
        const result = ApplePaySession.canMakePayments();
        
        // Handle both Promise (newer) and Boolean (older) returns
        if (result && typeof result.then === 'function') {
            result.then(function (canPay) {
                if (canPay) showApplePayButton();
            }).catch(function (err) {
                console.error('Apple Pay availability check failed:', err);
            });
        } else {
            if (result) showApplePayButton();
        }
    } catch (error) {
        console.error('Apple Pay availability check failed:', error);
    }
}

function showApplePayButton() {
    const button = document.getElementById('applePayButton');
    if (button) {
        button.style.display = 'inline-flex';
        button.addEventListener('click', beginApplePaySession);
    }
}

// 5. Begin Session
function beginApplePaySession() {
    if (!window.ApplePaySession) return;

    const version = resolveApplePayVersion();
    if (!version) {
        console.error('No supported Apple Pay version found.');
        return;
    }

    const totalAmount = '10.50'; // Your computed total

    // Configuration must match Bpayd agreement
    const paymentRequest = {
        countryCode: 'US',
        currencyCode: 'USD',
        supportedNetworks: ['visa', 'masterCard', 'amex', 'discover'],
        merchantCapabilities: ['supports3DS'],
        total: {
            label: 'Your Business Name',
            amount: totalAmount,
        },
    };

    const session = new ApplePaySession(version, paymentRequest);

    // Merchant Validation
    session.onvalidatemerchant = function (event) {
        fetch('/your-backend/apple-pay/validate-merchant', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                validationUrl: event.validationURL
            }),
        })
        .then(response => response.json())
        .then(data => {
            // data.result should be the merchant session object from Bpayd
            session.completeMerchantValidation(data.result);
        })
        .catch(err => {
            console.error('Merchant validation failed:', err);
            session.abort();
        });
    };

    // Payment Authorization
    session.onpaymentauthorized = function (event) {
        const rawToken = event.payment.token;
        // Ensure token is a JSON string
        const tokenString = typeof rawToken === 'string' 
            ? rawToken 
            : JSON.stringify(rawToken);

        fetch('/your-backend/apple-pay/process-payment', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                applePayToken: tokenString,
                amount: totalAmount
            }),
        })
        .then(response => response.json())
        .then(result => {
            if (result && result.success) {
                session.completePayment(ApplePaySession.STATUS_SUCCESS);
            } else {
                session.completePayment(ApplePaySession.STATUS_FAILURE);
            }
        })
        .catch(err => {
            console.error('Payment processing failed:', err);
            session.completePayment(ApplePaySession.STATUS_FAILURE);
        });
    };

    session.oncancel = function () {
        console.info('Apple Pay session cancelled by user.');
    };

    session.begin();
}

// Start initialization
document.addEventListener('DOMContentLoaded', initializeApplePay);
```

All other Apple Pay UI and configuration options (button style, locale, additional line items, etc.) should follow Apple’s guides. The Bpayd-specific requirements are:

- The supported networks should include at least `visa`, `masterCard`, `amex`, and `discover` (subject to the configuration agreed with Bpayd).
- `merchantCapabilities` must include `supports3DS`.
- You must forward the full Apple Pay `payment.token` payload to your back-end, **unchanged**.

## Web Domain Configuration for Bpayd

Apple requires **domain verification** before Apple Pay can be used on a website. This applies only to web integrations. With Bpayd, this process works as follows:

- You must provide Bpayd with **every domain** where you intend to show the Apple Pay button.
  - Domains must be specified **without protocol and without paths**.
  - Examples of valid entries:
    - `example.com`
    - `store.example.com`
    - `checkout.example.net`
  - Invalid examples (do **not** include protocol or subpaths):
    - `https://example.com`
    - `example.com/checkout`

- If you use multiple subdomains, you must list **each one explicitly**. Registering only `example.com` is not sufficient if you also use `checkout.example.com` or `shop.example.com`.

- Bpayd will:
  - Register those domains with Apple for Apple Pay on the web.
  - Provide you with one or more **verification files** and the exact URLs where they must be hosted for each domain (typically under the `/.well-known/` path).

- You must:
  - Deploy the provided verification file(s) to each specified domain at the exact path indicated by Bpayd.
  - Ensure the files are served over HTTPS and are publicly accessible.

Apple uses these files to verify that you control the domains. Apple Pay will only work on domains that:

- Have been registered with Apple through Bpayd, and
- Correctly host the domain verification file provided by Bpayd.

For Apple’s official description of this process, see:

- Apple Pay on the Web: Set up your server: <https://developer.apple.com/documentation/apple_pay_on_the_web/configuring_your_environment>

## iOS Front-End Implementation (PassKit)

> [!NOTE]
> **Disclaimer**: The following iOS implementation is provided as a **reference guide**. Your actual implementation may vary depending on your app architecture. You should adapt these examples to fit your needs rather than copying them verbatim.

On iOS, you integrate Apple Pay using PassKit (`PKPaymentRequest` and `PKPaymentAuthorizationController`). There is no domain verification or merchant validation step on iOS.

### 1. Configure the Apple Pay capability

- In Xcode, add the Apple Pay capability and include the Bpayd merchant identifier.
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
        request.merchantIdentifier = "merchant.gateway.bpayd.com"
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

## Flutter Front-End Implementation (pay package)

> [!NOTE]
> **Disclaimer**: The following Flutter implementation is provided as a **reference guide**. Your actual implementation may vary depending on your app architecture. You should adapt these examples to fit your needs rather than copying them verbatim.

Flutter's official `pay` package wraps the native Apple Pay flow on iOS. There is no domain verification or merchant validation step in Flutter (same as native iOS).

### 1. Add the package and configuration file

- Add the `pay` package to `pubspec.yaml` and run `flutter pub get`.
- Create an Apple Pay configuration JSON file (for example, `assets/apple_pay.json`) and register it in `pubspec.yaml`.

```yaml
dependencies:
pay: ^x.y.z # use the latest version from pub.dev

flutter:
assets:
    - assets/apple_pay.json
```

### 2. Define the Apple Pay configuration

```json
{
    "provider": "apple_pay",
    "data": {
        "merchantIdentifier": "merchant.gateway.bpayd.com",
        "displayName": "Your Business Name",
        "merchantCapabilities": ["3DS"],
        "supportedNetworks": ["visa", "masterCard", "amex", "discover"],
        "countryCode": "US",
        "currencyCode": "USD"
    }
}
```

### 3. Present the Apple Pay button and handle the token

```dart
import 'package:pay/pay.dart';

final applePayConfig = PaymentConfiguration.fromAsset('assets/apple_pay.json');

final paymentItems = [
    PaymentItem(
        label: 'Your Business Name',
        amount: '10.50',
        status: PaymentItemStatus.final_price,
    ),
];

ApplePayButton(
    paymentConfiguration: applePayConfig,
    paymentItems: paymentItems,
    style: ApplePayButtonStyle.black,
    type: ApplePayButtonType.buy,
    onPaymentResult: (result) {
        final tokenPayload = result['token'] ?? result;
        // Serialize tokenPayload to JSON and send it to your backend.
    },
    onError: (error) {
        // Handle UI errors.
    },
);
```

Make sure your iOS Runner target includes the Apple Pay capability and the Bpayd merchant identifier in Xcode.

## Back-End Implementation

This backend flow is shared across web, iOS, and Flutter integrations.

### Apple Pay sale endpoint

To process an Apple Pay payment, your back-end must call the Bpayd API Apple Pay sale endpoint.

**URL**: `https://services.bmspay.com/api/Transactions/SaleWithApplePay`  
**Method**: `POST`  
**Content-Type**: `application/json`

#### Required fields

At a minimum, your request must include:

- **Authentication fields**: `AppKey`, `AppType`, `UserName`, `Password`, `mid`, `cid`
- **Transaction fields**: `Amount`, `Token`, `UserTransactionNumber`

`UserTransactionNumber` must be **unique per transaction** and is used by Bpayd for transaction tracking and idempotency.

For the full list of supported fields and detailed schema for `SaleWithApplePay`, refer to the official Bpayd API documentation at [documentation.bmspay.com](https://documentation.bmspay.com/).

### Important: Token encoding

The Apple Pay token you receive on the front end is a JSON payload (web: `event.payment.token`, iOS: `payment.token.paymentData`, Flutter: the `onPaymentResult` payload). **Before sending it to the Bpayd API, you must Base64-encode it** and place the result in the `Token` field of the request.

The typical sequence is:

1. On the front end, obtain the full Apple Pay token payload and convert it to a JSON string (for example, `JSON.stringify(event.payment.token)` on the web, or a UTF-8 string from `payment.token.paymentData` on iOS).
2. Send that JSON string to your back-end (for example, in a field named `applePayToken`).
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

    "IsTest": true
}
```

This example shows the minimum structure expected by the Bpayd API for an Apple Pay sale. You can add any other supported fields as described in the official documentation.

### Merchant validation endpoint (web only)

Web integrations must support Apple’s **merchant validation** flow by calling Bpayd’s merchant validation endpoint from your back-end.

**URL**: `https://services.bmspay.com/api/Transactions/ValidateApplePayMerchant`  
**Method**: `POST`  
**Content-Type**: `application/json`

At a high level:

- Your front-end receives a `validationURL` from Apple in `onvalidatemerchant`.
- Your back-end calls `ValidateApplePayMerchant` with:
  - Your standard Bpayd authentication fields (`AppKey`, `AppType`, `UserName`, `Password`, `mid`, `cid`).
  - `ValidationUrl`: the `validationURL` received from Apple.
  - `Initiative`: `"web"`.
  - `InitiativeContext`: the domain that Apple is validating (must exactly match one of the Apple Pay domains registered with Bpayd, without protocol or path).
- Bpayd performs the domain checks and calls Apple’s servers.
- The response contains the **merchant session** object that your front-end must pass to `session.completeMerchantValidation`.

For the exact schema of the `ValidateApplePayMerchant` request and response, refer to [documentation.bmspay.com](https://documentation.bmspay.com/).

## Testing

Use the **Apple Pay sandbox** when testing your integration, and set `IsTest: true` in your requests to Bpayd. Follow Apple’s official guidance for configuring test cards and devices:

- Apple Pay on the Web testing: <https://developer.apple.com/documentation/apple_pay_on_the_web/testing_your_web-based_apple_pay_integration>
- Apple Pay in-app setup/testing (iOS + Flutter): <https://developer.apple.com/documentation/passkit/setting-up-apple-pay>

## Summary

Integrating Apple Pay with Bpayd API involves:

1. **Web domain setup**: Provide Bpayd with all domains where Apple Pay will be used and host the verification files they provide.
2. **Front-end**: Implement Apple Pay on the web (`ApplePaySession`) or in-app (iOS PassKit / Flutter `pay`) and obtain the Apple Pay token payload.
3. **Back-end**: Call `SaleWithApplePay` for payments, Base64-encoding the Apple Pay token before sending it to Bpayd.
4. **Web-only validation**: Call `ValidateApplePayMerchant` for merchant sessions on the web.
5. **Handle response**: Process the result and update your application accordingly.

The key requirements are to **correctly configure and verify your domains with Apple (web only)** and to **Base64-encode the Apple Pay token** before calling `SaleWithApplePay`. All other parameters follow standard Bpayd API conventions.

If you also need to support Google Pay, see the [Google Pay Integration Guide](google-pay-integration.md).
