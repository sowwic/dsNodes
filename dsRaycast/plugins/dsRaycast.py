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
    inOfsVectorEnum = om.MObject()
    outHitPoint = om.MObject()
    outNormal = om.MObject()
    outRotationX = om.MObject()
    outRotationY = om.MObject()
    outRotationZ = om.MObject()
    outRotation = om.MObject()
    outHitDistance = om.MObject()
    
    def __init__(self):
        ompx.MPxNode.__init__(self)


    def compute(self, pPlug, pDataBlock):
        plugsToEval = [DsRaycast.outHitPoint, DsRaycast.outNormal, DsRaycast.outRotation, DsRaycast.outHitDistance]

        if pPlug in plugsToEval:
            #Handles
            inMeshHandle = pDataBlock.inputValue(DsRaycast.inMesh)
            inSourceHandle = pDataBlock.inputValue(DsRaycast.inSource)
            inAimHandle = pDataBlock.inputValue(DsRaycast.inAim)
            inUpVectorHandle = pDataBlock.inputValue(DsRaycast.inUpVector)
            inDistanceHandle = pDataBlock.inputValue(DsRaycast.inDistance)
            inBothWaysHandle = pDataBlock.inputValue(DsRaycast.inBothWays)
            inOffsetHandle = pDataBlock.inputValue(DsRaycast.inOffset)
            inOfsVectorEnumHandle = pDataBlock.inputValue(DsRaycast.inOfsVectorEnum)
            outHitHandle = pDataBlock.outputValue(DsRaycast.outHitPoint)
            outNormalHandle = pDataBlock.outputValue(DsRaycast.outNormal)
            outRotationXHandle = pDataBlock.outputValue(DsRaycast.outRotationX)
            outRotationYHandle = pDataBlock.outputValue(DsRaycast.outRotationY)
            outRotationZHandle = pDataBlock.outputValue(DsRaycast.outRotationZ)
            outHitDistanceHandle = pDataBlock.outputValue(DsRaycast.outHitDistance)

            
            #Get data off handles
            fnMesh = om.MFnMesh(inMeshHandle.data())
            inSource = om.MFloatPoint(inSourceHandle.asFloatVector())
            inAim = om.MFloatVector(inAimHandle.asFloatVector())
            inUpVector = om.MVector(inUpVectorHandle.asVector())
            inDistance = inDistanceHandle.asFloat()
            inBothWays = inBothWaysHandle.asBool()
            inOffset = inOffsetHandle.asFloat()
            inOfsVectorEnum = inOfsVectorEnumHandle.asBool()
            hitPoint = om.MFloatPoint()
            aimVector = om.MFloatVector(inAim.x - inSource.x, inAim.y - inSource.y, inAim.z - inSource.z).normal() #get vector between source and aim points

            util = om.MScriptUtil()
            util.createFromDouble(0)
            hitRayParamPtr = util.asFloatPtr()

            intersection = fnMesh.closestIntersection(inSource,
                                                      aimVector,
                                                      None,
                                                      None,
                                                      False,
                                                      om.MSpace.kWorld,
                                                      inDistance,
                                                      inBothWays,
                                                      None,
                                                      hitPoint,
                                                      hitRayParamPtr, 
                                                      None,
                                                      None,
                                                      None,
                                                      None
                                                        )
            #Getting normal
            normalVector = om.MVector()
            mHitPoint = om.MPoint(hitPoint)
            fnMesh.getClosestNormal(mHitPoint, normalVector, om.MSpace.kWorld)

            hitRayParam = om.MScriptUtil.getFloat(hitRayParamPtr)
            
            #Apply offsets
            if inOfsVectorEnum:
                fNormalVector = om.MFloatVector(normalVector)
                offsetPoint = om.MFloatPoint(inOffset * fNormalVector.x, inOffset * fNormalVector.y, inOffset * fNormalVector.z)

            else:
                offsetPoint = om.MFloatPoint(inOffset * aimVector.x, inOffset * aimVector.y, inOffset * aimVector.z)

            hitPoint.x += offsetPoint.x
            hitPoint.y += offsetPoint.y
            hitPoint.z += offsetPoint.z

            #---------Creating Rotation
            util = om.MScriptUtil()
            baseMatrix = om.MMatrix()
            crossVector = normalVector ^ inUpVector
            inUpVector = normalVector ^ crossVector
            vectorArray = [  normalVector.x, normalVector.y, normalVector.z, 0.0,
                             inUpVector.x, inUpVector.y, inUpVector.z, 0.0,
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
            outRotationYHandle.setMAngle(eulerRotY)
            outRotationZHandle.setMAngle(eulerRotZ)
            outHitDistanceHandle.setFloat(hitRayParam)

            outHitHandle.setClean()
            outNormalHandle.setClean()
            outRotationXHandle.setClean()
            outRotationYHandle.setClean()
            outRotationZHandle.setClean()
            outHitDistanceHandle.setClean()

        else:
            return om.kUnknownParameter
            
def nodeCreator():
   return ompx.asMPxPtr(DsRaycast())

def nodeInitializer():
   
    typedAttributeFn = om.MFnTypedAttribute()
    numericAttributeFn = om.MFnNumericAttribute()
    unitAttrFn = om.MFnUnitAttribute()
    enumAttrFn = om.MFnEnumAttribute()
    
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
    DsRaycast.inUpVector = numericAttributeFn.createPoint('upVector', 'up')
    DsRaycast.addAttribute(DsRaycast.inUpVector)

    #Cast distance
    DsRaycast.inDistance = numericAttributeFn.create('castDistance', 'dis', om.MFnNumericData.kFloat, 100)
    DsRaycast.addAttribute(DsRaycast.inDistance)

    #Test direction
    DsRaycast.inBothWays = numericAttributeFn.create('bothWays', 'bw', om.MFnNumericData.kBoolean, 1)
    DsRaycast.addAttribute(DsRaycast.inBothWays)

    #Offset
    DsRaycast.inOffset = numericAttributeFn.create('offset', 'offs', om.MFnNumericData.kFloat, 0)
    DsRaycast.addAttribute(DsRaycast.inOffset)

    #Offset vector enum switch
    DsRaycast.inOfsVectorEnum = enumAttrFn.create('offsetVector', 'offsv', 0)
    enumAttrFn.addField('Aim', 0)
    enumAttrFn.addField('Normal', 1)
    DsRaycast.addAttribute(DsRaycast.inOfsVectorEnum)

    ##OUT
    #Hitpoint
    DsRaycast.outHitPoint = numericAttributeFn.createPoint("hitPoint", "hit")
    numericAttributeFn.setWritable(0)
    DsRaycast.addAttribute( DsRaycast.outHitPoint )
    
    #Normal
    DsRaycast.outNormal = numericAttributeFn.createPoint('normal', 'n')
    numericAttributeFn.setWritable(0)
    DsRaycast.addAttribute(DsRaycast.outNormal)
    
    #Rotation
    DsRaycast.outRotationX = unitAttrFn.create('rotateX', 'rx', om.MFnUnitAttribute.kAngle)
    DsRaycast.outRotationY = unitAttrFn.create('rotateY', 'ry', om.MFnUnitAttribute.kAngle)
    DsRaycast.outRotationZ = unitAttrFn.create('rotateZ', 'rz', om.MFnUnitAttribute.kAngle)
    DsRaycast.outRotation = numericAttributeFn.create('rotate', 'rs', DsRaycast.outRotationX, DsRaycast.outRotationY, DsRaycast.outRotationZ)
    DsRaycast.addAttribute(DsRaycast.outRotation)

    #Hit Distance
    DsRaycast.outHitDistance = numericAttributeFn.create('hitDistance', 'hd', om.MFnNumericData.kFloat)
    numericAttributeFn.setWritable(0)
    DsRaycast.addAttribute(DsRaycast.outHitDistance)
 
    

    #Affects
    DsRaycast.attributeAffects(DsRaycast.inMesh, DsRaycast.outHitPoint)
    DsRaycast.attributeAffects(DsRaycast.inSource, DsRaycast.outHitPoint)
    DsRaycast.attributeAffects(DsRaycast.inAim, DsRaycast.outHitPoint)
    DsRaycast.attributeAffects(DsRaycast.inOffset, DsRaycast.outHitPoint)

    DsRaycast.attributeAffects(DsRaycast.inMesh, DsRaycast.outNormal)
    DsRaycast.attributeAffects(DsRaycast.inSource, DsRaycast.outNormal)
    DsRaycast.attributeAffects(DsRaycast.inAim, DsRaycast.outNormal)

    DsRaycast.attributeAffects(DsRaycast.inMesh, DsRaycast.outRotation)
    DsRaycast.attributeAffects(DsRaycast.inSource, DsRaycast.outRotation)
    DsRaycast.attributeAffects(DsRaycast.inAim, DsRaycast.outRotation)
    DsRaycast.attributeAffects(DsRaycast.inUpVector, DsRaycast.outRotation)

    DsRaycast.attributeAffects(DsRaycast.inMesh, DsRaycast.outHitDistance)
    DsRaycast.attributeAffects(DsRaycast.inSource, DsRaycast.outHitDistance)
    DsRaycast.attributeAffects(DsRaycast.inAim, DsRaycast.outHitDistance)
    DsRaycast.attributeAffects(DsRaycast.inUpVector, DsRaycast.outHitDistance)


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