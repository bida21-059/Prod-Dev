from dash import Dash, html, dcc, Input, Output, no_update
import pandas as pd
from data_processor import get_data
from visualizations import generate_best_selling_products, generate_sales_by_traffic_source, generate_revenue_patterns, generate_regional_sales_insights, generate_conversion_rate, generate_predictive_sales_forecast, generate_peak_inquiry_periods, generate_regional_product_demand, generate_salesperson_revenue_forecast
import plotly.graph_objects as go
import os
from datetime import datetime

app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=['/assets/styles.css'])

# Load data
data = get_data()
df = data['raw']
model = data['model']

# Set default date range safely
if not df.empty and 'timestamp' in df.columns:
    start_date = df['timestamp'].min().date()
    end_date = df['timestamp'].max().date()
else:
    start_date = datetime(2025, 2, 1).date()
    end_date = datetime(2025, 5, 18).date()

# Generate valid dropdown options, excluding null values
salesperson_options = [{'label': 'Whole Sales Team', 'value': 'Whole Sales Team'}] + \
                     [{'label': str(s), 'value': str(s)} for s in df['team_member_id'].unique() if s is not None and pd.notna(s)]
if len(salesperson_options) == 1:  # Only 'Whole Sales Team' exists
    salesperson_options.append({'label': 'No Salespeople', 'value': 'None', 'disabled': True})

# Layout with navbar and tabs
app.layout = html.Div([
    # Navbar
    html.Div([
        html.H1("AI-Solutions Sales Performance Dashboard", style={'display': 'inline-block', 'fontSize': '24px', 'margin': '10px'}),
        html.Div([
            dcc.Tabs(id='tabs', value='visualizations', children=[
                dcc.Tab(label='Visualizations', value='visualizations', className='dash-tab'),
                dcc.Tab(label='KPI Cards', value='kpi-cards', className='dash-tab'),
            ], style={'display': 'inline-block'})
        ], className='dash-tabs')
    ], style={'backgroundColor': '#34495e', 'color': 'white', 'padding': '10px', 'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}),
    
    # Filters (compact, single row)
    html.Div([
        dcc.DatePickerRange(
            id='date-filter',
            start_date=start_date,
            end_date=end_date,
            display_format='MM/DD/YYYY',
            style={'display': 'inline-block', 'marginRight': '10px', 'fontSize': '12px'}
        ),
        dcc.Dropdown(
            id='country-filter',
            options=[{'label': str(c), 'value': str(c)} for c in df['country'].unique() if c is not None and pd.notna(c)],
            value='All',
            multi=False,
            placeholder="Select Country",
            style={'display': 'inline-block', 'width': '150px', 'verticalAlign': 'middle', 'marginRight': '10px', 'fontSize': '12px'}
        ),
        dcc.Dropdown(
            id='salesperson-filter',
            options=salesperson_options,
            value='Whole Sales Team',
            multi=False,
            placeholder="Select Salesperson",
            style={'display': 'inline-block', 'width': '150px', 'verticalAlign': 'middle', 'fontSize': '12px'}
        )
    ], style={'textAlign': 'center', 'margin': '10px 0', 'height': '40px'}),
    
    # Tab content
    html.Div(id='tab-content')
], style={'backgroundColor': '#f9f9f9', 'padding': '10px', 'height': '100vh', 'overflow': 'auto'})

# Callback to render tab content
@app.callback(
    Output('tab-content', 'children'),
    [Input('tabs', 'value'),
     Input('date-filter', 'start_date'),
     Input('date-filter', 'end_date'),
     Input('country-filter', 'value'),
     Input('salesperson-filter', 'value')]
)
def render_tab_content(tab, start_date, end_date, country, salesperson):
    # Handle None or invalid inputs
    if not start_date or not end_date or df is None or df.empty:
        return html.Div("No data available", style={'textAlign': 'center', 'margin': '20px', 'fontSize': '16px'})

    filtered_df = df[
        (df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)
    ]
    if country != 'All':
        filtered_df = filtered_df[filtered_df['country'] == country]
    if salesperson != 'Whole Sales Team' and salesperson != 'None':
        filtered_df = filtered_df[filtered_df['team_member_id'] == salesperson]
    
    if tab == 'visualizations':
        return html.Div([
            # 3x3 grid for visualizations
            html.Div([
                html.Div([
                    dcc.Graph(id='best-selling-products', figure=generate_best_selling_products(filtered_df), style={'height': '200px'})
                ], style={'display': 'inline-block', 'width': '32%', 'verticalAlign': 'top', 'marginRight': '1%'}),
                html.Div([
                    dcc.Graph(id='sales-by-traffic-source', figure=generate_sales_by_traffic_source(filtered_df), style={'height': '200px'})
                ], style={'display': 'inline-block', 'width': '32%', 'verticalAlign': 'top', 'marginRight': '1%'}),
                html.Div([
                    dcc.Graph(id='revenue-patterns', figure=generate_revenue_patterns(filtered_df), style={'height': '200px'})
                ], style={'display': 'inline-block', 'width': '32%', 'verticalAlign': 'top'}),
                html.Div([
                    dcc.Graph(id='regional-sales', figure=generate_regional_sales_insights(filtered_df), style={'height': '200px'})
                ], style={'display': 'inline-block', 'width': '32%', 'verticalAlign': 'top', 'marginRight': '1%'}),
                html.Div([
                    dcc.Graph(id='conversion-rate', figure=generate_conversion_rate(filtered_df), style={'height': '200px'})
                ], style={'display': 'inline-block', 'width': '32%', 'verticalAlign': 'top', 'marginRight': '1%'}),
                html.Div([
                    dcc.Graph(id='predictive-sales', figure=generate_predictive_sales_forecast(filtered_df), style={'height': '200px'})
                ], style={'display': 'inline-block', 'width': '32%', 'verticalAlign': 'top'}),
                html.Div([
                    dcc.Graph(id='peak-inquiry-periods', figure=generate_peak_inquiry_periods(filtered_df), style={'height': '200px'})
                ], style={'display': 'inline-block', 'width': '32%', 'verticalAlign': 'top', 'marginRight': '1%'}),
                html.Div([
                    dcc.Graph(id='regional-product-demand', figure=generate_regional_product_demand(filtered_df), style={'height': '200px'})
                ], style={'display': 'inline-block', 'width': '32%', 'verticalAlign': 'top', 'marginRight': '1%'}),
                html.Div([
                    dcc.Graph(id='salesperson-revenue-forecast', figure=generate_salesperson_revenue_forecast(filtered_df), style={'height': '200px'})
                ], style={'display': 'inline-block', 'width': '32%', 'verticalAlign': 'top'})
            ], style={'padding': '5px', 'textAlign': 'center'})
        ])
    elif tab == 'kpi-cards':
        # Calculate KPI metrics
        total_revenue = filtered_df['revenue'].sum() if not filtered_df.empty else 0
        total_inquiries = len(filtered_df)
        total_conversions = filtered_df['is_conversion'].sum() if not filtered_df.empty else 0
        conversion_rate = (total_conversions / total_inquiries * 100) if total_inquiries > 0 else 0
        top_product = filtered_df.groupby('product')['revenue'].sum().idxmax() if not filtered_df.empty else 'N/A'
        top_salesperson = filtered_df.groupby('team_member_id')['revenue'].sum().idxmax() if not filtered_df.empty and filtered_df['team_member_id'].notna().any() else 'N/A'
        
        return html.Div([
            # 2x2 grid for KPI cards
            html.Div([
                html.Div([
                    html.H3(f"${total_revenue:,.0f}", style={'fontSize': '20px', 'margin': '10px'}),
                    html.P("Total Revenue", style={'fontSize': '14px', 'margin': '10px'})
                ], className='kpi-card')
            ], style={'display': 'inline-block', 'width': '24%', 'verticalAlign': 'top', 'marginRight': '1%'}),
            html.Div([
                html.Div([
                    html.H3(f"{conversion_rate:.2f}%", style={'fontSize': '20px', 'margin': '10px'}),
                    html.P("Conversion Rate", style={'fontSize': '14px', 'margin': '10px'})
                ], className='kpi-card')
            ], style={'display': 'inline-block', 'width': '24%', 'verticalAlign': 'top', 'marginRight': '1%'}),
            html.Div([
                html.Div([
                    html.H3(top_product, style={'fontSize': '20px', 'margin': '10px'}),
                    html.P("Top Product", style={'fontSize': '14px', 'margin': '10px'})
                ], className='kpi-card')
            ], style={'display': 'inline-block', 'width': '24%', 'verticalAlign': 'top', 'marginRight': '1%'}),
            html.Div([
                html.Div([
                    html.H3(top_salesperson, style={'fontSize': '20px', 'margin': '10px'}),
                    html.P("Top Salesperson", style={'fontSize': '14px', 'margin': '10px'})
                ], className='kpi-card')
            ], style={'display': 'inline-block', 'width': '24%', 'verticalAlign': 'top'})
        ], style={'padding': '5px', 'textAlign': 'center'})
    
    return html.Div("Invalid tab selected", style={'textAlign': 'center', 'margin': '20px', 'fontSize': '16px'})

# Callback for visualizations (only triggered for visualizations tab)
@app.callback(
    [Output('best-selling-products', 'figure'),
     Output('sales-by-traffic-source', 'figure'),
     Output('revenue-patterns', 'figure'),
     Output('regional-sales', 'figure'),
     Output('conversion-rate', 'figure'),
     Output('predictive-sales', 'figure'),
     Output('peak-inquiry-periods', 'figure'),
     Output('regional-product-demand', 'figure'),
     Output('salesperson-revenue-forecast', 'figure')],
    [Input('date-filter', 'start_date'),
     Input('date-filter', 'end_date'),
     Input('country-filter', 'value'),
     Input('salesperson-filter', 'value'),
     Input('tabs', 'value')]
)
def update_visualizations(start_date, end_date, country, salesperson, tab):
    if tab != 'visualizations':
        # Prevent updates when not on visualizations tab
        return [no_update] * 9
    
    if not start_date or not end_date or df is None or df.empty:
        return [go.Figure().update_layout(title={'text': 'No Data', 'x': 0.5, 'xanchor': 'center'})] * 9

    filtered_df = df[
        (df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)
    ]
    if country != 'All':
        filtered_df = filtered_df[filtered_df['country'] == country]
    if salesperson != 'Whole Sales Team' and salesperson != 'None':
        filtered_df = filtered_df[filtered_df['team_member_id'] == salesperson]
    
    best_selling_fig = generate_best_selling_products(filtered_df)
    sales_by_traffic_fig = generate_sales_by_traffic_source(filtered_df)
    revenue_patterns_fig = generate_revenue_patterns(filtered_df)
    regional_sales_fig = generate_regional_sales_insights(filtered_df)
    conversion_rate_fig = generate_conversion_rate(filtered_df)
    predictive_sales_fig = generate_predictive_sales_forecast(filtered_df)
    peak_inquiry_periods_fig = generate_peak_inquiry_periods(filtered_df)
    regional_product_demand_fig = generate_regional_product_demand(filtered_df)
    salesperson_revenue_forecast_fig = generate_salesperson_revenue_forecast(filtered_df)
    
    return (best_selling_fig, sales_by_traffic_fig, revenue_patterns_fig, regional_sales_fig, 
            conversion_rate_fig, predictive_sales_fig, peak_inquiry_periods_fig, 
            regional_product_demand_fig, salesperson_revenue_forecast_fig)

if __name__ == '__main__':
    app.run_server(debug=True)