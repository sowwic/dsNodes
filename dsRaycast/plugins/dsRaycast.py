from maya import cmds as mc, OpenMaya as om, OpenMayaMPx as ompx, mel
import getpass, os, sys

MAYA_APP_DIR = mel.eval('getenv ("MAYA_APP_DIR")')
NAME = "dsRaycast"
VERSION = "1.0"
MAYAVERSION = "2018"
NODENAME = "dsRaycast"
NODEID = om.MTypeId(0x09833)

class DsRaycast(ompx.MPxNode):
   
    inMesh = om.MObject()
    inMode = om.MObject()
    inSourceMatrix = om.MObject()
    inAim = om.MObject()
    inAimAxis = om.MObject()
    inUpVector = om.MObject()
    inDistance = om.MObject()
    inBothWays = om.MObject()
    inOffset = om.MObject()
    inOfsVectorEnum = om.MObject()
    outHitPoint = om.MObject()
    outNormal = om.MObject()
    inDebug = om.MObject()
    outRotationX = om.MObject()
    outRotationY = om.MObject()
    outRotationZ = om.MObject()
    outRotation = om.MObject()
    outHitDistance = om.MObject()
    outSourcePt = om.MObject()

    

    def __init__(self):
        ompx.MPxNode.__init__(self)

    @staticmethod
    def rayCallback(*args):
        callbackType, callbackPlug, _, thisNode = args
        dependNode = om.MFnDependencyNode(thisNode.thisMObject())
        debugPlug = dependNode.findPlug("debugRay", False)

        if callbackPlug != debugPlug:
            return

        if debugPlug.asBool():
            dgMod = om.MDagModifier()
            drawVector = dgMod.createNode("drawVector")
            dgMod.doIt()

            sourcePlug = dependNode.findPlug("sourcePoint", False)
            aimPlug = dependNode.findPlug("hitPoint", False)
            messagePlug = dependNode.findPlug('message', False)

            drawVectorTrnDag = om.MFnDagNode(drawVector)
            drawVectorTrnDag.setLocked(True)
            drawVectorDepend = om.MFnDependencyNode(drawVectorTrnDag.child(0))
            sourceDestPlug = drawVectorDepend.findPlug("sourcePoint", False)
            aimDestPlug = drawVectorDepend.findPlug("aimPoint", False)
            messageDestPlug = drawVectorDepend.findPlug("drawMessage", False)

            dgMod = om.MDGModifier()
            dgMod.connect(sourcePlug, sourceDestPlug)
            dgMod.connect(aimPlug, aimDestPlug)
            dgMod.connect(messagePlug, messageDestPlug)
            dgMod.doIt()

        else:
            #Delete draw vector node connected through message
            sourcePlug = dependNode.findPlug("message", False)
            plugArray = om.MPlugArray()
            sourcePlug.connectedTo(plugArray, False, True)
            drawVectorTrn =  om.MFnDagNode(plugArray[0].node()).parent(0)
            drawVectorTrnDag = om.MFnDagNode(drawVectorTrn)
            drawVectorTrnDag.setLocked(0)

            dgMod = om.MDagModifier()
            dgMod.deleteNode(drawVectorTrn)
            dgMod.doIt()
            


    def postConstructor(self):
        node = self.thisMObject()
        om.MNodeMessage.addAttributeChangedCallback(node, self.rayCallback, self)

    def compute(self, pPlug, pDataBlock):
        plugsToEval = [DsRaycast.outHitPoint, DsRaycast.outNormal, DsRaycast.outRotation, DsRaycast.outHitDistance]


        if pPlug in plugsToEval:
            #Handles
            inMeshHandle = pDataBlock.inputValue(DsRaycast.inMesh)  #Target mesh
            inModeHandle = pDataBlock.inputValue(DsRaycast.inMode)
            inSourceMatrixHandle = pDataBlock.inputValue(DsRaycast.inSourceMatrix)  
            inAimHandle = pDataBlock.inputValue(DsRaycast.inAim)
            inAimAxisHandle = pDataBlock.inputValue(DsRaycast.inAimAxis)
            inUpVectorHandle = pDataBlock.inputValue(DsRaycast.inUpVector)
            inDistanceHandle = pDataBlock.inputValue(DsRaycast.inDistance)
            inBothWaysHandle = pDataBlock.inputValue(DsRaycast.inBothWays)
            inOffsetHandle = pDataBlock.inputValue(DsRaycast.inOffset)
            inOfsVectorEnumHandle = pDataBlock.inputValue(DsRaycast.inOfsVectorEnum)
            inDebugHandle = pDataBlock.inputValue(DsRaycast.inDebug)
            outHitHandle = pDataBlock.outputValue(DsRaycast.outHitPoint)
            outNormalHandle = pDataBlock.outputValue(DsRaycast.outNormal)
            outRotationXHandle = pDataBlock.outputValue(DsRaycast.outRotationX)
            outRotationYHandle = pDataBlock.outputValue(DsRaycast.outRotationY)
            outRotationZHandle = pDataBlock.outputValue(DsRaycast.outRotationZ)
            outHitDistanceHandle = pDataBlock.outputValue(DsRaycast.outHitDistance)
            outSourcePtHandle = pDataBlock.outputValue(DsRaycast.outSourcePt)
            

            #Get data off handles
            inDebug = inDebugHandle.asBool()
            fnMesh = om.MFnMesh(inMeshHandle.data())
            inAim = om.MFloatVector(inAimHandle.asFloatVector())
            inUpVector = om.MVector(inUpVectorHandle.asVector())
            inDistance = inDistanceHandle.asFloat()
            inBothWays = inBothWaysHandle.asBool()
            inMode = inModeHandle.asShort()
            inOffset = inOffsetHandle.asFloat()
            inOfsVectorEnum = inOfsVectorEnumHandle.asBool()
            hitPoint = om.MFloatPoint()
            inSourceMatrix = om.MMatrix(inSourceMatrixHandle.asMatrix())
            inAimAxis = inAimAxisHandle.asShort()

            #Getting axis vectors from source matrix
            sourceAxisX = [inSourceMatrix(0, 0), inSourceMatrix(0, 1), inSourceMatrix(0, 2)]
            sourceAxisY = [inSourceMatrix(1, 0), inSourceMatrix(1, 1), inSourceMatrix(1, 2)]
            sourceAxisZ = [inSourceMatrix(2, 0), inSourceMatrix(2, 1), inSourceMatrix(2, 2)]
            
            #Getting source point from matrix
            sourceTranslate = [inSourceMatrix(3, 0), inSourceMatrix(3, 1), inSourceMatrix(3, 2)]
            sourcePoint = om.MFloatPoint(sourceTranslate[0], sourceTranslate[1], sourceTranslate[2])

            #Getting aim vector
            if inMode == 0:
                aimVector = om.MFloatVector(inAim.x - sourceTranslate[0], inAim.y - sourceTranslate[1], inAim.z - sourceTranslate[2]) # Get relative vector
            
            elif inMode == 1:
                if inAimAxis == 0:
                    aimVector = om.MFloatVector(sourceAxisX[0], sourceAxisX[1], sourceAxisX[2])
                elif inAimAxis == 1:
                    aimVector = om.MFloatVector(sourceAxisY[0], sourceAxisY[1], sourceAxisY[2])
                elif inAimAxis == 2:
                    aimVector = om.MFloatVector(sourceAxisZ[0], sourceAxisZ[1], sourceAxisZ[2])

            util = om.MScriptUtil()
            util.createFromDouble(0)
            hitRayParamPtr = util.asFloatPtr()

            intersection = fnMesh.closestIntersection(sourcePoint,
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
            outSourcePtHandle.setMFloatVector(om.MFloatVector(sourcePoint))

            outHitHandle.setClean()
            outNormalHandle.setClean()
            outRotationXHandle.setClean()
            outRotationYHandle.setClean()
            outRotationZHandle.setClean()
            outHitDistanceHandle.setClean()
            outSourcePtHandle.setClean()

        else:
            return om.kUnknownParameter
            
def nodeCreator():
   return ompx.asMPxPtr(DsRaycast())

def nodeInitializer():
   
    typedAttributeFn = om.MFnTypedAttribute()
    numericAttributeFn = om.MFnNumericAttribute()
    unitAttrFn = om.MFnUnitAttribute()
    enumAttrFn = om.MFnEnumAttribute()
    matrixAttrFn = om.MFnMatrixAttribute()
    
    ##IN
    #Debug
    DsRaycast.inDebug = numericAttributeFn.create('debugRay', 'dbug', om.MFnNumericData.kBoolean, 0)
    DsRaycast.addAttribute(DsRaycast.inDebug)

    #Mesh
    DsRaycast.inMesh = typedAttributeFn.create('targetMesh','tm', om.MFnData.kMesh)
    DsRaycast.addAttribute(DsRaycast.inMesh)
    typedAttributeFn.setReadable(0)

    #Mode
    DsRaycast.inMode = enumAttrFn.create('mode', 'm', 0)
    enumAttrFn.addField('Between two', 0)
    enumAttrFn.addField('From single', 1)
    DsRaycast.addAttribute(DsRaycast.inMode)

    #Aim Axis
    DsRaycast.inAimAxis = enumAttrFn.create('aimAxis', 'axis', 0)
    enumAttrFn.addField('X', 0)
    enumAttrFn.addField('Y', 1)
    enumAttrFn.addField('Z', 2)
    DsRaycast.addAttribute(DsRaycast.inAimAxis)

    #Source Matrix
    DsRaycast.inSourceMatrix = matrixAttrFn.create('sourceMatrix', 'srs')
    DsRaycast.addAttribute(DsRaycast.inSourceMatrix)

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

    #SourcePt
    DsRaycast.outSourcePt = numericAttributeFn.createPoint('sourcePoint', 'sp')
    numericAttributeFn.setWritable(0)
    DsRaycast.addAttribute(DsRaycast.outSourcePt)


    #Affects
    DsRaycast.attributeAffects(DsRaycast.inMesh, DsRaycast.outHitPoint)
    DsRaycast.attributeAffects(DsRaycast.inAim, DsRaycast.outHitPoint)
    DsRaycast.attributeAffects(DsRaycast.inAimAxis, DsRaycast.outHitPoint)
    DsRaycast.attributeAffects(DsRaycast.inOffset, DsRaycast.outHitPoint)
    DsRaycast.attributeAffects(DsRaycast.inOfsVectorEnum, DsRaycast.outHitPoint)
    DsRaycast.attributeAffects(DsRaycast.inSourceMatrix, DsRaycast.outHitPoint)
    DsRaycast.attributeAffects(DsRaycast.inMode, DsRaycast.outHitPoint)

    DsRaycast.attributeAffects(DsRaycast.inMesh, DsRaycast.outNormal)
    DsRaycast.attributeAffects(DsRaycast.inSourceMatrix, DsRaycast.outNormal)
    DsRaycast.attributeAffects(DsRaycast.inAimAxis, DsRaycast.outNormal)
    DsRaycast.attributeAffects(DsRaycast.inAim, DsRaycast.outNormal)
    DsRaycast.attributeAffects(DsRaycast.inMode, DsRaycast.outNormal)
    DsRaycast.attributeAffects(DsRaycast.inAimAxis, DsRaycast.outNormal)

    DsRaycast.attributeAffects(DsRaycast.inMesh, DsRaycast.outRotation)
    DsRaycast.attributeAffects(DsRaycast.inSourceMatrix, DsRaycast.outRotation)
    DsRaycast.attributeAffects(DsRaycast.inAim, DsRaycast.outRotation)
    DsRaycast.attributeAffects(DsRaycast.inUpVector, DsRaycast.outRotation)
    DsRaycast.attributeAffects(DsRaycast.inMode, DsRaycast.outRotation)
    DsRaycast.attributeAffects(DsRaycast.inAimAxis, DsRaycast.outRotation)

    DsRaycast.attributeAffects(DsRaycast.inMesh, DsRaycast.outHitDistance)
    DsRaycast.attributeAffects(DsRaycast.inSourceMatrix, DsRaycast.outHitDistance)
    DsRaycast.attributeAffects(DsRaycast.inAim, DsRaycast.outHitDistance)
    DsRaycast.attributeAffects(DsRaycast.inOffset, DsRaycast.outHitDistance)
    DsRaycast.attributeAffects(DsRaycast.inUpVector, DsRaycast.outHitDistance)
    DsRaycast.attributeAffects(DsRaycast.inMode, DsRaycast.outHitDistance)
    DsRaycast.attributeAffects(DsRaycast.inAimAxis, DsRaycast.outHitDistance)

    DsRaycast.attributeAffects(DsRaycast.inSourceMatrix, DsRaycast.outSourcePt)
    DsRaycast.attributeAffects(DsRaycast.inOffset, DsRaycast.outSourcePt)


def initializePlugin(obj):
   plugin = ompx.MFnPlugin(obj, NAME, VERSION, MAYAVERSION)
   try:
       plugin.registerNode(NODENAME, NODEID, nodeCreator, nodeInitializer)
   except RuntimeError:
       sys.stderr.write("Failed to register node: %s" % NODENAME)

aeTemplate = open(os.path.join(MAYA_APP_DIR, 'scripts\dsNodes\dsRaycast\plugins\AEtemplate.mel'), "r").read()
mel.eval(aeTemplate)
mel.eval("refreshEditorTemplates; refreshAE;")



def uninitializePlugin(obj):
   plugin = ompx.MFnPlugin(obj)
   try:
       plugin.deregisterNode(NODEID)
   except Exception as err:
       sys.stderr.write("Failed to deregister node: %s\n%s" % (NODENAME, err))