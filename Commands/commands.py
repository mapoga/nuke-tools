import nuke
import math
import re
import os

def set_range(n, first, last):
    n.knob('first').setValue(first)
    n.knob('origfirst').setValue(first)
    n.knob('last').setValue(last)
    n.knob('origlast').setValue(last)

def range_from_filename(filename):
    dirname = os.path.dirname(filename)
    basename = os.path.basename(filename)
    match = re.search(r'(%0\dd|#+)', basename)
    if match:
        size = len(match.group(0))
        name_pattern = re.sub(r'(%0\dd|#+)', '(' + '\d'*size + ')', basename)

        names = os.listdir(dirname)
        numbers = []
        for n in names:
            match = re.match(name_pattern, n)
            if match:
                number = int(match.group(1))
                numbers.append(number)

        numbers = list(set(numbers))
        numbers.sort()
        return numbers[0], numbers[-1]

    return None, None

def reads_set_range_panel():
    p = nuke.Panel('Set Range')
    p.addSingleLineInput('first', 1001)
    p.addSingleLineInput('last', 1050)
    p.addBooleanCheckBox('Auto Range', True)
    panel = p.show()

    if panel == 1:
        first = int(p.value('first'))
        last = int(p.value('last'))

        for n in nuke.selectedNodes():
            if p.value('Auto Range') == True:
                tmp_first, tmp_last = range_from_filename(n.knob('file').value())
                if tmp_first != None and tmp_last != None:
                    set_range(n, tmp_first, tmp_last)
            else:
                set_range(n, first, last)

def camera_from_RS_metadata():
    '''
    Create a camera node based on RS metadata.
    Build for: Houdini -> Redshift -> Nuke
    '''
    node = nuke.selectedNode()
    mDat = node.metadata()
    reqFields = ['exr/rs/camera/%s' % i for i in ('fov', 'aperture', 'transform', 'aspect', 'nearPlane', 'farPlane')]
    if not set( reqFields ).issubset( mDat ):
        print('no metadata for camera found')
        return
    
    # User values
    first = node.firstFrame()
    last = node.lastFrame()

    panel = nuke.Panel('Camera from Redshift exr metadata')
    panel.addSingleLineInput('first', first)
    panel.addSingleLineInput('last', last)
    panel.addBooleanCheckBox('-Z Rotations', True)
    panel.addBooleanCheckBox('-Z World', False)
    panel.addSingleLineInput('Horizontal Aperture', 36)
    panel_result = panel.show()
    if panel_result == 1:

        negate_rot = panel.value('-Z Rotations')
        negate_world = panel.value('-Z World')
        first = int(panel.value('first'))
        last = int(panel.value('last'))
        hap_mult = float(panel.value('Horizontal Aperture'))


        cam = nuke.createNode( 'Camera2' )
        # Preps knobs
        for k in ( 'focal', 'haperture', 'vaperture', 'translate', 'rotate', 'near', 'far'):
            cam[k].setAnimated()
            

        for frame in range(first, last + 1):
            # Metadata
            aperture = mDat['exr/rs/camera/aperture']
            aspect = mDat['exr/rs/camera/aspect']
            fov = mDat['exr/rs/camera/fov']
            near = mDat['exr/rs/camera/nearPlane']
            far = mDat['exr/rs/camera/farPlane']
            #Convert
            valh = aperture[0] * hap_mult
            valv = valh / aspect
            focal = (valh / (2 * math.tan(math.pi * fov / 360)))
            # Set
            cam['focal'].setValueAt(float(focal),frame)
            cam['haperture'].setValueAt(float(valh),frame)
            cam['vaperture'].setValueAt(float(valv),frame)
            cam['near'].setValueAt(float(near),frame)
            cam['far'].setValueAt(float(far),frame)

            # Transform Initialize
            meta_transform = node.metadata( 'exr/rs/camera/transform', frame)
            xform = nuke.math.Matrix4()
            for k,v in enumerate(meta_transform):
                xform[k] = v

            # Negate Transform in Z axis local space.
            if negate_rot:
                xform.scale(1,1,-1)
            # Negate Transform in Z axis world space.
            if negate_world:
                m = nuke.math.Matrix4()
                m.makeIdentity()
                m.scaling(1,1,-1)
                xform = m * xform
            # Extract Translations
            translate = xform.transform(nuke.math.Vector3(0,0,0))
            # Extract ROtations
            rotate = xform.rotationsZXY()
            # Set values
            cam['translate'].setValueAt(float(translate.x),frame,0)
            cam['translate'].setValueAt(float(translate.y),frame,1)
            cam['translate'].setValueAt(float(translate.z),frame,2)
            cam['rotate'].setValueAt(float(math.degrees(rotate[0])),frame,0)
            cam['rotate'].setValueAt(float(math.degrees(rotate[1])),frame,1)
            cam['rotate'].setValueAt(-float(math.degrees(rotate[2])),frame,2)