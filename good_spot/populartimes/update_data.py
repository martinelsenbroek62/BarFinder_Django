import copy
from constance import config
from structlog import get_logger

log = get_logger()


def populartimes_extrapolation(populartimes, live, day, hour):
    log.msg("Extrapolation function ran.")
    matches = [item['data'] for item in populartimes if item['name'] == day]
    if not len(matches) == 1:
        log.msg("Extrapolation function stopped because there are no matches.")
        return

    match = matches[0]
    k = live - match[hour]

    extrapolate_for_num_hours = config.EXTRAPOLATE_FOR_NUM_HOURS

    match_new = copy.deepcopy(match)
    match_new[hour] = live

    for i in range(1, extrapolate_for_num_hours + 1):
        hour += 1
        match_new[hour] = match_new[hour] + k if match_new[hour] + k <= 100 else 100

    actual_populartimes = [{'name': item['name'], 'data': match_new} if item['name'] == day else item for item in
                           populartimes]
    return actual_populartimes
