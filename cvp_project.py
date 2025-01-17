# Install dependencies
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

required_packages = ['streamlit', 'numpy', 'matplotlib']
for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        install(package)
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import subprocess




# Title
st.title("Disney Strategy Decision Toolbox with Fully Dynamic Growth Rates")

# Segment Definitions
segments = ['Streaming Media', 'Parks & Experiences', 'Consumer Products', 'Box Office']
benchmarks = {
    'Streaming Media': {'best': 0.25, 'baseline': 0.15, 'worst': 0.05},
    'Parks & Experiences': {'best': 0.10, 'baseline': 0.07, 'worst': 0.03},
    'Consumer Products': {'best': 0.05, 'baseline': 0.03, 'worst': 0.01},
    'Box Office': {'best': 0.07, 'baseline': 0.05, 'worst': 0.03}
}

# Input Revenue and Costs for Each Segment
st.header("Input Revenue and Costs for Each Segment")
current_revenue = {}
fixed_costs = {}
variable_cost_per_unit = {}
sales_price_per_unit = {}
projected_sales_volume = {}

def input_segment_data(segment):
    current_revenue[segment] = st.number_input(f"{segment} Revenue Forecast ($B)", value=1.0, step=0.1)
    fixed_costs[segment] = st.number_input(f"Fixed Costs for {segment} ($M)", value=500.0, step=10.0)
    variable_cost_per_unit[segment] = st.number_input(f"Variable Cost per Unit for {segment} ($)", value=50.0, step=1.0)
    sales_price_per_unit[segment] = st.number_input(f"Sales Price per Unit for {segment} ($)", value=100.0, step=1.0)
    projected_sales_volume[segment] = st.number_input(f"Projected Sales Volume for {segment} (units)", value=100000, step=1000)

for segment in segments:
    st.subheader(segment)
    input_segment_data(segment)

# Competitor Data Input
st.header("Competitor Revenue Inputs and Growth Rates")
competitors = ['Netflix', 'Universal', 'Paramount', 'Warner Bros.']
competitor_revenue = {}
competitor_growth_rates = {}

for competitor in competitors:
    competitor_revenue[competitor] = st.number_input(f"{competitor} Annual Revenue Forecast ($B)", value=100.0, step=1.0)
    competitor_growth_rates[competitor] = st.slider(f"{competitor} Annual Growth Rate (%)", min_value=0.0, max_value=100.0, value=4.0) / 100

# Disney Growth Rate Adjustments
st.header("Adjust Disney Growth Rates for Each Segment and Scenario")
disney_segment_growth_rates = {}

for segment in segments:
    disney_segment_growth_rates[segment] = {
        'Best-case': st.slider(f"{segment} Best-case Growth Rate (%)", min_value=0.0, max_value=100.0, value=5.0) / 100,
        'Baseline': st.slider(f"{segment} Baseline Growth Rate (%)", min_value=0.0, max_value=100.0, value=3.0) / 100,
        'Worst-case': st.slider(f"{segment} Worst-case Growth Rate (%)", min_value=0.0, max_value=10.0, value=1.0) / 100
    }

# Calculation Functions
@st.cache_data
def calculate_cvp(fixed_costs, variable_cost, price, volume):
    cm_per_unit = price - variable_cost
    breakeven_volume = fixed_costs / cm_per_unit if cm_per_unit > 0 else float('inf')
    revenue = price * volume
    total_variable_cost = variable_cost * volume
    total_costs = fixed_costs + total_variable_cost
    profit = revenue - total_costs
    return cm_per_unit, breakeven_volume, revenue, total_costs, profit

results = {}
cvp_results = {}

for segment in segments:
    # Revenue Scenarios
    growth_rates = benchmarks[segment]
    current = current_revenue[segment]
    results[segment] = {
        'Best-case': current * (1 + growth_rates['best']),
        'Baseline': current * (1 + growth_rates['baseline']),
        'Worst-case': current * (1 + growth_rates['worst'])
    }

    # CVP Calculations
    cm, bev, rev, tc, profit = calculate_cvp(
        fixed_costs[segment] * 1e6,  # Convert to dollars
        variable_cost_per_unit[segment],
        sales_price_per_unit[segment],
        projected_sales_volume[segment]
    )
    cvp_results[segment] = {
        'Contribution Margin': cm,
        'Breakeven Volume': bev,
        'Projected Revenue': rev / 1e6,  # Convert to millions
        'Total Costs': tc / 1e6,
        'Profit': profit / 1e6
    }

# Generate Disney Trends
years = np.arange(2025, 2030)
disney_trends = {
    scenario: [
        sum(
            results[segment][scenario] * (1 + i * disney_segment_growth_rates[segment][scenario])
            for segment in segments
        )
        for i in range(len(years))
    ]
    for scenario in ['Best-case', 'Baseline', 'Worst-case']
}

# Generate Competitor Trends
competitor_trends = {
    comp: [competitor_revenue[comp] * (1 + i * competitor_growth_rates[comp]) for i in range(len(years))]
    for comp in competitors
}

# Visualization
st.header("Visualize Revenue Scenarios and Trends")

# Line Chart for Competitor Trends
fig_trend, ax_trend = plt.subplots(figsize=(12, 6))

# Plot Disney Trends
for scenario, trend in disney_trends.items():
    ax_trend.plot(years, trend, label=f'Disney {scenario}', marker='o', linestyle='--')

# Plot Competitor Trends
for competitor, trend in competitor_trends.items():
    ax_trend.plot(years, trend, label=f'{competitor} Trend', marker='x', linestyle='-')

ax_trend.set_title("Revenue Trends: Disney vs Competitors")
ax_trend.set_xlabel("Years")
ax_trend.set_ylabel("Revenue ($B)")
ax_trend.legend()
ax_trend.grid(axis='y', linestyle='--', linewidth=0.7)
st.pyplot(fig_trend)

# Bar Chart for Disney Revenue Scenarios
x = np.arange(len(segments))
width = 0.2
best_case = [results[seg]['Best-case'] for seg in segments]
baseline = [results[seg]['Baseline'] for seg in segments]
worst_case = [results[seg]['Worst-case'] for seg in segments]

fig_bar, ax_bar = plt.subplots(figsize=(12, 6))
ax_bar.bar(x - width, best_case, width, label='Best-case', color='green', hatch='/')
ax_bar.bar(x, baseline, width, label='Baseline', color='blue', hatch='\\')
ax_bar.bar(x + width, worst_case, width, label='Worst-case', color='red', hatch='*')
ax_bar.set_xticks(x)
ax_bar.set_xticklabels(segments)
ax_bar.set_title("Disney Revenue Scenarios by Segment")
ax_bar.set_xlabel("Segments")
ax_bar.set_ylabel("Revenue ($B)")
ax_bar.legend()
st.pyplot(fig_bar)

# Pie Chart for Cost Distribution
st.header("Cost Distribution")
fig_pie, ax_pie = plt.subplots()
total_costs = [cvp_results[seg]['Total Costs'] for seg in segments]
ax_pie.pie(total_costs, labels=segments, autopct='%1.1f%%', startangle=90)
ax_pie.set_title("Cost Distribution by Segment")
st.pyplot(fig_pie)

st.write("Best Decision tool for Disney Strategy Planning")

