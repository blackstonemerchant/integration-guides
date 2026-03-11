# Google Pay™ Flutter Integration

## Overview

This guide describes how to integrate Google Pay as a payment method in your **Flutter application** using the Flutter `pay` package and the Bpayd API. Google Pay provides a fast, secure way for customers to pay using the payment methods stored in their Google Account.

The integration involves two main components:

1. **Front-end (Flutter)**: Collecting the Google Pay payment token using the `pay` package
2. **Back-end**: Sending the Google Pay token to the Bpayd API for payment processing

There is no domain verification, certificate setup, or merchant validation step for Flutter -- the `pay` package wraps the native Android Google Pay flow and handles token encryption through Google Play Services.

## Prerequisites

Before you begin, make sure you have:

- **Bpayd API Credentials**: Provided by Bpayd/Blackstone for your integration:
  - `AppKey`: Application Key that uniquely identifies your application
  - `AppType`: Application Type identifier
  - `UserName`: API username
  - `Password`: API password
  - `mid`: Merchant ID
  - `cid`: Cashier ID

- **Google Pay configuration from Bpayd**:

      - `merchantId`: `8138048649892127088` (Google Pay merchant configured by Bpayd)
      - `merchantName`: the business name that will be shown to the shopper in Google Pay. You **may set this to your own business name**, as long as it follows Bpayd and Google branding policies.
      - `gatewayMerchantId`: the Payment Processor Merchant ID provided by Bpayd

- **Flutter app with Android target enabled** (Google Pay works on Android only).
- **`pay` package** added to `pubspec.yaml`.
- **Google Pay configuration JSON** file (for example, `assets/google_pay.json`) registered in `pubspec.yaml`.
- **Google Pay & Wallet Console**: Register at [pay.google.com/business/console](https://pay.google.com/business/console) for production access.

- **Essential Prerequisites & Policy Compliance**

  > ### Warning: **REQUIRED: Before Starting Integration**
  >
  > All merchants using Bpayd's Google Pay integration **MUST**:
  >
  > - **Accept** the [Google Pay API Terms of Service](https://payments.developers.google.com/terms/sellertos)
  > - **Adhere** to the [Google Pay and Wallet API Acceptable Use Policy](https://payments.developers.google.com/terms/aup)
  > - Register in the [Google Pay & Wallet Console](https://pay.google.com/business/console) if you require your own Google `merchantId`
  > - Confirm acceptance of cards supported by Google and enabled by Bpayd
  >
  > **These requirements are mandatory and non-negotiable for all implementations.**

- **Official Flutter resources**:
  - `pay` package: <https://pub.dev/packages/pay>
  - Flutter Google Pay plugin: <https://github.com/google-pay/flutter-plugin>
  - Example payment configuration: <https://github.com/google-pay/flutter-plugin/blob/main/pay/example/lib/payment_configurations.dart>

The first mention of the service must include the registered trademark: **Google Pay™**.

## Integration Flow

Flutter uses the Android Google Pay flow under the hood. The steps are:

1. The customer taps the Google Pay button rendered by the `pay` package.
2. The package presents the Google Pay sheet and the customer authorizes the payment.
3. `onPaymentResult` returns the Google Pay token payload.
4. Your app sends the token payload to your back-end.
5. Your back-end Base64-encodes the token and calls the Bpayd API `SaleWithGooglePay` endpoint.
6. Bpayd processes the payment and returns the result.
7. Your app displays the payment result to the customer.

## Responsibilities

### Bpayd provides

- Bpayd API credentials (`AppKey`, `AppType`, `UserName`, `Password`, `mid`, `cid`).
- Google Pay `merchantId` (`8138048649892127088`).
- `gatewayMerchantId` (Payment Processor Merchant ID used in `tokenizationSpecification`).

### Your application is responsible for

- Defining the Google Pay payment configuration JSON and loading it with `PaymentConfiguration.fromAsset`.
- Presenting a `GooglePayButton` and handling `onPaymentResult`.
- Calculating the final amount sent in payment items.
- Generating a unique `UserTransactionNumber` for each transaction.
- Forwarding the Google Pay token payload to your back-end exactly as received.
- Base64-encoding the token on the back-end before sending it to Bpayd.

## Front-End Implementation

> [!NOTE]
> **Disclaimer**: The following Flutter implementation is provided as a **reference guide**. Your actual implementation may vary depending on your app architecture. You should adapt these examples to fit your needs rather than copying them verbatim.

Flutter's official `pay` package wraps the native Google Pay flow on Android.

### 1. Add the package and configuration file

- Add the `pay` package to `pubspec.yaml` and run `flutter pub get`.
- Create a Google Pay configuration JSON file (for example, `assets/google_pay.json`) and register it in `pubspec.yaml`.

```yaml
dependencies:
  pay: ^x.y.z # use the latest version from pub.dev

flutter:
  assets:
    - assets/google_pay.json
```

### 2. Update AndroidManifest.xml

In your `android/app/src/main/AndroidManifest.xml`, add the Google Pay API meta-data inside the `<application>` tag:

```xml
<application
    ...>

    <meta-data
        android:name="com.google.android.gms.wallet.api.enabled"
        android:value="true" />

    ...
</application>
```

### 3. Define the Google Pay configuration

Create `assets/google_pay.json` with the following Bpayd-specific configuration:

```json
{
    "provider": "google_pay",
    "data": {
        "environment": "TEST",
        "apiVersion": 2,
        "apiVersionMinor": 0,
        "allowedPaymentMethods": [{
            "type": "CARD",
            "parameters": {
                "allowedAuthMethods": ["PAN_ONLY", "CRYPTOGRAM_3DS"],
                "allowedCardNetworks": ["VISA", "MASTERCARD"]
            },
            "tokenizationSpecification": {
                "type": "PAYMENT_GATEWAY",
                "parameters": {
                    "gateway": "blackstone",
                    "gatewayMerchantId": "<Payment Processor Merchant ID provided by Bpayd>"
                }
            }
        }],
        "merchantInfo": {
            "merchantId": "8138048649892127088",
            "merchantName": "<Your Business Name Shown To Customers>"
        },
        "transactionInfo": {
            "countryCode": "US",
            "currencyCode": "USD"
        }
    }
}
```

> [!NOTE]
> Change `"environment"` to `"PRODUCTION"` when going live. Update `countryCode` and `currencyCode` as needed for your market.

### 4. Present the Google Pay button and handle the token

```dart
import 'dart:convert';
import 'package:pay/pay.dart';

final googlePayConfig = PaymentConfiguration.fromAsset('assets/google_pay.json');

final paymentItems = [
    PaymentItem(
        label: 'Your Business Name',
        amount: '10.50',
        status: PaymentItemStatus.final_price,
    ),
];

GooglePayButton(
    paymentConfiguration: googlePayConfig,
    paymentItems: paymentItems,
    type: GooglePayButtonType.pay,
    onPaymentResult: (result) {
        // Extract the token from the payment result
        final tokenData = result['paymentMethodData']?['tokenizationData']?['token'];
        if (tokenData != null) {
            final tokenString = tokenData is String ? tokenData : jsonEncode(tokenData);
            // Send tokenString to your backend.
            // Your backend will Base64-encode it and call SaleWithGooglePay.
        }
    },
    onError: (error) {
        // Handle UI errors.
    },
    loadingIndicator: const Center(child: CircularProgressIndicator()),
);
```

All other Google Pay fields (button style, additional data requests, etc.) should be implemented according to Google's official guides. The Bpayd-specific requirements are the configuration shown in `google_pay.json` and that you forward the **unaltered Google Pay payment token** to your back-end.

## Required Documentation

When integrating Google Pay, you must provide Blackstone/Bpayd with screenshots of your complete buyflow. These screenshots are required to verify proper implementation and compliance with Google Pay guidelines.

### Required Screenshots

You must submit the following screenshots of your payment flow:

1. **Item Selection Screen**
   - When a user is browsing an item or service
   - Shows the product/service selection interface

2. **Pre-Purchase Screen**
   - When a user is ultimately ready to make a purchase
   - Shows the final order summary before payment method selection

3. **Payment Method Screen**
   - When a user selects Google Pay as their payment method
   - Must clearly show the Google Pay button and payment options

4. **Google Pay API Payment Screen**
   - When a user is shown the payment info they've saved to Google Pay
   - **Important**: Android won't allow you to take a screenshot of this screen, so you must take a picture of the screen using another device (camera or phone)

5. **Post-Purchase Screen**
   - When a user has made a successful purchase
   - Shows the confirmation or success message

### Submission Guidelines

- Ensure all screenshots clearly show the relevant screen and user interface elements
- Screenshots should represent the actual production interface (or final staging version)
- For the Google Pay API payment screen, use a separate device to photograph the screen
- **Review [Google Pay brand guidelines examples](https://developers.google.com/pay/api/android/guides/brand-guidelines) to ensure proper button implementation before submitting screenshots**
- Submit all screenshots to Blackstone/Bpayd as part of your integration approval process

## Back-End Implementation

### API Endpoint

**URL**: `https://services.bmspay.com/api/Transactions/SaleWithGooglePay`
**Method**: `POST`
**Content-Type**: `application/json`

### Required fields

At a minimum, your request must include:

- **Authentication fields**: `AppKey`, `AppType`, `UserName`, `Password`, `mid`, `cid`
- **Transaction fields**: `Amount`, `Token`, `UserTransactionNumber`

`UserTransactionNumber` must be **unique per transaction** and is used by Bpayd for transaction tracking and idempotency.

For the full list of supported fields and detailed schema for `SaleWithGooglePay`, refer to the official Bpayd API documentation at [documentation.bmspay.com](https://documentation.bmspay.com/).

### Important: Token encoding

The Google Pay token you receive from the `pay` package is the payment result payload. **Before sending it to the Bpayd API, you must Base64-encode it** and place the result in the `Token` field of the request.

The typical sequence is:

1. On the front end, obtain the Google Pay token from `onPaymentResult` and extract the token string.
2. Send that token string to your back-end.
3. On the back-end, Base64-encode the token string and assign the result to the `Token` field in the `SaleWithGooglePay` request body.

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
    "Token": "<BASE64_ENCODED_GOOGLE_PAY_TOKEN>",
    "UserTransactionNumber": "UNIQUE_TXN_123456",

    "IsTest": true
}
```

For the full list of supported fields, refer to the official Bpayd API documentation at [documentation.bmspay.com](https://documentation.bmspay.com/).

## Testing

Use the **Google Pay TEST environment** when testing your integration, and set `IsTest: true` in your requests to Bpayd. In `google_pay.json`, ensure `"environment"` is set to `"TEST"`.

- Google Pay test cards and scenarios: <https://developers.google.com/pay/api/android/guides/resources/test-card-suite>

> [!NOTE]
> In the TEST environment, debug-signed APKs work. For production, your APK must be signed with a release key, `"environment"` must be set to `"PRODUCTION"` in `google_pay.json`, and you must obtain your merchant ID from the [Google Pay & Wallet Console](https://pay.google.com/business/console).

## Summary

Integrating Google Pay with Flutter and Bpayd API involves:

1. **Setup**: Add the `pay` package, create the Google Pay configuration JSON, and update `AndroidManifest.xml`.
2. **Front-end**: Implement Google Pay using the `pay` package with Bpayd's configuration and obtain the Google Pay token payload.
3. **Back-end**: Encode token to Base64, call `/api/Transactions/SaleWithGooglePay` endpoint.
4. **Handle response**: Process the result and update your application accordingly.

The key requirement is to **Base64-encode the Google Pay token** before sending it to the Bpayd API. All other parameters follow standard Bpayd API conventions.

If you also need to support Apple Pay, see the Apple Pay Integration Guide for [Web](apple-pay-web.md), [iOS](apple-pay-ios.md), or [Flutter](apple-pay-flutter.md).
