#!usr/local/bin/env python3

# python imports
import os
import json
from datetime import date
from collections import namedtuple
import uuid
from pprint import pprint
# external imports
import requests
# project imports
from scraper_config.settings_local import geojson_stub, geojson_key
import file_writer

Geolocator = namedtuple(
    'Geolocator',
    [
        'address',
        'latitude',
        'longitude',
        'county',
        'state_long_name',
        'state_short_name',
        'country'
    ]
)

def get_data(source_file):
    with open(source_file) as f:
        return json.load(f)


def get_latest_json(json_dir):
    '''
    whatever is the most recent incomplete json, grabs it

    can be run independently of the scraper parts, so this can start up
    parsing the json locally without reaching out across the internets

    args: none

    returns: the most recent filename
    '''
    return sorted(os.listdir(json_dir))[-1]


def ping_api(address):
    '''
    catches the initial response from the Google geolocation API

    args: an address string

    returns: the response object
    '''
    p = {'address': address, 'key': geojson_key}
    return requests.get(geojson_stub, params=p)


def get_geolocation_data(address):
    '''
    leverages Google's address-conversion API to extract
    latitude and longitude as well as a better-formatted address details
    for each wine shipper.

    args: an address string to pass to the API

    returns: a namedtuple consisting of: 
    [0]address,
    [1]latitude,
    [2]longitude,
    [3]county,
    [4]state_long_name,
    [5]state_short_name
    [6]country
    '''
    county = ''
    state_long = ''
    state_short = ''
    country = ''

    # TODO: refactor into async
    r = ping_api(address)

    # addresses are self-reported and human-entered; they will always be
    # a little messy and the API will always miss a few
    try:
        # if the API whiffs, ['results'] will == []
        formatted_address = r.json()['results'][0]['formatted_address']
        lat = r.json()['results'][0]['geometry']['location']['lat']
        lng = r.json()['results'][0]['geometry']['location']['lng']
        address_components = r.json()['results'][0]['address_components']

        # the API is maddeningly stingy with lookups -- especially for data
        # that can move index positions. I feel dirty writing a loop here.
        # but Google made me.
        for line in address_components:
            if line['types'][0] == 'administrative_area_level_2':
                county = line['long_name']
            elif line['types'][0] == 'administrative_area_level_1':
                state_long = line['long_name']
                state_short = line['short_name']
            elif line['types'][0] == 'country':
                country = line['long_name']

        geolocator = Geolocator(
            formatted_address,
            lat,
            lng,
            county,
            state_long,
            state_short,
            country
        )

        return geolocator

    except IndexError:
        return None


def try_clean_api_address(address):
    '''
    we've collected a mapping of addresses the API hasn't been able to handle
    to ones it can, so this should give us a fuller overall data set
    '''
    with open('scraper/address_map.json') as f:
        j = json.load(f)
        for d in j:
            if d['given_address'] == address:
                yield d['api_address']
                break


def obj_builder(data_dict, geolocator):
    '''
    takes some of messy assigning out of build_shit(), where
    we might not always have a successful trip to the API.
    only gets called when we do.

    args: the target object, a dict, for our new data and a namedtuple
    of goodies from the API

    returns: the updated target object
    '''
    # print(geolocator)
    # print(data_dict)
    # print(geolocator.address[:-5])
    data_dict['api_address'] = geolocator.address[:-5]
    data_dict['latitude'] = geolocator.latitude
    data_dict['longitude'] = geolocator.longitude
    data_dict['county'] = geolocator.county
    data_dict['state_long'] = geolocator.state_long_name
    data_dict['state_short'] = geolocator.state_short_name
    data_dict['country'] = geolocator.country
    # print(data_dict['country'])

    return data_dict


def build_shit(source_file):
    data_dicts = get_data(source_file)
    # pprint(data_dicts)
    for d in data_dicts.keys():
        data_dicts[d]['uid'] = f'{uuid.uuid1()}'
        data_dicts[d]['scrape_date'] = f'{date.today()}'
        # print(data_dicts[d]['csv_address'])
        # print(data_dicts[d])

        # TODO: better error-handling so we're not nesting try-excepts
        try:
            geolocator = get_geolocation_data(data_dicts[d]['csv_address'])
            # print(data_dicts[d]['csv_address'])
            # print(geolocator)
            completed_dict = obj_builder(data_dicts[d], geolocator)


        except (AttributeError, TypeError):
            # when the API misses, we first check our
            # known bad addresses
            generator_address = try_clean_api_address(data_dicts[d]['csv_address'])

            try:
                mapped_address = [a for a in generator_address][0]
                geolocator = get_geolocation_data(mapped_address)
                completed_dict = obj_builder(data_dicts[d], geolocator)

            except (AttributeError, TypeError, IndexError):
                # TODO: logging misses?
                # print(data_dicts[d])
                
                # we can still have this in the data; then it's easy to see what the API missed
        #         print(data_dicts[d])
        #         yield data_dicts[d]
                continue

        # print(completed_dict)
        # yield completed_dict
        # pprint(data_dicts)
    return data_dicts

# def make_dicts_more_iterable(dicts):
#     return (d for d in dicts)


# def track_api_misses(miss, misses=[]):
#     '''
#     a collector for objects the API can't handle
#     '''
#     misses.append(miss)
#     with open('scraper/miss.log', 'a+') as log:
#         print(
#             'missed on:\n',
#             miss, '\n',
#             date.today(), '\n',
#             file=log
#         )

#     print(
#         'missed: ',
#         misses, '\n',
#         '{} total {}.'.format(
#             len(misses), 'miss' if len(misses) == 1 else 'misses'
#         )
#     )


if __name__ == '__main__':
    initial_json_dir = 'data/initial_json/'
    latest_json = get_latest_json(initial_json_dir)
    source_file = os.path.join(initial_json_dir, latest_json)

    final_json_dir = 'data/'
    final_json_file_format = latest_json
    outfile = os.path.join(final_json_dir, final_json_file_format)

    dicts = build_shit(source_file)
    # dicts_gen = make_dicts_more_iterable(dicts)

    file_writer.write_json(dicts, outfile)






