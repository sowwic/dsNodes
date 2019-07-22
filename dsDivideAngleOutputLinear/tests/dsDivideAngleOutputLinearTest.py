import maya.cmds as mc
from rigging.functions import *

mc.file(new=1,f=1)
mc.unloadPlugin("dsDivideAngleOutputLinear")

mc.loadPlugin(r'C:\Users\dmitris\Documents\maya\2018\scripts\plugins\plugins\dsDivideAngleOutputLinear.py')

############
# Unit test
dsDivide = mc.createNode("dsDivideAngleOutputLinear")
adl = create.addDoubleLinear()
a = create.locator()
b = create.locator()

a.rotateX > dsDivide + ".aa"
a.rotateY > dsDivide + ".ab"
dsDivide + ".output" > adl.input1