# Core APIs

Bpayd Core APIs enable direct, server-to-server and hosted checkout capabilities for custom web and mobile applications.

---

## Available Solutions

<div class="grid cards" markdown>

-   :material-api:{ .lg .middle } __API Reference__

    ---

    Explore the complete live API contract, including endpoints, request fields, response models, and examples.

    [:octicons-arrow-right-24: Open API Reference](api-reference/)

-   :material-link-variant:{ .lg .middle } __Payment Links__

    ---

    Generate pre-configured, hosted payment URLs or embed iframes with custom amounts, surcharges, and webhook callbacks.

    [:octicons-arrow-right-24: Payment Links Guide](payment-links.md)

-   :material-cellphone-charging:{ .lg .middle } __ATH Mobile Payment Button__

    ---

    Enable direct ATH Mobile payments on web and mobile checkouts for seamless peer-to-merchant transactions in Puerto Rico.

    [:octicons-arrow-right-24: ATH Mobile Guide](ath-mobile.md)

</div>

---

## Choosing the Right Approach

| Feature | Payment Links | ATH Mobile |
| :--- | :--- | :--- |
| **Hosting Model** | Hosted by Bpayd / Embedded iframe | Native button / deep-link into ATH Mobile app |
| **Supported Methods** | Credit cards, debit cards, tokens | ATH Móvil accounts and registered cards |
| **Integration Effort** | Low (REST API payload) | Low (Button component + webhooks) |
| **Best For** | Invoices, custom checkouts, SMS/Email billing | Regional checkouts, mobile-first flows |
