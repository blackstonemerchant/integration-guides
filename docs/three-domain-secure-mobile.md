# Blackstone 3DS Service Integration Guide (Mobile)

This guide provides instructions for integrating 3DS authentication into your Blackstone payment system for mobile applications. The 3DS implementation uses an external service (3DS Integrator) for client-side authentication, while Blackstone provides initial authentication credentials and processes the final payment with `SecureData` and `SecureTransactionId`.

## Overview

The mobile 3DS integration process involves:

1. **Blackstone-specific**: Obtain authentication credentials (`ApiKey`, `Token`) from Blackstone API.
2. **External service**: Use 3DS Integrator for mobile authentication flow (`authenticate/browser`, fingerprint/challenge, polling).
3. **Blackstone-specific**: Include `SecureData` and `SecureTransactionId` in final payment requests.

### Quick Path (TL;DR)

1. Backend requests `ApiKey` + `Token` from Blackstone.
2. Mobile builds 3DS payload (card mapping + browser/runtime fields).
3. Mobile calls `POST /v2.2/authenticate/browser`.
4. If fingerprint is required, open web context and submit `threeDSMethodData`.
5. If challenge is required, open web context and submit `creq` to `acsURL`.
6. Extract `transactionId` from provider callback URL.
7. Poll `GET /v2.2/transaction/{transactionId}/updates` until terminal status.
8. Continue payment only if `status` is `Y` or `A`.
9. Send final payment with `SecureData` + `SecureTransactionId`.

## Blackstone-Specific Integration

### Step 1: Obtain API Credentials from Blackstone

Make a request to the Blackstone API to obtain an `ApiKey` and a `Token`, which are required by 3DS Integrator. This request should be performed from your backend for security.

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
  "ApiKey": "...",
  "Token": "...",
  "ResponseCode": 200,
  "Msg": [
    "Operation Successful"
  ],
  "verbiage": null
}
```

## Integration Contracts (Required Before Implementation)

Define these contracts before implementing app flow so mobile, backend, QA, and support use the same data model.

### Token Contract (Blackstone)

**Input:** merchant credentials and app context (`mid`, `UserName`, `Password`, `AppType`, `AppKey`, `cid`).

**Output:**

```json
{
  "ApiKey": "string",
  "Token": "string",
  "ResponseCode": 200
}
```

### 3DS Runtime Result Contract (Normalized)

Use one normalized shape in app/backend telemetry even if provider names differ.

```json
{
  "status": "Y|A|N|U|R|C",
  "transStatusReason": "string",
  "authenticationValue": "string|null",
  "threeDsTransactionId": "string|null"
}
```

### Final Payment Contract (Blackstone Payment API)

When 3DS succeeds (`Y` or `A`), payment payload must include:

```json
{
  "SecureData": "<authenticationValue>",
  "SecureTransactionId": "<threeDsTransactionId>",
  "status": "Y",
  "transStatusReason": "01"
}
```

## 3DS Integrator Implementation

**Important**: Steps 2 and 3 use the external 3DS Integrator service. For protocol-level details, refer to [3DS Integrator Documentation](https://docs.3dsintegrator.com).

### Step 2: Client-Side 3DS Authentication (Mobile)

Using `ApiKey` and `Token` from Step 1, run this sequence.

**Reference mobile runtime configuration**
- `challengeIndicator` is typically `"01"` unless acquirer policy requires another value.
- Endpoints must be environment-based:
  - Sandbox: `https://api-sandbox.3dsintegrator.com/v2.2/authenticate/browser`
  - Production: `https://api.3dsintegrator.com/v2.2/authenticate/browser`
- Required headers:
  - `X-3DS-API-KEY: <ApiKey>`
  - `Authorization: Bearer <Token>`
  - `Accept: application/json`
  - `Content-Type: application/json`
- `threeDSRequestorURL` must use your configured callback domain (for example `https://your-domain/callback`).
- Recommended runtime states:
  - `loadingToken` -> `authenticating` -> `fingerprint` -> `challenge` -> `polling` -> `finished`

1. **Build authentication request (`authenticate/browser`)**

   Purpose: send card + runtime data to obtain initial 3DS branch.

   Inputs:
   - `ApiKey`, `Token`
   - Mapped card fields: `amount`, `pan`, `month`, `year`
   - Browser/runtime fields and `threeDSRequestorURL`

   Action:
   - Call `POST /v2.2/authenticate/browser` with required headers and JSON body.

   Success output:
   - Initial 3DS response with one of these paths:
     - fingerprint data (`methodURL`, `threeDSMethodData`)
     - challenge data (`status = C`, `acsURL`, `creq`)
     - transaction ID only (polling path)
     - final status already available

   Failure handling:
   - Any request/network/token error must stop payment flow and return controlled error.

   Sample request body (simplified):

   ```json
   {
     "challengeIndicator": "01",
     "amount": 25.5,
     "pan": "4111111111111111",
     "month": "12",
     "year": "27",
     "browser": {
       "browserAcceptHeader": "application/json",
       "browserJavaScriptEnabled": true,
       "browserJavaEnabled": false,
       "browserLanguage": "en-US",
       "browserColorDepth": "32",
       "browserTZ": "0",
       "browserScreenWidth": "390",
       "browserScreenHeight": "844",
       "browserUserAgent": "mobile-app-webview-or-runtime-user-agent"
     },
     "threeDSRequestorURL": "https://your-domain/callback"
   }
   ```

2. **Branch initial response**

   Purpose: choose correct next step from provider response.

   Decision rules:
   - If `methodURL` + `threeDSMethodData` exist: run fingerprint.
   - If `status = C` and `acsURL` + `creq` exist: run challenge.
   - If only transaction ID exists: start polling.
   - If terminal `status` is already present: classify directly.

   Failure handling:
   - If response is incomplete for all branches, fail safely and stop payment.

   **What "Open web context" means**
   - Open a dedicated in-app web container for one payment attempt.
   - Keep it isolated per attempt (no cross-attempt session sharing).
   - Enable JavaScript.
   - Enable redirects.
   - Enable URL-change listener to capture provider callback URLs.
   - Add timeout and explicit user-cancel handling.
   - Close only on terminal callback, cancel, timeout, or unrecoverable error.

3. **Execute fingerprint flow (if required)**

   Purpose: complete 3DS method step and capture `transactionId`.

   Inputs:
   - `methodURL`
   - `threeDSMethodData`

   Action:
   - Open web context.
   - Load auto-submit HTML form posting `threeDSMethodData` to `methodURL`.
   - Watch URLs and only process provider callback pattern:
     - `https://response-<env>.3dsintegrator.com/<region>/v2.2/fingerprint/{transactionId}`

   Deterministic transaction extraction:
   - Parse URL.
   - Split path segments.
   - Verify penultimate segment is `fingerprint`.
   - Read last segment as `transactionId`.
   - Validate non-empty UUID-like value.
   - Store as active transaction ID.
   - Start polling only once per new transaction ID (idempotency guard).

   Failure handling:
   - Ignore non-provider URLs, malformed callbacks, and duplicates.
   - If no valid callback arrives before timeout, fail safely.

   Fingerprint auto-submit payload concept:

   ```html
   <form action="<methodURL>" method="POST">
     <input type="hidden" name="threeDSMethodData" value="<threeDSMethodData>" />
   </form>
   ```

   **PSEUDOCODE ONLY — Fingerprint web context + callback watcher**
   ```text
   This is pseudocode for understanding flow; it is not framework-specific production code.

   function runFingerprint(methodURL, threeDSMethodData):
     webCtx = openWebContext(
       isolated = true,
       javascriptEnabled = true,
       redirectsEnabled = true,
       listenUrlChanges = true,
       timeoutSeconds = 120
     )

     html = buildAutoSubmitForm(
       action = methodURL,
       fields = { "threeDSMethodData": threeDSMethodData }
     )
     webCtx.loadHtml(html)

     webCtx.onUrlChange(url):
       if not matchesProviderFingerprintCallback(url):
         return

       txId = extractTransactionId(url, expectedSegment = "fingerprint")
       if txId is invalid:
         return

       if txId == state.activeTransactionId:
         return

       state.activeTransactionId = txId
       startPollingOnce(txId)
   ```

4. **Execute challenge flow (if required)**

   Purpose: complete issuer challenge and capture/confirm final transaction context.

   Inputs:
   - `acsURL`
   - `creq`

   Action:
   - Open web context (isolated, JS enabled, redirects enabled).
   - Load auto-submit HTML posting `creq` to `acsURL`.
   - Track callback URLs matching:
     - `https://response-<env>.3dsintegrator.com/<region>/v2.2/challenge/{transactionId}`

   Deterministic callback handling:
   - Parse URL and split path segments.
   - Verify penultimate segment is `challenge`.
   - Read last segment as callback `transactionId`.
   - Validate non-empty UUID-like value.
   - If callback ID differs from active ID, replace active ID and log transition.
   - Start/continue polling with active ID.

   Failure handling:
   - If user cancels, web context times out, or context errors, end as non-success and do not attempt payment.

   Challenge auto-submit payload concept:

   ```html
   <form action="<acsURL>" method="POST">
     <input type="hidden" name="creq" value="<creq>" />
   </form>
   ```

   **PSEUDOCODE ONLY — Challenge web context + callback tracking**
   ```text
   This is pseudocode for understanding flow; it is not framework-specific production code.

   function runChallenge(acsURL, creq):
     webCtx = openWebContext(
       isolated = true,
       javascriptEnabled = true,
       redirectsEnabled = true,
       listenUrlChanges = true,
       timeoutSeconds = 120
     )

     html = buildAutoSubmitForm(
       action = acsURL,
       fields = { "creq": creq }
     )
     webCtx.loadHtml(html)

     webCtx.onUrlChange(url):
       if not matchesProviderChallengeCallback(url):
         return

       callbackTxId = extractTransactionId(url, expectedSegment = "challenge")
       if callbackTxId is invalid:
         return

       if state.activeTransactionId exists and callbackTxId != state.activeTransactionId:
         logTransition(old = state.activeTransactionId, new = callbackTxId)

       state.activeTransactionId = callbackTxId
       startPollingOnce(callbackTxId)

     webCtx.onCancelOrTimeoutOrError():
       markThreeDSFailed("challenge_cancel_timeout_or_error")
       stopPaymentFlow()
   ```

5. **Poll transaction updates until terminal result**

   Purpose: resolve pending flow and retrieve terminal result.

   Endpoint:
   - `GET /v2.2/transaction/{transactionId}/updates`

   Start conditions:
   - After valid fingerprint callback.
   - After challenge callback (or challenge start if provider requires active polling).
   - After authenticate response when transaction ID already exists.

   Baseline polling policy:
   - Interval: 3 seconds.
   - Max attempts: 10.
   - First fetch immediately before first wait.

   Response handling:
   - `200`: process body (terminal result or challenge requirement).
   - `202` / `404` pending semantics: continue polling.
   - Other status/error: controlled failure, no charge.

   Challenge trigger during polling:
   - If body includes `status = "C"` and `acsURL` + `creq`, pause current polling loop and run challenge flow.

   Stop conditions:
   - Terminal status: `Y`, `A`, `N`, `U`, `R`.
   - Polling timeout.
   - User cancellation.
   - Unrecoverable network/provider error.

   **PSEUDOCODE ONLY — Polling lifecycle**
   ```text
   This is pseudocode for understanding flow; it is not framework-specific production code.

   function pollTransactionUpdates(transactionId):
     interval = 3 seconds
     maxAttempts = 10
     attempts = 0

     while attempts < maxAttempts:
       attempts = attempts + 1
       response = GET /v2.2/transaction/{transactionId}/updates

       if response.status == 200:
         body = response.data
         if requiresChallenge(body):
           runChallenge(body.acsURL, body.creq)
           continue
         if isTerminalStatus(body.status):
           return body

       if response.status in [202, 404]:
         sleep(interval)
         continue

       return failure("polling_error")

     return failure("polling_timeout")
   ```

6. **Classify final authentication result**

   Purpose: apply strict payment continuation policy.

   Decision matrix:

   | `status` | Action |
   |---|---|
   | `Y` | Continue to payment. |
   | `A` | Continue to payment. |
   | `N` | Stop payment (authentication failed). |
   | `U` | Stop payment (authentication unavailable). |
   | `R` | Stop payment (rejected). |
   | `C` | Treat as non-terminal; continue orchestration (challenge/polling), never pay on unresolved `C`. |

   Required captured outputs:
   - `status`
   - `transStatusReason`
   - `authenticationValue`
   - `threeDsTransactionId`

   Note:
   - If provider returns `transStatusReasonDetail`, map it to contract field `transStatusReason`.

7. **Handle failures and resiliency**

   Purpose: prevent invalid charges and duplicate submissions.

   Rules:
   - Token/authenticate/fingerprint/challenge/polling exceptions must end as controlled failure and stop payment.
   - User cancellation is non-success and stops payment.
   - Protect payment submission with idempotency keys.
   - Keep callback and polling processing idempotent by transaction ID.

   Error matrix:

   | Condition | Expected behavior |
   |---|---|
   | Token fetch failure | Stop flow, show recoverable error, no payment request. |
   | Authenticate network error | Stop flow, no payment request. |
   | Fingerprint callback missing/invalid | Timeout -> fail safely. |
   | Challenge canceled by user | Stop flow, no payment request. |
   | Polling timeout | Stop flow, no payment request. |
   | Polling returns unrecoverable error | Stop flow, no payment request. |

### Step 3: Provide Payment Attributes to 3DS (Mobile Data Mapping)

Instead of HTML form attributes, mobile integrations map payment values into the `authenticate/browser` payload.

**Important**: Step 3 does not call a separate endpoint. Step 3 prepares and validates the payload sent in **Step 2.1**.

#### Mapping Inputs to 3DS Fields

| Payment source field/expression | 3DS field | Transformation rule | Required validation |
|---|---|---|---|
| `creditCard.amount` | `amount` | Numeric amount forwarded as number. | Must be `> 0`. |
| `creditCard.cardNumber` | `pan` | Remove spaces/dashes. | Non-empty PAN, valid length by brand. |
| `creditCard.expDate.month` | `month` | Always format as `MM`. | Must not be `00`, must be 01-12. |
| `creditCard.expDate.year` | `year` | Convert to two-digit `YY`. | Must not be `00`, must not be expired. |

#### Execution Sequence (Step 3 -> Step 2.1)

1. Collect raw card/payment input.
2. Normalize `amount`, `pan`, `month`, `year`.
3. Validate required values.
4. Build full authenticate payload, including browser/runtime fields.
5. Send payload in Step 2.1 (`POST /authenticate/browser`).
6. Persist normalized fields and transaction IDs for traceability.

If mapping validation fails:
- Do not send `authenticate/browser`.
- Return user-safe validation error.

Normalization example:

```json
{
  "input": {
    "amount": "25.50",
    "cardNumber": "4111 1111 1111 1111",
    "expMonth": 12,
    "expYear": 2027
  },
  "output": {
    "amount": 25.5,
    "pan": "4111111111111111",
    "month": "12",
    "year": "27"
  }
}
```

Ready-to-send authenticate payload example:

```json
{
  "challengeIndicator": "01",
  "amount": 25.5,
  "pan": "4111111111111111",
  "month": "12",
  "year": "27",
  "browser": {
    "browserAcceptHeader": "application/json",
    "browserJavaScriptEnabled": true,
    "browserJavaEnabled": false,
    "browserLanguage": "en-US",
    "browserColorDepth": "32",
    "browserTZ": "0",
    "browserScreenWidth": "390",
    "browserScreenHeight": "844",
    "browserUserAgent": "mobile-app-webview-or-runtime-user-agent"
  },
  "threeDSRequestorURL": "https://your-domain/callback"
}
```

**PSEUDOCODE ONLY — Build authenticate payload (reference mapping behavior)**
```text
This is pseudocode for understanding flow; it is not framework-specific production code.

function buildThreeDsRequestFromPaymentInput(paymentInput):
  month = paymentInput.creditCard.expDate?.month.toString().padLeft(2, '0') ?? '00'
  year = paymentInput.creditCard.expDate != null
    ? (paymentInput.creditCard.expDate.year % 100).toString().padLeft(2, '0')
    : '00'

  return {
    "pan": paymentInput.creditCard.cardNumber?.replaceAll(' ', '') ?? '',
    "amount": paymentInput.creditCard.amount ?? 0.0,
    "month": month,
    "year": year
  }
```

**PSEUDOCODE ONLY — Build authenticate payload (recommended hardening)**
```text
This is pseudocode for understanding flow; it is not framework-specific production code.

function buildAuthenticatePayloadValidated(rawInput, runtimeContext):
  amount = normalizeAmount(rawInput.amount)
  pan = normalizePan(rawInput.cardNumber)
  month = normalizeMonth(rawInput.expMonth)
  year = normalizeYear(rawInput.expYear)

  if amount <= 0:
    return error("invalid_amount")
  if pan is empty or invalidPanLength(pan):
    return error("invalid_pan")
  if month == '00' or year == '00' or isExpired(month, year):
    return error("invalid_expiration")

  payload = {
    "challengeIndicator": "01",
    "amount": amount,
    "pan": pan,
    "month": month,
    "year": year,
    "browser": runtimeContext.browser,
    "threeDSRequestorURL": runtimeContext.callbackUrl
  }

  return payload
```

**Security notes for mobile mapping:**
- Do not persist PAN/CVV in local storage.
- Do not log `pan`, CVV, bearer token, or `authenticationValue`.
- Fetch `ApiKey`/`Token` from backend only.
- Keep sandbox and production endpoints configurable by environment.

## Blackstone Payment Processing

### Step 4: Include SecureData and SecureTransactionId in Payment Requests

After successful 3DS completion (`status = Y` or `A`), capture:

- `authenticationValue` -> `SecureData`
- `threeDsTransactionId` -> `SecureTransactionId`

Both values must be included in Blackstone payment requests.

Operational rules:
- Payment submission proceeds only after terminal success (`Y` or `A`).
- Any non-success result (including user cancel) must stop payment submission.
- Persist `status` and `transStatusReason` for traceability.

Example payload (simplified):

```json
{
  "amount": 25.50,
  "cardTokenOrPan": "....",
  "expDate": "MMYY",
  "cvv": "***",
  "SecureData": "<authenticationValue>",
  "SecureTransactionId": "<threeDsTransactionId>",
  "status": "Y",
  "transStatusReason": "01"
}
```

Sending `SecureTransactionId` enables 3DS log retrieval in Blackstone Portal for support, fraud analysis, and disputes.

**Required public contracts (APIs/interfaces/types):**

1. Payment API contract must accept and process:
   - `SecureData`
   - `SecureTransactionId`
2. Client payment model must carry:
   - `SecureData`
   - `SecureTransactionId`
   - `status`
   - `transStatusReason`
3. Logging/trace contract must include:
   - `SecureTransactionId` as primary 3DS correlation key
4. Optional backend verification contract must support:
   - `GET /v2.2/transaction/{transactionId}/updates`

### Optional: Verify 3DS Results From Your Backend

If you want backend-side verification, query 3DS Integrator updates using the same session credentials (`ApiKey`, `Token`) and `transactionId`.

**Request example:**

```bash
curl -X GET "https://api.3dsintegrator.com/v2.2/transaction/{transactionId}/updates" \
  -H "X-3DS-API-KEY: <ApiKey>" \
  -H "Authorization: Bearer <Token>"
```

Use response fields (`status`, `transStatusReason`) for server-side validation and risk controls.

Note: `"No result found for transaction as yet"` is typically a transient polling message, not a terminal validation error.

### Step 5: Testing

Validate at least the following scenarios:

| # | Scenario | Expected result |
|---|---|---|
| 1 | Frictionless success (`Y`) | Payment allowed; `SecureData` + `SecureTransactionId` present. |
| 2 | Challenge success (`Y`) | Payment allowed after challenge completion. |
| 3 | Attempted/accepted (`A`) | Payment allowed by strict policy. |
| 4 | Fail (`N`) | Payment blocked. |
| 5 | Unavailable (`U`) | Payment blocked. |
| 6 | Rejected (`R`) | Payment blocked. |
| 7 | Pending then success via polling | Payment allowed only after terminal `Y`/`A`. |
| 8 | Polling timeout | Payment blocked; controlled timeout error. |
| 9 | Token acquisition failure | Payment blocked; controlled auth error. |
| 10 | Network error during challenge/polling | Payment blocked; controlled network error. |
| 11 | User cancellation in challenge | Payment blocked; controlled cancel error. |
| 12 | Final payment payload validation | Request contains both `SecureData` and `SecureTransactionId`. |
| 13 | Portal/support traceability | Transaction retrievable by `SecureTransactionId`. |

## Go-Live (Production Domains and App Environments)

**Important**: Before production launch, coordinate with Blackstone to configure production hostnames/domains used by your payment experience and callback surfaces.

Each hostname must be configured explicitly. Examples:

- `example.com`
- `www.example.com`
- `app.example.com`

Go-live checklist:

1. Configure production 3DS endpoints (`api.3dsintegrator.com`) and production credentials.
2. Confirm callback/requestor domains are registered and reachable.
3. Verify environment separation (sandbox vs production keys and URLs).
4. Validate monitoring for status distribution (`Y`, `A`, `N`, `U`, `R`, timeout).
5. Validate telemetry includes `SecureTransactionId` and terminal status for support workflows.

## Summary

**Blackstone responsibilities:**

- Provide 3DS authentication credentials (`ApiKey`, `Token`) through backend integration.
- Process payments with `SecureData` and `SecureTransactionId`.
- Support portal traceability using `SecureTransactionId`.

**3DS Integrator responsibilities:**

- Execute authentication flow (`authenticate`, fingerprint/challenge, updates).
- Return authentication metadata (`status`, `transStatusReason`, `authenticationValue`, `threeDsTransactionId`).

**Mobile integration responsibilities:**

- Orchestrate the full 3DS flow in-app without framework-specific assumptions.
- Apply strict continuation policy (`Y`/`A` only).
- Ensure payment and logging contracts are complete.

**External documentation**: For advanced flow details and provider-specific nuances, see [docs.3dsintegrator.com](https://docs.3dsintegrator.com).
