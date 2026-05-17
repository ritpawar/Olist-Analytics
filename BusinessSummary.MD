# Olist E-Commerce — Operations Analytics Summary
**Prepared by:** Rutuja  
**Dataset:** 99,441 orders · Brazil · 2017–2018  
**Tools:** MySQL · Python · Streamlit

---

## Executive Summary
Analysis of 99,000+ Brazilian e-commerce orders reveals strong revenue 
growth driven by volume, but delivery performance in remote states and 
a cluster of underperforming sellers represent the highest operational 
risk to customer satisfaction.

---

## Key Findings

### 1. Revenue grew 4x in 18 months
Gross revenue scaled from R$271K in February 2017 to over R$1.1M by 
mid-2018 — entirely driven by order volume, not higher spending per 
customer. Average order value remained stable at R$147–160 throughout, 
suggesting the growth came from customer acquisition rather than 
upselling. November 2017 saw a sharp spike to R$1.15M, consistent 
with Black Friday demand.

**Recommendation:** Invest in retention — acquiring new customers is 
working, but average order value has room to grow through bundling or 
loyalty incentives.

---

### 2. Northern states deliver twice as slowly as São Paulo
Customers in RR (Roraima), AP (Amapá), and AM (Amazonas) wait an 
average of 27–29 days for delivery, compared to under 12 days in SP 
and MG. Despite this, promised delivery dates are consistently 
conservative — actual deliveries arrive earlier than estimated on 
average — meaning the problem is logistics capacity, not broken 
promises.

**Recommendation:** Partner with regional carriers in northern states 
or set more accurate customer expectations at checkout to reduce 
perceived wait times.

---

### 3. A small group of sellers drives most poor reviews
Several high-volume sellers (100+ orders) maintain average review 
scores below 2.5 out of 5, with poor review rates above 50%. These 
sellers generate significant revenue but damage platform trust. One 
seller processed 108 orders with an average score of 2.27 and 80 
poor reviews.

**Recommendation:** Implement a seller performance threshold — sellers 
below 3.0 average score after 50+ orders should enter a probation 
period with mandatory service improvement targets.

---

### 4. Health & Beauty is the star category
With R$1.24M in revenue and a 4.19 average satisfaction score, Health 
& Beauty leads on both dimensions simultaneously. In contrast, Office 
Furniture generates decent revenue but has the lowest satisfaction 
score (3.52), likely due to shipping damage on bulky items.

**Recommendation:** Prioritise seller recruitment in Health & Beauty. 
Introduce specialist packaging requirements for Office Furniture to 
reduce damage complaints.

---

### 5. Late delivery rate spikes in late 2018
15 weeks exceeded the 10% late delivery threshold, with the worst 
week reaching 29% in early 2018-09. An automated alert system now 
monitors this metric weekly and notifies the operations team when 
the threshold is breached.

**Recommendation:** Investigate the 2018-Q3 spike — likely a carrier 
capacity issue during peak season. Pre-negotiate surge capacity with 
logistics partners ahead of Q4.

---

## Data Quality Notes
- 99,441 orders loaded across 7 related tables
- Zero duplicate order IDs detected
- Zero timestamp logic violations
- 20 orders flagged for payment mismatches — investigated and 
  confirmed as legitimate split-payment transactions

---

*Dashboard available at localhost:8501 · Alert script runs daily at 8AM*
