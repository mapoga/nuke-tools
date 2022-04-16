import nuke

'''
Mask input from Ean Carr
https://community.foundry.com/discuss/topic/103390/finding-the-mask-input-of-a-node?mode=Post&postID=894423
https://gist.github.com/anonymous/a802f51391163a2bf0e3
'''

def node_has_mask(node):
    '''
    Does node have a mask input (on its right side)?
    
    @param node: the node object
    @return: True if node has a mask input, False if not
    '''
    return node.knobs().has_key('maskChannelMask')
    
def get_actual_min_inputs(node):
    '''
    Get actual minimum number of node inputs this node needs to do its job.
    Problem is, nodes with a maskChannelMask input falsely report number of
    inputs as one greater than actual minimum.
    
    IMO, we shouldn't regard a mask input as "required" because... it isn't.

    @param node: the node object
    @return: an integer representing the minimum total number of inputs, not including mask.
    '''
    min_inputs = node.minInputs()
    return (min_inputs -1) if (node_has_mask(node) and min_inputs > 0) else min_inputs

def get_actual_max_inputs(node):
    '''
    Get actual maximum number of node inputs this node will accept, not including mask (if any)
    or optional inputs.

    @param node: the node object
    @return: an integer representing the maximum total number of inputs, not including mask.
    '''
    return node.optionalInput()
    
def get_mask_input_index(node):
    '''
    Get the index of node's mask input. For example, Merge2's is always index 2. For (all?)
    other nodes, it's minimumInputs minus 1 if the node has a 'maskChannelMask' knob.
    '''
    if node.Class() == 'Merge2':
        # Merge2 is a special case. Mask input is always index 2.
        return 2
    elif node_has_mask(node):
        return node.minInputs() - 1
    else:
        # This node doesn't have a mask input.
        return None

def mask_cleanup():
    for n in nuke.selectedNodes():
        mask_input = get_mask_input_index(n)
        if mask_input != None:
            mask_node = n.input(mask_input)
            if mask_node:
                if mask_node.Class() != 'Dot':
                    dot = nuke.nodes.Dot( inputs=[ mask_node ], label=mask_node.knob('label').evaluate(), hide_input=True)
                    n.setInput(mask_input, dot)
                    dot.setXpos(n.xpos()+n.screenWidth() + 15)
                    dot.setYpos(n.ypos()+(n.screenHeight()/2)-6)
