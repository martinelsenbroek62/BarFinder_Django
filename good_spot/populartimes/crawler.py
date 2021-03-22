import calendar
import json
import ssl

import re
import urllib.request
import urllib.parse
from structlog import get_logger

from good_spot.places import models as places_models
from good_spot.proxy.exceptions import IPOverTimeException
from good_spot.proxy.models import Proxy

log = get_logger()

# user agent for populartimes request
user_agent = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/54.0.2840.98 Safari/537.36"}


def get_popularity_for_day(popularity):
    days_json = [[0 for _ in range(24)] for _ in range(7)]

    for day in popularity:

        day_no, pop_times = day[:2]

        if pop_times is not None:
            for el in pop_times:

                hour, pop = el[:2]
                days_json[day_no - 1][hour] = pop

                # day wrap
                if hour == 23:
                    day_no = day_no % 7 + 1

    # {"name" : "monday", "data": [...]} for each weekday as list
    return [
        {
            "name": list(calendar.day_name)[d],
            "data": days_json[d]
        } for d in range(7)
    ]


def get_current_popularity(place_identifier):
    """
    request information for a place and parse current popularity
    :param place_identifier: name and address string
    :return:
    """
    log.msg("`get_current_popularity` started.")
    params_url = {
        "tbm": "map",
        "tch": 1,
        "q": urllib.parse.quote_plus(place_identifier),
        # TODO construct own proto buffer
        "pb": "!4m12!1m3!1d4005.9771522653964!2d-122.42072974863942!3d37.8077459796541!2m3!1f0!2f0!3f0!3m2!1i1125!2i976"
              "!4f13.1!7i20!10b1!12m6!2m3!5m1!6e2!20e3!10b1!16b1!19m3!2m2!1i392!2i106!20m61!2m2!1i203!2i100!3m2!2i4!5b1"
              "!6m6!1m2!1i86!2i86!1m2!1i408!2i200!7m46!1m3!1e1!2b0!3e3!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e3!2b0!3e3!"
              "1m3!1e4!2b0!3e3!1m3!1e8!2b0!3e3!1m3!1e3!2b1!3e2!1m3!1e9!2b1!3e2!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e"
              "10!2b0!3e4!2b1!4b1!9b0!22m6!1sa9fVWea_MsX8adX8j8AE%3A1!2zMWk6Mix0OjExODg3LGU6MSxwOmE5ZlZXZWFfTXNYOGFkWDh"
              "qOEFFOjE!7e81!12e3!17sa9fVWea_MsX8adX8j8AE%3A564!18e15!24m15!2b1!5m4!2b1!3b1!5b1!6b1!10m1!8e3!17b1!24b1!"
              "25b1!26b1!30m1!2b1!36b1!26m3!2m2!1i80!2i92!30m28!1m6!1m2!1i0!2i0!2m2!1i458!2i976!1m6!1m2!1i1075!2i0!2m2!"
              "1i1125!2i976!1m6!1m2!1i0!2i0!2m2!1i1125!2i20!1m6!1m2!1i0!2i956!2m2!1i1125!2i976!37m1!1e81!42b1!47m0!49m1"
              "!3b1"
    }

    search_url = "https://www.google.de/search?" + "&".join(k + "=" + str(v) for k, v in params_url.items())

    gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)

    while (True):
        try:
            rotate_response = Proxy.rotate()
            log.msg('Proxy rotated: {}'.format(rotate_response))
            break
        except IPOverTimeException:
            log.error('IPOverTimeException when proxy rotated.')
            pass

    proxies = {
        "http": rotate_response['proxy_url'],
        "https": rotate_response['proxy_url']
    }
    proxy = urllib.request.ProxyHandler(proxies)
    opener = urllib.request.build_opener(proxy)
    urllib.request.install_opener(opener)

    log.msg('Tries to open search_url: {}'.format(search_url))
    resp = urllib.request.urlopen(urllib.request.Request(url=search_url, data=None, headers=user_agent),
                                  context=gcontext)
    Proxy.count_ip(rotate_response['proxy_external_ip'])

    data = resp.read().decode('utf-8')

    log.msg('Tries to load json.')
    # find eof json
    jend = data.rfind("}")
    if jend >= 0:
        data = data[:jend + 1]

    jdata = json.loads(data)["d"]  # sometimes here error - extra line

    popular_times = None
    try:
        # this expression tries to find substring
        # 1) starting from `[[[7`
        # 2) containing `06:00`
        # 3) ending with `,`, any number and `]]`
        popular_times = json.loads(re.search(r'\[\[\[7.+06:00.+?,\d\]\]', jdata.replace('\n', '')).group()[1:])
        log.msg('Popularity parsed using regex.')
    except Exception as e:
        log.error('Can not parse popularity using regex.')

    jdata = json.loads(jdata[4:])

    popular_times, rating, rating_n, current_popularity, extended_place_types = popular_times, None, None, None, None

    if not len(jdata) > 0:
        log.error('Something went wrong. Expected that `jdata` has length > 0, '
                  'but current length is {}'.format(len(jdata)))
        return rating, rating_n, popular_times, current_popularity, extended_place_types
    if not len(jdata[0]) > 1:
        log.error('Something went wrong. Expected that `jdata[0]` has length > 1, '
                  'but current length is {}'.format(len(jdata[0])))
        return rating, rating_n, popular_times, current_popularity, extended_place_types
    if not len(jdata[0][1]) > 0:
        log.error('Something went wrong. Expected that `jdata[0][1]` has length > 0, '
                  'but current length is {}'.format(len(jdata[0][1])))
        return rating, rating_n, popular_times, current_popularity, extended_place_types

    if not len(jdata[0][1][0]) > 14:
        log.error('Something went wrong. Expected that `jdata[0][1][0]` has length > 14, '
                  'but current length is {}'.format(len(jdata[0][1][0])))
        return rating, rating_n, popular_times, current_popularity, extended_place_types

        # get info from result array, has to be adapted if backend api changes
    info = jdata[0][1][0][14]

    if not popular_times:
        try:
            popular_times = info[84][0]
        except Exception as e:
            log.error('Something went wrong when tries to get `popular_times` from json.')
            print(e)

    try:
        # current_popularity is not available if popular_times is
        current_popularity = info[84][7][1]
    except Exception as e:
        log.error('Something went wrong when tries to get `current_popularity` from json.')
        print(e)

    try:
        extended_place_types = info[76][0]
    except Exception as e:
        log.error('Something went wrong when tries to get `extended_place_types` from json.')
        print(e)

    # ignore, there is either no info available or no popular times
    # TypeError: rating/rating_n/populartimes in None
    # IndexError: info is not available

    return popular_times, current_popularity, extended_place_types


def get_current_popular_times(place_id):
    """
    sends request to detail to get a search string and uses standard proto buffer to get additional information
    on the current status of popular times
    :return: json details
    """

    place_obj = places_models.Place.objects.get(google_place_id=place_id)
    place_identifier = "{} {}".format(place_obj.name, place_obj.address)
    popularity, current_popularity, extended_place_types = get_current_popularity(place_identifier)

    log.msg('Prepares and checks detail_json.')
    detail_json = {}

    if current_popularity is not None:
        detail_json["current_popularity"] = current_popularity
    detail_json["extended_place_types"] = extended_place_types

    detail_json["populartimes"] = get_popularity_for_day(popularity) if popularity is not None else []

    log.msg('Return detail_json.')
    return detail_json
