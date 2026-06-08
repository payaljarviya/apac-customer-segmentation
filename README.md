# APAC E-Commerce Customer Segmentation

In APAC e-commerce — Shopee, Lazada, Tokopedia, Grab — customer acquisition is expensive and the economics of retention are deeply asymmetric. The top 10% of customers typically generate more than half of revenue. Most marketing budgets treat all customers roughly equally. RFM segmentation is the practical fix for that gap.

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![Dataset](https://img.shields.io/badge/Dataset-UCI%20ML%20Repository-00A9CE?style=flat)](https://archive.ics.uci.edu/dataset/352/online+retail)

## The key finding

Champions are about 8% of customers and generate roughly 42% of revenue. That's not unusual for this type of dataset — it's actually the pattern you'd expect — but seeing it in the numbers is still clarifying when you're trying to make the case for a tiered retention strategy.

The more actionable finding: At-Risk customers share a behavioral signature before they churn. High historical frequency and spend, but declining recency. These customers are identifiable and reachable before they're gone. That's where the highest-ROI intervention sits.

| Segment | Share of customers | Share of revenue | Strategy |
|---------|-------------------|-----------------|----------|
| Champions | ~8% | ~42% | VIP program, referrals, early access |
| Loyal | High F and M, moderate R | High | Cross-sell, tier upgrade incentives |
| Potential | Moderate scores, recent buyers | Growing | Onboarding nudges, social proof |
| At Risk | High historical, declining recency | Declining | Win-back now |
| Lost | Low across all three | Minimal | Final attempt or write off |

## How RFM works

Every customer gets scored 1 to 4 on three dimensions:

```
Recency    = Days since last purchase (lower = better = higher score)
Frequency  = Number of unique orders  (higher = better = higher score)
Monetary   = Total spend              (higher = better = higher score)
```

Segments are assigned based on the composite score. The logic is simple enough to explain to any stakeholder, which matters when the output is a marketing playbook rather than a model artifact.

## Running the analysis

```bash
pip install pandas numpy matplotlib seaborn openpyxl
```

Download the [UCI Online Retail Dataset](https://archive.ics.uci.edu/dataset/352/online+retail) and save as `Online Retail.xlsx` in the project folder, then:

```bash
python rfm_segmentation.py
```

Charts go to `output/`, customer-level scores to `output/rfm_segments.csv`.

## Output files

| File | What it shows |
|------|---------------|
| `output/1_segment_overview.png` | Customer count and revenue share by segment |
| `output/2_rfm_distributions.png` | Recency, frequency, and monetary distributions |
| `output/3_segment_heatmap.png` | RFM score profile per segment |
| `output/4_aov_by_segment.png` | Average order value by segment |
| `output/rfm_segments.csv` | Customer-level RFM scores and segment labels |

## The marketing playbook

**Champions.** Protect this segment before trying to grow it. VIP loyalty tier with exclusive early access, referral incentives, and personalised recommendations. These customers are already advocates — the job is to keep them that way.

**At-Risk.** A "we miss you" email with a time-limited offer is a start, but the higher-value move is a short survey — why did they stop? Churn reason data is worth more than any single win-back. If there's no response after the win-back campaign, remove them from active spend. 

**Lost.** One final campaign with a meaningful incentive. If no response, redirect that budget to acquiring the next Potential-tier customer.

Built with Python, pandas, matplotlib, seaborn, and openpyxl.

---

*Payal Jarviya | MBA Candidate, SKK GSB Seoul | AI and Business Analytics + Marketing Analytics*

*Dataset: UCI Online Retail — [archive.ics.uci.edu/dataset/352/online+retail](https://archive.ics.uci.edu/dataset/352/online+retail)*
