#!usr/local/bin/env python3

# python imports
from datetime import date
import json

def write_json(dicts, outfile):
    '''
    stores our objects in a pprint format

    args: something serializable, ready to be formatted and written out

    returns: none
    '''
    print('writing json ....')
    j = json.dumps(dicts, sort_keys=True, indent=4)
    with open(outfile, 'w') as f:
        print(j, file=f)
        print('done writing.')
        return f.name
