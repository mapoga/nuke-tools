import nuke


def _chunks(lst, length):
    # Yield successive n-sized chunks from lst
    for i in xrange(0, len(lst), length):
        yield lst[i:i + length]


def create_tracker3(trackers, label=''):
    nodes = []
    # Chunk tracks by 4
    for chunks in _chunks(trackers, 4):

        # Create node
        node = nuke.nodes.Tracker3()
        nodes.append(node)
        if label:
            node['label'].setValue(label)
            node['enable1'].setFlag(0)

        # tracks loop
        for idx, track in enumerate(chunks):
            kid = idx+1
            node['enable{0}'.format(kid)].setValue('true')
            knob = node['track{0}'.format(kid)]
            knob.setAnimated()
            keys_x = []
            keys_y = []

            for key in track['keys']:
                frame = int(key['frame'])
                x = float(key['x'])
                y = float(key['y'])

                keys_x.append((frame, x))
                keys_y.append((frame, y))

            anim_x = knob.animation(0)
            anim_x.addKey([nuke.AnimationKey(frame, value)
                           for (frame, value) in keys_x])

            anim_y = knob.animation(1)
            anim_y.addKey([nuke.AnimationKey(frame, value)
                           for (frame, value) in keys_y])

    return nodes


def create_tracker4(trackers, label=''):
    # Refs
    # https://github.com/magnoborgo/RotoShapesToTrackers/blob
    # /master/RotoShapes_to_trackers.py
    # http://communiy.foundry.com/discuss/topic/99665
    # /python-with-new-tracker?mode=Post&postID=969555

    # Slower to create than tracker3 because of
    # lack of animation function

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
