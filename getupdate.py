#!/usr/bin/env python3

"""
This is a script to get the latest blog feed updates from the following url:
https://www.eff.org/rss/updates.xml
It parses feed and
"""

import os
import sys
import requests
import time
import argparse
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup


def get_feeds(url="https://www.eff.org/rss/updates.xml"):
    """Get a list of feed from url"""
    try:
        r = requests.get(url)
        xmltree = ET.fromstring(r.text)
        feeds = xmltree.find('channel').findall('item')
    except Exception as e:
        print(str(e),file=sys.stderr)
        exit(1)
    return feeds


def xml2dict(item):
    """Convert an xml item object to dict"""
    FIELDS = ['title', 'link', 'description', 'pubDate', 'guid',
              '{http://purl.org/dc/elements/1.1/}creator']
    xmldict = {}
    for i in FIELDS:
        xmldict[i] = item.find(i).text

    # format the item
    xmldict['category'] = [x.text for x in item.findall('category')]
    xmldict['categories'] = ', '.join(xmldict['category'])
    xmldict['creator'] = xmldict['{http://purl.org/dc/elements/1.1/}creator']
    xmldict['description'] = BeautifulSoup(xmldict['description'],
                               'html.parser').get_text()
    pubDate = time.strptime(xmldict['pubDate'], '%a, %d %b %Y %H:%M:%S +0000')
    xmldict['pubDate'] = time.mktime(pubDate)
    xmldict['pubDateStr'] = time.strftime('%Y/%m/%d', pubDate)

    return xmldict


def filter_date(item, before=7):
    """Filter items before the 'before' days"""
    limit = time.mktime(time.gmtime()) - 24 * 60 * 60 * before
    return item['pubDate'] > limit


def format_item(item):
    """Format the item to dump"""
    format_str = u'\n原文: [{title}]({link})\n\n{description}\n\n\
发布日期: {pubDateStr}, 原作者: {creator}, 分类: {categories}'
    return format_str.format(**item)


def main(argv):
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--last', '-l', type=int, nargs='?', default=7,
                        help='list up to N days before', )
    args = vars(parser.parse_args(argv[1:]))

    # Fetch xml feed and dump articles
    feeds = [xml2dict(x) for x in get_feeds()]
    feeds = sorted(feeds, key=lambda x: x['pubDate'])
    for x in feeds:
        if filter_date(x, before=args['last']):
            print(format_item(x))


if __name__ == '__main__':
    try:
        main(sys.argv)
    except BrokenPipeError:
        exit(0)
