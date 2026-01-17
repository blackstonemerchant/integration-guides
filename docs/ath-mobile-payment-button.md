# Developer Guide for checkout using ATH Mobile Payment Button in Blackstone

## Overview

ATH Mobile Payment Button integration extends the existing Blackstone Payment Links functionality to include ATH Mobile as an additional payment method option. **The entire process remains identical to standard Payment Links** - same API endpoints, same request/response structures, and same implementation workflow.

**Prerequisites:** This guide assumes familiarity with Blackstone Payment Links. For complete details on Payment Links structure, API endpoints, error codes, and implementation workflow, refer to the [**Developer Guide for checkout using BlackStone Payment Integration - Payment Links**](payment-links.md).

## What Makes ATH Mobile Different

ATH Mobile integration has only **one key difference** from standard Payment Links: it provides customers with an additional payment method option in the payment interface. All other functionality remains unchanged.

## Configuration

### Business Settings Setup

Before ATH Mobile appears as a payment option, configure it in the Blackstone portal:

1. Navigate to **Business Settings** > **Other** > **Allowed Payment Methods**
2. Enable ATH Mobile as a payment method for Payment Links
3. Enter your **ATH Mobile Public Token** (from your ATH Mobile merchant account)
4. Save configuration

### Required Credentials

**ATH Mobile Public Token:** Your ATH Mobile merchant account public token  
*Configure in:* Business Settings > Other > Allowed Payment Methods

## Implementation

**No changes required.** Use the exact same Payment Links API endpoints and workflows documented in the [Payment Links guide](payment-links.md).

## Quick Setup Checklist

- [ ] Complete standard Payment Links setup
- [ ] Obtain ATH Mobile merchant account and public token  
- [ ] Configure ATH Mobile in Business Settings > Other > Allowed Payment Methods
- [ ] Test Payment Link - verify ATH Mobile appears as payment option
- [ ] Verify payment completion and status updates work correctly

## Support

- **Payment Links functionality**: Use standard Payment Links documentation
- **ATH Mobile configuration**: Contact Blackstone support  
- **ATH Mobile payment processing**: Contact ATH Mobile support

---

**Summary:** ATH Mobile integration requires only portal configuration. Your existing Payment Links code needs no modifications - ATH Mobile simply appears as an additional payment method option for customers.
