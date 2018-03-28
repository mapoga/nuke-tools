# import-mocha-AE-tracks-to-nuke
#Python script script that takes a Mocha for AE planar track and creates a Nuke Tracker node.
#http://richardfrazer.com/tools-tutorials/import-mocha-ae-tracks-to-nuke-via-python/

#!/usr/bin/env python

import sys
import os
import re
import nuke



def lookupCoordinates(string):
   
    pattern = r'[-+]?\b[0-9]*\.?[0-9]+\b\t[-+]?\b[0-9]*\.?[0-9]+\b\t[-+]?\b[0-9]*\.?[0-9]'
    # search for - <int><tab><float/int><tab><float/int>
    
    coords = []
    
    matchObj = re.search(pattern, string)
    if matchObj:
        coords = matchObj.group().split('\t');
       
    return coords

def lookupFrameWidth(string):
    
    global frameWidth;

    pattern = r'Source Width\t\b\d+\b'
    
    
    matchObj = re.search(pattern, string)
    if matchObj:
        
        frameWidth = int(matchObj.group().split('\t')[1]);
        return frameWidth
    else:
        return
        
def lookupFrameHeight(string):
    
    global frameHeight;
            
    pattern = r'Source Height\t\b\d+\b'
    
    matchObj = re.search(pattern, string)
    if matchObj:
        frameHeight = int(matchObj.group().split('\t')[1]);
        return frameHeight
    else:
        return
        
def createNukeCornerPinNode(coordinatesArray):
    
    global frameHeight
    
    global frameOffset
    
    cornerPinNode = nuke.nodes.CornerPin2D(label='imported_Mocha-AE_Track')
    
    cornerPinNode['enable1'].setValue('true')
    cornerPinNode['enable2'].setValue('true')
    cornerPinNode['enable3'].setValue('true')
    cornerPinNode['enable4'].setValue('true')
    
    # LOWER LEFT
    
    track1 = cornerPinNode['to1']
    track1.setAnimated()
    track1keysX = []
    track1keysY = []
    
    for j in coordinatesArray[0]:
        tFrame = int(j[0]) + frameOffset
        tX = float(j[1])
        tY = frameHeight - float(j[2])
        
        track1keysX.append( (tFrame,tX) )
        track1keysY.append( (tFrame,tY) )
    
    #print "track1keysX: %s" % len(track1keysX)
    #print "track1keysY: %s" % len(track1keysY)
      
    # LOWER RIGHT
        
    track2 = cornerPinNode['to2']
    track2.setAnimated()
    track2keysX = []
    track2keysY = []
    
    for j in coordinatesArray[1]:
        tFrame = int(j[0]) + frameOffset
        tX = float(j[1])
        tY = frameHeight - float(j[2])
        
        track2keysX.append( (tFrame,tX) )
        track2keysY.append( (tFrame,tY) )
    
    #print "track2keysX: %s" % len(track1keysX)
    #print "track2keysY: %s" % len(track1keysY)
       
    # UPPER RIGHT
        
    track3 = cornerPinNode['to3']
    track3.setAnimated()
    track3keysX = []
    track3keysY = []
    
    for j in coordinatesArray[3]:
        tFrame = int(j[0]) + frameOffset
        tX = float(j[1])
        tY = frameHeight - float(j[2])
        
        track3keysX.append( (tFrame,tX) )
        track3keysY.append( (tFrame,tY) )
    
    #print "track3keysX: %s" % len(track3keysX)
    #print "track3keysY: %s" % len(track3keysY)
    
    # UPPER LEFT
        
    track4 = cornerPinNode['to4']
    track4.setAnimated()
    track4keysX = []
    track4keysY = []
    
    for j in coordinatesArray[2]:
        tFrame = int(j[0]) + frameOffset
        tX = float(j[1])
        tY = frameHeight - float(j[2])
        
        track4keysX.append( (tFrame,tX) )
        track4keysY.append( (tFrame,tY) )
    
    #print "track4keysX: %s" % len(track4keysX)
    #print "track4keysY: %s" % len(track4keysY)
    
    
    
    track1animX = track1.animation(0)
    track1animX.addKey([nuke.AnimationKey(frame, value) for (frame,value) in track1keysX])
    
    track1animY = track1.animation(1)
    track1animY.addKey([nuke.AnimationKey(frame, value) for (frame,value) in track1keysY])
    
    track2animX = track2.animation(0)
    track2animX.addKey([nuke.AnimationKey(frame, value) for (frame,value) in track2keysX])
    
    track2animY = track2.animation(1)
    track2animY.addKey([nuke.AnimationKey(frame, value) for (frame,value) in track2keysY])
    
    track3animX = track3.animation(0)
    track3animX.addKey([nuke.AnimationKey(frame, value) for (frame,value) in track3keysX])
    
    track3animY = track3.animation(1)
    track3animY.addKey([nuke.AnimationKey(frame, value) for (frame,value) in track3keysY])
    
    track4animX = track4.animation(0)
    track4animX.addKey([nuke.AnimationKey(frame, value) for (frame,value) in track4keysX])
    
    track4animY = track4.animation(1)
    track4animY.addKey([nuke.AnimationKey(frame, value) for (frame,value) in track4keysY])
    
    nuke.show(cornerPinNode)
    
    
    nuke.zoom(1, (cornerPinNode.xpos(), cornerPinNode.ypos() ) )
    
    return

def createNukeTrackerNode(coordinatesArray):
    
    global frameHeight
    
    global frameOffset
    
    trackerNode = nuke.nodes.Tracker3(label='imported_Mocha-AE_Track')
    
    trackerNode['enable1'].setValue('true')
    trackerNode['enable2'].setValue('true')
    trackerNode['enable3'].setValue('true')
    trackerNode['enable4'].setValue('true')
    
    # LOWER LEFT
    
    track1 = trackerNode['track1']
    track1.setAnimated()
    track1keysX = []
    track1keysY = []
    
    for j in coordinatesArray[2]:
        tFrame = int(j[0]) + frameOffset
        tX = float(j[1])
        tY = frameHeight - float(j[2])
        
        track1keysX.append( (tFrame,tX) )
        track1keysY.append( (tFrame,tY) )
        
    # LOWER RIGHT
        
    track2 = trackerNode['track2']
    track2.setAnimated()
    track2keysX = []
    track2keysY = []
    
    for j in coordinatesArray[3]:
        tFrame = int(j[0]) + frameOffset
        tX = float(j[1])
        tY = frameHeight - float(j[2])
        
        track2keysX.append( (tFrame,tX) )
        track2keysY.append( (tFrame,tY) )
        
    # UPPER LEFT
        
    track3 = trackerNode['track3']
    track3.setAnimated()
    track3keysX = []
    track3keysY = []
    
    for j in coordinatesArray[0]:
        tFrame = int(j[0]) + frameOffset
        tX = float(j[1])
        tY = frameHeight - float(j[2])
        
        track3keysX.append( (tFrame,tX) )
        track3keysY.append( (tFrame,tY) )
    

    # UPPER RIGHT
        
    track4 = trackerNode['track4']
    track4.setAnimated()
    track4keysX = []
    track4keysY = []
    
    for j in coordinatesArray[1]:
        tFrame = int(j[0]) + frameOffset
        tX = float(j[1])
        tY = frameHeight - float(j[2])
        
        track4keysX.append( (tFrame,tX) )
        track4keysY.append( (tFrame,tY) )
    
    track1animX = track1.animation(0)
    track1animX.addKey([nuke.AnimationKey(frame, value) for (frame,value) in track1keysX])
    
    track1animY = track1.animation(1)
    track1animY.addKey([nuke.AnimationKey(frame, value) for (frame,value) in track1keysY])
    
    track2animX = track2.animation(0)
    track2animX.addKey([nuke.AnimationKey(frame, value) for (frame,value) in track2keysX])
    
    track2animY = track2.animation(1)
    track2animY.addKey([nuke.AnimationKey(frame, value) for (frame,value) in track2keysY])
    
    track3animX = track3.animation(0)
    track3animX.addKey([nuke.AnimationKey(frame, value) for (frame,value) in track3keysX])
    
    track3animY = track3.animation(1)
    track3animY.addKey([nuke.AnimationKey(frame, value) for (frame,value) in track3keysY])
    
    track4animX = track4.animation(0)
    track4animX.addKey([nuke.AnimationKey(frame, value) for (frame,value) in track4keysX])
    
    track4animY = track4.animation(1)
    track4animY.addKey([nuke.AnimationKey(frame, value) for (frame,value) in track4keysY])
    
    nuke.show(trackerNode)
    
    
    nuke.zoom(1, (trackerNode.xpos(), trackerNode.ypos() ) )
    
    return  
    
def convertIncomingData(tPath, tTrackerNode, tCornerPinNode):

            
            try:
                f=open(tPath)
                lines = f.readlines()
            except Exception as e:
                print 'fail: %s' % e
                exit()
                
            
            global coordinatesArray;
            global frameWidth 
            global frameHeight
            
            coordinatesArray = []
            
            prevframe = -99999999999999
            
            pointArray = []
            
            
            for line in lines:
                lookupFrameWidth(line)
                lookupFrameHeight(line)
                

                coordinates = lookupCoordinates(line)
                
                if len(coordinates):
                    frame = int(coordinates[0])
                    if (frame > prevframe):
                        pointArray.append( coordinates )
                        prevframe = frame
                    else:
                        prevframe = -99999999999999
                        coordinatesArray.append( pointArray )
                        pointArray = []
                        pointArray.append( coordinates )
                        
            coordinatesArray.append( pointArray )
            
            
            if len(coordinatesArray):
                if (tTrackerNode):
                    createNukeTrackerNode(coordinatesArray)
                if (tCornerPinNode):
                    createNukeCornerPinNode(coordinatesArray)
       
def panel():
    global frameOffset 


    frameOffset = nuke.root().firstFrame()

    p = nuke.Panel('Import Mocha-AE track')
    p.addFilenameSearch('Select Mocha-AE track file (.txt)', '')
    p.addSingleLineInput('Frame offset', frameOffset)
    p.addBooleanCheckBox('Create Tracker node', True)
    p.addBooleanCheckBox('Create CornerPin node', True)
    p.addButton('Cancel')
    p.addButton('OK')

    ret = p.show()

    tPath = p.value('Select Mocha-AE track file (.txt)')

    #print tPath

    frameOffset = int(p.value('Frame offset'))

    if ret:
        convertIncomingData(tPath, p.value('Create Tracker node'), p.value('Create CornerPin node'))
            
        
        