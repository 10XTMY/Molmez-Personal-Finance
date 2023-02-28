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

This is a tool for generated a demo csv file
"""
import random
import csv
from datetime import date, timedelta


first_names = ['Emma', 'Noah', 'Olivia', 'Liam', 'Ava', 'William', 'Sophia', 'Mason', 'Isabella', 'James', 'Mia',
               'Benjamin', 'Charlotte', 'Jacob', 'Abigail', 'Michael', 'Emily', 'Elijah', 'Harper', 'Ethan', 'Amelia',
               'Alexander', 'Evelyn', 'Oliver', 'Elizabeth', 'Daniel', 'Sofia', 'Matthew', 'Avery', 'Aiden', 'Ella',
               'Jackson', 'Madison', 'Logan', 'Scarlett', 'Connor', 'Victoria', 'Luke', 'Aria', 'Jayden', 'Grace',
               'Jack', 'Chloe', 'Carter', 'Camila', 'Jaxon', 'Natalie', 'Julia', 'Hannah', 'Nicholas', 'Aubrey',
               'Isaac', 'Brooklyn', 'William', 'Lily', 'Owen', 'Eleanor', 'Gavin', 'Natalie', 'Caleb', 'Addison',
               'Ryan', 'Avery', 'Luke', 'Evelyn', 'Derek', 'Hazel', 'Samuel', 'Ellie', 'Christian', 'Stella', 'Isaiah',
               'Peyton', 'Aaron', 'Mila', 'Eli', 'Allison', 'Parker', 'Audrey', 'Adam', 'Aaliyah', 'Nathan', 'Violet',
               'Gabel', 'Rylee', 'Tyler', 'Mackenzie', 'Brayden', 'Aubree', 'Jace', 'Brooklyn', 'Cameron', 'Bella',
               'Jordan', 'Adalyn', 'Owen', 'Aurora', 'Nicholas', 'Liliana', 'Ethan', 'Avery', 'Gavin', 'Evelyn',
               'Jacob', 'Abigail', 'Jayden', 'Kaylee', 'Elias', 'Annabelle', 'Jonathan', 'Maria', 'Colton', 'Naomi',
               'Evan', 'Reagan', 'Isaac', 'Aurora', 'Gage', 'Brooklyn', 'Carson', 'Aaliyah', 'Nolan', 'Makayla',
               'Riley', 'Aubree', 'Landon', 'Brielle']
names_set = set(first_names)
first_names = list(names_set)
shops = ['Walmart', 'Target', 'Starbucks', 'CVS', '7-Eleven']
atms = ['Chase', 'Wells Fargo', 'Capital One', 'TD Bank', 'Bank of America']


def generate_transactions(num_transactions, start_date, end_date):
    transactions = []
    for i in range(num_transactions):
        # generate transaction date
        date = random_date(start_date, end_date)
        # generate transaction amount
        amount = round(random.uniform(-1500, 1500), 2)
        details = ''
        # randomly select either shop, atm or first_name
        if i % 2 == 0:
            if i % 3 == 0:
                details = random.choice(shops)
            else:
                details = random.choice(atms)
        else:
            if len(first_names) == 0:
                details = random.choice(shops)
            else:
                name = random.choice(first_names)
                details = name
                first_names.remove(f'{details}')
        transactions.append([date.strftime('%m/%d/%Y'), details, amount])
    return transactions


def random_date(start, end):
    return start + timedelta(
        seconds=random.randint(0, int((end - start).total_seconds())))


def write_transactions_to_csv(transactions, csv_file):
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Date', 'Details', 'Amount'])
        for transaction in transactions:
            writer.writerow(transaction)


if __name__ == '__main__':

    num_transactions = 600

    end_date = date.today()
    start_date = end_date - timedelta(days=180)
    transactions = generate_transactions(num_transactions, start_date, end_date)
    write_transactions_to_csv(transactions, 'transactions.csv')
