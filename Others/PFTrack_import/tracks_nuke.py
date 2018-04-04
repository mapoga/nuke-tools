"""
Creates a tracker3 or tracker4 node from a list of tracker keys.
trackers = [
    {'name': 'TrackerName',
     'keys': [
        {'frame': 0,
         'x': 10,
         'y': 20},
     ]
    },
]

"""
import nuke
# Nuke 11 switched to PySide2
try:
    from PySide import QtGui
    QtWidgets = QtGui
except:
    from PySide2 import QtGui, QtWidgets


class KeyFrame():
    """
    frame is an integer.
    attrs is a dict of parameters with their values
    """

    def __init__(self, frame, attrs):
        self.frame = frame
        self.attrs = attrs

    def nuke_anim_key(self, attr):
        return nuke.AnimationKey(self.frame, self.attrs[attr])


class Tracker():

    FILETYPES = ['pftrack', ]

    def from_file(cls, filepath, filetype):
        pass

    def __init__(self, name, keyframes):
        self.name = name
        self.keyframes = keyframes

    def nuke_attr_keys(self, attr):
        return [nuke.AnimationKey(key['frame'], key['x'])
                for key in track['keys']]

    def frames(self):
        return sorted([k.frame for k in self.keyframes])

    def attrs(self):
        if self.keyframes:
            return self.keyframes[0].attrs.keys()
        else:
            return []

    def nuke_tracker3(self):
        pass

    def nuke_tracker4(self):
        pass

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

        # Keys loop
        for key in track['keys']:
            frames.append(key['frame'])
            table.setValueAt(key['x'], key['frame'], (idx*columns)+x)
            table.setValueAt(key['y'], key['frame'], (idx*columns)+y)

        # Clear execution frame from auto key
        if not nuke.frame() in frames:
            for i in range(columns):
                table.removeKeyAt(nuke.frame(), (idx*columns)+i)
    return node
