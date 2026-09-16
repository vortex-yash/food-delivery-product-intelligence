# Executive Summary

## Overview

This Product Intelligence project analyzes a synthetic dataset representing a food delivery marketplace. The analysis covers 60,000 users, over 1.3 million product events, and 94,000+ orders.

The objective is to understand user behavior, identify funnel drop-offs, analyze retention and user segments, monitor product KPIs, and investigate localized conversion deterioration.

## Key Findings

### 1. Global Conversion Funnel

The product funnel shows an overall conversion rate of approximately 24.5% from app open to successful checkout.

The largest relative drop-off occurs between restaurant viewing and adding an item to the cart, indicating an opportunity to investigate restaurant discovery, menu engagement, pricing, and cart-entry friction.

### 2. Localized Checkout Deterioration

Root-cause analysis identified a localized checkout conversion issue.

Overall checkout success is approximately 84.5%, while users on **Android v1.9 in Chicago** have a checkout success rate of **72.79%**.

This represents an approximately **11.7 percentage-point decrease** versus the comparable baseline.

The finding suggests a targeted investigation of the Android v1.9 checkout experience and its interaction with the affected user segment.

### 3. Growth Metrics

- Total Users: 60,000
- Activated Users: approximately 24,000
- Activation Rate: approximately 40%
- Average Order Value (AOV): approximately $24.78
- Completed GMV: approximately $2.34M

## Strategic Recommendations

### Engineering

Investigate the Android v1.9 checkout journey for Chicago users. Compare checkout behavior and failure patterns against other Android versions and cities to isolate the underlying product or technical issue.

### Product

Investigate the view-to-cart drop-off using restaurant, cuisine, pricing, and user-segment dimensions. Potential follow-up analyses include menu engagement, cart-entry behavior, and experiment-driven improvements to the restaurant-to-cart journey.

### Growth

Analyze acquisition channels by user spend segment and repeat-purchase behavior. Use these findings to evaluate which acquisition channels generate users with stronger downstream engagement and completed order value.

## Limitations

- The dataset is fully synthetic and does not represent real company or customer data.
- The RCA anomaly is intentionally injected to demonstrate localized product-diagnostic analysis.
- User spend is used as a behavioral value measure; it should not be interpreted as formal customer lifetime value.
- The analysis identifies correlations and segments requiring investigation but does not establish the underlying technical cause without additional diagnostic data.