import nuke
import os
import re

def channels_to_layers(channels):
    layers = []
    for c in channels:
        parts = c.split('.')
        striped_parts = parts[:-1]
        striped = '.'.join(striped_parts)
        layers.append(striped)
    layers = list(set(layers))
    layers.sort()
    return layers

def node_offset(node, x, y):
    old_x = node.xpos()
    old_y = node.ypos()
    node.setXYpos(old_x+x, old_y+y)

def get_node_center(node):
    print(node.name()+' Get Center')
    print(node.name()+'_corner: ', node.xpos(), node.ypos())
    x = node.xpos() + (node.screenWidth()/2)
    y = node.ypos() + (node.screenHeight()/2)
    print(node.name()+'_center: ', x, y)
    print(node.name()+'_size: ', node.screenWidth(), node.screenHeight())
    return x, y

def set_node_center(node, x, y):
    print(node.name()+' Set Center', x, y)
    print(node.name()+'_corner: ', node.xpos(), node.ypos())
    node.setXpos(x-(node.screenWidth()/2))
    node.setYpos(y-(node.screenHeight()/2))
    print(node.name()+'_center: ', node.xpos()+(node.screenWidth()/2), node.ypos()+(node.screenHeight()/2))
    print(node.name()+'_size: ', node.screenWidth(), node.screenHeight())

def add_to_bound(bound, node):
    bound[0] = min(bound[0], node.xpos())
    bound[1] = max(bound[1], node.xpos()+node.screenWidth())
    bound[2] = min(bound[2], node.ypos())
    bound[3] = max(bound[3], node.ypos()+node.screenHeight())
    return bound

def split_layers(node, layers, Redshift_crypto=False):
    reads_spacing_y = 200
    layers_spacing_x = 300
    layers_spacing_y = 400
    all_spacing_y = 700
    pre_spacing_y = 500
    crypto_spacing_x = 700
    padding = [500, 700, 300, 100]

    bounds = [100000,-1000000,100000,-100000]
    bounds = add_to_bound(bounds, node)

    #Root
    root = nuke.nodes.Dot( inputs=[ node ] )
    node_offset(root, 0, reads_spacing_y)
    bounds = add_to_bound(bounds, root)

    #Black Base
    if nuke.NUKE_VERSION_MAJOR >= 12:
        black = nuke.nodes.Shuffle2( inputs=[ root ], label='Black', postage_stamp=True)
        black.knob('mappings').setValue([
            (-1, 'black', 'rgba.red'),
            (-1, 'black', 'rgba.green'),
            (-1, 'black', 'rgba.blue')
        ])
    else:
        black = nuke.nodes.Shuffle( inputs=[ root ], label='Black', postage_stamp=True)
        black.knob('red').setValue('black')
        black.knob('green').setValue('black')
        black.knob('blue').setValue('black')
    bounds = add_to_bound(bounds, black)
    b_end = black
    a_end = root

    #Layers
    for idx, layer in enumerate(layers):
        x = a_end.xpos()
        y = a_end.ypos()

        #Dot
        end = nuke.nodes.Dot( inputs=[ a_end ] )
        end.setXYpos(x-layers_spacing_x, y)
        a_end = end
        bounds = add_to_bound(bounds, a_end)

        #Shuffle
        name = layer.replace('beauty_aux_', '')
        if nuke.NUKE_VERSION_MAJOR >= 12:
            end = nuke.nodes.Shuffle2( inputs=[ end ], label=name, postage_stamp=True, in1=layer, in2='rgba')
            end.knob('mappings').setValue('rgba.alpha', 'rgba.alpha')
        else:
            end = nuke.nodes.Shuffle( inputs=[ end ], label=name, postage_stamp=True, in2='rgba')
            end.knob('in').setValue(layer)
            end.knob('alpha').setValue('alpha2')
        bounds = add_to_bound(bounds, end)

        #Unpremult
        end = nuke.nodes.Unpremult( inputs=[ end ] )
        node_offset(end, 0, 15)
        bounds = add_to_bound(bounds, end)

        #Dot
        end = nuke.nodes.Dot( inputs=[ end ] )
        node_offset(end, 0, layers_spacing_y +(idx*30))
        bounds = add_to_bound(bounds, end)

        #Merge
        merge_x, waste = get_node_center(b_end)
        waste, merge_y = get_node_center(end)
        b_end = nuke.nodes.Merge( inputs=[b_end, end], operation='plus', output='rgb')
        set_node_center(b_end, merge_x, merge_y)
        bounds = add_to_bound(bounds, b_end)

    #Premult
    pre = nuke.nodes.Premult( inputs=[ b_end ] )
    node_offset(pre, 0, all_spacing_y)
    b_end = pre
    bounds = add_to_bound(bounds, b_end)

    #Dot
    b_end = nuke.nodes.Dot( inputs=[ b_end ] )
    node_offset(b_end, 0, pre_spacing_y)
    bounds = add_to_bound(bounds, b_end)

    if Redshift_crypto:
        #Crypto
        bty_file = node.knob('file').value()
        btyx = node.xpos()
        btyy = node.ypos()
        range = [node.knob('first').value(), node.knob('last').value()]
        file_base, ext = os.path.splitext(bty_file)
    
        #Material
        #Read
        cryptoMat_file = file_base + '.crypto_Material' + ext + ' ' + str(range[0]) + '-' + str(range[1])
        cryptoMat = nuke.createNode('Read')
        cryptoMat.knob('file').fromUserText(cryptoMat_file)
        cryptoMat.setXYpos(btyx+crypto_spacing_x, btyy)
        bounds = add_to_bound(bounds, cryptoMat)
        
        #Shuffle
        if nuke.NUKE_VERSION_MAJOR >= 12:
            cryptoMat_shuffle = nuke.nodes.Shuffle2( inputs=[ cryptoMat, root ], label='MATERIAL')
            cryptoMat_shuffle.knob('fromInput2').setValue('{1} B A')
            cryptoMat_shuffle.knob('in2').setValue('rgba')
            cryptoMat_shuffle.knob('mappings').setValue(1, 'rgba.alpha', 'rgba.alpha')
        else:
            cryptoMat_shuffle = nuke.nodes.ShuffleCopy( inputs=[ cryptoMat, root ], label='MATERIAL')
            cryptoMat_shuffle.knob('alpha').setValue('alpha')

        _x, waste = get_node_center(cryptoMat)
        waste, _y = get_node_center(root)
        #set_node_center(cryptoMat_shuffle, _x, _y-6)
        set_node_center(cryptoMat_shuffle, _x, root.ypos())
        bounds = add_to_bound(bounds, cryptoMat_shuffle)
        
    
        #Node
        #Read
        cryptoNode_file = file_base + '.crypto_Node' + ext + ' ' + str(range[0]) + '-' + str(range[1])
        cryptoNode = nuke.createNode('Read')
        cryptoNode.knob('file').fromUserText(cryptoNode_file)
        cryptoNode.setXYpos(btyx+(2*crypto_spacing_x), btyy)
        bounds = add_to_bound(bounds, cryptoNode)
        
        #Shuffle
        if nuke.NUKE_VERSION_MAJOR >= 12:
            cryptoNode_shuffle = nuke.nodes.Shuffle2( inputs=[ cryptoNode, cryptoMat_shuffle ], label='NODE')
            cryptoNode_shuffle.knob('fromInput2').setValue('{1} B A')
            cryptoNode_shuffle.knob('in2').setValue('rgba')
            cryptoNode_shuffle.knob('mappings').setValue(1, 'rgba.alpha', 'rgba.alpha')
        else:
            cryptoNode_shuffle = nuke.nodes.ShuffleCopy( inputs=[ cryptoNode, cryptoMat_shuffle ], label='NODE')
            cryptoNode_shuffle.knob('alpha').setValue('alpha')
        _x, waste = get_node_center(cryptoNode)
        waste, _y = get_node_center(cryptoMat_shuffle)
        set_node_center(cryptoNode_shuffle, _x, _y)
        bounds = add_to_bound(bounds, cryptoNode_shuffle)

    #Render Layer
    head, tail = os.path.split(bty_file)
    head, version_part = os.path.split(head)
    head, render_layer = os.path.split(head)
    
    #Backdrop
    backdrop = nuke.nodes.BackdropNode(
        xpos = bounds[0]-padding[0], 
        bdwidth = bounds[1] - bounds[0] + padding[0] + padding[1], 
        ypos = bounds[2] - padding[2], 
        bdheight = bounds[3] - bounds[2] + padding[2] + padding[3], 
        note_font_size=200, 
        z_order = -100,
        label = render_layer
    )


def split_selected_reads():
	for n in nuke.selectedNodes():
	    if n.Class() == 'Read':
	        layers = channels_to_layers(n.channels())
	        
	        selected_layers = [l for l in layers if l.startswith('beauty_aux_')]
	    
	        split_layers(n, selected_layers, Redshift_crypto=True)
