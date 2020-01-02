import maya.mel as mel
import maya.OpenMaya as om
import maya.OpenMayaMPx as ommpx
import getpass, os, sys



class DsAttractDeformer(ommpx.MPxDeformerNode):

    VENDOR = 'Dmitrii Shevchenko'
    VERSION = '1.0'
    MAYAVERSION = '2020'
    NODENAME = 'dsAttractDeformer'
    NODEID = om.MTypeId(0x09113)

    MAX_ANGLE = 0.5 * 3.14159265 #90 degrees


    def __init__(self):
        super(DsAttractDeformer, self).__init__()

    def deform(self, pDataBlock, geoIter, worldMatrix, multiIndex):

        ## GET DATA
        envelope = pDataBlock.inputValue(self.envelope).asFloat()
        if envelope == 0:
            return
        
        maxDistance =  pDataBlock.inputValue(self.maxDistance).asFloat()
        if maxDistance == 0:
            return

        ## GET ATTRACT POINTS
        
        pointsDataHandle = pDataBlock.inputArrayValue(self.attractPoint)
        if pointsDataHandle.elementCount() == 0:
            return
            
        pointsArray = om.MFloatVectorArray()
        for i in range(0, pointsDataHandle.elementCount()):
            elementHandle = pointsDataHandle.inputValue()
            singlePoint =  elementHandle.asFloatVector()
            pointsArray.append(singlePoint)

       ## GET GEOMETRY NORMALS
        inputHandle = pDataBlock.outputArrayValue(self.input)
        inputHandle.jumpToElement(multiIndex)
        inputElementHandle = inputHandle.outputValue()
        
        inputGeom = inputElementHandle.child(self.inputGeom).asMesh()
        meshFn = om.MFnMesh(inputGeom)

        normals = om.MFloatVectorArray()
        meshFn.getVertexNormals(False, normals)
        inverseMatrix = worldMatrix.inverse()

        #DEFORM
        geoIter.reset()
        while not geoIter.isDone():
            ptLocal = geoIter.position()
            ptWorld = ptLocal * worldMatrix

            targetVector = pointsArray[0] - om.MFloatVector(ptWorld)
            if targetVector.length() <= maxDistance:
                normal = om.MVector(normals[geoIter.index()]) * worldMatrix
                normal = om.MFloatVector(normal)

                angle = normal.angle(targetVector)
                if angle <= DsAttractDeformer.MAX_ANGLE:
                    offset = targetVector * (maxDistance - targetVector.length()) / maxDistance
                    newPtWorld = ptWorld + om.MVector(offset)
                    newPtLocal = newPtWorld * inverseMatrix

                    geoIter.setPosition(newPtLocal)

            

            geoIter.next()




    @classmethod
    def creator(cls):
        return DsAttractDeformer()

    @classmethod
    def initialize(cls):
        numericFn = om.MFnNumericAttribute()

        cls.attractPoint =  numericFn.createPoint("attractPoints", "ap")
        numericFn.setArray(True)
        numericFn.setKeyable(True)

        cls.maxDistance = numericFn.create("maximumDistance", "maxDist", om.MFnNumericData.kFloat, 1.0)
        numericFn.setKeyable(True)
        numericFn.setMin(0.0)
        numericFn.setMax(6.0)

        
        cls.addAttribute(cls.attractPoint)
        cls.addAttribute(cls.maxDistance)

        outputGeom = ommpx.cvar.MPxGeometryFilter_outputGeom
        cls.attributeAffects(cls.maxDistance, outputGeom)
        cls.attributeAffects(cls.attractPoint, outputGeom)


    
def initializePlugin(obj):
    plugin = ommpx.MFnPlugin(obj, DsAttractDeformer.VENDOR, DsAttractDeformer.VERSION, DsAttractDeformer.MAYAVERSION)
    try:
        plugin.registerNode(DsAttractDeformer.NODENAME,
                            DsAttractDeformer.NODEID, 
                            DsAttractDeformer.creator, 
                            DsAttractDeformer.initialize, 
                            ommpx.MPxNode.kDeformerNode)
    except RuntimeError:
        sys.stderr.write('Failed to register node: {0}'.format( DsAttractDeformer.NODENAME))

# aeTemplate = open(os.path.join(mel.eval('getenv ("MAYA_APP_DIR")'), 'scripts\dsNodes\dsAttractDeformer\plugins\AEtemplate.mel'), "r").read()
# mel.eval(aeTemplate)
# mel.eval("refreshEditorTemplates; refreshAE;")


def uninitializePlugin(obj):
    plugin = ommpx.MFnPlugin(obj)
    try:
        plugin.deregisterNode(DsAttractDeformer.NODEID)
    except Exception as err:
        sys.stderr.write('Failed to deregister node: {0}{1}'.format((DsAttractDeformer.NODENAME, err)))