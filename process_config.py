import datetime
import json
import urllib

def process_data(config):
    search_query = config['search_query']

    username     = config['username']

    since_raw    = config['since'].split('-')
    since_year   = int(since_raw[2])
    since_month  = int(since_raw[0])
    since_day    = int(since_raw[1])
    since        = datetime.datetime(since_year, since_month, since_day)

    until_raw    = config['until'].split('-')
    until_year   = int(until_raw[2])
    until_month  = int(until_raw[0])
    until_day    = int(until_raw[1])
    until        = datetime.datetime(until_year, until_month, until_day)

    if username:
        return "from={}".format(username), since, until

    if search_query:
        return 'q="{}"'.format(urllib.quoteplus(search_query)), "{}".format(since), "{}".format(until)

    else:
        return None, None, None


with open('search_template_config.json', 'rb') as infile:
    config = json.load(infile)
    process_data(config)
