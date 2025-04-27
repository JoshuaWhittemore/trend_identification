import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
from datetime import datetime
from collections import Counter
import logging
import sys
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Create logger
logger = logging.getLogger(__name__)

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
        
        # Topic distribution
        html.Div([
            html.H2("Topic Distribution"),
            dcc.Graph(id='topic-graph')
        ]),
        
        # Topic details
        html.Div([
            html.H2("Topic Details"),
            html.Div(id='topic-details')
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
        
        # Hashtag Analysis Section
        html.Div([
            html.H2("Hashtag Analysis"),
            
            # Hashtag frequency bar chart
            html.Div([
                html.H3("Hashtag Frequency"),
                dcc.Graph(id='hashtag-frequency-graph')
            ]),
            
            # Hashtag co-occurrence network
            html.Div([
                html.H3("Hashtag Co-occurrence Network"),
                dcc.Graph(id='hashtag-network-graph')
            ])
        ]),
        
        # Keyword Analysis Section
        html.Div([
            html.H2("Keyword Analysis"),
            
            # Keyword frequency bar chart
            html.Div([
                html.H3("Keyword Frequency"),
                dcc.Graph(id='keyword-frequency-graph')
            ]),
            
            # Keyword details
            html.Div([
                html.H3("Keyword Details"),
                dcc.Dropdown(
                    id='keyword-selector',
                    options=[],  # Will be populated in callback
                    value=None,
                    placeholder="Select a keyword to view details"
                ),
                html.Div(id='keyword-details')
            ]),
            
            # Related terms network graph
            html.Div([
                html.H3("Related Terms Network"),
                dcc.Graph(id='related-terms-graph')
            ])
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
     Output('topic-graph', 'figure'),
     Output('topic-details', 'children'),
     Output('day-graph', 'figure'),
     Output('hour-graph', 'figure'),
     Output('hashtag-frequency-graph', 'figure'),
     Output('hashtag-network-graph', 'figure'),
     Output('keyword-frequency-graph', 'figure'),
     Output('keyword-selector', 'options'),
     Output('keyword-details', 'children'),
     Output('related-terms-graph', 'figure')],
    [Input('time-window-selector', 'value'),
     Input('keyword-selector', 'value')]
)
def update_graphs(time_window, selected_keyword):
    try:
        logger.info("Starting graph update")
        
        # Load processed data
        logger.info("Loading processed data")
        df = pd.read_csv('output/processed_data.csv')
        
        # Load keyword analysis data
        logger.info("Loading keyword analysis data")
        keyword_df = pd.read_csv('output/keyword_analysis.csv')
        
        # Parse timestamps
        logger.info("Parsing timestamps")
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
        logger.info("Creating comment volume graph")
        volume_fig = px.line(
            df.groupby(pd.Grouper(key='timestamp', freq=time_window)).size().reset_index(),
            x='timestamp',
            y=0,
            title='Comment Volume Over Time'
        )
        
        # Comment length distribution
        logger.info("Creating comment length graph")
        length_fig = px.histogram(
            df,
            x='comment_length',
            title='Distribution of Comment Lengths',
            nbins=50
        )
        
        # Topic distribution
        logger.info("Creating topic distribution graph")
        if 'topic_id' in df.columns:
            topic_fig = px.pie(
                df.groupby('topic_id').size().reset_index(),
                values=0,
                names='topic_id',
                title='Distribution of Topics'
            )
        else:
            topic_fig = go.Figure()
            topic_fig.add_annotation(
                text="Topic distribution data not available",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False
            )
        
        # Topic details
        logger.info("Creating topic details")
        topic_details = "Topic details not available"
        if 'topic_id' in df.columns:
            topic_details = html.Div([
                html.Div([
                    html.H3(f"Topic {topic_id}"),
                    html.P(f"Number of comments: {count}")
                ]) for topic_id, count in df.groupby('topic_id').size().items()
            ])
        
        # Day of week distribution
        logger.info("Creating day of week graph")
        day_fig = px.bar(
            df.groupby('day_of_week').size().reset_index(),
            x='day_of_week',
            y=0,
            title='Comment Activity by Day of Week'
        )
        
        # Hour of day distribution
        logger.info("Creating hour of day graph")
        hour_fig = px.bar(
            df.groupby('hour').size().reset_index(),
            x='hour',
            y=0,
            title='Comment Activity by Hour'
        )
        
        # Hashtag frequency analysis
        logger.info("Analyzing hashtags")
        all_hashtags = []
        for tags in df['hashtags']:
            if isinstance(tags, str):
                # Convert string representation of list to actual list
                tags = eval(tags)
            all_hashtags.extend(tags)
        
        hashtag_counts = Counter(all_hashtags)
        hashtag_df = pd.DataFrame({
            'hashtag': list(hashtag_counts.keys()),
            'count': list(hashtag_counts.values())
        }).sort_values('count', ascending=False)
        
        # Hashtag frequency bar chart
        logger.info("Creating hashtag frequency graph")
        hashtag_freq_fig = px.bar(
            hashtag_df.head(20),  # Show top 20 hashtags
            x='hashtag',
            y='count',
            title='Top 20 Hashtags',
            labels={'hashtag': 'Hashtag', 'count': 'Frequency'}
        )
        
        # Hashtag co-occurrence network
        logger.info("Creating hashtag co-occurrence network")
        co_occurrences = Counter()
        for tags in df['hashtags']:
            if isinstance(tags, str):
                tags = eval(tags)
            if len(tags) > 1:
                for i in range(len(tags)):
                    for j in range(i + 1, len(tags)):
                        pair = tuple(sorted([tags[i], tags[j]]))
                        co_occurrences[pair] += 1
        
        # Create network graph
        nodes = set()
        edges = []
        for (tag1, tag2), count in co_occurrences.most_common(50):  # Top 50 co-occurrences
            nodes.add(tag1)
            nodes.add(tag2)
            edges.append({
                'source': tag1,
                'target': tag2,
                'value': count
            })
        
        nodes = [{'id': tag, 'group': 1} for tag in nodes]
        
        hashtag_network_fig = go.Figure(data=[
            go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=[node['id'] for node in nodes],
                    color=["blue" if node['group'] == 1 else "lightblue" for node in nodes]
                ),
                link=dict(
                    source=[nodes.index({'id': edge['source'], 'group': 1}) for edge in edges],
                    target=[nodes.index({'id': edge['target'], 'group': 1}) for edge in edges],
                    value=[edge['value'] for edge in edges]
                )
            )
        ])
        
        hashtag_network_fig.update_layout(title_text="Hashtag Co-occurrence Network")
        
        # Keyword frequency bar chart
        logger.info("Creating keyword frequency graph")
        keyword_freq_fig = px.bar(
            keyword_df,
            x='keyword',
            y='frequency',
            title='Keyword Frequency',
            labels={'keyword': 'Keyword', 'frequency': 'Frequency'}
        )
        
        # Keyword selector options
        keyword_options = [{'label': word, 'value': word} for word in keyword_df['keyword']]
        
        # Keyword details
        logger.info("Creating keyword details")
        keyword_details = "Select a keyword to view details"
        if selected_keyword:
            keyword_row = keyword_df[keyword_df['keyword'] == selected_keyword].iloc[0]
            
            # Parse related_terms from string to list of dictionaries
            related_terms = eval(keyword_row['related_terms']) if isinstance(keyword_row['related_terms'], str) else keyword_row['related_terms']
            synonyms = eval(keyword_row['synonyms']) if isinstance(keyword_row['synonyms'], str) else keyword_row['synonyms']
            key_phrases = eval(keyword_row['key_phrases']) if isinstance(keyword_row['key_phrases'], str) else keyword_row['key_phrases']
            
            # Find sample comments containing the keyword
            sample_comments = df[df['comment_text'].str.contains(selected_keyword, case=False, na=False)].head(5)
            
            keyword_details = html.Div([
                html.H3(f"Keyword: {selected_keyword}"),
                html.P(f"Frequency: {keyword_row['frequency']}"),
                html.H4("Synonyms:"),
                html.Ul([html.Li(syn) for syn in synonyms]),
                html.H4("Related Terms:"),
                html.Ul([html.Li(f"{term['term']} ({term['count']})") for term in related_terms]),
                html.H4("Key Phrases:"),
                html.Ul([html.Li(f"{phrase['phrase']} ({phrase['count']})") for phrase in key_phrases]),
                html.H4("Sample Comments:"),
                html.Div([
                    html.Div([
                        html.P("Media Caption:", style={'fontWeight': 'bold'}),
                        html.P(row['media_caption'], style={'marginBottom': '10px', 'fontStyle': 'italic'}),
                        html.P("Comment:", style={'fontWeight': 'bold'}),
                        html.P(row['comment_text']),
                        html.P(f"Timestamp: {row['timestamp']}", style={'fontSize': '0.8em', 'color': 'gray'})
                    ], style={
                        'marginBottom': '20px',
                        'padding': '15px',
                        'border': '1px solid #ddd',
                        'borderRadius': '5px',
                        'backgroundColor': '#f9f9f9'
                    })
                    for _, row in sample_comments.iterrows()
                ])
            ])
        
        # Related terms network graph
        logger.info("Creating related terms network")
        if selected_keyword:
            keyword_row = keyword_df[keyword_df['keyword'] == selected_keyword].iloc[0]
            related_terms = eval(keyword_row['related_terms']) if isinstance(keyword_row['related_terms'], str) else keyword_row['related_terms']
            
            # Create nodes and edges for the network graph
            nodes = [{'id': selected_keyword, 'group': 1}]
            edges = []
            
            for term in related_terms:
                nodes.append({'id': term['term'], 'group': 2})
                edges.append({
                    'source': selected_keyword,
                    'target': term['term'],
                    'value': term['count']
                })
            
            related_terms_fig = go.Figure(data=[
                go.Sankey(
                    node=dict(
                        pad=15,
                        thickness=20,
                        line=dict(color="black", width=0.5),
                        label=[node['id'] for node in nodes],
                        color=["blue" if node['group'] == 1 else "lightblue" for node in nodes]
                    ),
                    link=dict(
                        source=[nodes.index({'id': edge['source'], 'group': 1}) for edge in edges],
                        target=[nodes.index({'id': edge['target'], 'group': 2}) for edge in edges],
                        value=[edge['value'] for edge in edges]
                    )
                )
            ])
            
            related_terms_fig.update_layout(title_text=f"Related Terms for {selected_keyword}")
        else:
            related_terms_fig = go.Figure()
            related_terms_fig.add_annotation(
                text="Select a keyword to view related terms",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False
            )
        
        logger.info("Graph update completed successfully")
        return (volume_fig, length_fig, topic_fig, topic_details, day_fig, hour_fig,
                hashtag_freq_fig, hashtag_network_fig, keyword_freq_fig, keyword_options,
                keyword_details, related_terms_fig)
                
    except Exception as e:
        logger.error(f"Error updating graphs: {str(e)}", exc_info=True)
        # Return empty figures in case of error
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text=f"Error: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False
        )
        return [empty_fig] * 12

if __name__ == '__main__':
    logger.info("Starting Dash application")
    app.run_server(debug=True, host='0.0.0.0') 