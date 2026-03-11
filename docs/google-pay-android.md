# Google Pay™ Android Integration

## Overview

This guide describes how to integrate Google Pay as a payment method in your **Android application** using the Google Pay API and the Bpayd API. Google Pay provides a fast, secure way for customers to pay using the payment methods stored in their Google Account.

The integration involves two main components:

1. **Front-end (Android)**: Implementing the Google Pay button and obtaining the payment token using the Google Pay API for Android
2. **Back-end**: Sending the Google Pay token to the Bpayd API for payment processing

There is no domain verification, certificate setup, or merchant validation step for Android -- Google Pay handles authentication and token encryption through the Google Play Services infrastructure.

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

- **Android development environment**:
      - Android Studio
      - Minimum SDK: API 21 (Android 5.0)
      - Google Play Services installed on test device
      - `com.google.android.gms:play-services-wallet` dependency

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

- **Official Android documentation**:
  - Google Pay API for Android - Overview: <https://developers.google.com/pay/api/android/overview>
  - Android Integration Checklist: <https://developers.google.com/pay/api/android/guides/test-and-deploy/integration-checklist>
  - Android Brand Guidelines: <https://developers.google.com/pay/api/android/guides/brand-guidelines>
  - Android Tutorial: <https://developers.google.com/pay/api/android/guides/tutorial>

The first mention of the service must include the registered trademark: **Google Pay™**.

## Integration Flow

The complete Google Pay Android payment flow consists of these steps:

1. Your app checks if Google Pay is available on the device using `isReadyToPay`.
2. If available, the app displays the Google Pay button.
3. The customer taps the Google Pay button.
4. Google Pay displays the available payment methods and the customer authorizes the payment.
5. Google Pay returns an encrypted payment token to your app.
6. Your app sends the token to your back-end server.
7. Your back-end calls the Bpayd API with the token.
8. Bpayd processes the payment and returns the result.
9. Your app displays the payment result to the customer.

## Responsibilities

- **Bpayd provides:**

  - Bpayd API credentials (`AppKey`, `AppType`, `UserName`, `Password`, `mid`, `cid`).
  - Google Pay `merchantId` (`8138048649892127088`).
  - `gatewayMerchantId` (Payment Processor Merchant ID used in `tokenizationSpecification`).

- **Your application is responsible for:**

  - Building the Google Pay Android integration (`isReadyToPay`, `loadPaymentData`, button rendering/UX).
  - Calculating the final amount sent in `transactionInfo.totalPrice` and the `currencyCode`.
  - Generating a unique `UserTransactionNumber` for each transaction.
  - Forwarding the Google Pay token to Bpayd exactly as received from Google Pay.

## Front-End Implementation

> [!NOTE]
> **Disclaimer**: The following Android implementation is provided as a **reference guide**. Your actual implementation may vary depending on your app architecture (Jetpack Compose, MVVM, etc.). You should adapt these examples to fit your needs rather than copying them verbatim.

### 1. Add dependencies

Add the Google Pay dependency to your app-level `build.gradle`:

```groovy
dependencies {
    implementation 'com.google.android.gms:play-services-wallet:19.4.0'
}
```

### 2. Update AndroidManifest.xml

Add the Google Pay API meta-data inside the `<application>` tag:

```xml
<application
    ...>

    <meta-data
        android:name="com.google.android.gms.wallet.api.enabled"
        android:value="true" />

    ...
</application>
```

### 3. Google Pay configuration for Bpayd

The following Kotlin code shows how to configure Google Pay with Bpayd's parameters. The configuration must match the values provided by Bpayd.

```kotlin
import com.google.android.gms.wallet.*
import org.json.JSONArray
import org.json.JSONObject

object GooglePayConfig {

    // Bpayd-specific configuration
    private const val GATEWAY = "blackstone"
    private const val GATEWAY_MERCHANT_ID = "<Payment Processor Merchant ID provided by Bpayd>"
    private const val MERCHANT_ID = "8138048649892127088" // Bpayd Google Pay merchant
    private const val MERCHANT_NAME = "<Your Business Name Shown To Customers>"

    /**
     * Card networks supported by Bpayd.
     */
    private val allowedCardNetworks = JSONArray(listOf("VISA", "MASTERCARD"))

    /**
     * Authentication methods required by Bpayd.
     */
    private val allowedAuthMethods = JSONArray(listOf("PAN_ONLY", "CRYPTOGRAM_3DS"))

    /**
     * Gateway tokenization specification for Bpayd.
     */
    private fun gatewayTokenizationSpecification(): JSONObject =
        JSONObject().apply {
            put("type", "PAYMENT_GATEWAY")
            put("parameters", JSONObject().apply {
                put("gateway", GATEWAY)
                put("gatewayMerchantId", GATEWAY_MERCHANT_ID)
            })
        }

    /**
     * Allowed payment methods with Bpayd's configuration.
     */
    private fun allowedPaymentMethods(): JSONArray =
        JSONArray().put(
            JSONObject().apply {
                put("type", "CARD")
                put("parameters", JSONObject().apply {
                    put("allowedAuthMethods", allowedAuthMethods)
                    put("allowedCardNetworks", allowedCardNetworks)
                })
                put("tokenizationSpecification", gatewayTokenizationSpecification())
            }
        )

    /**
     * Creates an IsReadyToPayRequest to check Google Pay availability.
     */
    fun isReadyToPayRequest(): JSONObject =
        JSONObject().apply {
            put("apiVersion", 2)
            put("apiVersionMinor", 0)
            put("allowedPaymentMethods", allowedPaymentMethods())
        }

    /**
     * Creates a PaymentDataRequest for a given price and currency.
     */
    fun paymentDataRequest(price: String, currencyCode: String): JSONObject =
        JSONObject().apply {
            put("apiVersion", 2)
            put("apiVersionMinor", 0)
            put("allowedPaymentMethods", allowedPaymentMethods())
            put("transactionInfo", JSONObject().apply {
                put("totalPrice", price)
                put("totalPriceStatus", "FINAL")
                put("currencyCode", currencyCode)
            })
            put("merchantInfo", JSONObject().apply {
                put("merchantId", MERCHANT_ID)
                put("merchantName", MERCHANT_NAME)
            })
        }
}
```

### 4. Implement the payment flow

The following example shows how to check availability, display the Google Pay button, and handle the payment result in an Activity:

```kotlin
import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.activity.result.ActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import com.google.android.gms.common.api.ApiException
import com.google.android.gms.wallet.*

class CheckoutActivity : AppCompatActivity() {

    private lateinit var paymentsClient: PaymentsClient

    // Register the activity result launcher for Google Pay
    private val paymentLauncher = registerForActivityResult(
        ActivityResultContracts.StartIntentSenderForResult()
    ) { result: ActivityResult ->
        handlePaymentResult(result)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_checkout)

        // Create the PaymentsClient
        val walletOptions = Wallet.WalletOptions.Builder()
            .setEnvironment(WalletConstants.ENVIRONMENT_TEST) // Use ENVIRONMENT_PRODUCTION for live
            .build()
        paymentsClient = Wallet.getPaymentsClient(this, walletOptions)

        // Check if Google Pay is available
        checkGooglePayAvailability()
    }

    private fun checkGooglePayAvailability() {
        val request = IsReadyToPayRequest.fromJson(
            GooglePayConfig.isReadyToPayRequest().toString()
        )

        paymentsClient.isReadyToPay(request).addOnCompleteListener { task ->
            try {
                if (task.result == true) {
                    // Show the Google Pay button
                    showGooglePayButton()
                }
            } catch (e: ApiException) {
                // Google Pay is not available
            }
        }
    }

    private fun showGooglePayButton() {
        val googlePayButton = findViewById<View>(R.id.googlePayButton)
        googlePayButton.visibility = View.VISIBLE
        googlePayButton.setOnClickListener { requestPayment() }
    }

    private fun requestPayment() {
        val totalAmount = "10.50" // Your computed total amount
        val currencyCode = "USD"  // Your currency code

        val request = PaymentDataRequest.fromJson(
            GooglePayConfig.paymentDataRequest(totalAmount, currencyCode).toString()
        )

        val task = paymentsClient.loadPaymentData(request)
        AutoResolveHelper.resolveTask(task, this, paymentLauncher)
    }

    private fun handlePaymentResult(result: ActivityResult) {
        when (result.resultCode) {
            RESULT_OK -> {
                result.data?.let { intent ->
                    val paymentData = PaymentData.getFromIntent(intent)
                    val paymentInfo = paymentData?.toJson()

                    // Extract the token from the payment data
                    val token = paymentInfo?.let { json ->
                        org.json.JSONObject(json)
                            .getJSONObject("paymentMethodData")
                            .getJSONObject("tokenizationData")
                            .getString("token")
                    }

                    // Forward token to your back-end exactly as received
                    token?.let { sendTokenToBackend(it) }
                }
            }
            RESULT_CANCELED -> {
                // The user cancelled the payment
            }
            AutoResolveHelper.RESULT_ERROR -> {
                val status = AutoResolveHelper.getStatusFromIntent(result.data)
                // Handle error
            }
        }
    }

    private fun sendTokenToBackend(token: String) {
        // Send the token to your back-end server.
        // Your back-end will Base64-encode it and call SaleWithGooglePay.
    }
}
```

> [!NOTE]
> For the Google Pay button, you should use the official `PayButton` from the [Google Pay Button API](https://developers.google.com/pay/api/android/guides/brand-guidelines) to ensure compliance with brand guidelines. The example above uses a simple view for clarity.

All other Google Pay fields (button style, additional data requests, etc.) should be implemented according to Google's official guides. The Bpayd-specific requirements are the configuration shown in `GooglePayConfig` and that you forward the **unaltered Google Pay payment token** to your back-end.

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
- For the Google Pay API payment screen on Android, use a separate device to photograph the screen
- **Review [Google Pay brand guidelines examples](https://developers.google.com/pay/api/android/guides/brand-guidelines) to ensure proper button implementation before submitting screenshots**
- Submit all screenshots to Blackstone/Bpayd as part of your integration approval process

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

The Google Pay token you receive in your app is a JSON payload. **Before sending it to the Bpayd API, you must Base64-encode it** and place the result in the `Token` field of the request.

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

This example shows the minimum structure expected by the Bpayd API for a Google Pay sale. You can add any other supported fields as described in the official documentation.

## Testing

Use a **Google Pay TEST environment** (`WalletConstants.ENVIRONMENT_TEST`) with `IsTest: true` when exercising your integration, and rely on Google's official test cards and scenarios:

- Google Pay test cards and scenarios: <https://developers.google.com/pay/api/android/guides/resources/test-card-suite>

> [!NOTE]
> In the TEST environment, debug-signed APKs work. For production, your APK must be signed with a release key and you must obtain your merchant ID from the [Google Pay & Wallet Console](https://pay.google.com/business/console).

## Summary

Integrating Google Pay on Android with Bpayd API involves:

1. **Setup**: Add the Google Pay dependency and configure `AndroidManifest.xml`.
2. **Front-end**: Implement the Google Pay button, check availability, and obtain the payment token.
3. **Back-end**: Encode token to Base64, call `/api/Transactions/SaleWithGooglePay` endpoint.
4. **Handle response**: Process success/failure and update your application accordingly.

The key requirement is to **Base64-encode the Google Pay token** before sending it to the Bpayd API. All other parameters follow standard Bpayd API conventions.

If you also need to support Apple Pay, see the Apple Pay Integration Guide for [Web](apple-pay-web.md), [iOS](apple-pay-ios.md), or [Flutter](apple-pay-flutter.md).
