# John Olan S. Gomez
# Data Analyst Specialist Class
# Python Programming Professional Certificate

import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# Load the Excel file
file_path = r"C:\Users\Olan\Documents\Olan\Data Analyst Specialist Bootcamp\Python\Activities\HRDataset.xlsx"
df = pd.read_excel(file_path)

# Initialize the Dash app
app = Dash(__name__)

# Layout of the dashboard
app.layout = html.Div([
    html.H1("Human Resources Dashboard", style={"textAlign": "center", "fontFamily":"Helvetica"}),

    # Dropdown for filtering by department
    html.Div([
        html.Label("Filter by Department:"),
        dcc.Dropdown(
            id="department-filter",
            options=[{"label": department, "value": department} for department in df["Department"].unique()],
            value=None,  # Default to no filter
            placeholder="Select a Department",
            style={"width": "50%", "fontFamily":"Roboto"}
        )
    ], style={"fontFamily":"Roboto"}),

    # Summary Cards
    html.Div([
        html.Div(id="card-activeEmp", style={"width": "30%", "display": "inline-block", "padding": "20px"}),
        html.Div(id="card-AvgSalary", style={"width": "30%", "display": "inline-block", "padding": "20px"}),
        html.Div(id="card-topDept", style={"width": "30%", "display": "inline-block", "padding": "20px"}),
    ], style={"display": "flex", "justifyContent": "space-around", "marginTop": "20px"}),

    # Line chart
    dcc.Graph(id="line-chart"),

    html.Div([
        # Bar chart
        dcc.Graph(id="bar-chart"),
        # Pie chart
        dcc.Graph(id="pie-chart"),
    ], style={"display": "flex", "justifyContent": "space-around", "marginTop": "20px"}),

    # Line chart - Performance Score
    dcc.Graph(id="line-chart2"),

    # Bar chart - Turnover rate
    dcc.Graph(id="bar-chart2"),
])


# Callbacks to update the dashboard
@app.callback(
    [
        Output("card-activeEmp", "children"),
        Output("card-AvgSalary", "children"),
        Output("card-topDept", "children"),
        Output("line-chart", "figure"),
        Output("bar-chart", "figure"),
        Output("pie-chart", "figure"),
        Output("line-chart2", "figure"),
        Output("bar-chart2", "figure"),
    ],
    [Input("department-filter", "value")]
)
def update_dashboard(selected_dept):
    # Filter data based on selection
    filtered_df = df if selected_dept is None else df[df["Department"] == selected_dept]

    # Summary metrics
    # total active employees
    total_activeEmp = filtered_df["EmploymentStatus"].value_counts().get('Active', 0)

    # Average salary
    avg_salary = filtered_df["Salary"].mean()

    # Filter for rows where PerformanceScore is "Exceeds"
    exceeds_df = filtered_df[filtered_df["PerformanceScore"] == "Exceeds"]
    # Group by Department and count the number of "Exceeds"
    exceeds_count = exceeds_df.groupby("Department").size().reset_index(name="ExceedsCount")
    # Get the department with the highest number of "Exceeds"
    top_department = None if exceeds_count.empty else exceeds_count.sort_values(by="ExceedsCount",
                                                                                ascending=False).head(1)

    # Create cards
    card_abroad = html.Div([
        html.H2("Total Active Employees", style={"textAlign": "center"}),
        html.H1(f"{total_activeEmp:,}", style={"textAlign": "center", "color": "green"})
    ], style={"fontFamily":"Helvetica"})

    card_locally = html.Div([
        html.H2("Average Salary", style={"textAlign": "center"}),
        html.H1(f"P{avg_salary:,.2f}", style={"textAlign": "center", "color": "blue"})
    ], style={"fontFamily":"Helvetica"})

    card_employees = html.Div([
        html.H2("Top Performing Department", style={"textAlign": "center"}),
        html.H1(f"{top_department.iloc[0]['Department'] if top_department is not None else 'N/A'}",
                style={"textAlign": "center", "color": "orange"})
    ], style={"fontFamily":"Helvetica"})

    # Line Chart: Hiring trend
    # Convert 'DateofHire' to datetime
    filtered_df["DateofHire"] = pd.to_datetime(filtered_df["DateofHire"], errors='coerce')

    # Drop rows with invalid or missing hire dates
    filtered_df = filtered_df.dropna(subset=["DateofHire"])

    # Create a new column for Year
    filtered_df["HireYear"] = filtered_df["DateofHire"].dt.to_period("Y").astype(str)

    # Group by HireMonth and count hires
    hire_trend = filtered_df.groupby("HireYear").size().reset_index(name="Hires")

    # Sort by date
    hire_trend["HireYear"] = pd.to_datetime(hire_trend["HireYear"])
    hire_trend = hire_trend.sort_values("HireYear")

    line_fig = px.line(hire_trend, x="HireYear", y="Hires", title="Hiring Trend Over Time",
                       labels={"HireYear": "Hire Date", "Hires": "Number of Hires"},
                       markers=True)

    line_fig.update_layout(xaxis_tickformat='%Y', xaxis_title="Date of Hire", yaxis_title="Number of Hires")

    # Bar Chart: Gender Distribution
    # Count employees by gender
    gender_counts = filtered_df["Sex"].value_counts().reset_index()
    gender_counts.columns = ["Gender", "Count"]

    # Plot bar chart
    bar_fig = px.bar(gender_counts, x="Gender", y="Count",
                     title="Employee Distribution by Gender",
                     text="Count", color="Gender")

    # Pie Chart: Percentage of races in the company
    # Group by RaceDesc and count the number of employees
    race_counts = filtered_df["RaceDesc"].value_counts().reset_index()
    race_counts.columns = ["Race", "Count"]

    pie_fig = px.pie(race_counts, values="Count", names="Race",
                     title="Employee Distribution by Race",
                     hole=0.3)
    pie_fig.update_traces(textposition='inside', textinfo='percent+label')

    # Line chart - Performance score over time
    # Create a performance score mapping (assuming scores like "Exceeds", "Fully Meets", etc.)
    perf_mapping = {
        "Exceeds": 4,
        "Fully Meets": 3,
        "Needs Improvement": 2,
        "PIP": 1,
        # Add other possible performance categories as needed
    }

    # Make a copy to avoid modifying the original dataframe
    perf_df = filtered_df.copy()

    # Add numeric performance score column
    perf_df["PerformanceScoreNumeric"] = perf_df["PerformanceScore"].map(perf_mapping)

    # Convert DateofHire to datetime (if DateofReview is not available)
    perf_df["DateofReview"] = pd.to_datetime(perf_df.get("DateofReview", perf_df["DateofHire"]), errors='coerce')

    # Drop rows with missing values
    perf_df = perf_df.dropna(subset=["DateofReview", "PerformanceScoreNumeric"])

    # Group by Year-Month and calculate average numeric performance score
    perf_df["YearMonth"] = perf_df["DateofReview"].dt.to_period("M").astype(str)
    perf_over_time = perf_df.groupby("YearMonth")["PerformanceScoreNumeric"].mean().reset_index()

    # Convert YearMonth to datetime for proper plotting
    perf_over_time["YearMonth"] = pd.to_datetime(perf_over_time["YearMonth"])

    # Line chart
    line_fig2 = px.line(perf_over_time, x="YearMonth", y="PerformanceScoreNumeric",
                        title="Average Performance Score Over Time",
                        labels={"YearMonth": "Date", "PerformanceScoreNumeric": "Average Performance Score"},
                        markers=True)

    line_fig2.update_layout(xaxis_tickformat='%Y-%m')

    # Bar chart - Turnover rate
    # Count total employees per department
    total_dept = filtered_df.groupby("Department").size().reset_index(name="TotalEmployees")

    # Count terminated employees per department (both types of termination)
    terminated_df = filtered_df[
        filtered_df["EmploymentStatus"].isin(["Terminated for Cause", "Voluntarily Terminated"])]
    terminated_dept = terminated_df.groupby("Department").size().reset_index(name="TerminatedEmployees")

    # Merge data
    turnover = pd.merge(total_dept, terminated_dept, on="Department", how="left")
    turnover["TerminatedEmployees"] = turnover["TerminatedEmployees"].fillna(0)

    # Calculate turnover rate
    turnover["TurnoverRate"] = (turnover["TerminatedEmployees"] / turnover["TotalEmployees"]) * 100

    # Bar chart for turnover rate
    bar_fig2 = px.bar(turnover, x="Department", y="TurnoverRate",
                      title="Turnover Rate by Department (%)",
                      labels={"TurnoverRate": "Turnover Rate (%)", "Department": "Department"},
                      text=turnover["TurnoverRate"].apply(lambda x: f"{x:.2f}%"))

    bar_fig2.update_traces(textposition='outside')
    bar_fig2.update_layout(yaxis_range=[0, turnover["TurnoverRate"].max() * 1.1 + 5])

    # Return all components in the correct order
    return card_abroad, card_locally, card_employees, line_fig, bar_fig, pie_fig, line_fig2, bar_fig2

# Run the dash app
if __name__ == "__main__":
    app.run(debug=True, port=8051)