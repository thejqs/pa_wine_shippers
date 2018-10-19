#!usr/bin/env python3

# python
import csv
from datetime import date
# from collections import namedtuple
import os
import uuid
from pprint import pprint
# external imports
import requests
import tabula
# project imports
# import geolocator
import file_writer

# Licensee = namedtuple(
#     'Licensee',
#     [
#         'license_no',
#         'name',
#         'address',
#         'phone'
#     ]
# )


def get_pdf(url):
    '''
    collects the daily pdf of PLCB licensees who can
    ship wine to residents directly

    args: a url string to the pdf

    returns: a response object containing the raw pdf
    '''
    return requests.get(url)


def copy_pdf(pdf, file_location):
    '''
    stashes the pdf in a consistent replace

    args: the response object containing the pdf

    returns: none
    '''
    with open(file_location, 'wb') as f:
        f.write(pdf.content)


def get_latest_pdf(pdf_dir):
    '''
    whatever is the most recent pdf, grabs it
    can be run independently of the scraper parts, so this can start up
    parsing the pdf locally without reaching out across the internets

    args: none

    returns: the most recent filename
    '''
    return sorted(os.listdir(pdf_dir))[-1]


def pdf_to_csv(pdf, csvfile):
    '''
    leverages the tabula-py library to extract the data in the pdf into something more manageable -- a csv

    args: the pdf to extract from; the csv to write to

    returns: none
    '''
    tabula.convert_into(pdf, csvfile, output_format='csv', options='--pages all', java_options=["-Djava.awt.headless=true"])


def mostly_clean_data(csvfile):
    '''
    given a csv, clean up the data, skipping extra headers, reassembling addresses, etc.

    args: the csv file

    returns: a dict of cleaned data
    '''
    with open(csvfile) as f:
        r = csv.reader(f)
        headers = next(r)
        data = {}
        last_key_added = ''
        for row in r:
            if row == headers:
                continue

            elif row[0]:
                last_key_added = row[1]
                data[last_key_added] = {
                    'plcb_id': row[0],
                    'licensee_no': row[1],
                    'name': row[2],
                    'csv_address': row[3],
                    'phone': row[4]
                }

            # sometimes a piece of the address gets parsed to another, otherwise empty, row
            elif not row[0]:
                # print(row)
                data[last_key_added]['csv_address'] += f', {row[3]}'

        # HOW IS PART OF THE ADDRESS FOR THE LAST ENTRY ON EVERY PAGE CUT OFF LIKE THE WORST PAIR OF JORTS -- CAN THE API SAVE ME?
        # pprint([(k, v['address']) for k, v in data.items()])
        # pprint(data['82267'])
        # pprint(data['92077'])
        # pprint(data['82030'])
        return data



if __name__ == '__main__':
    url = 'http://www.apps.lcb.pa.gov/webapp/reports/REP597_Report.pdf'
    pdf_dir = 'pdfs/'
    pdf_file_format = f'wine_pdf-{date.today()}.pdf'
    pdf_location = os.path.join(pdf_dir, pdf_file_format)
    csv_dir = 'data/csv/'
    csv_file_format = f'wine_shippers-{date.today()}.csv'
    csv_location = os.path.join(csv_dir, csv_file_format)
    json_dir = 'data/initial_json/'
    json_file_format = f'wine_shippers-{date.today()}.json'
    json_location = os.path.join(json_dir, json_file_format) 

    pdf = get_pdf(url)
    copy_pdf(pdf, pdf_location)
    latest_pdf = get_latest_pdf(pdf_dir)
    pdf_to_csv(f'{pdf_dir}{latest_pdf}', csv_location)
    scrubbed_data = mostly_clean_data(csv_location)
    file_writer.write_json(scrubbed_data, json_location)



