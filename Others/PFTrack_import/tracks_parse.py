import re


def _lookup_name(string):
    pattern = r'(^")([^"]+)("$)'

    matchObj = re.search(pattern, string)
    if matchObj:
        return matchObj.group(2)
    return


def _lookup_keyframe(string):
    pattern = r'^(-?\d+)\s(-?\d+\.?\d*)\s(-?\d+\.?\d*)\s(-?\d+\.?\d*)$'

    matchObj = re.search(pattern, string)
    if matchObj:
        return {'frame': int(matchObj.group(1)),
                'x': float(matchObj.group(2)),
                'y': float(matchObj.group(3))}
    return


def pftrack(filepath):

    # Open file
    try:
        file_ = open(filepath, 'r')
    except OSError as error:
        print('Error reading file: {0}'.format(error))
        file_.close()

    trackers = []
    tracker = {'name': '', 'keys': []}

    # Lines loop
    for idx, line in enumerate(file_):

        # keyframe
        key = _lookup_keyframe(line)
        if key:
            tracker['keys'].append(key)

        # name
        name = _lookup_name(line)
        if name:
            if tracker['name'] and tracker['keys']:
                trackers.append(tracker)
            tracker = {'name': name, 'keys': []}

    # End of file
    if tracker['name'] and tracker['keys']:
        trackers.append(tracker)
    file_.close()

    return trackers
