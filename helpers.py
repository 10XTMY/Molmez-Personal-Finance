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

These are the helper functions used in the main app (analytics.py and upload.py)
"""
import csv
import base64
import io
import locale
import numpy as np
import pandas as pd
import plotly.express as px
from datetime import date
from dash import html, dash_table


locale.setlocale(locale.LC_ALL, '')


def tuple_insert(tup, pos, ele):
    tup = tup[:pos] + (ele,) + tup[pos:]
    return tup


def verify_upload(uploaded_file, content_string):
    if not uploaded_file.endswith('.csv'):
        return 0, 'please select a .csv file'
    decoded = base64.b64decode(content_string)
    decoded_csv = io.StringIO(decoded.decode('utf-8-sig'))
    reader = csv.reader(decoded_csv)
    # get the first line
    row1 = next(reader)
    if row1 == ['Date', 'Details', 'Amount']:
        converted = io.StringIO(decoded.decode('utf-8-sig'))
        return 1, bank_csv_to_data_frame(converted)
    else:
        return 0, 'csv layout should be: Date,Details,Amount'


def bank_csv_to_data_frame(csv_input):
    df = pd.read_csv(csv_input, dtype=object)
    df['Amount'] = df['Amount'].str.replace(',', '')
    df['Amount'] = df['Amount'].astype(float)
    df['Amount'] = df['Amount'].round(2)
    df['Details'] = df['Details'].str.replace(')', '')
    df['Date'] = df['Date'].apply(pd.to_datetime, dayfirst=True)
    df.set_index('Date', inplace=True)
    return df


def new_graph(data_frame, graph_type, graph_style):
    if graph_type == 'line':
        graph_new = px.line(data_frame,
                            x=data_frame.index,
                            y=data_frame['Amount'],
                            hover_data=['Details', 'Amount'],
                            template='plotly_dark').update_layout(graph_style)
    elif graph_type == 'bubble':
        graph_new = px.scatter(data_frame,
                               x=data_frame.index,
                               y=data_frame['Amount'],
                               hover_data=['Details', 'Amount'],
                               size=data_frame['Amount'],
                               color=data_frame['Amount'],
                               template='plotly_dark').update_layout(graph_style)
    elif graph_type == 'funnel':
        graph_new = px.funnel(data_frame,
                              x=data_frame.index,
                              y=data_frame['Amount'],
                              color=data_frame['Details'],
                              template='plotly_dark').update_layout(graph_style)
    else:
        graph_new = px.bar(data_frame,
                           x=data_frame.index,
                           y=data_frame['Amount'],
                           barmode="group",
                           color=data_frame['Amount'],
                           hover_data=['Details', 'Amount'],
                           template='plotly_dark').update_layout(graph_style)

    return graph_new


def calculate_total(data_frame):
    outgoing = data_frame.loc[(data_frame['Amount'] < 0)]
    total_outgoing = outgoing.sum(axis=0, numeric_only=True)
    total_out = np.absolute(np.round(total_outgoing["Amount"], 2))
    if not total_out:
        total_out = 0

    incoming = data_frame.loc[(data_frame['Amount'] > 0)]
    total_incoming = incoming.sum(axis=0, numeric_only=True)
    total_in = np.round(total_incoming["Amount"], 2)
    if not total_in:
        total_in = 0

    return total_in, total_out


def filter_by_date_range(data_frame, from_date, to_date):
    start_date_object = date.fromisoformat(from_date)
    start_date_string = start_date_object.strftime('%d-%m-%Y')

    end_date_object = date.fromisoformat(to_date)
    end_date_string = end_date_object.strftime('%d-%m-%Y')

    start_date = pd.to_datetime(start_date_string, dayfirst=True)
    end_date = pd.to_datetime(end_date_string, dayfirst=True)

    mask = (data_frame.index >= start_date) & (data_frame.index <= end_date)
    date_range = data_frame.loc[mask]
    if date_range.empty:
        return data_frame
    return date_range


def filter_by_incoming_payments(data_frame):
    filtered_data_frame = data_frame.loc[(data_frame['Amount'] > 0)]
    return filtered_data_frame


def filter_by_outgoing_payments(data_frame):
    filtered_data_frame = data_frame.loc[(data_frame['Amount'] < 0)]
    filtered_data_frame['Amount'] = filtered_data_frame['Amount'].astype(str)
    filtered_data_frame['Amount'] = filtered_data_frame['Amount'].str.replace('-', '')
    filtered_data_frame['Amount'] = filtered_data_frame['Amount'].astype(float)
    return filtered_data_frame


def isolate_keywords(data_frame, keywords):
    filtered_data_frame = data_frame.loc[data_frame['Details'].str.contains('|'.join(keywords),
                                                                            case=False,
                                                                            regex=False)]
    return filtered_data_frame


def remove_keywords(data_frame, keywords):
    if keywords:
        filtered_data_frame = data_frame
        for word in keywords:
            filtered_data_frame = filtered_data_frame.loc[~filtered_data_frame['Details'].str.contains(pat=word,
                                                                                                       case=False)]
        return filtered_data_frame
    else:
        return data_frame


def filter_by_amount(data_frame, amount, min_filter, max_filter):
    if min_filter:
        filtered_data_frame = data_frame.loc[data_frame['Amount'] > amount]
    elif max_filter:
        filtered_data_frame = data_frame.loc[data_frame['Amount'] < amount]
    else:
        return data_frame
    return filtered_data_frame


def filter_by_min_max(data_frame, min_amount, max_amount):
    filtered_data_frame = data_frame.loc[data_frame['Amount'] > min_amount]
    filtered_data_frame = filtered_data_frame.loc[filtered_data_frame['Amount'] < max_amount]
    return filtered_data_frame


def update_json_output(df, in_out, savings_number):
    filtered_by_out = False

    if len(in_out) == 1 and in_out[0] == 'paid_out':
        filtered_by_out = True
    total_in, total_out = calculate_total(df)

    if filtered_by_out and not total_out:
        total_out = total_in
        total_in = 0

    if total_in and total_out:
        diff = round(abs(total_in - total_out), 2)
    else:
        diff = 0

    return_string = f'{{\nTotal in: {total_in:n}\nTotal out: {total_out:n}\nDifference: {diff:n}..}}'
    indent = '  '
    return_string = return_string.replace('\n', '\n' + indent)
    return_string = return_string.replace('..', '\n')

    if savings_number:
        savings_df = isolate_keywords(df, savings_number)
        savings_out, savings_in = calculate_total(savings_df)
        savings_total = round(abs(savings_out - savings_in), 2)

        savings_string = f'{{\nSavings in: {savings_in:n}\nSavings out: {savings_out:n}\n' \
                         f'Total Savings: {savings_total:n}..}}'
        savings_string = savings_string.replace('\n', '\n' + indent)
        savings_string = savings_string.replace('..', '\n')
        return_string += f'\n{savings_string}'

    return html.Pre(return_string)


def sort_by_duplicate_count_with_totals(data_frame):
    # store total amounts for repeated payments
    # for this data frame the .groupby() method performs better than .unique() or .drop_duplicates()
    df_grouped = data_frame.groupby('Details')['Amount'].sum().reset_index()
    # store the count of repeat payments
    duplicate_count = data_frame.groupby(['Details'], as_index=False).size()
    # replace the amounts with the totals
    duplicate_count['Amount'] = df_grouped[df_grouped['Details'].isin(duplicate_count['Details'])]['Amount'].values
    # sort the data frame by the repeat count (descending)
    duplicate_count = duplicate_count.sort_values('size', ascending=False)
    return duplicate_count


def calculate_top_single_payments(data_frame, max_list):

    # collate repeat transactions and apply totals along with a repeat count
    duplicates_sorted = sort_by_duplicate_count_with_totals(data_frame)

    # select only the unique entries
    single_payments = duplicates_sorted[duplicates_sorted['size'] == 1].reset_index()

    # split into two data frames for incoming and outgoing
    single_payments_in = single_payments.copy()
    single_payments_out = single_payments.copy()
    single_payments_in['In'] = single_payments_in['Amount'].where(single_payments_in['Amount'] > 0)
    single_payments_out['Out'] = single_payments_out['Amount'].where(single_payments_out['Amount'] < 0)

    # round float amounts to 2 decimal places
    single_payments_in['In'] = single_payments_in['In'].round(2)
    # drop nan rows
    single_payments_in.dropna(inplace=True)

    single_payments_out['Out'] = single_payments_out['Out'].round(2)
    single_payments_out.dropna(inplace=True)

    # drop all undesired columns for data table output
    single_payments_in.drop('Amount', axis=1, inplace=True)
    single_payments_in.drop('index', axis=1, inplace=True)
    single_payments_in.drop('size', axis=1, inplace=True)
    single_payments_out.drop('Amount', axis=1, inplace=True)
    single_payments_out.drop('index', axis=1, inplace=True)
    single_payments_out.drop('size', axis=1, inplace=True)

    # sort out going from lowest to highest and trim to required list length
    single_payments_out = single_payments_out.sort_values('Out', ascending=True)
    single_payments_out = single_payments_out.reset_index(drop=True)
    if single_payments_out.shape[0] > max_list - 1:
        single_payments_out = single_payments_out[single_payments_out.index <= max_list - 1]

    # sort incoming from highest to lowest and trim to required list length
    single_payments_in = single_payments_in.sort_values('In', ascending=False)
    single_payments_in = single_payments_in.reset_index(drop=True)
    if single_payments_in.shape[0] > max_list - 1:
        single_payments_in = single_payments_in[single_payments_in.index <= max_list - 1]

    # [ ** WARNING: below screws up the sorting mechanism on the dash.dash_table component ** ]
    # add commas to thousands
    # single_payments_out['Out'] = single_payments_out['Out'].map('{:,.2f}'.format)
    # single_payments_in['In'] = single_payments_in['In'].map('{:,.2f}'.format)

    # reset nan entries to 0
    single_payments_out = single_payments_out.replace('nan', 0)
    single_payments_in = single_payments_in.replace('nan', 0)

    return single_payments_out, single_payments_in


def calculate_top_repeat_transactions(data_frame, max_list):
    # collate repeat transactions and apply totals along with a repeat count
    duplicate_count = sort_by_duplicate_count_with_totals(data_frame)

    # extract all multi-payments, exclude singles
    top_multi_payments = duplicate_count[duplicate_count['size'] > 1].reset_index()

    # trim to required list length
    if top_multi_payments.shape[0] > max_list - 1:
        top_multi_payments = top_multi_payments[top_multi_payments.index <= max_list - 1]

    # reset the index to 0->, dropping the now disordered index
    top_multi_payments = top_multi_payments.reset_index(drop=True)
    # the original index has also been stored into its own column
    # drop it like its hot
    top_multi_payments.drop('index', axis=1, inplace=True)
    # rename the repeat transaction count column
    top_multi_payments.rename(columns={'size': 'Count'}, inplace=True)
    # round all payments to 2 decimal places
    top_multi_payments['Amount'] = top_multi_payments['Amount'].round(2)

    # split the payment amounts by positive/negative into In and Out columns
    top_multi_payments['In'] = top_multi_payments['Amount'].where(top_multi_payments['Amount'] > 0)
    top_multi_payments['Out'] = top_multi_payments['Amount'].where(top_multi_payments['Amount'] < 0)
    # drop the original payment amounts column
    top_multi_payments.drop('Amount', axis=1, inplace=True)

    # [ ** WARNING: below screws up the sorting mechanism on the dash.dash_table component ** ]
    # add commas to thousands
    # top_multi_payments['In'] = top_multi_payments['In'].map('{:,.2f}'.format)
    # top_multi_payments['Out'] = top_multi_payments['Out'].map('{:,.2f}'.format)
    # above mapping causes empty cells to contain 'nan' strings
    # reset nan entries to 0
    # top_multi_payments = top_multi_payments.replace('nan', 0)

    return top_multi_payments


def data_frame_to_table(data_frame):
    payments_table = dash_table.DataTable(data=data_frame.to_dict('records'),
                                          columns=[{"name": i, "id": i} for i in data_frame.columns],
                                          sort_action="native",
                                          sort_mode="multi",
                                          row_deletable=False,
                                          style_data={'background': '#fff1d2',
                                                      'fontFamily': 'Segoe UI, serif',
                                                      'fontSize': '1rem'
                                                      },
                                          style_header={'background': '#707070',
                                                        'color': 'white',
                                                        'fontFamily': 'Segoe UI, serif',
                                                        'fontSize': '1rem',
                                                        'textAlign': 'center'},
                                          style_cell={'padding': '10px'},
                                          export_format='csv',
                                          style_as_list_view=True
                                          )
    return payments_table


def generate_pdf(tables, graph):
    pass
