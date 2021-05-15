import nuke
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
