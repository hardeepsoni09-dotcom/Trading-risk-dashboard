import pandas as pd
import webbrowser
import plotly.express as px
import plotly.graph_objects as gr
from plotly.subplots import make_subplots

# 1. Load and clean data
df = pd.read_csv('collective2_strategy_trading_record_for_FPStrategy.csv')
# Clean numeric columns safely
df['Trade P/L'] = pd.to_numeric(df['Trade P/L'], errors='coerce')
df['DD $'] = pd.to_numeric(df['DD $'], errors='coerce')

# Parse times & calculate hold metrics
df['Open Time ET'] = pd.to_datetime(df['Open Time ET'])
df['Closed Time ET'] = pd.to_datetime(df['Closed Time ET'])
df['Hold Minutes'] = (df['Closed Time ET'] - df['Open Time ET']).dt.total_seconds() / 60
df['Hour'] = df['Open Time ET'].dt.hour
df['Win'] = df['Trade P/L'] > 0
df = df.sort_values('Open Time ET')
df['Cumulative P/L'] = df['Trade P/L'].cumsum()

# 2. Define Dashboard Layout (3x3 Grid)
fig = make_subplots(
    rows=3, cols=3,
    subplot_titles=(
        'Cumulative P/L Over Time', 'P/L Distribution by Instrument', 'Overall Win Rate',
        'Avg P/L by Hour (ET)', 'Drawdown % vs P/L', 'Total P/L by Instrument',
        'Hold Time Distribution', 'Win Rate by Instrument (%)', 'Key Performance Metrics'
    ),
    specs=[[{"type": "scatter"}, {"type": "box"}, {"type": "pie"}],
           [{"type": "bar"}, {"type": "scatter"}, {"type": "bar"}],
           [{"type": "histogram"}, {"type": "bar"}, {"type": "domain"}]]
)

# --- Row 1 ---
# 1. Cumulative P/L
fig.add_trace(gr.Scatter(x=df['Open Time ET'], y=df['Cumulative P/L'], mode='lines', name='Cum P/L', line=dict(color='navy')), row=1, col=1)

# 2. P/L Boxplot
for symbol in df['Symbol'].unique():
    fig.add_trace(gr.Box(y=df[df['Symbol'] == symbol]['Trade P/L'], name=symbol, boxpoints='outliers'), row=1, col=2)

# 3. Win/Loss Pie
win_counts = df['Win'].value_counts()
fig.add_trace(gr.Pie(labels=['Win', 'Loss'], values=[win_counts.get(True, 0), win_counts.get(False, 0)], marker=dict(colors=['#2ecc71', '#e74c3c'])), row=1, col=3)

# --- Row 2 ---
# 4. Avg P/L by Hour
hourly_avg = df.groupby('Hour')['Trade P/L'].mean().sort_index()
fig.add_trace(gr.Bar(x=hourly_avg.index, y=hourly_avg.values, marker_color=['#2ecc71' if x > 0 else '#e74c3c' for x in hourly_avg.values], name='Hourly Avg'), row=2, col=1)

# 5. Drawdown vs P/L Scatter
fig.add_trace(gr.Scatter(x=df['DD as %'], y=df['Trade P/L'], mode='markers', marker=dict(size=10, color=df['Hold Minutes'], colorscale='Viridis', showscale=True, colorbar=dict(title="Hold Min", x=0.62, y=0.5, len=0.3)), text=df['Symbol']), row=2, col=2)

# 6. Total P/L by Instrument
total_by_symbol = df.groupby('Symbol')['Trade P/L'].sum().sort_values()
fig.add_trace(gr.Bar(x=total_by_symbol.values, y=total_by_symbol.index, orientation='h', marker_color=['#2ecc71' if x > 0 else '#e74c3c' for x in total_by_symbol.values]), row=2, col=3)

# --- Row 3 ---
# 7. Hold Time Histogram
fig.add_trace(gr.Histogram(x=df['Hold Minutes'], nbinsx=20, marker_color='purple'), row=3, col=1)

# 8. Win Rate by Instrument
win_rate = (df.groupby('Symbol')['Win'].mean() * 100).sort_values()
fig.add_trace(gr.Bar(x=win_rate.index, y=win_rate.values, marker_color='teal'), row=3, col=2)

# 9. Summary Stats Table
stats_text = f"""
<b>Total Trades:</b> {len(df)}<br>
<b>Wins / Losses:</b> {win_counts.get(True, 0)} / {win_counts.get(False, 0)}<br>
<b>Net P/L:</b> ${df['Trade P/L'].sum():,.2f}<br>
<b>Avg Win:</b> ${df[df['Win']]['Trade P/L'].mean():,.2f}<br>
<b>Avg Loss:</b> ${df[~df['Win']]['Trade P/L'].mean():,.2f}<br>
<b>Max Win:</b> ${df['Trade P/L'].max():,.2f}<br>
<b>Max Loss:</b> ${df['Trade P/L'].min():,.2f}<br>
<b>Avg Hold:</b> {df['Hold Minutes'].mean():.1f} min<br>
<b>Max DD %:</b> {df['DD as %'].min():.2f}%
"""
# Display the summary text perfectly inside the subplot box
# Display the summary text using global screen coordinates
fig.add_annotation(
    text=stats_text.replace('\n', '<br>'),  # Converts text lines to Plotly format
    xref="paper", yref="paper",              # Tells Plotly to use global screen coordinates
    x=0.82, y=0.02,                          # Dynamically positions it perfectly in the bottom-right corner
    showarrow=False,
    align="left",
    font=dict(family="Courier New, monospace", size=11),
    bordercolor="lightgray",
    borderwidth=1,
    borderpad=10,
    bgcolor="whitesmoke",
    xanchor="left",
    yanchor="bottom"
)
# Update layout styling
fig.update_layout(title_text='FPStrategy Interactive Trading Dashboard', title_font_size=24, height=1000, width=1400, showlegend=False)
fig.write_html('trading_dashboard.html')
import os; os.system('start trading_dashboard.html')