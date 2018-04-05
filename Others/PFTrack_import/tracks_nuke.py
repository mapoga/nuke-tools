"""
Creates a tracker3 or tracker4 node from a list of tracker keys.

trackers = [
    {'name': 'TrackerName',
     'keys': [
        {'frame': 0,
         'x': 10,
         'y': 20}},
     ]
    }},
]

"""
import nuke
# Nuke 11 switched to PySide2
try:
    from PySide import QtGui
    from PySide.QtGui import QApplication as QApp
except:
    from PySide2 import QtGui
    from PySide2.QtGui import QGuiApplication as QApp


def create_tracker3(trackers, label=''):
    """ Creates an old tracker3 node.
    It is prefered to use the tracker4 instead."""

    def iter_chunk(lst, size):
        """Yield successive n-sized chunks from lst"""
        for i in xrange(0, len(lst), size):
            yield lst[i:i + size]

    nodes = []
    # Chunk tracks by 4
    for chunks in iter_chunk(trackers, 4):
        # Create node
        node = nuke.nodes.Tracker3()
        nodes.append(node)
        if label:
            node['label'].setValue(label)
            node['enable1'].setFlag(0)
        for idx, track in enumerate(chunks, 1):
            # knobs
            node['enable{0}'.format(idx)].setValue('true')
            knob = node['track{0}'.format(idx)]
            knob.setAnimated()
            anim_x = knob.animation(0)
            anim_y = knob.animation(1)
            # animation
            keys_x = [nuke.AnimationKey(key['frame'], key['x'])
                      for key in track['keys']]
            keys_y = [nuke.AnimationKey(key['frame'], key['y'])
                      for key in track['keys']]
            anim_x.addKey(keys_x)
            anim_y.addKey(keys_y)
    return nodes


def create_tracker4_safe(trackers, label):
    """Creates a new tracker4 node.
    Very slow given knobs available functions."""

    # Refs
    # https://github.com/magnoborgo/RotoShapesToTrackers/blob
    # /master/RotoShapes_to_trackers.py
    # http://communiy.foundry.com/discuss/topic/99665
    # /python-with-new-tracker?mode=Post&postID=969555

    node = nuke.createNode('Tracker4')
    if label:
        node['label'].setValue(label)
        node['add_track'].setFlag(0)

    table = node['tracks']
    columns = 31
    x = 2
    y = 3
    # Tracks loop
    for idx, track in enumerate(trackers):
        node['add_track'].execute()
        frames = []
        current_frame = int(nuke.frame())
        # Keys loop
        for key in track['keys']:
            frames.append(key['frame'])
            table.setValueAt(key['x'], key['frame'], (idx*columns)+x)
            table.setValueAt(key['y'], key['frame'], (idx*columns)+y)
        # Clear execution frame from auto key and other knobs
        knob_ranges = range(columns)
        knob_ranges
        if current_frame in frames:
            knob_ranges.pop(y)
            knob_ranges.pop(x)
        for i in knob_ranges:
            table.removeKeyAt(current_frame, (idx*columns)+i)
    return node


def create_tracker4_copy(trackers, label=''):
    """ Creates a string version of the tracker4 node. Could be pasted.
    Much faster than using nuke's functions for that node.
    Probably not forward compatible given its a hack. Made in nuke 11.0v1
    """

    # first_frame, keys (string of keys seperated by a space)
    curve_str = 'x{0} {1}'
    # name, curve_x, curve_y
    track_str = (' {{ {{}}  "{0}" {{curve {1}}} {{curve {2}}} {{}}  {{}}'
                 '  1 0 0 {{}}  1 0 -32 -32 32 32 -22 -22 22 22 {{}} {{}}  '
                 '{{}}  {{}}  {{}}  {{}}  {{}}  {{}}  {{}}  {{}}  '
                 '{{}}   }}')
    # tracks_count, trackers_str, center_x, center_y, label
    tracker_str = ('Tracker4 {{\n'
                   'tracks {{ {{ 1 31 {0} }} \n'
                   '{{ {{ 5 1 20 enable e 1 }}\n'
                   '{{ 3 1 75 name name 1 }}\n'
                   '{{ 2 1 58 track_x track_x 1 }}\n'
                   '{{ 2 1 58 track_y track_y 1 }}\n'
                   '{{ 2 1 63 offset_x offset_x 1 }}\n'
                   '{{ 2 1 63 offset_y offset_y 1 }}\n'
                   '{{ 4 1 27 T T 1 }}\n'
                   '{{ 4 1 27 R R 1 }}\n'
                   '{{ 4 1 27 S S 1 }}\n'
                   '{{ 2 0 45 error error 1 }}\n'
                   '{{ 1 1 0 error_min error_min 1 }}\n'
                   '{{ 1 1 0 error_max error_max 1 }}\n'
                   '{{ 1 1 0 pattern_x pattern_x 1 }}\n'
                   '{{ 1 1 0 pattern_y pattern_y 1 }}\n'
                   '{{ 1 1 0 pattern_r pattern_r 1 }}\n'
                   '{{ 1 1 0 pattern_t pattern_t 1 }}\n'
                   '{{ 1 1 0 search_x search_x 1 }}\n'
                   '{{ 1 1 0 search_y search_y 1 }}\n'
                   '{{ 1 1 0 search_r search_r 1 }}\n'
                   '{{ 1 1 0 search_t search_t 1 }}\n'
                   '{{ 2 1 0 key_track key_track 1 }}\n'
                   '{{ 2 1 0 key_search_x key_search_x 1 }}\n'
                   '{{ 2 1 0 key_search_y key_search_y 1 }}\n'
                   '{{ 2 1 0 key_search_r key_search_r 1 }}\n'
                   '{{ 2 1 0 key_search_t key_search_t 1 }}\n'
                   '{{ 2 1 0 key_track_x key_track_x 1 }}\n'
                   '{{ 2 1 0 key_track_y key_track_y 1 }}\n'
                   '{{ 2 1 0 key_track_r key_track_r 1 }}\n'
                   '{{ 2 1 0 key_track_t key_track_t 1 }}\n'
                   '{{ 2 1 0 key_centre_offset_x key_centre_offset_x 1 }}\n'
                   '{{ 2 1 0 key_centre_offset_y key_centre_offset_y 1 }}\n'
                   '}}\n'
                   '{{ \n'
                   '{1}\n'
                   '\n'
                   '}} \n'
                   '}}\n'
                   '\n'
                   'center {{{2} {3}}}\n'
                   'label {4}\n'
                   'selected true\n'
                   '}}')

    def single_keys(keys, attr):
        return [{'first_frame': k['frame'], 'keys': [k[attr]]} for k in keys]

    def chunks_to_string(chunks):
        chunks_str = []
        for c in chunks:
            f = ['x{0}'.format(c['first_frame']), ]
            f.extend(c['keys'])
            chunks_str.append(' '.join([str(i) for i in f]))
        return ' '.join(chunks_str)

    tracks = []
    for t in trackers:
        x_cont = single_keys(t['keys'], 'x')
        y_cont = single_keys(t['keys'], 'y')

        x_cont_str = chunks_to_string(x_cont)
        y_cont_str = chunks_to_string(y_cont)
        track = track_str.format(t['name'], x_cont_str, y_cont_str)
        tracks.append(track)
    tracks_str = '\n'.join(tracks)
    root_format = nuke.root().knob('format').value()
    center_x = float(root_format.width()) * 0.5
    center_y = float(root_format.height()) * 0.5
    tracker = tracker_str.format(len(trackers), tracks_str,
                                 center_x, center_y, label)

    return tracker


def paste_string(node_string):
    """ Pastes a given string and restore the previous clipboard"""

    clip = QApp.clipboard()
    bkp_txt = clip.text()
    clip.setText(node_string)
    nuke.nodePaste(r'%clipboard%')
    # restore previous clipboard
    clip.setText(bkp_txt)


def create_tracker4(trackers, label):
    """ Creates a tracker4 node. Handles which function to use"""

    try:
        node_string = create_tracker4_copy(trackers, label)
        print('node_string')
        paste_string(node_string)
    except:
        try:
            print('create_tracker4(): Tracker4_copy() failed!'
                  ' Reverting to Tracker4_safe(). SLOW!!!!!')
            Tracker4_safe(trackers, label)
        except:
            print('create_tracker4(): Complete failure.'
                  ' Could not create tracker4.')
