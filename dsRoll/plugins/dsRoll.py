from maya import cmds as mc, OpenMaya as om, OpenMayaMPx as ompx, mel
import getpass, os, sys



class DsRollNode(ompx.MPxNode):

    VENDOR = 'Dmitrii Shevchenko'
    VERSION = '1.0'
    MAYAVERSION = '2020'
    NODENAME = 'dsRoll'
    NODEID = om.MTypeId(0x09773)

    inAttr = om.MObject()
    outAttr = om.MObject()

    def __init__(self):
        super(DsRollNode, self).__init__()

    @classmethod
    def creator(cls):
        return DsRollNode()

    @classmethod
    def initialize(cls):
        numericFn = om.MFnNumericAttribute()
        unitFn = om.MFnUnitAttribute()

        cls.distanceObj = numericFn.create("distance", "dist", om.MFnNumericData.kDouble, 0.0)
        numericFn.setReadable(True)
        numericFn.setKeyable(True)

        cls.radiusObj = numericFn.create("radius", "rad", om.MFnNumericData.kDouble, 0.0)
        numericFn.setReadable(True)
        numericFn.setKeyable(True)

        cls.rotationObj = unitFn.create("rotation", "rot", om.MFnUnitAttribute.kAngle, 0.0)

        cls.addAttribute(cls.distanceObj)
        cls.addAttribute(cls.radiusObj)
        cls.addAttribute(cls.rotationObj)

        cls.attributeAffects(cls.distanceObj, cls.rotationObj)
        cls.attributeAffects(cls.radiusObj, cls.rotationObj)

    def compute(self, pPlug, pDataBlock):
        if pPlug == self.rotationObj:
            distance = pDataBlock.inputValue(DsRollNode.distanceObj).asDouble()
            radius = pDataBlock.inputValue(DsRollNode.radiusObj).asDouble()

            if radius == 0:
                rotation = 0
            else:
                rotation = distance/radius

            rotationDataHandle = pDataBlock.outputValue(DsRollNode.rotationObj)
            rotationDataHandle.setDouble(rotation)

            pDataBlock.setClean(pPlug)


    
def initializePlugin(obj):
    plugin = ompx.MFnPlugin(obj, DsRollNode.VENDOR, DsRollNode.VERSION, DsRollNode.MAYAVERSION)
    try:
        plugin.registerNode(DsRollNode.NODENAME,
                            DsRollNode.NODEID, 
                            DsRollNode.creator, 
                            DsRollNode.initialize, 
                            ompx.MPxNode.kDependNode)
    except RuntimeError:
        sys.stderr.write('Failed to register node: {0}'.format( DsRollNode.NODENAME))

aeTemplate = open(os.path.join(mel.eval('getenv ("MAYA_APP_DIR")'), 'scripts\dsNodes\dsRoll\plugins\AEtemplate.mel'), "r").read()
mel.eval(aeTemplate)
mel.eval("refreshEditorTemplates; refreshAE;")


def uninitializePlugin(obj):
    plugin = ompx.MFnPlugin(obj)
    try:
        plugin.deregisterNode(DsRollNode.NODEID)
    except Exception as err:
        sys.stderr.write('Failed to deregister node: {0}{1}'.format((DsRollNode.NODENAME, err)))