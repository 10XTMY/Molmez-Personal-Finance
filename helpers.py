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

These are the helper functions used in the main app (analytics.py and upload.py)
"""
import base64
import io
import locale
import numpy as np
import pandas as pd
import plotly.express as px
from dash import html, dash_table

locale.setlocale(locale.LC_ALL, '')


def tuple_insert(tup, pos, ele):
    tup = tup[:pos] + (ele,) + tup[pos:]
    return tup


def verify_upload(uploaded_file, content_string):
    """
    Verifies the uploaded CSV file and converts it to a pandas DataFrame.
    :param uploaded_file: name of the uploaded file.
    :param content_string: content of the file in base64 encoding.
    :return: tuple containing a status code and DataFrame or error message.
    """
    try:
        if not uploaded_file.endswith('.csv'):
            return 0, 'Please select a .csv file'

        decoded = base64.b64decode(content_string)
        decoded_csv = io.StringIO(decoded.decode('utf-8-sig'))
        header = pd.read_csv(decoded_csv, nrows=1).columns.tolist()

        if header == ['Date', 'Details', 'Amount']:
            # reset StringIO object to read from the beginning
            decoded_csv.seek(0)
            df = bank_csv_to_data_frame(decoded_csv)
            return 1, df
        else:
            return 0, 'CSV layout should be: Date, Details, Amount'

    except Exception as e:
        return 0, f'Error processing uploaded file: {e}'


def bank_csv_to_data_frame(csv_input):
    """
    Converts a bank CSV file to a pandas DataFrame with formatted columns.
    :param csv_input: path to the CSV file.
    :return: pandas DataFrame.
    """
    try:
        # read CSV and perform initial transformations
        df = pd.read_csv(csv_input, dtype=object)
        df['Amount'] = df['Amount'].str.replace(',', '').astype(float).round(2)
        df['Details'] = df['Details'].str.replace(')', '')
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)

        # set 'Date' as the index
        df.set_index('Date', inplace=True)

        return df

    except KeyError as e:
        raise KeyError(f"DataFrame column error processing the CSV file: {e}")
    except ValueError as e:
        raise ValueError(f"Data processing error processing the CSV file: {e}")
    except Exception as e:
        raise Exception(f"Error processing the CSV file: {e}")


def new_graph(data_frame, graph_type, graph_style):
    """
    Creates a new graph based on the specified type and style.
    :param data_frame: pandas DataFrame.
    :param graph_type: type of the graph ('line', 'bubble', 'funnel', 'bar').
    :param graph_style: style settings for the graph.
    :return: plotly graph object.
    """
    # common parameters for all graphs
    common_params = {
        'x': data_frame.index,
        'y': data_frame['Amount'],
        'hover_data': ['Details', 'Amount'],
        'template': 'plotly_dark'
    }

    if graph_type == 'line':
        graph_new = px.line(data_frame, **common_params)
    elif graph_type == 'bubble':
        graph_new = px.scatter(data_frame, size=data_frame['Amount'], color=data_frame['Amount'], **common_params)
    elif graph_type == 'funnel':
        graph_new = px.funnel(data_frame, color=data_frame['Details'], **common_params)
    else:  # default to bar graph
        graph_new = px.bar(data_frame, barmode="group", color=data_frame['Amount'], **common_params)

    # apply additional styling
    graph_new.update_layout(graph_style)

    return graph_new


def calculate_total(data_frame):
    """
    Calculates the total incoming and outgoing amounts from a DataFrame.
    :param data_frame: pandas DataFrame with an 'Amount' column.
    :return: total incoming and outgoing amounts.
    """
    try:
        # calculate total outgoing amount
        total_out = data_frame.loc[data_frame['Amount'] < 0, 'Amount'].sum()
        total_out = np.round(np.abs(total_out), 2)

        # calculate total incoming amount
        total_in = data_frame.loc[data_frame['Amount'] > 0, 'Amount'].sum()
        total_in = np.round(total_in, 2)

        return total_in, total_out

    except KeyError as e:
        raise KeyError(f"DataFrame column error calculating totals: {e}")
    except ValueError as e:
        raise ValueError(f"Data processing error calculating totals: {e}")
    except Exception as e:
        raise Exception(f"Error calculating totals: {e}")


def filter_by_date_range(data_frame, from_date, to_date):
    """
    Filters the DataFrame based on a given date range.
    :param data_frame: pandas DataFrame with a DateTimeIndex.
    :param from_date: start date in ISO format (YYYY-MM-DD).
    :param to_date: end date in ISO format (YYYY-MM-DD).
    :return: pandas DataFrame within the specified date range.
    """
    try:
        # convert ISO format dates to datetime objects
        start_date = pd.to_datetime(from_date)
        end_date = pd.to_datetime(to_date)

        # ensure the DataFrame index is of datetime type
        if not pd.api.types.is_datetime64_any_dtype(data_frame.index):
            raise TypeError("DataFrame index must be a DateTimeIndex.")

        # create a date range mask and filter the DataFrame
        mask = (data_frame.index >= start_date) & (data_frame.index <= end_date)
        date_range = data_frame.loc[mask]

        # return the original DataFrame if the filtered DataFrame is empty
        return date_range if not date_range.empty else data_frame

    except KeyError as e:
        raise KeyError(f"DataFrame column error filtering by date range: {e}")
    except TypeError as e:
        raise TypeError(f"DataFrame index error filtering by date range: {e}")
    except ValueError as e:
        raise ValueError(f"Data processing error filtering by date range: {e}")
    except Exception as e:
        raise Exception(f"Error filtering by date range: {e}")


def filter_by_incoming_payments(data_frame):
    return data_frame.loc[(data_frame['Amount'] > 0)]


def filter_by_outgoing_payments(data_frame):
    """
    Filters the DataFrame for outgoing payments and adjusts the 'Amount' column.
    :param data_frame: pandas DataFrame with an 'Amount' column.
    :return: pandas DataFrame
    """
    try:
        # filter for rows where 'Amount' is less than 0 (outgoing payments)
        filtered_data_frame = data_frame.loc[data_frame['Amount'] < 0]

        # process 'Amount': remove negative sign and convert to float
        filtered_data_frame['Amount'] = filtered_data_frame['Amount'].abs()

        return filtered_data_frame

    except KeyError as e:
        raise KeyError(f"DataFrame column error filtering by outgoing payments: {e}")
    except ValueError as e:
        raise ValueError(f"Data processing error filtering by outgoing payments: {e}")
    except Exception as e:
        raise Exception(f"Error filtering by outgoing payments: {e}")


def isolate_keywords(data_frame, keywords):
    """
        Isolates rows in the 'Details' that contain any of the specified keywords.
        :param data_frame: pandas DataFrame with a 'Details' column.
        :param keywords: list of keywords to isolate.
        :return: pandas DataFrame.
        """
    try:
        # filter out empty strings from the keywords list
        keywords = [keyword.strip() for keyword in keywords if keyword.strip()]

        # if no valid keywords are provided, return the original DataFrame
        if not keywords:
            return data_frame

        # add a pipe separator between keywords to create a regex pattern as a logical OR
        pattern = '|'.join(keywords)
        print(f'isolating keywords: {pattern}')
        filtered_data_frame = data_frame.loc[data_frame['Details'].str.contains(pattern, case=False, regex=True)]

        return filtered_data_frame

    except KeyError as e:
        raise KeyError(f"DataFrame column error isolating keywords: {e}")
    except ValueError as e:
        raise ValueError(f"Data processing error isolating keywords: {e}")
    except Exception as e:
        raise Exception(f"Error isolating keywords: {e}")


def remove_keywords(data_frame, keywords):
    """
    Removes rows from 'Details' that contain any of the specified keywords.
    :param data_frame: pandas DataFrame with a 'Details' column.
    :param keywords: list of keywords based on which rows are to be removed.
    :return: pandas DataFrame after removing rows with specified keywords.
    """
    # filter out empty strings from the keywords list
    keywords = [keyword.strip() for keyword in keywords if keyword.strip()]

    # if no valid keywords are provided, return the original DataFrame
    if not keywords:
        return data_frame

    try:
        # add a pipe separator between keywords to create a regex pattern as a logical OR
        pattern = '|'.join(keywords)
        filtered_data_frame = data_frame.loc[~data_frame['Details'].str.contains(pattern, case=False, regex=True)]

        return filtered_data_frame

    except KeyError as e:
        raise KeyError(f"DataFrame column error removing keywords: {e}")
    except ValueError as e:
        raise ValueError(f"Data processing error removing keywords: {e}")
    except Exception as e:
        raise Exception(f"Error removing keywords: {e}")


def filter_by_amount(data_frame, amount, min_filter, max_filter):
    """
        Filters the DataFrame based on a given amount threshold.
        :param data_frame: pandas DataFrame with an 'Amount' column.
        :param amount: threshold amount for filtering.
        :param min_filter: Boolean if filtering for amounts greater than the threshold.
        :param max_filter: Boolean if filtering for amounts less than the threshold.
        :return: A pandas DataFrame filtered based on the specified amount condition.
        """
    try:
        if 'Amount' not in data_frame.columns:
            raise KeyError("'Amount' column not found in DataFrame.")

        if min_filter:
            return data_frame.loc[data_frame['Amount'] > amount]
        elif max_filter:
            return data_frame.loc[data_frame['Amount'] < amount]
        else:
            return data_frame

    except KeyError as e:
        raise KeyError(f"DataFrame column error filtering by amount: {e}")
    except ValueError as e:
        raise ValueError(f"Data processing error filtering by amount: {e}")
    except Exception as e:
        raise Exception(f"Error filtering by amount: {e}")


def filter_by_min_max(data_frame, min_amount, max_amount):
    """
    Filters the DataFrame based on minimum and maximum amount thresholds.
    :param data_frame: pandas DataFrame with an 'Amount' column.
    :param min_amount: minimum amount threshold for filtering.
    :param max_amount: maximum amount threshold for filtering.
    :return: A pandas DataFrame filtered based on the specified min and max amounts.
    """
    try:
        if 'Amount' not in data_frame.columns:
            raise KeyError("'Amount' column not found in DataFrame.")

        return data_frame.loc[(data_frame['Amount'] > min_amount) & (data_frame['Amount'] < max_amount)]

    except KeyError as e:
        raise KeyError(f"DataFrame column error filtering by min max: {e}")
    except ValueError as e:
        raise ValueError(f"Data processing error filtering by min max: {e}")
    except Exception as e:
        raise Exception(f"Error filtering by min max: {e}")


def _format_json_output(*args):
    """
    Formats a series of labels and values into a JSON-like string.
    :param args: sequence of labels and values.
    :return: string.
    """
    indent = '  '
    formatted_output = '{\n'
    for i in range(0, len(args), 2):
        label, value = args[i], args[i + 1]
        formatted_output += f'{indent}{label}: {value:n}\n'
    formatted_output = formatted_output.rstrip('\n') + '\n}'
    return formatted_output


def update_json_output(data_frame, in_out, savings_number):
    """
    Prepares a JSON-like formatted string output from DataFrame calculations.
    :param data_frame: A pandas DataFrame.
    :param in_out: A list indicating the type of transactions ('paid_in', 'paid_out').
    :param savings_number: Keywords for isolating savings data.
    :return: A Dash HTML component containing the formatted string.
    """
    try:
        filtered_by_out = len(in_out) == 1 and in_out[0] == 'paid_out'
        total_in, total_out = calculate_total(data_frame)

        if filtered_by_out:
            total_out, total_in = (total_in, 0) if not total_out else (total_out, total_in)

        diff = round(abs(total_in - total_out), 2) if total_in and total_out else 0

        return_string = _format_json_output('Total in', total_in, 'Total out', total_out, 'Difference', diff)

        if savings_number:
            savings_df = isolate_keywords(data_frame, savings_number)
            savings_out, savings_in = calculate_total(savings_df)
            savings_total = round(abs(savings_out - savings_in), 2)

            savings_string = _format_json_output('Savings in', savings_in, 'Savings out', savings_out, 'Total Savings',
                                                 savings_total)
            return_string += '\n' + savings_string

        return html.Pre(return_string)

    except KeyError as e:
        raise KeyError(f"DataFrame column error updating JSON output: {e}")
    except ValueError as e:
        raise ValueError(f"Data processing error updating JSON output: {e}")
    except Exception as e:
        raise Exception(f"Error updating JSON output: {e}")


def sort_by_duplicate_count_with_totals(data_frame):
    """
    Groups the DataFrame by 'Details', sums the 'Amount' for each group, counts the duplicates,
    and sorts the result by the duplicate count in descending order.
    :param data_frame: pandas DataFrame with 'Details' and 'Amount' columns.
    :return: pandas DataFrame.
    """
    try:
        if 'Details' not in data_frame.columns or 'Amount' not in data_frame.columns:
            raise KeyError("Required columns 'Details' and 'Amount' not found in DataFrame.")

        # group by 'Details' and calculate sum and size
        grouped = data_frame.groupby('Details')['Amount'].agg(['sum', 'size']).reset_index()
        grouped = grouped.rename(columns={'sum': 'Amount', 'size': 'Count'})

        # sort by 'Count' (duplicate count) in descending order
        sorted_df = grouped.sort_values('Count', ascending=False)

        return sorted_df

    except KeyError as e:
        raise KeyError(f"DataFrame column error sorting by duplicate count with totals: {e}")
    except ValueError as e:
        raise ValueError(f"Data processing error sorting by duplicate count with totals: {e}")
    except Exception as e:
        raise Exception(f"Error sorting by duplicate count with totals: {e}")


def _prepare_payments_df(df, column_name, max_list):
    """
    Prepares a DataFrame for payment data.
    :param df: pandas DataFrame.
    :param column_name: name for the new column ('In' or 'Out').
    :param max_list: maximum number of entries to return.
    :return: pandas DataFrame.
    """
    df[column_name] = df['Amount'].round(2).abs()
    df = df.sort_values(column_name, ascending=(column_name == 'Out')).head(max_list)
    df.reset_index(drop=True, inplace=True)
    df.drop(['Amount', 'Count'], axis=1, inplace=True)

    # reset NaN entries to 0
    df.fillna(0, inplace=True)

    return df


def calculate_top_single_payments(data_frame, max_list):
    """
    Processes a DataFrame to identify and split top single incoming and outgoing payments.
    :param data_frame: pandas DataFrame.
    :param max_list: maximum number of entries to return.
    :return: two pandas DataFrames - one for incoming payments and one for outgoing payments.
    """
    try:
        # collate repeat transactions and apply totals along with a repeat count
        duplicates_sorted = sort_by_duplicate_count_with_totals(data_frame)

        # select only the unique entries
        single_payments = duplicates_sorted[duplicates_sorted['Count'] == 1]
        if single_payments.empty:
            return pd.DataFrame(), pd.DataFrame()

        # split into two data frames for incoming and outgoing
        single_payments_in = single_payments[single_payments['Amount'] > 0].copy()
        single_payments_out = single_payments[single_payments['Amount'] < 0].copy()

        # round float amounts to 2 decimal places and drop unnecessary columns
        single_payments_in = _prepare_payments_df(single_payments_in, 'In', max_list)
        single_payments_out = _prepare_payments_df(single_payments_out, 'Out', max_list)

        return single_payments_out, single_payments_in

    except KeyError as e:
        raise KeyError(f"DataFrame column error calculating top single payments: {e}")
    except ValueError as e:
        raise ValueError(f"Data processing error calculating top single payments: {e}")
    except Exception as e:
        raise Exception(f"Error calculating top single payments: {e}")


def calculate_top_repeat_transactions(data_frame, max_list):
    """
    Processes a DataFrame to identify and collect top repeat transactions.
    :param data_frame: pandas DataFrame.
    :param max_list: maximum number of repeat transactions to return.
    :return: pandas DataFrame.
    """
    try:

        # collate repeat transactions and apply totals along with a repeat count
        duplicate_count = sort_by_duplicate_count_with_totals(data_frame)

        if 'Amount' not in duplicate_count.columns or 'Count' not in duplicate_count.columns:
            raise KeyError("Required columns 'Amount' or 'Count' not found in DataFrame.")

        # extract all multi-payments, exclude singles
        top_multi_payments = duplicate_count[duplicate_count['Count'] > 1].head(max_list)

        if top_multi_payments.empty:
            return pd.DataFrame()

        # round amounts to 2 decimal places
        top_multi_payments['Amount'] = top_multi_payments['Amount'].round(2)

        # Split the payment amounts by positive/negative into In and Out columns
        top_multi_payments['In'] = top_multi_payments['Amount'].where(top_multi_payments['Amount'] > 0, 0)
        top_multi_payments['Out'] = top_multi_payments['Amount'].where(top_multi_payments['Amount'] < 0, 0)

        # drop the original Amount column
        top_multi_payments.drop('Amount', axis=1, inplace=True)
    except KeyError as e:
        raise KeyError(f"DataFrame column error calculating top repeat transactions: {e}")
    except ValueError as e:
        raise ValueError(f"Data processing error calculating top repeat transactions: {e}")
    except Exception as e:
        raise Exception(f"Error calculating top repeat transactions: {e}")

    return top_multi_payments

# TABLE_STYLE = {
#     'style_data': {
#         'background': '#fff1d2',
#         'fontFamily': 'Segoe UI, serif',
#         'fontSize': '1rem'
#     },
#     'style_header': {
#         'background': '#707070',
#         'color': 'white',
#         'fontFamily': 'Segoe UI, serif',
#         'fontSize': '1rem',
#         'textAlign': 'center'
#     },
#     'style_cell': {
#         'padding': '10px'
#     }
# }


def data_frame_to_table(data_frame):
    payments_table = dash_table.DataTable(data=data_frame.to_dict('records'),
                                          columns=[{"name": col, "id": col} for col in data_frame.columns],
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
                                          # **TABLE_STYLE
                                          )
    return payments_table


def generate_pdf(tables, graph):
    pass
