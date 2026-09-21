# Interview Guide & Resume Bullets

## Resume Bullets

- **Product Analytics Pipeline:** Built an end-to-end product analytics pipeline using Python and DuckDB to analyze a synthetic food-delivery dataset containing 60,000 users, 1.3M+ events, and 94K+ orders.

- **Root Cause Analysis:** Segmented checkout performance across platform, app version, and city to identify a localized **11.7 percentage-point decrease** in checkout success for Android v1.9 users in Chicago.

- **Advanced SQL Analytics:** Developed funnel, cohort-retention, segmentation, and RCA analyses using CTEs, window functions, conditional aggregation, joins, and date-based transformations.

- **Automated KPI Monitoring:** Developed a Python-based monitoring workflow using z-scores to flag unusual changes in daily checkout success rates.

- **Dashboarding & Visualization:** Built an interactive Streamlit and Plotly dashboard covering product KPIs, funnel performance, checkout RCA, retention cohorts, and user-value segmentation.

- **Data Quality & Testing:** Implemented pytest-based checks covering data validation, funnel metrics, retention, segmentation, RCA, and monitoring logic.

---

## Interview Defensibility (Q&A)

### Q: Why DuckDB instead of Postgres or dbt?

**A:** DuckDB was chosen because it is an analytical OLAP database that works well with local analytical workloads and does not require a database server. It was appropriate for this laptop-scale portfolio project and allowed me to focus on SQL-based product analytics.

I deliberately did not use dbt because the goal of this project was to demonstrate analytical SQL, product metrics, segmentation, and RCA rather than build a production data-transformation framework.

---

### Q: How did you calculate retention?

**A:** I used a cohort-based approach. Users were grouped into **first-active-week cohorts**, based on the first week in which they became active in the product.

I then mapped each user's subsequent activity to activity weeks and calculated the number of active users at each week elapsed since their first active week. This was divided by the original cohort size to obtain weekly retention.

---

### Q: Walk me through the RCA.

**A:** I first looked at the overall checkout success rate and then segmented checkout performance across dimensions such as platform, app version, and city.

This revealed that the **Android v1.9 + Chicago** segment had a checkout success rate of **72.79%**, compared with an overall/comparable baseline of approximately **84.5%** — an approximately **11.7 percentage-point difference**.

The analysis identifies the affected segment, but the available dataset does not contain technical failure reasons. Therefore, the next step would be to work with Engineering to investigate the checkout flow, application logs, payment errors, and other diagnostic data for that segment.

---

### Q: What is the difference between GMV and revenue in this project?

**A:** The dataset contains `order_value`, so I use the sum of completed order values as **Completed GMV**.

I don't label it company revenue because the dataset doesn't model accounting revenue, commissions, taxes, refunds, or other financial components.

---

### Q: Is your "LTV" actually lifetime value?

**A:** No. The project uses **total completed order spend per user** as a behavioral value measure.

I intentionally avoid calling it formal LTV because calculating true customer lifetime value would require assumptions or additional information about customer lifetime, future purchases, margins, retention, and potentially acquisition costs.

---

### Q: How did you identify the largest funnel drop-off?

**A:** I calculated conversion between consecutive stages of the session-level funnel:

App Open → Search → View Restaurant → Add to Cart → Checkout Start → Checkout Success.

For each step, I divided the number of sessions reaching the next stage by the number reaching the previous stage.

I then compared these consecutive-stage conversion rates to identify the largest relative drop-off in the funnel.

---

### Q: How does the anomaly monitoring work?

**A:** The monitoring script calculates the daily checkout success rate and compares each day's rate with the historical mean and standard deviation.

A z-score is then calculated for each day. Days with an absolute z-score above the configured threshold are flagged for investigation.

The monitoring is designed to detect unusual global movement, while the RCA analysis provides a second layer for identifying localized segment-level problems.

---

### Q: What would you do if Engineering asked you to investigate the Android v1.9 issue further?

**A:** I would break the problem down further by:

1. Checking the affected segment's funnel stage-by-stage.

2. Comparing Android v1.9 against other Android versions in Chicago.

3. Comparing Chicago against other cities for Android v1.9.

4. Examining checkout failure/error codes if available.

5. Checking whether the issue is concentrated in specific restaurant, payment, or user segments.

6. Validating the finding over time to determine when the deterioration started.

7. Working with Engineering to identify and validate the underlying technical cause.