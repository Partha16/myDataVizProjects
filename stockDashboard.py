import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import pandas_datareader.data as web
import datetime
import dash_table as dt
import plotly.graph_objects as go

# https://stooq.com/
start = datetime.datetime(2020, 1, 1)
stocks = ['AMZN','GOOGL','FB','PFE','MRNA','BNTX','AAPL','MSFT','TSLA','JPM','JNJ']
df = web.DataReader(stocks,'stooq', start=start)
# df=df.melt(ignore_index=False, value_name="price").reset_index()
df = df.stack().reset_index()

print(df[:15])


colors = {"background": "#000000", "text": "#ffFFFF"}
tod = df['Date'][0]
recent = df[df['Date'] == tod];
recent = recent[['Symbols','Close','High','Low','Open','Volume']]

title1 = "Stocks Yesterday ("+ str(tod) +") :"
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )





def serve_layout():
   return (dbc.Container([
    # Main Title
    dbc.Row(
        dbc.Col(html.H1("Stock Market Dashboard",
                        className='text-center text-primary mb-4'),
                width=12)
    ),
    
    # Today Stock details
    dbc.Row(
            # dbc.Col([html.H2(title1),
            #          dash_table.DataTable(
            #                          id='table',
            #                          columns=[{"name": i, "id": i} for i in recent.columns],
            #                          data=recent.to_dict('records')
            #                          )])
            [
                dbc.Col(
                    [html.H2(title1),
                        dt.DataTable(
                                id="table",
                                columns=[{"name": i, "id": i} for i in recent.columns],
                                data=recent.to_dict('records'),
                                style_table={"height": "auto"},
                                style_cell={
                                    "white_space": "normal",
                                    "height": "auto",
                                    "backgroundColor": colors["background"],
                                    "color": "#03A062",
                                    "font_size": "16px",
                                },
                                style_data={"border": "#4d4d4d"},
                                style_header={
                                    "backgroundColor": colors["background"],
                                    "fontWeight": "bold",
                                    "border": "#4d4d4d",
                                },
                                style_cell_conditional=[
                                    {"if": {"column_id": c}, "textAlign": "center"}
                                    for c in ["attribute", "value"]
                                ],
                            )
                        ],
                            width={"size": 6, "offset": 3},)
                ]
    ),

    #Title 2
    dbc.Row(
            dbc.Col(html.H2('Stock prices over time:'))
    ),
    
    #Candle Graph
    dbc.Row(
        dbc.Col([
            dcc.Dropdown(id='main_id', multi=False, value='AMZN',
                         options=[{'label':x, 'value':x}
                                  for x in sorted(df['Symbols'].unique())],
                         ),
            dcc.Graph(id='Candle', figure={})
            ]
        )
    ),
        
    dbc.Row([

        dbc.Col([
            dcc.Dropdown(id='my-dpdn', multi=True, value=['AMZN'],
                         options=[{'label':x, 'value':x}
                                  for x in sorted(df['Symbols'].unique())],
                         ),
            dcc.Graph(id='line-fig', figure={})
        ]# width={'size':5, 'offset':1, 'order':1},
           ,xs=15, sm=12, md=12, lg=7, xl=5
        ),

        dbc.Col([
            dcc.Dropdown(id='my-dpdn2', multi=True, value=['PFE','BNTX'],
                         options=[{'label':x, 'value':x}
                                  for x in sorted(df['Symbols'].unique())],
                         ),
            dcc.Graph(id='line-fig2', figure={})
        ] #width={'size':5, 'offset':0, 'order':2},
         ,xs=12, sm=12, md=12, lg=7, xl=5
        ),

    ], no_gutters=True, justify='between'),  # Horizontal:start,center,end,between,around

    dbc.Row(
        dbc.Col([
            html.P("Select Company Stock:",
                   style={"textDecoration": "underline"}),
            dcc.Checklist(id='my-checklist', value=['FB', 'GOOGL', 'AMZN'],
                          options=[{'label':x, 'value':x}
                                   for x in sorted(df['Symbols'].unique())],
                          labelClassName="mr-3"),
            dcc.Graph(id='my-hist', figure={}),
        ] #width={'size':5, 'offset':1},
           # xs=12, sm=12, md=12, lg=5, xl=5
        )
        , align="center"),  # Vertical: start, center, end
    dbc.Row([
        dbc.Col(
            html.Div(
                [
                    html.Button("Click me", id="example-button", className="mr-2"),
                    html.H3(id="example-output", style={"vertical-align": "middle"})
                ]
)
            ),
        dbc.Col(
            )
        ])
], fluid=True)
       

)

app.layout = serve_layout  

# Callback section: connecting the components
# ************************************************************************
#Candlestick Graph
@app.callback(
    Output('Candle', 'figure'),
    Input('main_id','value')
)
def update_graph(stock_slctd):
    dff = df[df['Symbols']==stock_slctd]
    figIn = go.Figure(data=[go.Candlestick(x=dff['Date'],
                open=dff['Open'],
                high=dff['High'],
                low=dff['Low'],
                close=dff['Close'])],
                layout={
                    "height": 1000,
                    "title": "CandleStick Graph",
                    "showlegend": True,
                    "plot_bgcolor": colors["background"],
                    "paper_bgcolor": colors["background"],
                    "font": {"color": colors["text"]},
                })
    return figIn

# Line chart - Single
@app.callback(
    Output('line-fig', 'figure'),
    Input('my-dpdn', 'value')
)
def update_graph(stock_slctd):
    dff = df[df['Symbols'].isin(stock_slctd)]
    figln = px.line(dff, x='Date', y='High',color='Symbols')
    figln.update_layout(paper_bgcolor=colors["background"])
    figln.update_layout(plot_bgcolor=colors["background"])
    figln.update_layout(title = "Line graph Graph of High")
    figln.update_layout(font = {"color": colors["text"]})
    return figln


# Line chart - multiple
@app.callback(
    Output('line-fig2', 'figure'),
    Input('my-dpdn2', 'value')
)
def update_graph(stock_slctd):
    dff = df[df['Symbols'].isin(stock_slctd)]
    figln2 = px.line(dff, x='Date', y='Open', color='Symbols')
    figln2.update_layout(paper_bgcolor=colors["background"])
    figln2.update_layout(plot_bgcolor=colors["background"])
    figln2.update_layout(title = "Line graph Graph of Open")
    figln2.update_layout(font = {"color": colors["text"]})
    return figln2


# Histogram
@app.callback(
    Output('my-hist', 'figure'),
    Input('my-checklist', 'value')
)
def update_graph(stock_slctd):
    dff = df[df['Symbols'].isin(stock_slctd)]
    dff = dff[dff['Date']==tod]
    fighist = px.histogram(dff, x='Symbols', y='Close')
    fighist.update_layout(paper_bgcolor=colors["background"])
    fighist.update_layout(plot_bgcolor=colors["background"])
    fighist.update_layout(title = "Histogram Graph of the sum of all closes")
    fighist.update_layout(font = {"color": colors["text"]})
    return fighist

@app.callback(
    Output("example-output", "children"),
    [Input("example-button", "n_clicks")]
)
def on_button_click(n):
    global df
    df = web.DataReader(['AMZN','GOOGL','FB','PFE','MRNA','BNTX','AAPL','MSFT','TSLA','JPM','JNJ','AEP'],
                    'stooq', start=datetime.datetime(2020, 1, 1))
    df = df.stack().reset_index()
    return "Refresh data."

if __name__=='__main__':
    app.run_server(debug=True, port=8000)
