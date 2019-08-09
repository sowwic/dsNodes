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

class drawVector(omui.MPxLocatorNode):

    id = om.MTypeId( 0x80067 )
    drawDbClassification = "drawdb/geometry/vector"
    drawRegistrantId = "drawVectorPlugin"

    size = None## The size of the foot
    sourcePt = om.MObject()
    aimPt = om.MObject()
    vector = om.MObject()
    distance = om.MObject()
    drawMode = om.MObject()

    @staticmethod
    def creator():
        return drawVector()

    @staticmethod
    def initialize():
        unitFn = om.MFnUnitAttribute()
        numericFn = om.MFnNumericAttribute()
        enumFn = om.MFnEnumAttribute()

        drawVector.size = unitFn.create( "size", "sz", om.MFnUnitAttribute.kDistance )
        unitFn.default = om.MDistance(1.0)
        
        ######VECTOR
        drawVector.drawMode = enumFn.create('drawingMode', 'drm', 0)
        enumFn.addField('Between two', 0)
        enumFn.addField('From single', 1)
        drawVector.sourcePt = numericFn.createPoint('sourcePoint', 'sp')
        drawVector.aimPt = numericFn.createPoint('aimPoint', 'ap')

        om.MPxNode.addAttribute( drawVector.size )
        ######VECTOR
        om.MPxNode.addAttribute( drawVector.drawMode )
        om.MPxNode.addAttribute( drawVector.sourcePt )
        om.MPxNode.addAttribute( drawVector.aimPt)

    def __init__(self):
        omui.MPxLocatorNode.__init__(self)

    def compute(self, plug, data):
        return None

#############################################################################
##
## Viewport 2.0 override implementation
##
#############################################################################
class drawVectorData(om.MUserData):
    def __init__(self):
        om.MUserData.__init__(self, False) ## don't delete after draw

        ######VECTOR
        self.fsourcePt = om.MPoint()
        self.faimPt = om.MPoint()

class drawVectorDrawOverride(omr.MPxDrawOverride):
    @staticmethod
    def creator(obj):
        return drawVectorDrawOverride(obj)

    @staticmethod
    def draw(context, data):
        return

    def __init__(self, obj):
        omr.MPxDrawOverride.__init__(self, obj, drawVectorDrawOverride.draw)

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

    def disableInternalBoundingBoxDraw(self):
        return self.mCustomBoxDraw

    def prepareForDraw(self, objPath, cameraPath, frameContext, oldData):
        ## Retrieve data cache (create if does not exist)
        data = oldData
        if not isinstance(data, drawVectorData):
            data = drawVectorData()
        
        fPoints = self.getPoints(objPath)
        data.fColor = omr.MGeometryUtilities.wireframeColor(objPath)
        data.fsourcePt = fPoints[0]
        data.faimPt = fPoints[1]

        return data

    def hasUIDrawables(self):
        return True

    def addUIDrawables(self, objPath, drawManager, frameContext, data):
        locatordata = data
        if not isinstance(locatordata, drawVectorData):
            return
        drawManager.beginDrawable()
        #Draw Vector
        drawManager.setColor( locatordata.fColor )
        drawManager.setDepthPriority(5)
        drawManager.line(locatordata.fsourcePt, locatordata.faimPt)

        drawManager.endDrawable()


    def getPoints(self, objPath):
        ## Retrieve value of the source point attribute from the node
        drawVectorNode = objPath.node()
        sourcePlug = om.MPlug(drawVectorNode, drawVector.sourcePt)
        aimPlug = om.MPlug(drawVectorNode, drawVector.aimPt)

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
    plugin = om.MFnPlugin(obj, "Dmitrii Shevchenko", "1.0", "Any")

    try:
        plugin.registerNode("drawVector", drawVector.id, drawVector.creator, drawVector.initialize, om.MPxNode.kLocatorNode, drawVector.drawDbClassification)
    except:
        sys.stderr.write("Failed to register node\n")
        raise

    try:
        omr.MDrawRegistry.registerDrawOverrideCreator(drawVector.drawDbClassification, drawVector.drawRegistrantId, drawVectorDrawOverride.creator)
    except:
        sys.stderr.write("Failed to register override\n")
        raise

def uninitializePlugin(obj):
    plugin = om.MFnPlugin(obj)

    try:
        plugin.deregisterNode(drawVector.id)
    except:
        sys.stderr.write("Failed to deregister node\n")
        pass

    try:
        omr.MDrawRegistry.deregisterDrawOverrideCreator(drawVector.drawDbClassification, drawVector.drawRegistrantId)
    except:
        sys.stderr.write("Failed to deregister override\n")
        pass