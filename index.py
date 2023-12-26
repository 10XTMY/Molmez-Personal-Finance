"""
Bank Statement Analysis Plotly Dash App

This is a Plotly Dash app that analyses bank statements and provides various visualizations to help users understand
their spending habits.

It uses the following technologies and libraries:
- Python 3.7
- Plotly Dash
- Pandas
- Numpy

The app is intended for educational or demonstration purposes only and should not be used in a production environment
without further testing and security measures.

To run the app, you will need to have Python and the required libraries installed.
You can run the app by running the command 'python, python3, or py (depending on your setup) index.py' in the terminal.

This project is released under the MIT License.

Run this script to launch app

-- Select a CSV file with the layout: "Date,Details,Amount" eg. "DD/MM/YYYY,TRANSACTION NAME,-45.76"
-- Click View Analytics

Author: @10XTMY, Molmez LTD (www.molmez.io)
Date Published: 30 January 2023
"""
from dash import dcc, html, Input, Output, callback
from app import app, server  # *** do not remove 'server', required import ***
from apps import analytics, upload


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content', children=[

    ]),
    dcc.Store(id='data-set', storage_type='session')
])


@callback(Output('page-content', 'children'),
          Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/analytics':
        return analytics.layout
    else:
        return upload.layout


if __name__ == '__main__':
    app.run_server(debug=False)
