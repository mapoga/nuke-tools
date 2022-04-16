import nuke
import os

dirname = os.path.dirname(os.path.abspath(__file__))

Nodes = nuke.toolbar('Nodes')


#######################################################
##################### Tools Begin #####################
Tools = Nodes.addMenu('Tools', icon='Tools_icon.png')

Threed = Tools.addMenu('3D', icon='3D_icon.png')
Threed.addCommand('N Matte', 'nuke.createNode(\'N Facing.nk\')',
                  icon='N Facing_icon.png')
Threed.addCommand('P Matte', 'nuke.createNode(\'P Matte.nk\')',
                  icon='P Matte_icon.png')
Threed.addCommand('Z Convert', 'nuke.createNode(\'Z Convert.nk\')',
                  icon='Z Convert_icon.png')
Threed.addCommand('Z to P', 'nuke.createNode(\'Z to P.nk\')',
                  icon='Z Merge_icon.png')
Threed.addCommand('Z Merge', 'nuke.createNode(\'Z Merge.nk\')',
                  icon='Z Merge_icon.png')
Threed.addCommand('Vector', 'nuke.createNode(\'Vector.nk\')',
                  icon='Z Merge_icon.png')
Threed.addCommand('Screen Space Transform', 'nuke.createNode(\'ScreenSpaceTransform.nk\')',
                  icon='Z Merge_icon.png')
Threed.addCommand('RS Depth Fix', 'nuke.createNode(\'RS_Depth_Fix.nk\')',
                  icon='Z Merge_icon.png')
Threed.addCommand('VolumeProcedural', 'nuke.createNode(\'VolumeProcedural.nk\')',
                  icon='VolumeProcedural.png')
Threed.addCommand('SSAO', 'nuke.createNode(\'SSAO.nk\')',
                  icon='VolumeProcedural.png')


Edge = Tools.addMenu('Edge', icon='Edge_icon.png')
Edge.addCommand('Edge Extend', 'nuke.createNode(\'Edge Extend.nk\')',
                icon='Edge Extend_icon.png')
Edge.addCommand('Format Feather', 'nuke.createNode(\'Format Feather.nk\')',
                icon='Format Feather_icon.png')
Edge.addCommand('Linear Smooth', 'nuke.createNode(\'Linear Smooth.nk\')',
                icon='Linear Smooth_icon.png')
Edge.addCommand('ST Generate', 'nuke.createNode(\'ST Generate.nk\')',
                icon='ST Generate_icon.png')
Edge.addCommand('Splatter', 'nuke.createNode(\'Splatter.nk\')',
                icon='Splatter_icon.png')
Edge.addCommand('Seamless', 'nuke.createNode(\'Seamless.nk\')',
                icon='Format Feather_icon.png')
Edge.addCommand('Tile Lazy', 'nuke.createNode(\'Tile Lazy.nk\')',
                icon='Format Feather_icon.png')
Edge.addCommand('CropToBBox', 'nuke.createNode(\'CropToBBox.nk\')',
                icon='Format Feather_icon.png')
Edge.addCommand('Gradient', 'nuke.createNode(\'Gradient.nk\')',
                icon='Format Feather_icon.png')
Edge.addCommand('LensDefects', 'nuke.createNode(\'LensDefects.nk\')',
                icon='Format Feather_icon.png')

Time = Tools.addMenu('Time', icon='Time_icon.png')
Time.addCommand('Frame Skip', 'nuke.createNode(\'Frame Skip.nk\')',
                icon='Frame Skip.png')
Time.addCommand('Loop Lazy', 'nuke.createNode(\'Loop Lazy.nk\')',
                icon='Loop Lazy_icon.png')


Views = Tools.addMenu('Views', icon='Views_icon.png')
Views.addCommand('Stereo Layout', 'nuke.createNode(\'Stereo Layout.nk\')',
                 icon='Stereo Layout_icon.png')


Others = Tools.addMenu('Others', icon='Others_icon.png')
Others.addCommand('MochaAE', 'import mochaAE_import as mae\nmae.panel()',
                  icon='MochaAE.png')
Others.addCommand('PFTrack',
                  'import tracks_qt\ntracks_qt.panel()',
                  icon='PFTrack_import_icon.png')
Others.addCommand('mmColorTarget', 'nuke.createNode(\'mmColorTarget.nk\')',
                  icon='mmColorTarget.png')
dg_PerspLines = Others.addMenu('dg_PerspLines', icon='Camera.png')
dg_PerspLines.addCommand('dg_PerspLines',
                         'nuke.createNode("dg_PerspLines.nk")',
                         icon='dg_PerspLines_icon.png')
dg_PerspLines.addCommand('dg_Horizon', 'dg_PerspLines_Horizon()',
                         icon='dg_Horizon_icon.png')
dg_PerspLines.addCommand('dg_CamFromLines', 'dg_PerspLines_AlignCamera()',
                         icon='Camera.png')
import readFromWrite
Others.addCommand('Read from Write',
                             'readFromWrite.ReadFromWrite()',
                             'ctrl+r')

Commands = Tools.addMenu('Commands', icon='ToolSets_icon.png')
import commands
import camera
Commands.addCommand('Read Range',
                  'commands.reads_set_range_panel()',
                  'shift+r')
Commands.addCommand('Camera from metadata',
                  "camera.cameraFromSelectedNodeMetadata(presetsFile=os.path.normpath(os.path.join(dirname, 'Commands/cameraMetadataPresets.json')))",
                  'shift+c')
###################### Tools End ######################
#######################################################

nuke.addOnUserCreate(lambda:nuke.thisNode()['first_frame'].setValue(nuke.frame()), nodeClass='FrameHold')