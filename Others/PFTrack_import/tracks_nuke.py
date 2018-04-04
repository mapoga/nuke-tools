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
try:
    from PySide import QtGui
except:
    from PySide2 import QtGui



def create_tracker3(trackers, label=''):

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
            node['enable{0}}'.format(idx)].setValue('true')
            knob = node['track{0}}'.format(idx)]
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


def create_tracker4(trackers, label=''):
    # Refs
    # https://github.com/magnoborgo/RotoShapesToTrackers/blob
    # /master/RotoShapes_to_trackers.py
    # http://communiy.foundry.com/discuss/topic/99665
    # /python-with-new-tracker?mode=Post&postID=969555

    # Slower to create than tracker3, lacking animation function

    # Create node
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
    # first_frame, keys (string of keys seperated by a space)
    curve_str = 'x{0} {1}'
    # name, curve_x, curve_y
    track_str = (' {{ {{}}  "{0}" {{curve {1}}} {{curve {2}}} {{}}  {{}}  1 0 0 '
                 '{{}}  1 0 -32 -32 32 32 -22 -22 22 22 {{}} {{}}  '
                 '{{}}  {{}}  {{}}  {{}}  {{}}  {{}}  {{}}  {{}}  '
                 '{{}}   }}')

    # trackers_str, center_x, center_y, label
    tracker_str = ('Tracker4 {{\ntracks {{ {{ 1 31 2 }} \n{{ {0}\n\n'
                   '}} \n}}\n\ncenter {{{1} {2}}}\nlabel {3}\n'
                   'selected true\n}}')

    def continuous_keys_chunks(keys, attr):
        chunks = []
        cont_values = []
        first = None
        last = None
        for k in keys:
            if last is not None:
                if k['frame'] == last+1:
                    # continuous
                    cont_values.append(k[attr])
                    last = k['frame']
                else:
                    # end of chunk
                    chunks.append({'first_frame': first, 'keys': cont_values})
                    cont_values = []
                    last = None
                    first = []
            else:
                # first key
                cont_values = [k[attr], ]
                first = k['frame']
                last = k['frame']

        if cont_values:
            chunks.append({'first_frame': first, 'keys': cont_values})

        return chunks

    def chunk_stringify(chunks):
        chunks_str = []
        for c in chunks:
            f = ['x{0}'.format(c['first_frame']), ]
            f.extend(c['keys'])
            chunks_str.append(' '.join(f))
        return ' '.join(chunks_str)

    tracks = []
    for t in trackers:
        x_cont = continuous_keys_chunks(t['keys'], 'x')
        print(x_cont)
        y_cont = continuous_keys_chunks(t['keys'], 'y')
        x_cont_str = chunk_stringify(x_cont)
        y_cont_str = chunk_stringify(y_cont)
        track = track_str.format(t['name'], x_cont_str, y_cont_str)
        tracks.append(track)
    tracks_str = '\n{0}'.join(tracks)
    tracker = tracker_str.format(tracks_str, 1000, 1000)

    clip = QtGui.QApplication.clipboard()
    clip.setText(tracker)



