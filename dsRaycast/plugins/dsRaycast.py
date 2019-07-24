from maya import cmds as mc, OpenMaya as om, OpenMayaMPx as ompx, mel
import getpass, os, sys

NAME = "dsRaycast"
VERSION = "1.0"
MAYAVERSION = "2018"
NODENAME = "dsRaycast"
NODEID = om.MTypeId(0x09833)

class DsRaycast(ompx.MPxNode):
   
    inMesh = om.MObject()
    inSource = om.MObject()
    inAim = om.MObject()
    inDistance = om.MObject()
    inBothWays = om.MObject()
    outHitPoint = om.MObject()
    outNormal = om.MObject()
   
    def __init__(self):
        ompx.MPxNode.__init__(self)
       
    def compute(self, pPlug, pDataBlock):
       
        if pPlug == DsRaycast.outHitPoint:
            #Handles
            inMeshHandle = pDataBlock.inputValue(DsRaycast.inMesh)
            inSourceHandle = pDataBlock.inputValue(DsRaycast.inSource)
            inAimHandle = pDataBlock.inputValue(DsRaycast.inAim)
            inDistanceHandle = pDataBlock.inputValue(DsRaycast.inDistance)
            inBothWaysHandle = pDataBlock.inputValue(DsRaycast.inBothWays)
            outHitHandle = pDataBlock.outputValue(DsRaycast.outHitPoint)
            outNormalhandle = pDataBlock.outputValue(DsRaycast.outNormal)

            inMesh = inMeshHandle.asMeshTransformed()
            fnMesh = om.MFnMesh(inMesh)
            inSource = om.MFloatPoint(inSourceHandle.asFloatVector())
            inAim = om.MFloatVector(inAimHandle.asFloatVector())
            inDistance = inDistanceHandle.asFloat()
            inBothWays = inBothWaysHandle.asBool()
            hitPoint = om.MFloatPoint()

            
            intersection = fnMesh.closestIntersection(inSource,
                                                      inAim,
                                                      None,
                                                      None,
                                                      False,
                                                      om.MSpace.kWorld,
                                                      inDistance,
                                                      inBothWays,
                                                      #fnMesh.autoUniformGridParams(),
                                                      None,
                                                      hitPoint,
                                                      None, 
                                                      None,
                                                      None,
                                                      None,
                                                      None                                            
                                                        )
            #Getting normal             
            normalVector = om.MVector()
            mHitPoint = om.MPoint(hitPoint)
            fnMesh.getClosestNormal(mHitPoint, normalVector, om.MSpace.kWorld)


            outHitHandle.setMFloatVector(om.MFloatVector(hitPoint))
            outNormalhandle.setMFloatVector(om.MFloatVector(normalVector))

            outHitHandle.setClean()
            outNormalhandle.setClean()

          
        else:
           
            return om.kUnknownParameter
       
def nodeCreator():
   return ompx.asMPxPtr(DsRaycast())

def nodeInitializer():
   
    typedAttributeFn = om.MFnTypedAttribute()
    numericAttributeFn = om.MFnNumericAttribute()
    
    ##IN
    #Mesh
    DsRaycast.inMesh = typedAttributeFn.create('targetMesh','tm', om.MFnData.kMesh)
    DsRaycast.addAttribute(DsRaycast.inMesh)
    typedAttributeFn.setReadable(0)
    
    #Source
    DsRaycast.inSource = numericAttributeFn.createPoint("source", "srs")
    DsRaycast.addAttribute(DsRaycast.inSource)

    #Aim
    DsRaycast.inAim = numericAttributeFn.createPoint("aim", "aim")
    DsRaycast.addAttribute(DsRaycast.inAim)

    #Distance
    DsRaycast.inDistance = numericAttributeFn.create('distance', 'dis', om.MFnNumericData.kFloat, 100)
    DsRaycast.addAttribute(DsRaycast.inDistance)

    #Test direction
    DsRaycast.inBothWays = numericAttributeFn.create('bothWays', 'bw', om.MFnNumericData.kBoolean, 1)
    DsRaycast.addAttribute(DsRaycast.inBothWays)


    ##OUT
    #Hitpoint
    DsRaycast.outHitPoint = numericAttributeFn.createPoint("hitPoint", "hit")
    numericAttributeFn.setWritable(0)

    DsRaycast.addAttribute( DsRaycast.outHitPoint )
    
    #Normal
    DsRaycast.outNormal = numericAttributeFn.createPoint('normal', 'n')
    DsRaycast.addAttribute(DsRaycast.outNormal)
    numericAttributeFn.setWritable(0)
    
    #Affects
    DsRaycast.attributeAffects(DsRaycast.inMesh, DsRaycast.outHitPoint)
    DsRaycast.attributeAffects(DsRaycast.inSource, DsRaycast.outHitPoint)
    DsRaycast.attributeAffects(DsRaycast.inAim, DsRaycast.outHitPoint)

    DsRaycast.attributeAffects(DsRaycast.inMesh, DsRaycast.outNormal)
    DsRaycast.attributeAffects(DsRaycast.inSource, DsRaycast.outNormal)
    DsRaycast.attributeAffects(DsRaycast.inAim, DsRaycast.outNormal)



def initializePlugin(obj):
   plugin = ompx.MFnPlugin(obj, NAME, VERSION, MAYAVERSION)
   try:
       plugin.registerNode(NODENAME, NODEID, nodeCreator, nodeInitializer)
   except RuntimeError:
       sys.stderr.write("Failed to register node: %s" % NODENAME)

aeTemplate = open(r'C:\Users\dmitris\Documents\maya\scripts\dsNodes\dsRaycast\AEtemplate.mel', "r").read()
mel.eval(aeTemplate)
mel.eval("refreshEditorTemplates; refreshAE;")



def uninitializePlugin(obj):
   plugin = ompx.MFnPlugin(obj)
   try:
       plugin.deregisterNode(NODEID)
   except Exception as err:
       sys.stderr.write("Failed to deregister node: %s\n%s" % (NODENAME, err))