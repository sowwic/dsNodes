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
    inUpVector = om.MObject()
    inDistance = om.MObject()
    inBothWays = om.MObject()
    inOffset = om.MObject()
    outHitPoint = om.MObject()
    outNormal = om.MObject()
    outRotationX = om.MObject()
   
    def __init__(self):
        ompx.MPxNode.__init__(self)
       
    def compute(self, pPlug, pDataBlock):
       
        if pPlug == DsRaycast.outHitPoint:
            #Handles
            inMeshHandle = pDataBlock.inputValue(DsRaycast.inMesh)
            inSourceHandle = pDataBlock.inputValue(DsRaycast.inSource)
            inAimHandle = pDataBlock.inputValue(DsRaycast.inAim)
            inUpVectorHandle = pDataBlock.inputValue(DsRaycast.inUpVector)
            inDistanceHandle = pDataBlock.inputValue(DsRaycast.inDistance)
            inBothWaysHandle = pDataBlock.inputValue(DsRaycast.inBothWays)
            inOffsetHandle = pDataBlock.inputValue(DsRaycast.inOffset)
            outHitHandle = pDataBlock.outputValue(DsRaycast.outHitPoint)
            outNormalHandle = pDataBlock.outputValue(DsRaycast.outNormal)
            outRotationXHandle = pDataBlock.outputValue(DsRaycast.outRotationX)
            
            #Get data off handles
            fnMesh = om.MFnMesh(inMeshHandle.data())
            inSource = om.MFloatPoint(inSourceHandle.asFloatVector())
            inAim = om.MFloatVector(inAimHandle.asFloatVector())
            inUpVector = om.MVector(inUpVectorHandle.asVector())
            inDistance = inDistanceHandle.asFloat()
            inBothWays = inBothWaysHandle.asBool()
            inOffset = om.MFloatPoint(inOffsetHandle.asFloatVector())
            hitPoint = om.MFloatPoint()
            aimVector = om.MFloatVector(inAim.x - inSource.x, inAim.y - inSource.y, inAim.z - inSource.z) #get vector between source and aim points
            

            intersection = fnMesh.closestIntersection(inSource,
                                                      aimVector,
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
            
            #Apply offsets
            hitPoint.x += inOffset.x
            hitPoint.y += inOffset.y
            hitPoint.z += inOffset.z

            #---------Creating Rotation
            util = om.MScriptUtil()
            baseMatrix = om.MMatrix()
            crossVector = normalVector ^ inUpVector
            vectorArray = [  inUpVector.x, inUpVector.y, inUpVector.z, 0.0,
                             normalVector.x, normalVector.y, normalVector.z, 0.0,
                             crossVector.x, crossVector.y, crossVector.z, 0.0,
                             0.0, 0.0, 0.0, 0.0]

            util.createMatrixFromList(vectorArray, baseMatrix)
            transformMatrix = om.MTransformationMatrix(baseMatrix)
            eulerRot = transformMatrix.eulerRotation()
            
            eulerRotX = om.MAngle(eulerRot.x)
            eulerRotY = om.MAngle(eulerRot.y)
            eulerRotZ = om.MAngle(eulerRot.z)

            #Setting outputs to handles
            outHitHandle.setMFloatVector(om.MFloatVector(hitPoint))
            outNormalHandle.setMFloatVector(om.MFloatVector(normalVector))
            outRotationXHandle.setMAngle(eulerRotX)

            outHitHandle.setClean()
            outNormalHandle.setClean()
            outRotationXHandle.setClean()

        else:
            return om.kUnknownParameter
            
def nodeCreator():
   return ompx.asMPxPtr(DsRaycast())

def nodeInitializer():
   
    typedAttributeFn = om.MFnTypedAttribute()
    numericAttributeFn = om.MFnNumericAttribute()
    unitAttrFn = om.MFnUnitAttribute()
    
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

    #Up vector
    DsRaycast.inUpVector = numericAttributeFn.createPoint('upvector', 'up')
    DsRaycast.addAttribute(DsRaycast.inUpVector)

    #Cast distance
    DsRaycast.inDistance = numericAttributeFn.create('castDistance', 'dis', om.MFnNumericData.kFloat, 100)
    DsRaycast.addAttribute(DsRaycast.inDistance)

    #Test direction
    DsRaycast.inBothWays = numericAttributeFn.create('bothWays', 'bw', om.MFnNumericData.kBoolean, 1)
    DsRaycast.addAttribute(DsRaycast.inBothWays)

    #Cast Distance
    DsRaycast.inOffset = numericAttributeFn.createPoint('offset', 'offs')
    DsRaycast.addAttribute(DsRaycast.inOffset)


    ##OUT
    #Hitpoint
    DsRaycast.outHitPoint = numericAttributeFn.createPoint("hitPoint", "hit")
    numericAttributeFn.setWritable(0)

    DsRaycast.addAttribute( DsRaycast.outHitPoint )
    
    #Normal
    DsRaycast.outNormal = numericAttributeFn.createPoint('normal', 'n')
    DsRaycast.addAttribute(DsRaycast.outNormal)
    numericAttributeFn.setWritable(0)

    #Rotation
    DsRaycast.outRotationX = unitAttrFn.create('rotationX', 'rx', unitAttrFn.kAngle)
    DsRaycast.addAttribute(DsRaycast.outRotationX)
    
    #Affects
    DsRaycast.attributeAffects(DsRaycast.inMesh, DsRaycast.outHitPoint)
    DsRaycast.attributeAffects(DsRaycast.inSource, DsRaycast.outHitPoint)
    DsRaycast.attributeAffects(DsRaycast.inAim, DsRaycast.outHitPoint)
    DsRaycast.attributeAffects(DsRaycast.inOffset, DsRaycast.outHitPoint)

    DsRaycast.attributeAffects(DsRaycast.inMesh, DsRaycast.outNormal)
    DsRaycast.attributeAffects(DsRaycast.inSource, DsRaycast.outNormal)
    DsRaycast.attributeAffects(DsRaycast.inAim, DsRaycast.outNormal)

    DsRaycast.attributeAffects(DsRaycast.inMesh, DsRaycast.outRotationX)
    DsRaycast.attributeAffects(DsRaycast.inSource, DsRaycast.outRotationX)
    DsRaycast.attributeAffects(DsRaycast.inAim, DsRaycast.outRotationX)
    DsRaycast.attributeAffects(DsRaycast.inUpVector, DsRaycast.outRotationX)


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