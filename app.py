"""
Bank Statement Analysis Dash App

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

Author: @10XTMY, Molmez LTD (www.molmez.io)
Date Published: 30 January 2023

This script sets up the app that index.py will launch
"""
import dash

# include google fonts
external_stylesheets = ['https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@700;900&display=swap']

# meta_tags are required for the app layout to be mobile responsive
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True,
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )
server = app.server
