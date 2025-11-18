# Google Pay Integration Guide

## Overview

This guide describes how to integrate Google Pay as a payment method in your website or application using the Bpayd API. Google Pay provides a fast, secure way for customers to pay using the payment methods stored in their Google Account.

The integration involves two main components:

1. **Front-end**: Implementing the Google Pay button and obtaining the payment token
2. **Back-end**: Sending the Google Pay token to the Bpayd API for payment processing

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

- **HTTPS**: Google Pay requires a secure connection (HTTPS) for production environments
- **Supported Browser**: Google Pay works in Chrome, Safari, Firefox, and Edge

## Integration Flow

The complete Google Pay payment flow consists of these steps:

1. The customer clicks the Google Pay button on your website.
2. Google Pay displays the available payment methods and the customer authorizes the payment.
3. Google Pay returns an encrypted payment token to your front-end.
4. Your front-end sends the token to your back-end server.
5. Your back-end calls the Bpayd API with the token.
6. Bpayd processes the payment and returns the result.
7. Your application displays the payment result to the customer.

## Responsibilities

At a high level, responsibilities are split as follows:

- **Bpayd provides:**
  - Bpayd API credentials (`AppKey`, `AppType`, `UserName`, `Password`, `mid`, `cid`).
  - Google Pay `merchantId` (`8138048649892127088`).
  - `gatewayMerchantId` (Payment Processor Merchant ID used in `tokenizationSpecification`).

- **Your application is responsible for:**
  - Building the Google Pay client integration (`isReadyToPay`, `loadPaymentData`, button rendering/UX).
  - Calculating the final amount sent in `transactionInfo.totalPrice` and the `currencyCode`.
  - Generating a unique `UserTransactionNumber` for each transaction.
  - Forwarding the Google Pay token to Bpayd exactly as received from Google Pay.

## Front-End Implementation

On the front end, you integrate Google Pay using Google’s official Web API. The typical flow is:

1. Load the Google Pay JavaScript library.
2. Create a `PaymentsClient` in **TEST** or **PRODUCTION** environment.
3. Configure the allowed card networks and authentication methods.
4. Configure `merchantInfo`.
5. Render the Google Pay button.
6. When the user authorizes the payment, obtain the Google Pay payment token and send it to your back-end.

For the full Google Pay implementation details, see:

- Google Pay Web overview: <https://developers.google.com/pay/api/web/overview>
- Integrate the Google Pay API: <https://developers.google.com/pay/api/web/guides/setup>
- Google Pay brand guidelines: <https://developers.google.com/pay/api/web/guides/brand-guidelines>

### Google Pay configuration for Bpayd

When integrating Google Pay with Bpayd, there are **two Google Pay client methods** you must implement, and each one expects a specific request payload. The JavaScript examples below show exactly which fields must be sent in each call.

**1. Availability check – `isReadyToPay`**

```javascript
const paymentsClient = new google.payments.api.PaymentsClient({
  environment: 'TEST', // or 'PRODUCTION' when going live
});

// isReadyToPay: checks if Google Pay is available with Bpayd’s configuration
const isReadyToPayRequest = {
  apiVersion: 2,
  apiVersionMinor: 0,
  allowedPaymentMethods: [{
    type: 'CARD',
    parameters: {
      // Authentication methods required by Bpayd
      allowedAuthMethods: ['PAN_ONLY', 'CRYPTOGRAM_3DS'],
      // Card networks supported by Bpayd
      allowedCardNetworks: ['VISA', 'MASTERCARD'],
    },
    tokenizationSpecification: {
      type: 'PAYMENT_GATEWAY',
      parameters: {
        gateway: 'fiserv',
        gatewayMerchantId: '<Payment Processor Merchant ID provided by Bpayd>',
      },
    },
  }],
};

paymentsClient.isReadyToPay(isReadyToPayRequest)
  .then(response => {
    if (response.result) {
      // Create and render the Google Pay button.
      // The onClick handler will later call paymentsClient.loadPaymentData.
      const button = paymentsClient.createButton({
        onClick: processGooglePay,
      });
      document.getElementById('googlePayButton').appendChild(button);
    } else {
      // Google Pay is not available on this device/browser
    }
  })
  .catch(err => {
    console.error('Error checking Google Pay availability:', err);
  });
```

**2. Payment request – `loadPaymentData`**

```javascript
// loadPaymentData: requests a Google Pay payment and returns the token
function processGooglePay() {
  // totalAmount should be your computed order total (amount + taxes/fees, etc.)
  const totalAmount = /* your computed total amount */ 0;

  const paymentDataRequest = {
    apiVersion: 2,
    apiVersionMinor: 0,
    allowedPaymentMethods: [{
      type: 'CARD',
      parameters: {
        // Same auth methods and networks as in isReadyToPay
        allowedAuthMethods: ['PAN_ONLY', 'CRYPTOGRAM_3DS'],
        allowedCardNetworks: ['VISA', 'MASTERCARD'],
      },
      tokenizationSpecification: {
        type: 'PAYMENT_GATEWAY',
        parameters: {
          gateway: 'fiserv',
          gatewayMerchantId: '<Payment Processor Merchant ID provided by Bpayd>',
        },
      },
    }],
    transactionInfo: {
      totalPriceStatus: 'FINAL',
      totalPrice: String(totalAmount),
      currencyCode: '<Your currency code>',  // e.g. "USD"
    },
    merchantInfo: {
      merchantId: '8138048649892127088',           // Bpayd Google Pay merchant
      merchantName: '<Your Business Name Shown To Customers>',
    },
  };

  paymentsClient.loadPaymentData(paymentDataRequest)
    .then(paymentData => {
      const googlePayToken = paymentData.paymentMethodData.tokenizationData.token;
      // Forward googlePayToken to your back-end exactly as received
    })
    .catch(err => {
      console.error('Payment failed or was canceled:', err);
    });
}
```

All other Google Pay fields (supported networks, button style, etc.) should be implemented according to Google’s official guides. The Bpayd-specific requirements are the configuration shown in these two calls and that you forward the **unaltered Google Pay payment token** to your back-end.

## Back-End Implementation

### API Endpoint

**URL**: `https://services.bmspay.com/api/Transactions/SaleWithGooglePay`  
**Method**: `POST`  
**Content-Type**: `application/json`

### Request Parameters

At a minimum, your request must include:

- **Authentication fields**: `AppKey`, `AppType`, `UserName`, `Password`, `mid`, `cid`
- **Transaction fields**: `Amount`, `Token`, `UserTransactionNumber`

`UserTransactionNumber` must be **unique per transaction** and is used by Bpayd for transaction tracking and idempotency.

For the full list of supported fields and detailed schema for `SaleWithGooglePay`, refer to the official Bpayd API documentation at [documentation.bmspay.com](https://documentation.bmspay.com/).

### Important: Token Encoding

The Google Pay token you receive on the front end is a JSON payload. **Before sending it to the Bpayd API, you must Base64-encode it** and place the result in the `Token` field of the request.

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

  "CurrencyCode": "USD",
  "CustomerEmail": "customer@example.com",
  "IpAddress": "203.0.113.10",
  "Source": 1,
  "PosCode": 0,
  "IsTest": true
}
```

This example shows the minimum structure expected by the Bpayd API for a Google Pay sale. You can add any other supported fields as described in the official documentation.

## Testing

Use a **Google Pay TEST environment** with `IsTest: true` when exercising your integration, and rely on Google’s official test cards and scenarios:

- Google Pay test cards and scenarios: <https://developers.google.com/pay/api/android/guides/resources/test-card-suite>

## Summary

Integrating Google Pay with Bpayd API involves:

1. **Front-end**: Implement Google Pay button, obtain payment token
2. **Back-end**: Encode token to Base64, call `/api/Transactions/SaleWithGooglePay` endpoint
3. **Handle response**: Process success/failure and update your application accordingly

The key requirement is to **Base64-encode the Google Pay token** before sending it to the Bpayd API. All other parameters follow standard Bpayd API conventions.
