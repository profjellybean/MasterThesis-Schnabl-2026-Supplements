import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# 1. Load data with robust naming
try:
    df = pd.read_csv('dspace_data.csv', sep=None, engine='python', header=0, 
                     names=['resource_id', 'start_time', 'end_time', 'workflow_stage', 'wait_time_hours'])
    df['workflow_stage'] = df['workflow_stage'].astype(str).str.strip()
    # Convert start_time to datetime for the timeline
    df['start_time'] = pd.to_datetime(df['start_time'])
    df['month_year'] = df['start_time'].dt.to_period('M').dt.to_timestamp()
except Exception as e:
    print(f"Error loading data: {e}")
    exit()

# --- DASHBOARD 1: DISTRIBUTION & SLA ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))

sns.boxplot(
    data=df, x='workflow_stage', y='wait_time_hours', 
    order=sorted(df['workflow_stage'].unique()), palette="viridis", ax=ax1,
    showmeans=True, fliersize=1, meanprops={"marker":"o", "markerfacecolor":"white", "markeredgecolor":"black"}
)
ax1.set_yscale("log")
ax1.set_title('Distribution & Outliers (Log Scale)', fontsize=14)
ax1.tick_params(axis='x', rotation=15)

sns.ecdfplot(data=df, x='wait_time_hours', hue='workflow_stage', palette="viridis", ax=ax2, linewidth=3)
ax2.set_xscale("log")
ax2.set_title('Cumulative Efficiency (SLA)', fontsize=14)
ax2.grid(True, which="both", ls="-", alpha=0.5)
ax2.axhline(0.5, color='black', linestyle='--', alpha=0.3)
ax2.axhline(0.9, color='red', linestyle='--', alpha=0.3)

plt.suptitle(f'DSpace Workflow Analysis 2023–2025 (Publications: {df["resource_id"].nunique():,})', fontsize=18)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('dspace_analysis_dashboard.png', dpi=300)
print("Dashboard saved: dspace_analysis_dashboard.png")

# --- DASHBOARD 2: PERFORMANCE TRENDS WITH REGRESSION ---
plt.figure(figsize=(15, 8))

# Filter out skipped Step 2 items AND eliminate extreme outliers (> 200 hours)
trend_df = df[~((df['workflow_stage'].str.contains('Step 2') | 
                 df['workflow_stage'].str.contains('FIS -> Library')) & 
                (df['wait_time_hours'] < 0.02)) & 
              (df['wait_time_hours'] <= 200)].copy()

# Define palette and stages to ensure color matching
stages = sorted(trend_df['workflow_stage'].unique())
palette = sns.color_palette("viridis", len(stages))

# Plot monthly medians (faded lines)
sns.lineplot(data=trend_df, x='month_year', y='wait_time_hours', hue='workflow_stage', 
             hue_order=stages, palette=palette, estimator='median', errorbar=None, linewidth=2, alpha=0.3)

slowdown_results = []

# --- STANDARD LINEAR REGRESSION LOOP ---
for i, stage in enumerate(stages):
    stage_data = trend_df[trend_df['workflow_stage'] == stage].groupby('month_year')['wait_time_hours'].median().reset_index()
    
    if not stage_data.empty:
        stage_data['month_ordinal'] = stage_data['month_year'].apply(lambda x: x.toordinal())
        
        # STANDARD LINEAR FIT (No log math)
        slope, intercept = np.polyfit(stage_data['month_ordinal'], stage_data['wait_time_hours'], 1)
        
        line_color = palette[i]
        
        x_range = np.array([stage_data['month_ordinal'].min(), stage_data['month_ordinal'].max()])
        
        # Standard linear line: y = mx + b
        y_trend = slope * x_range + intercept
        
        plt.plot(pd.to_datetime([pd.Timestamp.fromordinal(int(x)) for x in x_range]), 
                 y_trend, 
                 color=line_color, linestyle='--', linewidth=3, 
                 label=f'Trend: {stage}')
        
        # Calculate annual % change based on the starting value of the trendline
        annual_change_hours = slope * 365
        start_val = y_trend[0]
        annual_growth_rate = (annual_change_hours / start_val) * 100 if start_val > 0 else 0
        
        slowdown_results.append({'Stage': stage, 'Annual % Change': annual_growth_rate})

plt.title('Performance Trends: Median Wait Time & Annual Trends (Capped at 200h)', fontsize=16)
plt.ylabel('Median Hours')
plt.grid(True, which="both", ls="-", alpha=0.3)
plt.legend(title='Stage & Trends', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('workflow_trends.png')
print("Trends chart saved: workflow_trends.png (Linear regression included)")

# --- DASHBOARD 3: THE COST OF REJECTION ---
rejected_ids = df[df['workflow_stage'].str.contains('Rejected')]['resource_id'].unique()
df['path_type'] = df['resource_id'].apply(lambda x: 'Rejected at least once' if x in rejected_ids else 'Straight to Archive')

plt.figure(figsize=(10, 6))
lifecycle_costs = df.groupby(['resource_id', 'path_type'])['wait_time_hours'].sum().reset_index()
sns.barplot(data=lifecycle_costs, x='path_type', y='wait_time_hours', palette=['#2ecc71', '#e74c3c'], errorbar=('ci', 95))
plt.title('The Penalty of a Mistake: Total lifecycle hours per item', fontsize=16)
plt.ylabel('Total Hours in System')
plt.savefig('rejection_cost.png')
print("Rejection analysis saved: rejection_cost.png")

# --- TEXT SUMMARY SECTION ---
# --- TEXT SUMMARY SECTION ---
print("\n" + "="*60)
print("DSPACE WORKFLOW PERFORMANCE SUMMARY (2023 - 2025)")
print("="*60)
print(f"TOTAL UNIQUE PUBLICATIONS: {df['resource_id'].nunique():,}")
print("-" * 60)

stats = df.groupby('workflow_stage')['wait_time_hours'].agg(['median', 'mean', 'count']).reset_index()
stats.columns = ['Workflow Stage', 'Median (h)', 'Mean (h)', 'Count']
print(stats.sort_values('Workflow Stage').to_string(index=False))

print("-" * 60)
print("ANNUAL TRENDS (Compound Growth/Decline)")
for res in slowdown_results:
    # Use the new key name 'Annual % Change'
    rate = res['Annual % Change']
    direction = "SLOWER" if rate > 0 else "FASTER"
    print(f"{res['Stage']:<35}: {abs(rate):.1f}% {direction} per year")

print("-" * 60)
bottleneck = df.groupby('workflow_stage')['wait_time_hours'].sum().idxmax()
total_wasted = df.groupby('workflow_stage')['wait_time_hours'].sum().max()
print(f"MOST TOTAL TIME SPENT IN: {bottleneck}")
print(f"Aggregate wait time: {total_wasted:,.0f} business hours.")

avg_cost = lifecycle_costs.groupby('path_type')['wait_time_hours'].mean()
cost_diff = avg_cost['Rejected at least once'] - avg_cost['Straight to Archive']
print("-" * 60)
print(f"HIDDEN COST OF REJECTION: +{cost_diff:.1f} hours per item")
print(f"Items rejected at least once: {len(rejected_ids)} ({len(rejected_ids)/df['resource_id'].nunique()*100:.1f}%)")
print("="*60 + "\n")

# --- WELLNESS CHECK: LIBRARY BYPASS ---
lib_step = df[df['workflow_stage'] == '2. FIS -> Library']
skipped_lib = lib_step[lib_step['wait_time_hours'] < 0.02]

skip_rate = (len(skipped_lib) / len(lib_step)) * 100 if len(lib_step) > 0 else 0

print("-" * 60)
print("DATA WELLNESS CHECK: LIBRARY STEP")
print(f"Total items reaching Library step : {len(lib_step):,}")
print(f"Items skipped/zero-time (< 1.2m)  : {len(skipped_lib):,} ({skip_rate:.1f}%)")
print("-" * 60)

plt.show()