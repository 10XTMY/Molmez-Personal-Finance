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

Author: @10XTMY, Molmez LTD (www.molmez.io)
Date Published: 30 January 2023

This upload page is displayed as the main page when the app loads in the browser
The user can either upload their own csv files or click view analytics to load a demo data set
"""
from dash import html, dcc, callback, Output, Input, State
from helpers import verify_upload


UPLOAD_SECTION = dcc.Upload(
    id='upload-data',
    children=html.A('SELECT'),
    # allow multiple files to be uploaded?
    multiple=False
)

LOGO_FILE_HOVER = '../assets/Molmez_1080_logo_Neon_250x250.png'
LOGO_FILE = '../assets/Molmez_1080_logo_White_250x250.png'

LANDING_PAGE_BODY_TEXT = 'Hello :)\n\n' \
                         'please select or drag and drop a\n' \
                         '.csv balance sheet to analyse'

LANDING_PAGE_BOTTOM_TEXT = 'csv layout:\nDate,Details,Amount'

layout = html.Div([
    html.Div([
        html.Div([
            html.A(href='https://molmez.io/',
                   children=[html.Img(alt='Link to Molmez ltd website',
                                      src=LOGO_FILE, className='logo-image'),
                             html.Img(alt='Link to Molmez ltd website',
                                      src=LOGO_FILE_HOVER, className='logo-image-hover')
                             ],
                   className='logo-card'),
            html.Div(children=[
                         html.Plaintext(children=LANDING_PAGE_BODY_TEXT, className='text-main'),
                         html.Plaintext(children=LANDING_PAGE_BOTTOM_TEXT, className='text-main-bottom'),
                         html.Div(UPLOAD_SECTION, className='button-select'),
                         html.Plaintext(id='txt-status', children='File Loaded...', className='text-status'),
                         dcc.Link('view analytics', href='/analytics', className='button-analytics')
                     ], className='body-container')
        ], className='circle-inner')
    ], className='circle-outer'),
    html.Plaintext(id='csv-output-title', children=[], className='csv-output-title'),
    html.Plaintext(id='csv-output', children=[], className='csv-output')
], className='container'
)


@callback(Output('txt-status', 'children'),
          Output('data-set', 'data'),
          Output('csv-output-title', 'children'),
          Output('csv-output', 'children'),
          Input('upload-data', 'contents'),
          State('upload-data', 'filename'),
          State('upload-data', 'last_modified'))
def display_page(contents, filename, last_modified):
    if not filename:
        return 'select file...', '', '', ''

    content_type, content_string = contents.split(',')

    # verify upload returns [0 or 1, error message or decoded csv]
    result = verify_upload(filename, content_string)
    if result[0]:
        df_dict = result[1].reset_index().to_dict('records')
        return 'loaded csv file', df_dict, '', ''
    else:
        example_string = 'Date,Details,Amount\n29/11/2023,John Spartan,32.95\n' \
                         '29/11/2023,John Spartan,-45.90\n29/11/2023,Simon Pheonix,-11.68\n' \
                         '29/11/2023,Mason Storm,17.19\n29/11/2023,Edgar Friendly,-8.32\n' \
                         '28/11/2023,Colonel Kurtz,-3.99\n28/11/2023,Travis Bickle,22.89\n' \
                         '28/11/2023,Ben Richards,-3.97\n28/11/2023,Harley Stone,-6.18\n' \
                         '28/11/2023,Nada,140.00\n28/11/2023,Leon,-1.20\n' \
                         '28/11/2023,Douglas Quaid,-2.49\n28/11/2023,John Matrix,-1.59'
        return result[1], '', 'CSV Example:', example_string
