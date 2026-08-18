# Bpayd Developer Documentation

Welcome to the **Blackstone Merchant Services (Bpayd)** developer documentation. Here you will find step-by-step integration guides, SDK examples, and testing tools to accept and process payments securely.

[🚀 Explore Sandbox](getting-started/sandbox.md){ .md-button .md-button--primary }
[📖 API Reference](core-apis/api-reference/){ .md-button }

---

## What are you building?

Select your development environment to find the relevant guides and code samples:

=== "🌐 Web Applications"

    Integrate checkout experiences into custom websites and single-page apps (React, Vue, Angular, or vanilla JavaScript).

    <div class="grid cards" markdown>

    -   :material-link-variant: __Hosted Payment Links__
        
        Generate secure checkout pages with custom amounts, surcharges, and webhooks.
        
        [:octicons-arrow-right-24: Payment Links Guide](core-apis/payment-links.md)

    -   :material-apple: __Apple Pay on the Web__
        
        Accept 1-click biometric payments in Safari using Apple Pay JS and Bpayd tokens.
        
        [:octicons-arrow-right-24: Apple Pay Web Guide](digital-wallets/apple-pay/web.md)

    -   :material-google: __Google Pay on the Web__
        
        Seamless Google Pay checkout across Chrome, Edge, Safari, and Firefox.
        
        [:octicons-arrow-right-24: Google Pay Web Guide](digital-wallets/google-pay/web.md)

    -   :material-shield-check: __3D Secure 2.0 (Web)__
        
        Add EMV 3DS authentication iframe to reduce fraud and enable liability shift.
        
        [:octicons-arrow-right-24: 3DS Web Guide](security/3d-secure-web.md)

    </div>

=== "📱 Mobile Apps (iOS, Android & Flutter)"

    Accept in-app payments with native digital wallets and regional mobile payment methods.

    <div class="grid cards" markdown>

    -   :material-apple: __Apple Pay for iOS__
        
        Native Swift & Objective-C integration using PassKit framework.
        
        [:octicons-arrow-right-24: iOS Guide](digital-wallets/apple-pay/ios.md)

    -   :material-google: __Google Pay for Android__
        
        Native Kotlin & Java integration using Google Play Services.
        
        [:octicons-arrow-right-24: Android Guide](digital-wallets/google-pay/android.md)

    -   :material-cellphone: __Flutter Cross-Platform__
        
        Unified Apple Pay & Google Pay integration using the official `pay` plugin.
        
        - [:octicons-arrow-right-24: Apple Pay (Flutter)](digital-wallets/apple-pay/flutter.md)
        - [:octicons-arrow-right-24: Google Pay (Flutter)](digital-wallets/google-pay/flutter.md)

    -   :material-cellphone-charging: __ATH Mobile Payment Button__
        
        Direct peer-to-merchant payments for customers in Puerto Rico.
        
        [:octicons-arrow-right-24: ATH Mobile Guide](core-apis/ath-mobile.md)

    -   :material-shield-lock: __3D Secure Mobile SDK__
        
        Mobile 3DS verification and challenge handling for native apps.
        
        [:octicons-arrow-right-24: 3DS Mobile Guide](security/3d-secure-mobile.md)

    </div>

=== "🔌 E-Commerce & Invoicing"

    Connect Bpayd payment processing to your existing platforms with ready-to-use plugins.

    <div class="grid cards" markdown>

    -   :material-cart-outline: __WooCommerce Plugin__
        
        Official WordPress payment gateway supporting credit cards, surcharges, refunds, and 3DS.
        
        [:octicons-arrow-right-24: WooCommerce Setup](plugins/woocommerce.md)

    -   :material-calculator: __Xero Invoicing__
        
        Enable credit card payment options directly on your Xero invoices.
        
        [:octicons-arrow-right-24: Xero Guide](plugins/xero.md)

    -   :material-account-group: __Zoho CRM__
        
        Collect customer payments and manage billing records inside Zoho CRM.
        
        [:octicons-arrow-right-24: Zoho CRM Guide](plugins/zoho.md)

    </div>

---

## Documentation Sections

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } __Getting Started__

    ---

    Testing credentials, test card numbers, and sandbox environment configuration.

    [:octicons-arrow-right-24: Sandbox Environment](getting-started/sandbox.md)

-   :material-api:{ .lg .middle } __Core APIs__

    ---

    Payment Links hosted checkout endpoints and ATH Mobile integration.

    [:octicons-arrow-right-24: Go to Core APIs](core-apis/index.md)

-   :material-wallet:{ .lg .middle } __Digital Wallets__

    ---

    Apple Pay & Google Pay implementation guides for Web, iOS, Android, and Flutter.

    [:octicons-arrow-right-24: Go to Digital Wallets](digital-wallets/index.md)

-   :material-shield-lock:{ .lg .middle } __Security & 3DS__

    ---

    3D Secure 2.0 authentication flows and fraud prevention.

    [:octicons-arrow-right-24: Go to Security](security/index.md)

-   :material-puzzle-outline:{ .lg .middle } __Plugins & CRMs__

    ---

    Ready-made extensions for WooCommerce, Xero, and Zoho CRM.

    [:octicons-arrow-right-24: Go to Plugins](plugins/index.md)

-   :material-tools:{ .lg .middle } __Operations__

    ---

    Specialized workflows such as check payments using stored customer tokens.

    [:octicons-arrow-right-24: Go to Operations](operations/checks-with-token.md)

</div>

---

## Developer Resources

<div class="grid cards" markdown>

-   :material-book-open-page-variant: __API Reference__

    Browse the live REST API contract, request fields, response models, and examples.

    [:octicons-arrow-right-24: Explore the API](core-apis/api-reference/)

-   :material-heart-pulse: __API Status__

    Live system status and uptime monitoring.

    [:octicons-link-external-24: Status Page](https://blackstone.betteruptime.com/){:target="_blank"}

-   :material-package-variant-closed: __.NET NuGet Client__

    Official C# / .NET client library for Bpayd APIs.

    [:octicons-link-external-24: BmsPayClient Package](https://www.nuget.org/packages/BmsPayClient){:target="_blank"}

-   :material-help-circle-outline: __Technical Support__

    Direct developer and merchant account assistance.

    [:octicons-mail-24: Contact Support](mailto:info@blackstonemerchant.com)

</div>
