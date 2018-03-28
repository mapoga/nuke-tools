import nuke


nuke.menu('Nodes').addCommand('dgTools/PerspLines/dg_PerspLines','nuke.createNode("dg_PerspLines")','')

nuke.menu('Nodes').addCommand('dgTools/PerspLines/dg_Horizon','dg_PerspLines_Horizon()','')

nuke.menu('Nuke').addCommand('dgTools/PerspLines/Align camera for 2 selected nodes','dg_PerspLines_AlignCamera()', 'Shift+V')

