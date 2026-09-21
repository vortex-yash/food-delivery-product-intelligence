# Executive Summary

## Overview

This Product Intelligence project analyzes a synthetic dataset representing a food delivery marketplace. The analysis covers 60,000 users, over 1.3 million product events, and 94,000+ orders.

The objective is to understand user behavior, identify funnel drop-offs, analyze retention and user segments, monitor product KPIs, and investigate localized conversion deterioration.

## Key Findings

### 1. Global Conversion Funnel

The product funnel shows an overall conversion rate of **24.48%** from app open to successful checkout.

| Funnel Stage | Sessions |
|---|---:|
| App Open | 386,679 |
| Search | 329,001 |
| Restaurant View | 246,991 |
| Add to Cart | 160,367 |
| Checkout Start | 112,072 |
| Checkout Success | 94,650 |

The largest relative drop-off occurs between **restaurant viewing and adding an item to the cart**, indicating an opportunity to investigate restaurant discovery, menu engagement, pricing, and cart-entry friction.

### 2. Localized Checkout Deterioration

Root-cause analysis identified a localized checkout conversion signal.

Overall checkout success is approximately **84.5%**, while users on **Android v1.9 in Chicago** have a checkout success rate of **72.79%**.

This represents an approximately **11.7 percentage-point difference** versus the comparable baseline.

The finding identifies a targeted segment for further investigation of the Android v1.9 checkout experience and its interaction with the affected user segment. It does not establish the underlying technical cause.

### 3. Growth & Monetization Metrics

- **Total Users:** 60,000
- **Activated Users:** 46,375
- **Activation Rate:** 77.29%
- **Repeat Purchase Rate:** 56.62%
- **Average Order Value (AOV):** $22.94
- **Total Completed GMV:** $2,064,110.22

These metrics provide a high-level view of activation, repeat purchasing, and monetization performance in the synthetic dataset.

### 4. User Spend Segmentation

Users are divided into three approximately equal-sized groups using `NTILE(3)` based on total completed-order spend.

| Segment | Completed Spend |
|---|---:|
| Low Value | ≤ $15.79 |
| Medium Value | > $15.79 and ≤ $42.32 |
| High Value | > $42.32 |

Each segment contains approximately 20,000 users.

This data-driven approach avoids arbitrary fixed spending thresholds and allows downstream behaviour to be compared across balanced user groups.

## Strategic Recommendations

### Engineering

Investigate the Android v1.9 checkout journey for Chicago users. Compare checkout behavior and failure patterns against other Android versions and cities to isolate potential product or technical issues.

### Product

Investigate the restaurant-view → add-to-cart drop-off using restaurant, cuisine, pricing, and user-segment dimensions. Potential follow-up analyses include menu engagement, cart-entry behavior, and experiment-driven improvements to the restaurant-to-cart journey.

### Growth

Analyze acquisition channels by user spend segment and repeat-purchase behavior. Compare channels using downstream metrics such as activation, repeat purchase, completed orders, and spend behaviour rather than acquisition volume alone.

## Limitations

- The dataset is fully synthetic and does not represent real company or customer data.
- The RCA anomaly is intentionally injected to demonstrate localized product-diagnostic analysis.
- User spend is used as a behavioural value measure; it should not be interpreted as formal customer lifetime value.
- The analysis identifies correlations and segments requiring investigation but does not establish the underlying technical cause without additional diagnostic data.
- The project metrics are based on the generated dataset and should not be interpreted as real-world food-delivery business performance.