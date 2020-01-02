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
        thisNode = self.thisMObject()

        ## GET DATA
        envelope = pDataBlock.inputValue(self.envelope).asFloat()
        if envelope == 0:
            return

        suspendWarnings = pDataBlock.inputValue(self.aWarnings).asBool()
        
        maxDistanceUv = om.MRampAttribute(thisNode, self.aMaxDistanceUV)
        falloff = om.MRampAttribute(thisNode, self.aFalloff)
        
        projectOnNormal = pDataBlock.inputValue( self.aProjectOnNormal).asFloat()
        if( projectOnNormal ):
            # aNormalDirectionLimit
            normalDirectionLimit = pDataBlock.inputValue( self.aNormalDirectionLimit ).asShort()
            # inputGeom
            hInput = pDataBlock.outputArrayValue( self.input )
            hInput.jumpToElement( multiIndex )
            hInputGeom = hInput.outputValue().child( self.inputGeom )
            oInputGeom = hInputGeom.asMesh()
            mfInputGeom = om.MFnMesh( oInputGeom )

        maxDistance =  pDataBlock.inputValue(self.maxDistance).asFloat()
        if maxDistance == 0:
            return

        inputMatrix = pDataBlock.inputValue(self.aInputMatrix).asMatrix()
        plugInputMatrix = om.MPlug(thisNode, self.aInputMatrix)
        if not plugInputMatrix.isConnected():
            if not suspendWarnings:
                self.warning(thisNode, "Missing incoming connection to InputMatrix")
            return
 

        dhInputShape = pDataBlock.inputValue(self.inputShape)
        dagNodeFn = self.getConnectedDagNode(self.inputShape)
        if not dagNodeFn:
            if not suspendWarnings:
                self.warning(thisNode, "Missing incoming connection to InputShape")
            return

        ##GET INPUT SHAPE TYPE
        inputShapeType = None 
        targetFn = None
        if dhInputShape.type() == om.MFnNurbsCurveData.kNurbsCurve:
            inputShapeType = "curve"
            targetFn = om.MFnNurbsCurve(dagNodeFn)
        elif dhInputShape.type() == om.MFnNurbsCurveData.kNurbsSurface:
            inputShapeType = "nurbs"
            targetFn = om.MFnNurbsSurface(dagNodeFn)

        ## LOOP VARIABLES
        d_util = om.MScriptUtil()
        d_util.createFromDouble(0.0)
        d_ptr = d_util.asDoublePtr()

        f_util = om.MScriptUtil()
        f_util.createFromDouble(0.0)
        f_ptr = f_util.asFloatPtr()

        f2_util = om.MScriptUtil()
        f2_util.createFromList([0.0, 0.0], 2)
        f2_util = f2_util.asFloat2Ptr()

        loopPoint = om.MPoint()
        loopVec = om.MVector()

        matrixInverse = worldMatrix.inverse()
        paAllpoints = om.MPointArray()
        geoIter.allPositions(paAllpoints)

        ## DEFORM
        count = 0
        while not geoIter.isDone():
            iterIndex = geoIter.index()
            #current point
            pt = geoIter.position()
            #get painted weight
            wPt = self.weightValue(pDataBlock, multiIndex, iterIndex)
            if (wPt == 0.0):
                count+=1
                geoIter.next()
                continue
            #set point to world space
            pt *= worldMatrix

            ## GET CLOSEST POINT
            closePt = None
            dUvalue = None
            if inputShapeType == "curve":
                closePt = targetFn.closestPoint(pt, d_ptr, 0.00001, om.MSpace.kWorld)
                dUvalue = om.MScriptUtil.getDouble(d_ptr)
            elif inputShapeType == "nurbs":
                closePt = targetFn.closestPoint(pt, d_ptr, None, False, 0.00001, om.MSpace.kWorld)
                dUvalue = om.MScriptUtil.getDouble(d_ptr)

            #Make it a local vector for the vertex
            vecMove = closePt - pt
            #Adjust max distance 
            maxDistanceUv.getValueAtPosition(dUvalue, f_ptr)
            maxDistLocal = maxDistance * om.MScriptUtil.getFloat(f_ptr)
            #Check if vertex is in range
            if vecMove.length() < maxDistLocal:
                #Adjust with falloff
                dPercent = vecMove.length() / maxDistLocal
                falloff.getValueAtPosition(float(1.0 - dPercent), f_ptr)
                valueFalloff = om.MScriptUtil.getFloat(f_ptr)
                vecMove *= valueFalloff
                #Adjust with vertex normal
                if projectOnNormal:
                    mfInputGeom.getVertexNormal(iterIndex, loopVec, om.MSpace.kWorld)
                    #normalize
                    loopVec.normalize()
                    #project move vector on normal
                    dVecDotProduct = vecMove * loopVec
                    loopVec *=dVecDotProduct
                    if normalDirectionLimit == 1 and dVecDotProduct <= 0:
                        #only positive
                        loopVec *=0
                    elif normalDirectionLimit == 2 and dVecDotProduct >0:
                        #only negative
                        loopVec *= 0
                    #blend
                    vecMove = vecMove * (1-projectOnNormal) + loopVec*projectOnNormal

                #Adjust with envelope and painted value
                vecMove *= envelope * wPt
                pt += vecMove
                #back to object space
                pt *= matrixInverse
                #save point positions
                paAllpoints.set(pt, count)
            
            count+=1
            geoIter.next()

        geoIter.setAllPositions(paAllpoints)
    





    def getConnectedDagNode( self, attrArg ):
        plugArg = om.MPlug( self.thisMObject(), attrArg )
        dagPath = om.MDagPath()
        if( plugArg.isConnected() ):
            plugArr = om.MPlugArray()
            plugArg.connectedTo( plugArr, True, False )
            plugDag = om.MPlug( plugArr[0] )
            oDagNode = plugDag.node()
            fnDagNode = om.MFnDagNode( oDagNode )
            fnDagNode.getPath( dagPath )
            return dagPath
        else:
            return None

    def warning(self, thisNode_arg, msg_arg ):
        fnThis = om.MFnDependencyNode( thisNode_arg )
        nameThis = fnThis.name()
        om.MGlobal.displayWarning("{0}: {1}".format(nameThis, msg_arg))


    def accessoryNodeSetup(self, cmd):
        thisNode = self.thisMObject()
        # aFalloff
        hFalloff = om.MRampAttribute( thisNode, self.aFalloff)
        
        a1 = om.MFloatArray()# positions
        b1 = om.MFloatArray()# values
        c1 = om.MIntArray()# interpolations
        
        a1.append(float(0.0))
        a1.append(float(1.0))
        
        b1.append(float(0.0))
        b1.append(float(1.0))
        
        c1.append(om.MRampAttribute.kSmooth)
        c1.append(om.MRampAttribute.kSmooth)
        
        hFalloff.addEntries(a1,b1,c1)
        
        # aMaxDistanceUv
        hMaxDistUv = om.MRampAttribute( thisNode, self.aMaxDistanceUV)
        
        as1 = om.MFloatArray()# positions
        bs1 = om.MFloatArray()# values
        cs1 = om.MIntArray()# interpolations
        
        as1.append(float(0.5))
        bs1.append(float(1.0))
        cs1.append(om.MRampAttribute.kSmooth)
        
        hMaxDistUv.addEntries(as1,bs1,cs1)




    @classmethod
    def creator(cls):
        return DsAttractDeformer()

    @classmethod
    def initialize(cls):
        numericFn = om.MFnNumericAttribute()
        genericFn = om.MFnGenericAttribute()
        matrixFn = om.MFnMatrixAttribute()
        rampFn = om.MRampAttribute()
        enumFn = om.MFnEnumAttribute()

        cls.maxDistance = numericFn.create("maximumDistance", "maxDist", om.MFnNumericData.kFloat, 1.0)
        numericFn.setKeyable(True)
        numericFn.setMin(0.0)
        numericFn.setMax(6.0)

        cls.aProjectOnNormal = numericFn.create("projectOnNormal", "projectOnNormal", om.MFnNumericData.kFloat, 0.0)
        numericFn.setKeyable(True)
        numericFn.setMin(0.0)
        numericFn.setMax(1.0)

        cls.aWarnings = numericFn.create("suspendWarnings", "suspendWarnings", om.MFnNumericData.kBoolean, 0)
        numericFn.setChannelBox(True)

        cls.inputShape = genericFn.create("inputShape", "inputShape")
        genericFn.setReadable(False)
        genericFn.addDataAccept(om.MFnNurbsCurveData.kNurbsCurve)
        genericFn.addDataAccept(om.MFnNurbsCurveData.kNurbsSurface)

        cls.aInputMatrix = matrixFn.create("inputMatrix", "inputMatrix")
        matrixFn.setReadable(False)

        cls.aMaxDistanceUV = rampFn.createCurveRamp("maxDistanceUv", "maxDistanceUv")
        cls.aFalloff = rampFn.createCurveRamp("falloff", "falloff")

        cls.aNormalDirectionLimit = enumFn.create("normalDirectionLimit", "normalDirectionLimit", 0)
        enumFn.setKeyable(True)
        enumFn.addField("off", 0)
        enumFn.addField("Only positive", 1)
        enumFn.addField("Only negative", 2)


        cls.addAttribute(cls.maxDistance)
        cls.addAttribute(cls.inputShape)
        cls.addAttribute(cls.aInputMatrix)
        cls.addAttribute(cls.aMaxDistanceUV)
        cls.addAttribute(cls.aFalloff)
        cls.addAttribute(cls.aProjectOnNormal)
        cls.addAttribute(cls.aWarnings)
        cls.addAttribute(cls.aNormalDirectionLimit)

        outputGeom = ommpx.cvar.MPxGeometryFilter_outputGeom
        cls.attributeAffects(cls.maxDistance, outputGeom)
        cls.attributeAffects(cls.inputShape, outputGeom)
        cls.attributeAffects(cls.aInputMatrix, outputGeom)
        cls.attributeAffects(cls.aMaxDistanceUV, outputGeom)
        cls.attributeAffects(cls.aFalloff, outputGeom)
        cls.attributeAffects(cls.aProjectOnNormal, outputGeom)
        cls.attributeAffects(cls.aNormalDirectionLimit, outputGeom)


    
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

aeTemplate = open(os.path.join(mel.eval('getenv ("MAYA_APP_DIR")'), 'scripts\dsNodes\dsAttractDeformer\plugins\AEtemplate.mel'), "r").read()
mel.eval(aeTemplate)
mel.eval("refreshEditorTemplates; refreshAE;")


def uninitializePlugin(obj):
    plugin = ommpx.MFnPlugin(obj)
    try:
        plugin.deregisterNode(DsAttractDeformer.NODEID)
    except Exception as err:
        sys.stderr.write('Failed to deregister node: {0}{1}'.format((DsAttractDeformer.NODENAME, err)))