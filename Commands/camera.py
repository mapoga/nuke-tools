import math
import nuke
import nukescripts
import json

class CameraFromMetadataPanel(nukescripts.PythonPanel):
    def __init__(self, node, presets):
        nukescripts.PythonPanel.__init__(self, 'Camera from Metadata')
        self.presets = presets
        self.node = node
        self.presetTab = nuke.Tab_Knob(
            'presetTab',
            'Preset')
        self.preset = nuke.Enumeration_Knob(
            'preset',
            'preset',
            [p['name'] for p in self.presets['presets']])
        self.settingsTab = nuke.Tab_Knob(
            'settingsTab',
            'Settings')
        self.cameraTransformMatrix = nuke.String_Knob(
            'cameraTransformMatrix',
            'camera transform matrix',
            '')
        self.cameraTransformMatrixOrder = nuke.Enumeration_Knob(
            'cameraTransformMatrixOrder',
            'order',
            ['row-major',
             'column-major'])
        self.cameraTransformMatrixOrder.clearFlag(nuke.STARTLINE)
        self.flipZRot = nuke.Boolean_Knob(
            'flipZRot',
            'flip Z Rot')
        self.flipZPos = nuke.Boolean_Knob(
            'flipZPos',
            'flip Z Pos')
        self.flipZWorld = nuke.Boolean_Knob(
            'flipZWorld',
            'flip Z World')
        self.invert = nuke.Boolean_Knob(
            'invert',
            'invert')
        self.fov = nuke.String_Knob(
            'fov',
            'Field of View',
            '')
        self.near = nuke.String_Knob(
            'near',
            'near',
            '')
        self.far = nuke.String_Knob(
            'far',
            'far',
            '')
        self.pixelAspect = nuke.String_Knob(
            'pixelAspect',
            'pixel aspect',
            '')
        self.filmAspect = nuke.String_Knob(
            'filmAspect',
            'film aspect',
            '')
        self.apertures = nuke.String_Knob(
            'apertures',
            'apertures',
            '')
        self.horizontalAperture = nuke.String_Knob(
            'horizontalAperture',
            'horizontal aperture',
            '')
        self.verticalAperture = nuke.String_Knob(
            'verticalAperture',
            'vertical aperture',
            '')
        self.reconstructedHorizontalAperture = nuke.Double_Knob(
            'reconstructedHorizontalAperture',
            'reconstructed horizontal aperture')
        self.endTabs = nuke.EndTabGroup_Knob(
            'endTabs',
            'endTabs')
        default = self.presets.get('default')
        if default:
            self.preset.setValue(str(default))
            self.applyPreset(str(default))

        self.first = nuke.Int_Knob('first', 'first')
        self.first.setValue(self.node.firstFrame())
        self.last = nuke.Int_Knob('last', 'last')
        self.last.setValue(self.node.lastFrame())
        self.last.clearFlag(nuke.STARTLINE)
        for k in (
                self.presetTab,
                self.preset,
                self.settingsTab,
                self.cameraTransformMatrix,
                self.cameraTransformMatrixOrder,
                self.invert,
                self.flipZRot,
                self.flipZPos,
                self.flipZWorld,
                self.fov,
                self.near,
                self.far,
                self.pixelAspect,
                self.filmAspect,
                self.apertures,
                self.horizontalAperture,
                self.verticalAperture,
                self.reconstructedHorizontalAperture,
                self.endTabs,
                self.first,
                self.last
                  ):
            self.addKnob(k)

    def applyPreset(self, preset_name):
        preset = None
        for p in self.presets['presets']:
            if p['name'] == preset_name:
                preset = p
        parameters = preset['parameters']
        for key in parameters:
            if isinstance(key, unicode):
                key = str(key)
            knob = getattr(self, key)
            value = parameters[key]
            if isinstance(value, unicode):
                value = str(value)
            knob.setValue(value)

    def knobChanged(self, knob):
        if knob == self.preset:
            self.applyPreset(knob.value())

    def getCombinedAperture(self, frame):
        metadata = self.node.metadata(time=frame)

        pixelAspect = metadata.get(self.pixelAspect.value(), 1)
        filmAspect = metadata.get(self.filmAspect.value(), 1)
        apertures = metadata.get(self.apertures.value(), [1,1])
        horizontalAperture = metadata.get(self.horizontalAperture.value(), 1)
        verticalAperture = metadata.get(self.verticalAperture.value(), 1)
        reconstructedHorizontalAperture = self.reconstructedHorizontalAperture.value()

        h = (filmAspect*apertures[0]*horizontalAperture)/pixelAspect
        v = apertures[0]*verticalAperture
        v = reconstructedHorizontalAperture * (v/h)
        h = reconstructedHorizontalAperture
        return [h, v]

    def focal(self, aperture, angleOfView):
        opposite = aperture / 2
        theta = math.radians(angleOfView / 2)
        return opposite / math.tan(theta)

    def createCamera(self):
        cam = nuke.createNode('Camera2')
        # Preps knobs
        for k in ( 'focal', 'haperture', 'vaperture', 'translate', 'rotate', 'near', 'far'):
            cam[k].setAnimated()

        task = nuke.ProgressTask( 'Baking camera from metadata in {0}'.format(self.node.name()))

        for frame in range(self.first.value(), self.last.value() + 1):
            if task.isCancelled():
                break
            task.setMessage( 'processing frame {0}'.format(frame))
            # Metadata
            metadata = self.node.metadata(time=frame)
            if metadata:
	            fov = metadata.get(self.fov.value(), 45)
	            near = metadata.get(self.near.value(), 0.1)
	            far = metadata.get(self.far.value(), 10000)
	            apertures = self.getCombinedAperture(frame=frame)
	            #Convert
	            haperture = apertures[0]
	            vaperture = apertures[1]
	            focal = self.focal(haperture, fov)
	            # Set
	            cam['focal'].setValueAt(float(focal),frame)
	            cam['haperture'].setValueAt(float(haperture),frame)
	            cam['vaperture'].setValueAt(float(vaperture),frame)
	            cam['near'].setValueAt(float(near),frame)
	            cam['far'].setValueAt(float(far),frame)

	            # Transform Initialize
	            meta_transform = self.node.metadata(self.cameraTransformMatrix.value(), frame)
	            xform = nuke.math.Matrix4()
	            for k,v in enumerate(meta_transform):
	                xform[k] = v
	            # row-major matrix
	            if self.cameraTransformMatrixOrder.value() == 'column-major':
	                xform.transpose()
	            # invert
	            if self.invert.value():
	                xform = xform.inverse()
	            # Negate Transform in Z axis local space.
	            if self.flipZRot.value():
	                xform.scale(1,1,-1)
	            # Negate Transform in Z axis world space.
	            if self.flipZPos.value():
	                m = nuke.math.Matrix4()
	                m.makeIdentity()
	                m.scaling(1,1,-1)
	                xform = m * xform
	            # flip Z World
	            if self.flipZWorld.value():
	                m = nuke.math.Matrix4()
	                m.makeIdentity()
	                m.scaling(1,1,-1)
	                xform = xform * m
	            # Extract Translations
	            translate = xform.transform(nuke.math.Vector3(0,0,0))
	            # Extract Rotations
	            rotate = xform.rotationsZXY()
	            # Set values
	            cam['translate'].setValueAt(float(translate.x),frame,0)
	            cam['translate'].setValueAt(float(translate.y),frame,1)
	            cam['translate'].setValueAt(float(translate.z),frame,2)
	            cam['rotate'].setValueAt(float(math.degrees(rotate[0])),frame,0)
	            cam['rotate'].setValueAt(float(math.degrees(rotate[1])),frame,1)
	            cam['rotate'].setValueAt(float(math.degrees(rotate[2])),frame,2)

	            task.setProgress( int( float(frame-self.first.value()) / float(self.last.value()-self.first.value()+1) * 100 ) )


        return cam


def cameraFromSelectedNodeMetadata(presetsFile=''):
    node = nuke.selectedNode()
    presets = {}
    with open(presetsFile) as f:
        presets = json.load(f)
    panel = CameraFromMetadataPanel(node, presets)
    result = panel.showModalDialog()
    if result == 1:
        cam = panel.createCamera()
