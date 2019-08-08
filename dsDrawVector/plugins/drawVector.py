import sys
import maya.api.OpenMaya as om
import maya.api.OpenMayaUI as omui
import maya.api.OpenMayaAnim as oma
import maya.api.OpenMayaRender as omr

def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass

def matrixAsArray(matrix):
    array = []
    for i in range(16):
        array.append(matrix[i])
    return array

## Foot Data
##
sole = [ [  0.00, 0.0, -0.70 ],
                 [  0.04, 0.0, -0.69 ],
                 [  0.09, 0.0, -0.65 ],
                 [  0.13, 0.0, -0.61 ],
                 [  0.16, 0.0, -0.54 ],
                 [  0.17, 0.0, -0.46 ],
                 [  0.17, 0.0, -0.35 ],
                 [  0.16, 0.0, -0.25 ],
                 [  0.15, 0.0, -0.14 ],
                 [  0.13, 0.0,  0.00 ],
                 [  0.00, 0.0,  0.00 ],
                 [ -0.13, 0.0,  0.00 ],
                 [ -0.15, 0.0, -0.14 ],
                 [ -0.16, 0.0, -0.25 ],
                 [ -0.17, 0.0, -0.35 ],
                 [ -0.17, 0.0, -0.46 ],
                 [ -0.16, 0.0, -0.54 ],
                 [ -0.13, 0.0, -0.61 ],
                 [ -0.09, 0.0, -0.65 ],
                 [ -0.04, 0.0, -0.69 ],
                 [ -0.00, 0.0, -0.70 ] ]
heel = [ [  0.00, 0.0,  0.06 ],
                 [  0.13, 0.0,  0.06 ],
                 [  0.14, 0.0,  0.15 ],
                 [  0.14, 0.0,  0.21 ],
                 [  0.13, 0.0,  0.25 ],
                 [  0.11, 0.0,  0.28 ],
                 [  0.09, 0.0,  0.29 ],
                 [  0.04, 0.0,  0.30 ],
                 [  0.00, 0.0,  0.30 ],
                 [ -0.04, 0.0,  0.30 ],
                 [ -0.09, 0.0,  0.29 ],
                 [ -0.11, 0.0,  0.28 ],
                 [ -0.13, 0.0,  0.25 ],
                 [ -0.14, 0.0,  0.21 ],
                 [ -0.14, 0.0,  0.15 ],
                 [ -0.13, 0.0,  0.06 ],
                 [ -0.00, 0.0,  0.06 ] ]
soleCount = 21
heelCount = 17

class footPrint(omui.MPxLocatorNode):
    id = om.MTypeId( 0x80408 )
    drawDbClassification = "drawdb/geometry/footPrint"
    drawRegistrantId = "FootprintNodePlugin"

    size = None## The size of the foot

    sourcePt = om.MObject()
    aimPt = om.MObject()
    vector = om.MObject()
    distance = om.MObject()
    drawMode = om.MObject()

    @staticmethod
    def creator():
        return footPrint()

    @staticmethod
    def initialize():
        unitFn = om.MFnUnitAttribute()
        numericFn = om.MFnNumericAttribute()
        enumFn = om.MFnEnumAttribute()

        footPrint.size = unitFn.create( "size", "sz", om.MFnUnitAttribute.kDistance )
        unitFn.default = om.MDistance(1.0)
        
        ######VECTOR
        footPrint.drawMode = enumFn.create('drawingMode', 'drm', 0)
        enumFn.addField('Between two', 0)
        enumFn.addField('From single', 1)
        footPrint.sourcePt = numericFn.createPoint('sourcePoint', 'sp')
        footPrint.aimPt = numericFn.createPoint('aimPoint', 'ap')

        om.MPxNode.addAttribute( footPrint.size )
        ######VECTOR
        om.MPxNode.addAttribute( footPrint.drawMode )
        om.MPxNode.addAttribute( footPrint.sourcePt )
        om.MPxNode.addAttribute( footPrint.aimPt)

    def __init__(self):
        omui.MPxLocatorNode.__init__(self)

    def compute(self, plug, data):
        return None

#############################################################################
##
## Viewport 2.0 override implementation
##
#############################################################################
class footPrintData(om.MUserData):
    def __init__(self):
        om.MUserData.__init__(self, False) ## don't delete after draw

        self.fColor = om.MColor()
        self.fSoleLineList = om.MPointArray()
        self.fSoleTriangleList = om.MPointArray()
        self.fHeelLineList = om.MPointArray()
        self.fHeelTriangleList = om.MPointArray()

        ######VECTOR
        self.fsourcePt = om.MPoint()
        self.faimPt = om.MPoint()

class footPrintDrawOverride(omr.MPxDrawOverride):
    @staticmethod
    def creator(obj):
        return footPrintDrawOverride(obj)

    @staticmethod
    def draw(context, data):
        return

    def __init__(self, obj):
        omr.MPxDrawOverride.__init__(self, obj, footPrintDrawOverride.draw)

        ## We want to perform custom bounding box drawing
        ## so return True so that the internal rendering code
        ## will not draw it for us.
        self.mCustomBoxDraw = True
        self.mCurrentBoundingBox = om.MBoundingBox()
        
    def supportedDrawAPIs(self):
    ## this plugin supports both GL and DX
        return omr.MRenderer.kOpenGL | omr.MRenderer.kDirectX11 | omr.MRenderer.kOpenGLCoreProfile

    def isBounded(self, objPath, cameraPath):
        return False

    def boundingBox(self, objPath, cameraPath):
        corner1 = om.MPoint( -0.17, 0.0, -0.7 )
        corner2 = om.MPoint( 0.17, 0.0, 0.3 )

        multiplier = self.getMultiplier(objPath)
        corner1 *= multiplier
        corner2 *= multiplier

        self.mCurrentBoundingBox.clear()
        self.mCurrentBoundingBox.expand( corner1 )
        self.mCurrentBoundingBox.expand( corner2 )

        return self.mCurrentBoundingBox

    def disableInternalBoundingBoxDraw(self):
        return self.mCustomBoxDraw

    def prepareForDraw(self, objPath, cameraPath, frameContext, oldData):
        ## Retrieve data cache (create if does not exist)
        data = oldData
        if not isinstance(data, footPrintData):
            data = footPrintData()

        ## compute data and cache it
        global soleCount, sole
        global heelCount, heel

        fMultiplier = self.getMultiplier(objPath)
        fPoints = self.getPoints(objPath)

        data.fSoleLineList.clear()
        for i in range(soleCount):
            data.fSoleLineList.append( om.MPoint(sole[i][0] * fMultiplier, sole[i][1] * fMultiplier, sole[i][2] * fMultiplier) )

        data.fHeelLineList.clear()
        for i in range(heelCount):
            data.fHeelLineList.append( om.MPoint(heel[i][0] * fMultiplier, heel[i][1] * fMultiplier, heel[i][2] * fMultiplier) )

        data.fSoleTriangleList.clear()
        for i in range(1,soleCount-1):
            data.fSoleTriangleList.append( om.MPoint(sole[0][0] * fMultiplier, sole[0][1] * fMultiplier, sole[0][2] * fMultiplier) )
            data.fSoleTriangleList.append( om.MPoint(sole[i][0] * fMultiplier, sole[i][1] * fMultiplier, sole[i][2] * fMultiplier) )
            data.fSoleTriangleList.append( om.MPoint(sole[i+1][0] * fMultiplier, sole[i+1][1] * fMultiplier, sole[i+1][2] * fMultiplier) )

        data.fHeelTriangleList.clear()
        for i in range(1,heelCount-1):
            data.fHeelTriangleList.append( om.MPoint(heel[0][0] * fMultiplier, heel[0][1] * fMultiplier, heel[0][2] * fMultiplier) )
            data.fHeelTriangleList.append( om.MPoint(heel[i][0] * fMultiplier, heel[i][1] * fMultiplier, heel[i][2] * fMultiplier) )
            data.fHeelTriangleList.append( om.MPoint(heel[i+1][0] * fMultiplier, heel[i+1][1] * fMultiplier, heel[i+1][2] * fMultiplier) )

        data.fColor = omr.MGeometryUtilities.wireframeColor(objPath)

        data.fsourcePt = fPoints[0]
        data.faimPt = fPoints[1]

        return data

    def hasUIDrawables(self):
        return True

    def addUIDrawables(self, objPath, drawManager, frameContext, data):
        locatordata = data
        if not isinstance(locatordata, footPrintData):
            return

        drawManager.beginDrawable()
        #Draw Vector
        drawManager.line(locatordata.fsourcePt, locatordata.faimPt)

        ##Draw the foot print solid/wireframe
        drawManager.setColor( locatordata.fColor )
        drawManager.setDepthPriority(5)

        if (frameContext.getDisplayStyle() & omr.MFrameContext.kGouraudShaded):
            drawManager.mesh(omr.MGeometry.kTriangles, locatordata.fSoleTriangleList)
            drawManager.mesh(omr.MGeometry.kTriangles, locatordata.fHeelTriangleList)

        drawManager.mesh(omr.MUIDrawManager.kClosedLine, locatordata.fSoleLineList)
        drawManager.mesh(omr.MUIDrawManager.kClosedLine, locatordata.fHeelLineList)

        ## Draw a text "Foot"
        pos = om.MPoint( 0.0, 0.0, 0.0 )  ## Position of the text
        textColor = om.MColor( (0.1, 0.8, 0.8, 1.0) )  ## Text color

        drawManager.setColor( textColor )
        drawManager.setFontSize( omr.MUIDrawManager.kSmallFontSize )
        drawManager.text(pos, "Footprint", omr.MUIDrawManager.kCenter )

        drawManager.endDrawable()

    def getMultiplier(self, objPath):
        ## Retrieve value of the size attribute from the node
        footprintNode = objPath.node()
        plug = om.MPlug(footprintNode, footPrint.size)
        if not plug.isNull:
            sizeVal = plug.asMDistance()
            return sizeVal.asCentimeters()

        return 1.0

    def getPoints(self, objPath):
        ## Retrieve value of the source point attribute from the node
        footprintNode = objPath.node()
        sourcePlug = om.MPlug(footprintNode, footPrint.sourcePt)
        aimPlug = om.MPlug(footprintNode, footPrint.aimPt)

        if not sourcePlug.isNull:
            sourcePtHandle = sourcePlug.asMDataHandle()
            sourcePt = om.MPoint(sourcePtHandle.asFloatVector())

            if not aimPlug.isNull:
                aimPtHandle = aimPlug.asMDataHandle()
                aimPt = om.MPoint(aimPtHandle.asFloatVector())
                return sourcePt, aimPt
            
            return sourcePt
        
        return 1.0

def initializePlugin(obj):
    plugin = om.MFnPlugin(obj, "Autodesk", "3.0", "Any")

    try:
        plugin.registerNode("footPrint", footPrint.id, footPrint.creator, footPrint.initialize, om.MPxNode.kLocatorNode, footPrint.drawDbClassification)
    except:
        sys.stderr.write("Failed to register node\n")
        raise

    try:
        omr.MDrawRegistry.registerDrawOverrideCreator(footPrint.drawDbClassification, footPrint.drawRegistrantId, footPrintDrawOverride.creator)
    except:
        sys.stderr.write("Failed to register override\n")
        raise

def uninitializePlugin(obj):
    plugin = om.MFnPlugin(obj)

    try:
        plugin.deregisterNode(footPrint.id)
    except:
        sys.stderr.write("Failed to deregister node\n")
        pass

    try:
        omr.MDrawRegistry.deregisterDrawOverrideCreator(footPrint.drawDbClassification, footPrint.drawRegistrantId)
    except:
        sys.stderr.write("Failed to deregister override\n")
        pass