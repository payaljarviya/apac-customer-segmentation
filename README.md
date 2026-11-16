# Customer Segmentation with RFM

Customer acquisition is expensive and the economics of retention are asymmetric: a minority of customers carry most of the value. Most marketing budgets treat all customers roughly equally. RFM segmentation is the practical fix for that gap.

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![Dataset](https://img.shields.io/badge/Dataset-UCI%20ML%20Repository-00A9CE?style=flat)](https://archive.ics.uci.edu/dataset/352/online+retail)

## The data

UCI Online Retail. A **UK-based online retailer**, December 2010 to December 2011. This is not an APAC dataset, and an earlier version of this README described it as one. It is corrected here.

541,909 raw transaction rows cleaned to **397,884**, covering **4,338 customers**. Removed: cancellations (invoice numbers beginning with C), rows with no customer ID, and rows with nonpositive quantity or unit price.

## The key finding

**Champions are 29.2% of customers and hold 76.8% of positive transaction value.**

The more actionable finding is At Risk: high historical frequency and spend, but declining recency. These customers are identifiable and reachable before they are gone, and that is where the highest-return intervention sits. They are 14.2% of customers holding 6.9% of value.

| Segment | Customers | Share of customers | Share of value | Strategy |
|---------|-----------|-------------------|----------------|----------|
| Champions | 1,268 | 29.2% | 76.8% | VIP program, referrals, early access |
| Potential | 833 | 19.2% | 8.4% | Onboarding nudges, social proof |
| Loyal | 717 | 16.5% | 5.7% | Cross-sell, tier upgrade incentives |
| At Risk | 614 | 14.2% | 6.9% | Win-back now, plus a churn-reason survey |
| Lost | 906 | 20.9% | 2.2% | One final attempt, or write off |

**"Share of value" means positive transaction value after the exclusions above.** It is not net revenue. Cancellations and returns are excluded rather than netted, because netting lets a returned order cancel a genuine one and understates a customer's actual purchasing behaviour.

## How RFM works

Every customer is scored 1 to 4 on three dimensions, by quartile:

```
Recency    = Days since last purchase (lower = better = higher score)
Frequency  = Number of unique orders  (higher = better = higher score)
Monetary   = Total spend              (higher = better = higher score)
```

Segments come from the composite total (3 to 12):

```
total >= 10                    -> Champions
total >= 7  and Recency >= 3   -> Loyal
total >= 6  and Recency >= 2   -> Potential
Recency <= 2 and total >= 5    -> At Risk
otherwise                      -> Lost
```

These thresholds are a judgment call, not a standard. A stricter Champions rule produces a smaller group holding a smaller share of value. The rule above is stated explicitly so the numbers in this README are reproducible from the script.

The logic is simple enough to explain to any stakeholder, which matters when the output is a marketing playbook rather than a model artifact.

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
| `output/1_segment_overview.png` | Customer count and value share by segment |
| `output/2_rfm_distributions.png` | Recency, frequency, and monetary distributions |
| `output/3_segment_heatmap.png` | RFM score profile per segment |
| `output/4_aov_by_segment.png` | Average order value by segment |
| `output/rfm_segments.csv` | Customer-level RFM scores and segment labels |

## The marketing playbook

**Champions.** Protect this segment before trying to grow it. VIP loyalty tier with exclusive early access, referral incentives, and personalised recommendations. These customers are already advocates and the job is to keep them that way.

**At Risk.** A win-back email with a time-limited offer is a start, but the higher-value move is a short survey asking why they stopped. Churn reason data is worth more than any single win-back campaign. If there is no response, remove them from active spend.

**Lost.** One final campaign with a meaningful incentive. If no response, redirect that budget to acquiring the next Potential-tier customer.

## Limitations

- One retailer, one market, thirteen months. Segment proportions will not transfer to a different business.
- RFM uses transaction history only. It says nothing about why a customer behaves as they do, which is what the At Risk survey above is for.
- The segment thresholds are set by hand rather than learned from the data.

Built with Python, pandas, matplotlib, seaborn, and openpyxl.

---

*Payal Jarviya | MBA Candidate, SKK GSB Seoul | AI and Business Analytics + Marketing Analytics*

*Dataset: UCI Online Retail, [archive.ics.uci.edu/dataset/352/online+retail](https://archive.ics.uci.edu/dataset/352/online+retail)*
