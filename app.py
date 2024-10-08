import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import pyodbc
from dotenv import load_dotenv
import os

###############################
load_dotenv()
###############################
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Healthcare App Dashboard"
server = app.server  # For deployment if needed
###############################
def fetch_data(query):
    conn = pyodbc.connect(
        f"DRIVER={os.getenv('DRIVER')};"
        f"SERVER={os.getenv('SERVER')};"
        f"DATABASE={os.getenv('DATABASE')};"
        f"UID={os.getenv('DB_UID')};"
        f"PWD={os.getenv('DB_PWD')};"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
    )
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

###############################
# Fetch service categories
service_query = """
SELECT DISTINCT ServiceCategory
FROM Services;
"""
df_services = fetch_data(service_query)

###############################
# Fetch patient demographics
patient_demo_query = """
SELECT
    Gender,
    DATEDIFF(year, DateOfBirth, GETDATE()) AS Age
FROM Patients;
"""
df_patient_demo = fetch_data(patient_demo_query)

###############################
# Fetch appointment data with service categories
appointment_status_query = """
SELECT
    CAST(A.AppointmentDateTime AS DATE) AS AppointmentDate,
    A.Status,
    S.ServiceCategory
FROM Appointments A
JOIN Services S ON A.ServiceID = S.ServiceID;
"""
df_appointment_status = fetch_data(appointment_status_query)
# Convert AppointmentDate to datetime
df_appointment_status['AppointmentDate'] = pd.to_datetime(df_appointment_status['AppointmentDate'])

###############################
# Fetch revenue data with service categories
revenue_query = """
SELECT
    B.PaymentDate,
    B.TotalAmount,
    S.ServiceCategory
FROM Billing B
JOIN Appointments A ON B.AppointmentID = A.AppointmentID
JOIN Services S ON A.ServiceID = S.ServiceID;
"""
df_revenue = fetch_data(revenue_query)
df_revenue['PaymentDate'] = pd.to_datetime(df_revenue['PaymentDate'])

###############################
# Visuals
# Age Distribution
fig_age_distribution = px.histogram(df_patient_demo, x='Age', nbins=20, title='Patient Age Distribution')
# Gender Ratio
fig_gender_ratio = px.pie(df_patient_demo, names='Gender', title='Gender Ratio')

# Initialize empty figures for graphs to be updated
fig_appointments_over_time = {}
fig_revenue_over_time = {}
fig_appointment_status = {}

###############################
# Revenue Growth Over Year
# Prepare data for Revenue Growth Over Year
df_revenue['Year'] = df_revenue['PaymentDate'].dt.year
df_revenue_year = df_revenue.groupby('Year')['TotalAmount'].sum().reset_index()
df_revenue_year.rename(columns={'TotalAmount': 'TotalRevenue'}, inplace=True)
df_revenue_year.sort_values('Year', inplace=True)
df_revenue_year['YoY_Growth'] = df_revenue_year['TotalRevenue'].pct_change() * 100  # Convert to percentage

# Create the figure
fig_revenue_growth = px.bar(
    df_revenue_year,
    x='Year',
    y='TotalRevenue',
    title='Annual Revenue with Year-over-Year Growth',
    text='YoY_Growth'
)
fig_revenue_growth.update_traces(
    texttemplate='%{text:.2f}%',
    textposition='outside'
)
fig_revenue_growth.update_layout(
    yaxis_title='Total Revenue',
    xaxis_title='Year',
    uniformtext_minsize=8,
    uniformtext_mode='hide'
)

###############################
# Year-to-Date Revenue
# Prepare data for Year-to-Date Revenue
today = pd.Timestamp('today')
current_year = today.year
today_dayofyear = today.dayofyear

# Calculate cumulative revenue up to today's date for each year
df_revenue['DayOfYear'] = df_revenue['PaymentDate'].dt.dayofyear
df_ytd = df_revenue[df_revenue['DayOfYear'] <= today_dayofyear]
df_ytd_cumulative = df_ytd.groupby(['Year'])['TotalAmount'].sum().reset_index()
df_ytd_cumulative.rename(columns={'TotalAmount': 'CumulativeRevenue'}, inplace=True)

# Create the figure
fig_ytd_revenue = px.bar(
    df_ytd_cumulative,
    x='Year',
    y='CumulativeRevenue',
    title='Year-to-Date Revenue Comparison'
)
fig_ytd_revenue.update_layout(
    yaxis_title='Cumulative Revenue',
    xaxis_title='Year'
)

###############################
# App layout and filters
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Healthcare App Dashboard", className='text-center text-primary mb-4'), width=12)
    ]),
    # Date Picker and Service Category Dropdown
    dbc.Row([
        dbc.Col([
            html.Label('Select Date Range'),
            dcc.DatePickerRange(
                id='date-range-picker',
                min_date_allowed=df_appointment_status['AppointmentDate'].min(),
                max_date_allowed=df_appointment_status['AppointmentDate'].max(),
                start_date=df_appointment_status['AppointmentDate'].min(),
                end_date=df_appointment_status['AppointmentDate'].max(),
                display_format='YYYY-MM-DD',
                style={'margin-bottom': '20px'}
            )
        ], width=6),
        dbc.Col([
            html.Label('Select Service Category'),
            dcc.Dropdown(
                id='service-category-dropdown',
                options=[
                    {'label': category, 'value': category} for category in df_services['ServiceCategory'].unique()
                ],
                value=df_services['ServiceCategory'].unique().tolist(),  # Default to all categories selected
                multi=True,
                style={'margin-bottom': '20px'}
            )
        ], width=6),
    ]),
    # Visualizations
    dbc.Row([
        dbc.Col(dcc.Graph(id='appointments-over-time'), width=6),
        dbc.Col(dcc.Graph(id='revenue-over-time'), width=6),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='age-distribution', figure=fig_age_distribution), width=6),
        dbc.Col(dcc.Graph(id='gender-ratio', figure=fig_gender_ratio), width=6),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='appointment-status'), width=6),
        dbc.Col(dcc.Graph(id='revenue-growth', figure=fig_revenue_growth), width=6),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='ytd-revenue', figure=fig_ytd_revenue), width=6),
    ]),
], fluid=True)

###############################
@app.callback(
    Output('appointments-over-time', 'figure'),
    Output('revenue-over-time', 'figure'),
    Output('appointment-status', 'figure'),
    Input('date-range-picker', 'start_date'),
    Input('date-range-picker', 'end_date'),
    Input('service-category-dropdown', 'value')
)
def update_figures(start_date, end_date, selected_categories):
    # Convert dates to datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # Filter appointment data
    filtered_appointments = df_appointment_status[
        (df_appointment_status['AppointmentDate'] >= start_date) &
        (df_appointment_status['AppointmentDate'] <= end_date) &
        (df_appointment_status['ServiceCategory'].isin(selected_categories))
    ]

    # Total Appointments Over Time
    appointment_counts = filtered_appointments.groupby('AppointmentDate').size().reset_index(name='Count')
    fig_appointments = px.scatter(
        appointment_counts,
        x='AppointmentDate',
        y='Count',
        title='Total Appointments Over Time',
        trendline='ols'
    )

    # Appointment Status Distribution
    status_counts = filtered_appointments['Status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    fig_status = px.bar(
        status_counts,
        x='Status',
        y='Count',
        title='Appointment Status Distribution'
    )

    # Filter revenue data
    filtered_revenue = df_revenue[
        (df_revenue['PaymentDate'] >= start_date) &
        (df_revenue['PaymentDate'] <= end_date) &
        (df_revenue['ServiceCategory'].isin(selected_categories))
    ]
    revenue_totals = filtered_revenue.groupby('PaymentDate')['TotalAmount'].sum().reset_index()
    fig_revenue = px.line(
        revenue_totals,
        x='PaymentDate',
        y='TotalAmount',
        title='Revenue Over Time'
    )

    return fig_appointments, fig_revenue, fig_status

###############################
if __name__ == '__main__':
    app.run_server(debug=True)