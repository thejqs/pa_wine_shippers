#!usr/bin/env python3
# stdlib imports
from collections import Counter, namedtuple
import os
import json
# project imports
import pandas as pd
import numpy as np
import matplotlib
# sets the matplotlib backend at runtime to one that can use
# a Python virtualenv
matplotlib.use('Agg')
import matplotlib.pyplot as plt

AxisDataSet = namedtuple(
    'AxisDataSet',
    [
        'y_position',
        'y_labels',
        'x_vals'
    ]
)


class ChartBuilder():

    # def get_freshest_data(self):
    #     '''
    #     uses data from the most recent file we have
    #
    #     args: none
    #
    #     returns: a pandas dataframe
    #     '''
    #     newest_file = sorted(os.listdir('data/'))[-1]
    #
    #     return pd.read_json('data/{}'.format(newest_file))

    def set_chart_data(self, top_values):
        '''
        processes values for use in a horizontal bar chart

        args: a tuple of [0]string value
                         [1]number of occurrences in the dataframe column

        returns: a namedtuple for structured parsing
        '''
        y_pos = np.arange(len(top_values))
        y_labels = [c[0] for c in top_values]
        x_vals = [c[1] for c in top_values]

        return AxisDataSet(
            y_pos,
            y_labels,
            x_vals
        )

    def build_chart(self, chart_data, title, filename):
        '''
        args: a namedtuple of [0]numpy arange for y-axis position
                              [1]a list of y-axis labels
                              [2]a list of x-axis values

        returns: none
        '''
        fig, ax = plt.subplots()
        ax.barh(chart_data[0], chart_data[2], align='center', alpha=0.5)
        plt.yticks(chart_data[0], chart_data[1])
        plt.title(title)
        similar_charts = ['emails', 'phones', 'addresses']
        for i, v in enumerate(chart_data[2]):
            if filename in similar_charts:
                ax.text(v - 2, i - .15, str(v))
            elif filename == 'states':
                if v > 500:
                    ax.text(v - 40, i - .15, str(v))
                else:
                    ax.text(v + 3, i - .25, str(v))
            elif filename == 'counties':
                if v > 200:
                    ax.text(v - 30, i - .25, str(v))
                else:
                    ax.text(v + 3, i - .15, str(v))
        fig.savefig('app/static/img/{}.png'.format(filename), bbox_inches='tight')

    # something something magic numbers something something.
    # having looked into the data a bit, these are where
    # it seems to get interesting consistently.
    # TODO: um, no more magic numbers, clearly
    def make_state_chart(self, dataframe):
        '''
        sets the chart of the top states represented in the data

        args: a pandas dataframe containing a 'state' column header

        returns: none
        '''
        top_states = Counter(dataframe.state_long).most_common(7)
        chart_data = self.set_chart_data(top_states)
        filename = 'states'
        title = 'Top 7 states for wine-shippers'
        self.build_chart(chart_data, title, filename)

    def make_counties_chart(self, dataframe):
        '''
        sets the chart of the top counties represented in the data

        args: a pandas dataframe containing a 'county' column header

        returns: none
        '''
        top_counties = Counter(dataframe.county + ', ' + dataframe.state_short).most_common(14)
        chart_data = self.set_chart_data(top_counties)
        filename = 'counties'
        title = 'Top 14 counties for wine-shippers'
        self.build_chart(chart_data, title, filename)

    def make_address_chart(self, dataframe):
        '''
        sets the chart of the top addresses represented in the data

        args: a pandas dataframe containing an 'address' column header

        returns: none
        '''
        top_addresses = Counter(dataframe.api_address).most_common(10)
        chart_data = self.set_chart_data(top_addresses)
        filename = 'addresses'
        title = 'Top 10 addresses for wine-shippers'
        self.build_chart(chart_data, title, filename)

    def make_emails_chart(self, dataframe):
        '''
        sets the chart of the top emails represented in the data

        args: a pandas dataframe containing an 'email' column header

        returns: none
        '''
        top_emails = Counter([a for a in dataframe.email if a != 'no email listed']).most_common(12)
        chart_data = self.set_chart_data(top_emails)
        filename = 'emails'
        title = 'Top 12 email addresses for wine-shippers'
        self.build_chart(chart_data, title, filename)

    def make_phone_chart(self, dataframe):
        '''
        sets the chart of the top phone numbers represented in the data

        args: a pandas dataframe containing an 'phone' column header

        returns: none
        '''
        top_phones = Counter([a for a in dataframe.phone if a != 'no phone given']).most_common(12)
        chart_data = self.set_chart_data(top_phones)
        filename = 'phones'
        title = 'Top 12 phone numbers for wine-shippers'
        self.build_chart(chart_data, title, filename)

    def make_charts(self, filename):
        '''
        primary wrapper function to create and save all our charts

        args: none

        returns: none
        '''
        # dataframe = self.get_freshest_data()
        with open(filename) as f:
            j = json.load(f)
            data = (j[key] for key in j)
            dataframe = pd.read_json(json.dumps(list(data)))
            self.make_state_chart(dataframe)
            self.make_counties_chart(dataframe)
            self.make_address_chart(dataframe)
            self.make_phone_chart(dataframe)


if __name__ == '__main__':
    # newest_file = 'wine_shippers-2017-06-03.json'
    newest_file = sorted(os.listdir('data/'))[-1]
    builder = ChartBuilder()
    builder.make_charts('data/{}'.format(newest_file))
