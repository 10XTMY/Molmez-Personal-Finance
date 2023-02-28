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

Author: 0xtommyOfficial, Molmez LTD (www.molmez.io)
Date Published: 30 January 2023

This is the script that performs the data analysis and returns the html displaying the results
"""
import dash
import pandas as pd
from dash import html, dcc, callback
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from pathlib import Path
from helpers import bank_csv_to_data_frame, filter_by_date_range, \
    filter_by_incoming_payments, filter_by_outgoing_payments, new_graph, \
    filter_by_amount, filter_by_min_max, isolate_keywords, remove_keywords, \
    update_json_output, calculate_top_repeat_transactions, data_frame_to_table, calculate_top_single_payments


PATH = Path(__file__).parent
DATA_PATH = PATH.joinpath("../datasets").resolve()
DEFAULT_CSV_FILE = DATA_PATH.joinpath('transactions.csv').resolve()

PAGE_TITLE = [html.H1(children='Beware of little expenses. A small leak will sink a great ship.'),
              html.H4(children='- Benjamin Franklin.', style={'paddingLeft': 20})]

DATE_RANGE_HEADER = html.Div(className='range-title-div',
                             children=[html.H3(children='Date Range'),
                                       html.H4(children='Clear Date',
                                               id='btn-clear-date',
                                               style={'cursor': 'pointer'})])

DATE_RANGE_PICKER = html.Div(className='date-range-div',
                             children=dcc.DatePickerRange(
                                 id='date-range-picker',
                                 start_date_placeholder_text="Start Period",
                                 end_date_placeholder_text="End Period",
                                 calendar_orientation='vertical',
                                 clearable=True))

KEYWORD_FILTER = html.Div([html.Div(html.H3(children='Keyword(s)'), style={'marginBottom': '-5%'}),
                           html.Div(html.H4(children='Isolate'), style={'marginBottom': '-5%'}),
                           html.Div(
                               dcc.Input(
                                   className='keyword-filter-input',
                                   id='input-keyword-isolate',
                                   type='text',
                                   placeholder='isolate by keyword, seperated by ","'),
                               style={'width': '100%', 'marginBottom': '-2.5%'}),
                           html.Div(html.H4(children='Remove'), style={'marginBottom': '-5%'}),
                           html.Div(
                               dcc.Input(
                                   className='keyword-filter-input',
                                   id='input-keyword-remove',
                                   type='text',
                                   placeholder='remove by keyword, seperated by ","'),
                               style={'width': '100%'})])

SAVINGS_FILTER = html.Div([html.Div(html.H3(children='Savings'), style={'marginBottom': '-5%'}),
                           html.Div(html.H4(children='Account Number'), style={'marginBottom': '-5%'}),
                           html.Div(
                               dcc.Input(
                                   className='savings-filter-input',
                                   id='input-savings-account-number',
                                   type='text',
                                   placeholder='savings account number...'),
                               style={'width': '100%', 'marginBottom': '-2.5%'})])

IN_OUT_FILTER = html.Div([html.Div(html.H3(children='Incoming || Outgoing')),
                          html.Div(
                              className='in-out-buttons-div',
                              children=dcc.Checklist(
                                  id='in-out-selection',
                                  options=[{'label': 'Paid in',
                                            'value': 'paid_in'},
                                           {'label': 'Paid out',
                                            'value': 'paid_out'}],
                                  value=[],
                                  className='in-out-checklist'))])

MIN_MAX_FILTER = html.Div([html.Div(html.H3(children='Amount'),
                                    style={'marginTop': '-15px'}),
                           html.Div(
                               className='min-max-inputs-div',
                               children=[
                                   dcc.Input(
                                       className='minimum-filter-input',
                                       id='minimum-input',
                                       type='number',
                                       placeholder='Min',
                                       style={'marginRight': '10px'}),
                                   dcc.Input(
                                       className='maximum-filter-input',
                                       id='maximum-input',
                                       type='number',
                                       placeholder='Max')])])

GRAPH_TYPE_FILTER = html.Div([html.Div(html.H3(children='Graph Type')),
                              html.Div(
                                  className='graph-type-div',
                                  children=[
                                      html.Button('Bar',
                                                  id='btn-bar-graph',
                                                  className='graph-select-button',
                                                  n_clicks=0),
                                      html.Button('Funnel',
                                                  id='btn-funnel-graph',
                                                  className='graph-select-button',
                                                  n_clicks=0),
                                      html.Button('Line',
                                                  id='btn-line-graph',
                                                  className='graph-select-button',
                                                  n_clicks=0),
                                      html.Button('Bubble',
                                                  id='btn-bubble-graph',
                                                  className='graph-select-button',
                                                  n_clicks=0)])])

OUTPUT_BOX = html.Div(id='output-container-div', className='output-container')

layout = html.Div(
    className='outer-frame',
    children=[
        html.Div(className='dashboard-title',
                 children=PAGE_TITLE),
        html.Div(className='main-frame',
                 children=[
                     html.Div(className='main-graph-frame',
                              id='main-graph',
                              children=[]),
                     html.Div(className='right-column-frame',
                              children=[DATE_RANGE_HEADER,
                                        DATE_RANGE_PICKER,
                                        KEYWORD_FILTER,
                                        SAVINGS_FILTER,
                                        IN_OUT_FILTER,
                                        MIN_MAX_FILTER,
                                        GRAPH_TYPE_FILTER,
                                        OUTPUT_BOX])
                 ]),
        html.Div(children=[
            html.H3(children=['"Top" list length:'], className='table-title'),
            dcc.Input(
                className='top-list-length-input',
                id='top-list-length',
                type='number',
                placeholder='20',
                style={'marginLeft': '10px'})
        ], className='table-control-container'),
        html.Div(id='table-container',
                 className='tables-outer',
                 children=[
                     html.Div([html.H3(id='top-single-in-title', children='Top 20 Single Incoming',
                                       className='table-title'),
                               html.Div(id='single-in-table', children=[], className='table')]),
                     html.Div([html.H3(id='top-repeat-title', children='Top 20 Repeat Transactions',
                                       className='table-title'),
                               html.Div(id='multi-buy-table', children=[], className='table')]),
                     html.Div([html.H3(id='top-single-out-title', children='Top 20 Single Outgoing',
                                       className='table-title'),
                               html.Div(id='single-out-table', children=[], className='table')])
                 ])
    ])


@callback(
    Output('date-range-picker', 'start_date'),
    Output('date-range-picker', 'end_date'),
    [Input('btn-clear-date', 'n_clicks')],
    [State('date-range-picker', 'start_date')],
    [Input('btn-clear-date', 'n_clicks')],
    [State('date-range-picker', 'end_date')])
def clear_date_range(start_clicks, current_start_date, end_clicks, current_end_date):
    if (start_clicks is not None) and (start_clicks > 0) or (end_clicks is not None) and (end_clicks > 0):
        return None, None
    elif not end_clicks:
        return current_start_date, current_end_date


@callback(
    Output('main-graph', 'children'),
    Output('output-container-div', 'children'),
    Output('multi-buy-table', 'children'),
    Output('single-in-table', 'children'),
    Output('single-out-table', 'children'),
    Output('top-single-in-title', 'children'),
    Output('top-single-out-title', 'children'),
    Output('top-repeat-title', 'children'),
    Input('data-set', 'data'),
    Input('date-range-picker', 'start_date'),
    Input('date-range-picker', 'end_date'),
    Input('in-out-selection', 'value'),
    Input('input-keyword-remove', 'value'),
    Input('input-keyword-isolate', 'value'),
    Input('minimum-input', 'value'),
    Input('maximum-input', 'value'),
    Input('btn-bar-graph', 'n_clicks'),
    Input('btn-funnel-graph', 'n_clicks'),
    Input('btn-line-graph', 'n_clicks'),
    Input('btn-bubble-graph', 'n_clicks'),
    Input('input-savings-account-number', 'value'),
    Input('top-list-length', 'value'))
def update_graph(data, start_date, end_date, in_out,
                 key_remove, key_isolate,
                 minimum, maximum, bar_gr,
                 funnel_gr, line_gr, scatter_gr,
                 savings, top_list_length):
    ctx = dash.callback_context

    if not ctx.triggered:
        print('not triggered')
        raise PreventUpdate
    else:
        if data:
            data_frame = pd.DataFrame(data)
            data_frame['Date'] = data_frame['Date'].apply(pd.to_datetime, dayfirst=True)
            data_frame.set_index('Date', inplace=True)
        else:
            data_frame = bank_csv_to_data_frame(DEFAULT_CSV_FILE)
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        filtered_df = data_frame.copy()
        figure_type = 'bar'

        # graph type
        if trigger_id == 'btn-bar-graph':
            figure_type = 'bar'
        elif trigger_id == 'btn-funnel-graph':
            figure_type = 'funnel'
        elif trigger_id == 'btn-line-graph':
            figure_type = 'line'
        elif trigger_id == 'btn-bubble-graph':
            if len(in_out) == 1:
                figure_type = 'bubble'

        # filter by date selection
        if start_date and end_date:
            filtered_df = filter_by_date_range(filtered_df, start_date, end_date)

        # set up the "Top" tables to output beneath the graph
        # length specified by user?
        if not top_list_length:
            # set to default length
            top_list_length = 20

        top_repeat_payments = calculate_top_repeat_transactions(filtered_df, top_list_length)
        top_repeat_payments_table = data_frame_to_table(top_repeat_payments)
        top_single_payments_out, top_single_payments_in = calculate_top_single_payments(filtered_df, top_list_length)
        top_single_out_table = data_frame_to_table(top_single_payments_out)
        top_single_in_table = data_frame_to_table(top_single_payments_in)

        # convert to dictionary for use in a report (feature yet to be implemented)
        # repeat_payments_dict = top_repeat_payments.to_dict()
        # top_singles_out_dict = top_single_payments_out.to_dict()
        # top_singles_in_dict = top_single_payments_in.to_dict()

        # print(json.dumps(repeat_payments_dict, indent=4))
        # print(json.dumps(top_singles_out_dict, indent=4))
        # print(json.dumps(top_singles_in_dict, indent=4))

        single_in_title = f'Top {top_list_length} Single Incoming'
        single_out_title = f'Top {top_list_length} Single Outgoing'
        repeat_title = f'Top {top_list_length} Repeat Transactions'

        # filter by incoming / outgoing
        if len(in_out) == 1:
            if in_out[0] == 'paid_in':
                filtered_df = filter_by_incoming_payments(filtered_df)
            elif in_out[0] == 'paid_out':
                filtered_df = filter_by_outgoing_payments(filtered_df)
        elif figure_type == 'bubble':
            # if current graph type is bubble reset to bar
            # bubble graph can only work with either incoming or outgoing
            figure_type = 'bar'

        # filter by keyword(s)
        if key_remove and not key_isolate:
            # remove by keyword(s)
            keywords = key_remove.split(',')
            filtered_df = remove_keywords(filtered_df, keywords)
        elif key_isolate and not key_remove:
            # isolate by keyword(s)
            keywords = key_isolate.split(',')
            filtered_df = isolate_keywords(filtered_df, keywords)

        # filter by amounts
        if minimum and maximum:
            filtered_df = filter_by_min_max(filtered_df, minimum, maximum)
        elif minimum:
            filtered_df = filter_by_amount(filtered_df, minimum, True, False)
        elif maximum:
            filtered_df = filter_by_amount(filtered_df, maximum, False, True)

        # get the output for balance and savings report (bottom right sidebar)
        balance_output = update_json_output(filtered_df, in_out, savings)

        # main graph set up
        graph_style = {'plot_bgcolor': '#fff1d2',
                       'paper_bgcolor': '#fff1d2',
                       'font': {'color': '#212121'}}
        try:
            figure = new_graph(filtered_df, figure_type, graph_style)
        except:
            figure = new_graph(data_frame, figure_type, graph_style)

        graph = dcc.Graph(id='bank-graph',
                          figure=figure,
                          className='main-graph-figure')

        return graph, balance_output, top_repeat_payments_table, top_single_in_table, top_single_out_table,\
            single_in_title, single_out_title, repeat_title
