"""
APAC E-Commerce Customer Segmentation — RFM Analysis
======================================================
Author: Payal Jarviya
MBA Candidate | SKK GSB Seoul | AI & Business Analytics

Business Question:
    Which customer segments drive disproportionate revenue — and what
    targeted marketing strategy should each segment receive?

Method: RFM (Recency, Frequency, Monetary) Segmentation
    - Recency:   How recently did the customer purchase?
    - Frequency: How often do they purchase?
    - Monetary:  How much do they spend?

Dataset: UCI Online Retail Dataset
    https://archive.ics.uci.edu/dataset/352/online+retail
    Direct download: https://archive.ics.uci.edu/static/public/352/online+retail.zip

Instructions:
    1. Download the dataset from the link above
    2. Extract and place 'Online Retail.xlsx' in this folder
    3. Run: python rfm_segmentation.py
    4. Results saved to 'output/' folder
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore')

# ─── CONFIG ────────────────────────────────────────────────────────────────────
PALETTE = {
    'Champions':       '#1a3a5c',
    'Loyal Customers': '#2E75B6',
    'Potential':       '#5BA3D9',
    'At Risk':         '#E67E22',
    'Lost':            '#C0392B',
}
NAVY   = '#1a3a5c'
BLUE   = '#2E75B6'
LIGHT  = '#D5E8F0'
RED    = '#C0392B'
GREEN  = '#27AE60'
ORANGE = '#E67E22'
GRAY   = '#666666'
BG     = '#f8f9fa'

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.facecolor': BG,
    'figure.facecolor': 'white',
    'axes.titlesize': 13,
    'axes.titleweight': 'bold',
    'axes.titlepad': 12,
})

os.makedirs('output', exist_ok=True)


# ─── LOAD & CLEAN ─────────────────────────────────────────────────────────────
def load_data(path='Online Retail.xlsx'):
    print(f"\n{'='*60}")
    print("  Loading Online Retail dataset...")
    print(f"{'='*60}")

    df = pd.read_excel(path)
    print(f"  Raw shape: {df.shape[0]:,} rows × {df.shape[1]} columns")

    # Remove cancellations (InvoiceNo starting with 'C')
    df = df[~df['InvoiceNo'].astype(str).str.startswith('C')]

    # Remove rows without CustomerID
    df = df.dropna(subset=['CustomerID'])

    # Remove negative quantities and prices
    df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]

    # Calculate total amount per line
    df['TotalAmount'] = df['Quantity'] * df['UnitPrice']

    # Convert InvoiceDate to datetime
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

    print(f"  Clean shape: {df.shape[0]:,} rows (removed cancellations, nulls, negatives)")
    print(f"  Date range: {df['InvoiceDate'].min().date()} to {df['InvoiceDate'].max().date()}")
    print(f"  Unique customers: {df['CustomerID'].nunique():,}")
    print(f"  Countries: {df['Country'].nunique()}")
    return df


# ─── RFM CALCULATION ──────────────────────────────────────────────────────────
def calculate_rfm(df):
    print("\n  Calculating RFM metrics...")

    snapshot_date = df['InvoiceDate'].max() + pd.DateOffset(days=1)

    rfm = df.groupby('CustomerID').agg({
        'InvoiceDate':  lambda x: (snapshot_date - x.max()).days,  # Recency
        'InvoiceNo':    'nunique',                                  # Frequency
        'TotalAmount':  'sum'                                       # Monetary
    }).reset_index()
    rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']

    # Score 1–4 (4 = best)
    rfm['R_Score'] = pd.qcut(rfm['Recency'],   q=4, labels=[4, 3, 2, 1], duplicates='drop')
    rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), q=4, labels=[1, 2, 3, 4], duplicates='drop')
    rfm['M_Score'] = pd.qcut(rfm['Monetary'],  q=4, labels=[1, 2, 3, 4], duplicates='drop')

    rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)
    rfm['RFM_Total'] = rfm[['R_Score', 'F_Score', 'M_Score']].astype(int).sum(axis=1)

    print(f"  RFM table built: {len(rfm):,} customers scored")
    return rfm


# ─── SEGMENTATION ─────────────────────────────────────────────────────────────
def assign_segments(rfm):
    def segment(row):
        r = int(row['R_Score'])
        f = int(row['F_Score'])
        m = int(row['M_Score'])
        total = r + f + m

        if total >= 10:
            return 'Champions'
        elif total >= 7 and r >= 3:
            return 'Loyal Customers'
        elif total >= 6 and r >= 2:
            return 'Potential'
        elif r <= 2 and total >= 5:
            return 'At Risk'
        else:
            return 'Lost'

    rfm['Segment'] = rfm.apply(segment, axis=1)
    return rfm


# ─── CHART 1: Segment Size & Revenue Share ─────────────────────────────────────
def chart_segment_overview(rfm):
    print("\n[1] Segment Size & Revenue Contribution")

    seg_stats = rfm.groupby('Segment').agg(
        Customers=('CustomerID', 'count'),
        Revenue=('Monetary', 'sum'),
        Avg_Order_Value=('Monetary', 'mean'),
        Avg_Frequency=('Frequency', 'mean'),
        Avg_Recency=('Recency', 'mean')
    ).reset_index()

    total_customers = seg_stats['Customers'].sum()
    total_revenue   = seg_stats['Revenue'].sum()
    seg_stats['Cust_Pct'] = (seg_stats['Customers'] / total_customers * 100).round(1)
    seg_stats['Rev_Pct']  = (seg_stats['Revenue']   / total_revenue   * 100).round(1)

    # Sort by Revenue descending
    seg_stats = seg_stats.sort_values('Revenue', ascending=False)

    print("\n  === SEGMENT SUMMARY ===")
    for _, row in seg_stats.iterrows():
        print(f"  {row['Segment']:18s} | {row['Customers']:5,} customers ({row['Cust_Pct']:4.1f}%) "
              f"| Revenue: ${row['Revenue']:,.0f} ({row['Rev_Pct']:4.1f}%) "
              f"| Avg Order: ${row['Avg_Order_Value']:,.0f}")

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    colors = [PALETTE.get(s, BLUE) for s in seg_stats['Segment']]

    # Chart A: Customer count
    ax = axes[0]
    bars = ax.bar(seg_stats['Segment'], seg_stats['Cust_Pct'], color=colors, edgecolor='white')
    ax.set_title('Customer Distribution by Segment')
    ax.set_ylabel('% of Total Customers', color=GRAY)
    for bar, val in zip(bars, seg_stats['Cust_Pct']):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                f'{val:.1f}%', ha='center', va='bottom', fontsize=9, color=NAVY, fontweight='bold')
    ax.tick_params(axis='x', rotation=15)

    # Chart B: Revenue share
    ax = axes[1]
    wedges, texts, autotexts = ax.pie(
        seg_stats['Revenue'], labels=seg_stats['Segment'],
        autopct='%1.1f%%', colors=colors, startangle=90,
        wedgeprops={'edgecolor': 'white', 'linewidth': 1.5}
    )
    for at in autotexts:
        at.set_fontsize(9)
        at.set_fontweight('bold')
        at.set_color('white')
    ax.set_title('Revenue Share by Segment')

    fig.tight_layout()
    fig.savefig('output/1_segment_overview.png', dpi=150, bbox_inches='tight')
    plt.close(fig)

    # Print the key insight
    champs = seg_stats[seg_stats['Segment'] == 'Champions']
    if not champs.empty:
        print(f"\n  KEY INSIGHT: Champions = {champs['Cust_Pct'].values[0]:.1f}% of customers, "
              f"{champs['Rev_Pct'].values[0]:.1f}% of revenue")

    return seg_stats


# ─── CHART 2: RFM Score Distributions ─────────────────────────────────────────
def chart_rfm_distributions(rfm):
    print("\n[2] RFM Score Distributions")

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    titles = ['Recency (days since last purchase)',
              'Frequency (number of orders)',
              'Monetary Value ($)']
    cols   = ['Recency', 'Frequency', 'Monetary']
    colors_list = [NAVY, BLUE, ORANGE]

    for ax, col, title, color in zip(axes, cols, titles, colors_list):
        data = rfm[col]
        # Cap at 99th percentile for cleaner visualization
        cap = data.quantile(0.99)
        data_capped = data[data <= cap]
        data_capped.hist(bins=40, ax=ax, color=color, edgecolor='white', alpha=0.85)
        ax.axvline(data.mean(),   color=RED,    linestyle='--', linewidth=1.5,
                   label=f'Mean: {data.mean():,.0f}')
        ax.axvline(data.median(), color=GREEN,  linestyle='--', linewidth=1.5,
                   label=f'Median: {data.median():,.0f}')
        ax.set_title(title)
        ax.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig('output/2_rfm_distributions.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  Saved: output/2_rfm_distributions.png")


# ─── CHART 3: Segment Heatmap (Avg RFM by Segment) ───────────────────────────
def chart_segment_heatmap(rfm):
    print("\n[3] Segment Profile Heatmap")

    seg_means = rfm.groupby('Segment')[['R_Score', 'F_Score', 'M_Score']].mean()
    seg_means.columns = ['Recency Score', 'Frequency Score', 'Monetary Score']
    order = ['Champions', 'Loyal Customers', 'Potential', 'At Risk', 'Lost']
    seg_means = seg_means.reindex([s for s in order if s in seg_means.index])

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.heatmap(seg_means, annot=True, fmt='.2f', cmap='Blues',
                linewidths=0.5, ax=ax, vmin=1, vmax=4,
                annot_kws={'size': 11, 'weight': 'bold'})
    ax.set_title('Segment RFM Profile (1=Worst, 4=Best)')
    ax.set_ylabel('')
    ax.set_xlabel('')

    fig.tight_layout()
    fig.savefig('output/3_segment_heatmap.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  Saved: output/3_segment_heatmap.png")


# ─── CHART 4: Average Order Value by Segment ─────────────────────────────────
def chart_aov_by_segment(rfm):
    print("\n[4] Average Order Value by Segment")

    aov = rfm.groupby('Segment')['Monetary'].mean().sort_values(ascending=False)
    order = ['Champions', 'Loyal Customers', 'Potential', 'At Risk', 'Lost']
    aov = aov.reindex([s for s in order if s in aov.index])

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = [PALETTE.get(s, BLUE) for s in aov.index]
    bars = ax.bar(aov.index, aov.values, color=colors, edgecolor='white')
    ax.set_title('Average Customer Lifetime Spend by Segment')
    ax.set_ylabel('Average Total Spend ($)', color=GRAY)

    for bar, val in zip(bars, aov.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                f'${val:,.0f}', ha='center', va='bottom', fontsize=9, color=NAVY, fontweight='bold')

    ax.tick_params(axis='x', rotation=10)
    fig.tight_layout()
    fig.savefig('output/4_aov_by_segment.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  Saved: output/4_aov_by_segment.png")


# ─── MARKETING PLAYBOOK ───────────────────────────────────────────────────────
def print_marketing_playbook(seg_stats):
    playbook = {
        'Champions': {
            'objective':  'Retain, grow, and leverage as advocates',
            'tactics':    ['VIP loyalty tier with exclusive early access', 'Referral program with premium incentives', 'Personalized product recommendations based on purchase history', 'Ask for reviews and testimonials'],
            'kpi':        'Retention rate, referral conversion, share-of-wallet'
        },
        'Loyal Customers': {
            'objective':  'Increase purchase frequency and average order value',
            'tactics':    ['Cross-sell and bundle campaigns', 'Tiered rewards — reward reaching Champion status', 'Birthday / anniversary offers', 'Monthly "loyalty member" exclusive deals'],
            'kpi':        'Frequency increase, AOV uplift'
        },
        'Potential': {
            'objective':  'Convert to Loyal — increase engagement before they disengage',
            'tactics':    ['Onboarding email sequence (if newer customer)', 'Product education content', '"What others bought" social proof campaigns', 'Mild urgency promotions (48hr offers)'],
            'kpi':        'Second purchase rate, frequency increase'
        },
        'At Risk': {
            'objective':  'Win back before they churn permanently',
            'tactics':    ['Re-engagement email: "We miss you" + targeted offer', 'Survey: why did they stop? (insight + re-engagement)', 'Time-limited win-back discount (10-15%)', '"New arrivals since your last visit" campaign'],
            'kpi':        'Win-back rate, re-activation within 60 days'
        },
        'Lost': {
            'objective':  'Attempt reactivation or accept churn',
            'tactics':    ['Final win-back campaign with meaningful incentive', 'If no response, remove from active campaign lists to protect sender reputation', 'Use purchase history to understand why they churned (product, price, experience?)'],
            'kpi':        'Reactivation rate; if <5% — accept as lost and reallocate budget'
        }
    }

    print(f"\n{'='*70}")
    print("  MARKETING STRATEGY PLAYBOOK BY SEGMENT")
    print(f"{'='*70}")

    for seg, p in playbook.items():
        match = seg_stats[seg_stats['Segment'] == seg]
        if not match.empty:
            row = match.iloc[0]
            print(f"\n  [{seg.upper()}]  {row['Customers']:,} customers · {row['Rev_Pct']:.1f}% of revenue")
        else:
            print(f"\n  [{seg.upper()}]")
        print(f"  Objective: {p['objective']}")
        print("  Tactics:")
        for t in p['tactics']:
            print(f"    • {t}")
        print(f"  KPI: {p['kpi']}")

    print(f"\n{'='*70}\n")


# ─── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    df  = load_data()
    rfm = calculate_rfm(df)
    rfm = assign_segments(rfm)

    seg_stats = chart_segment_overview(rfm)
    chart_rfm_distributions(rfm)
    chart_segment_heatmap(rfm)
    chart_aov_by_segment(rfm)
    print_marketing_playbook(seg_stats)

    # Export segment table
    rfm.to_csv('output/rfm_segments.csv', index=False)
    print("  Customer-level RFM data saved: output/rfm_segments.csv")
    print(f"\n  All charts saved to ./output/")
    print("  Next steps:")
    print("  1. Review segment sizes and revenue percentages")
    print("  2. Update README Key Findings table with real numbers")
    print("  3. Use 3 best charts for LinkedIn post")
