# Source: http://richardfrazer.com/tools-tutorials/import-mocha-ae-tracks-to-nuke-via-python/
# Modified for PFTrack and the tracker4 node
# Modified by mathieugouletaubin@gmail.com

# todo
### -try and use the newer tracker node and keep names
### -pyqt panel with trackers selection
# -Modify to use with other tracker files

import sys
import os
import re
import nuke
from PySide import QtGui, QtCore




def lookupTrackerName(string):
	pattern = r'(^")([^"]+)("$)'

	matchObj = re.search(pattern, string)
	if matchObj:
		return matchObj.group(2);
	return

def lookupKeyframe(string):
	pattern = r'^(-?\d+)\s(-?\d+\.?\d*)\s(-?\d+\.?\d*)\s(-?\d+\.?\d*)$'

	matchObj = re.search(pattern, string)
	if matchObj:
		return { 'frame': int(matchObj.group(1)), 'xpos': float(matchObj.group(2)), 'ypos': float(matchObj.group(3)) };
	return

def parsePFTracks(filepath):

	# Open file
	try:
		f = open(filepath, 'r')
	except OSError as e:
		print('Error reading file: {0}'.format(e))
		f.close()


	trackers = []
	tracker = {'name': None, 'keys': []}

	# Lines loop
	for idx, line in enumerate(f):

		# keyframe
		key = lookupKeyframe(line)
		if key:
			tracker['keys'].append(key)

		# name
		name = lookupTrackerName(line)
		if name:
			if tracker['name'] and tracker['keys']:
				trackers.append(tracker)
			tracker = {'name': name, 'keys': []}

	# End of file
	if tracker['name'] and tracker['keys']:
		trackers.append(tracker)
	f.close()

	return trackers

def chunks(l, length):
	# Yield successive n-sized chunks from l
	for i in xrange(0, len(l), length):
		yield l[i:i + length]

def createTracker3(trackers, frameOffset=0, label=''):

	for tracks in chunks(trackers, 4):

		trackerNode = nuke.nodes.Tracker3(label='PFTrack_import')
		if label:
			trackerNode['label'].setValue(label)
			trackerNode['enable1'].setFlag(0)


		for idx, track in enumerate(tracks):
			kid = idx+1
			trackerNode['enable{0}'.format(kid)].setValue('true')
			trackKnob = trackerNode['track{0}'.format(kid)]
			trackKnob.setAnimated()
			trackKnobkeysX = []
			trackKnobkeysY = []

			for j in track['keys']:
				tFrame = int(j['frame']) + frameOffset
				tX = float(j['xpos'])
				tY = float(j['ypos'])

				trackKnobkeysX.append( (tFrame,tX) )
				trackKnobkeysY.append( (tFrame,tY) )

			trackKnobanimX = trackKnob.animation(0)
			trackKnobanimX.addKey([nuke.AnimationKey(frame, value) for (frame,value) in trackKnobkeysX])

			trackKnobanimY = trackKnob.animation(1)
			trackKnobanimY.addKey([nuke.AnimationKey(frame, value) for (frame,value) in trackKnobkeysY])


def createTracker(trackers, frameOffset=0, label=''):
	# ref 1 https://github.com/magnoborgo/RotoShapesToTrackers/blob/master/RotoShapes_to_trackers.py
	# ref 2 http://community.foundry.com/discuss/topic/99665/python-with-new-tracker?mode=Post&postID=969555

	n = nuke.createNode('Tracker4')
	if label:
		n['label'].setValue(label)
		n['add_track'].setFlag(0)
	n.setName('PFTrack')
	table = n['tracks']
	numColumns = 31
	colTrackX = 2
	colTrackY = 3

	for idx, track in enumerate(trackers):
		n['add_track'].execute()
		frames = []
		for k in track['keys']:
			frames.append(k['frame'])
			table.setValueAt(k['xpos'], k['frame']+frameOffset, (idx*numColumns)+colTrackX)
			table.setValueAt(k['ypos'], k['frame']+frameOffset, (idx*numColumns)+colTrackY)

		# Clear execution frame from auto key
		if not nuke.frame() in frames:
			for i in range(numColumns):
				table.removeKeyAt(nuke.frame(), (idx*numColumns)+i)



def panel():

	frameOffset = 0

	p = nuke.Panel('Import PFTrack track')
	p.addFilenameSearch('Select PFTrack track file (.txt)', '')
	p.addSingleLineInput('Frame offset', frameOffset)
	p.addBooleanCheckBox('Use tracker3 node', False)
	p.addButton('Cancel')
	p.addButton('OK')

	ret = p.show()

	tPath = p.value('Select PFTrack track file (.txt)')
	isOld = p.value('Use tracker3 node')

	frameOffset = int(p.value('Frame offset'))

	if ret:
		tracks = parsePFTracks(tPath)
		if isOld:
			createTracker3(tracks, frameOffset)
		else:
			createTracker(tracks, frameOffset)