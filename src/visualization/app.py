import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
from datetime import datetime

app = dash.Dash(__name__)

def create_layout():
    return html.Div([
        html.H1("Treehut Social Media Trend Analysis"),
        
        # Time series of comment volume
        html.Div([
            html.H2("Comment Volume Over Time"),
            dcc.Graph(id='comment-volume-graph')
        ]),
        
        # Comment length distribution
        html.Div([
            html.H2("Comment Length Distribution"),
            dcc.Graph(id='comment-length-graph')
        ]),
        
        # Day of week distribution
        html.Div([
            html.H2("Comment Activity by Day of Week"),
            dcc.Graph(id='day-graph')
        ]),
        
        # Hour of day distribution
        html.Div([
            html.H2("Comment Activity by Hour"),
            dcc.Graph(id='hour-graph')
        ]),
        
        # Time window selector
        html.Div([
            html.Label("Select Time Window:"),
            dcc.Dropdown(
                id='time-window-selector',
                options=[
                    {'label': 'Daily', 'value': '1D'},
                    {'label': 'Weekly', 'value': '1W'},
                    {'label': 'Monthly', 'value': '1M'}
                ],
                value='1D'
            )
        ])
    ])

app.layout = create_layout()

@app.callback(
    [Output('comment-volume-graph', 'figure'),
     Output('comment-length-graph', 'figure'),
     Output('day-graph', 'figure'),
     Output('hour-graph', 'figure')],
    [Input('time-window-selector', 'value')]
)
def update_graphs(time_window):
    # Load processed data from output directory
    df = pd.read_csv('output/processed_data.csv')
    
    # Print available columns for debugging
    print("Available columns:", df.columns.tolist())
    
    # Parse timestamps using the same approach as the processor
    try:
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed')
    except ValueError:
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'], dayfirst=True)
        except ValueError:
            try:
                df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601')
            except ValueError:
                df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S.%f%z')
    
    # Comment volume over time
    volume_fig = px.line(
        df.groupby(pd.Grouper(key='timestamp', freq=time_window)).size().reset_index(),
        x='timestamp',
        y=0,
        title='Comment Volume Over Time'
    )
    
    # Comment length distribution
    length_fig = px.histogram(
        df,
        x='comment_length',
        title='Distribution of Comment Lengths',
        nbins=50
    )
    
    # Day of week distribution
    day_fig = px.bar(
        df.groupby('day_of_week').size().reset_index(),
        x='day_of_week',
        y=0,
        title='Comment Activity by Day of Week'
    )
    
    # Hour of day distribution
    hour_fig = px.bar(
        df.groupby('hour').size().reset_index(),
        x='hour',
        y=0,
        title='Comment Activity by Hour of Day'
    )
    
    return volume_fig, length_fig, day_fig, hour_fig

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True) 