import nuke
from math import sqrt as sqrt
from math import atan as atan
from math import pi as PI

def dg_PerspLines_selectOnly(node):
	if nuke.NUKE_VERSION_MAJOR<8:
		for n in nuke.selectedNodes():
			n.setSelected(False)
		node.setSelected(True)
	else:
		node.selectOnly()

def dg_PerspLines_OnCreate():
	tn=nuke.thisNode()
	if not tn.knobs().get('additional'):
		tn.addKnob(nuke.Tab_Knob('additional','additional lines'))
		
		k=nuke.PyScript_Knob('add')
		k.setCommand('dg_PerspLines_AddLine()')
		tn.addKnob(k)
		
		tn['p00'].setValue([0,0])
		tn['p01'].setValue([tn.width()/3,tn.height()/3])
		tn['p10'].setValue([2*tn.width()/3,tn.height()/3])
		tn['p11'].setValue([tn.width(),0])
	
def dg_PerspLines_AddLine():
	
	gn=nuke.thisGroup()
	dg_PerspLines_selectOnly(gn.node('add'))
	nuke.nodeCopy('%clipboard%' )
	dg_PerspLines_selectOnly(gn.node('base'))
	n=nuke.nodePaste('%clipboard%')
	
	tn=nuke.thisNode()
	
	k=nuke.XY_Knob(n.name())
	k.setValue([n.width()/2,n.height()/2])
	tn.addKnob(k)
	n['p'].setExpression('parent.'+n.name())
	
	k=nuke.PyScript_Knob('delete_'+n.name(),'delete')
	tn.addKnob(k)
	k.clearFlag(nuke.STARTLINE)
	k.setCommand('\n'.join(['nuke.delete(nuke.thisGroup().node("'+n.name()+'"))','nuke.thisNode().removeKnob(nuke.thisNode()["'+n.name()+'"])','nuke.thisNode().removeKnob(nuke.thisKnob())']))
	

nuke.addOnCreate(dg_PerspLines_OnCreate,nodeClass='dg_PerspLines')


# Estimate Focal and Align Camera

def dg_PerspLines_AlignCamera():
    nodes=nuke.selectedNodes()
    if not len(nodes)==2:
        nuke.message('Illegal amount of selected nodes.\nPlease select exactly two dg_PerspLines nodes')
        return
    for n in nodes:
        if not n.Class()=='dg_PerspLines':
            nuke.message('One of selected nodes is not dg_PerspLines')
            return
    
    V1 = nodes[0]['PT'].value()
    V2 = nodes[1]['PT'].value()
    
    K = (V2[1]-V1[1])/(V2[0]-V1[0])
    print K
    
    Oi = [nodes[0].width()/2,nodes[0].height()/2]
    print Oi
    
    Vix = (1/K*Oi[0]+Oi[1]+K*V1[0]-V1[1])/(K+1/K)
    Viy = -1/K*(Vix-Oi[0])+Oi[1]
    Vi = [Vix,Viy]
    print Vi
    
    ViV1 = sqrt(pow(Vi[0]-V1[0],2)+pow(Vi[1]-V1[1],2))
    ViV2 = sqrt(pow(Vi[0]-V2[0],2)+pow(Vi[1]-V1[1],2))
    
    print ViV1
    print ViV2
    
    OcVi = sqrt(ViV1*ViV2)
    OiVi = sqrt(pow(Oi[0]-Vi[0],2)+pow(Oi[1]-Vi[1],2))
    print OcVi
    print OiVi
    
    f = sqrt(pow(OcVi,2)-pow(OiVi,2))
    print f
    
    f_scale = sqrt(pow(Oi[0]*2,2)+pow(Oi[1]*2,2))/f
    
    
    camNode = nuke.createNode('Camera',inpanel=False)
    camNode['tile_color'].setValue(884320767)
    
    camNode['focal'].setValue(sqrt(pow(camNode['haperture'].value(),2)+pow(camNode['vaperture'].value(),2))/f_scale)
    
    
    Rx = atan((Oi[1]-Vi[1])/f)*180/PI
    Ry = atan(min(ViV1,ViV2)/f)*180/PI
    Ry2 = atan(max(ViV1,ViV2)/f)*180/PI
    Rz = -atan(K)*180/PI
    
    camNode['rotate'].setValue([Rx,Ry,Rz])
    camNode['translate'].setValue([0,1,0])
    
    k = nuke.Double_Knob('Ry')
    k.setValue(Ry2)
    camNode.addKnob(nuke.Tab_Knob('alternate'))
    camNode.addKnob(k)
    
    k=nuke.PyScript_Knob('swap')
    k.setCommand('dg_PerspLines_swap(nuke.thisNode())')
    camNode.addKnob(k)

def dg_PerspLines_swap(node):
	R=node['rotate'].value()
	P=R[1]
	node['rotate'].setValue([R[0],node['Ry'].value(),R[2]])
	node['Ry'].setValue(P)
    
   
def dg_PerspLines_Horizon():
	nodes=nuke.selectedNodes()
	if not len(nodes)==2:
		nuke.message('Illegal amount of selected nodes.\nPlease select exactly two dg_PerspLines nodes')
		return
	for n in nodes:
		if not n.Class()=='dg_PerspLines':
			nuke.message('One of selected nodes is not dg_PerspLines')
			return
	i=1
	if nodes[0].input(0)==nodes[1]:
		i=0
	
	dg_PerspLines_selectOnly(nodes[i])
	
	n=nuke.createNode('dg_Horizon')
	n['vp1'].setExpression(nodes[0].name()+'.PT')
	n['vp2'].setExpression(nodes[1].name()+'.PT')