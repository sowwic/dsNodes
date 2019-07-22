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
    outHitPoint = om.MObject()
   
    def __init__(self):
        ompx.MPxNode.__init__(self)
       
    def compute(self, pPlug, pDataBlock):
       
        if pPlug == DsRaycast.outHitPoint:
            #Handles
            inMeshHandle = pDataBlock.inputValue(DsRaycast.inMesh)
            inSourceHandle = pDataBlock.inputValue(DsRaycast.inSource)
            inAimHandle = pDataBlock.inputValue(DsRaycast.inAim)
            outHitHandle = pDataBlock.outputValue(DsRaycast.outHitPoint)

            inMesh = inMeshHandle.asMeshTransformed()
            fnMesh = om.MFnMesh(inMesh)
            inSource = om.MFloatPoint(inSourceHandle.asFloatVector())
            xinAim = om.MFloatVector(inAimHandle.asFloatVector())
            #dirVector = om.MFloatVector(inAim[0] - inSource[0], inAim[1] - inSource[1],inAim[2] - inSource[2] )
            hitPoint = om.MFloatPoint()

            
            intersection = fnMesh.closestIntersection(inSource,
                                                      inAim,
                                                      None,
                                                      None,
                                                      False,
                                                      om.MSpace.kWorld,
                                                      200000,
                                                      True,
                                                      #fnMesh.autoUniformGridParams(),
                                                      None,
                                                      hitPoint,
                                                      None, 
                                                      None,
                                                      None,
                                                      None,
                                                      None                                            
                                                        )
            print(intersection)
            print(inSource.x, inSource.y, inSource.z)
            print(inAim.x, inAim.y, inAim.z)


            outHitHandle.setMFloatVector(om.MFloatVector(hitPoint))
            outHitHandle.setClean()

          
        else:
           
            return om.kUnknownParameter
       
def nodeCreator():
   return ompx.asMPxPtr(DsRaycast())

def nodeInitializer():
   
    typedAttributeFn = om.MFnTypedAttribute()
    numericAttributeFn = om.MFnNumericAttribute()
    
    ##IN
    #Mesh
    DsRaycast.inMesh = typedAttributeFn.create('targetMesh',
                                                'tm',
                                                om.MFnData.kMesh
                                                )
    DsRaycast.addAttribute(DsRaycast.inMesh)
    typedAttributeFn.setReadable(0)
    
    #Source
    DsRaycast.inSource = numericAttributeFn.createPoint("source", 
                                              "srs"
                                              )
    DsRaycast.addAttribute(DsRaycast.inSource)

    #Aim
    DsRaycast.inAim = numericAttributeFn.createPoint("aim", 
                                              "aim"
                                              )
    DsRaycast.addAttribute(DsRaycast.inAim)

    
    
    ##OUT
    DsRaycast.outHitPoint = numericAttributeFn.createPoint("hitPoint", 
                                              "hit"
                                              )
    #numericAttributeFn.setWritable(0)

    DsRaycast.addAttribute( DsRaycast.outHitPoint )
    
    DsRaycast.attributeAffects(DsRaycast.inMesh, DsRaycast.outHitPoint)
    DsRaycast.attributeAffects(DsRaycast.inSource, DsRaycast.outHitPoint)
    DsRaycast.attributeAffects(DsRaycast.inAim, DsRaycast.outHitPoint)



def initializePlugin(obj):
   plugin = ompx.MFnPlugin(obj, NAME, VERSION, MAYAVERSION)
   try:
       plugin.registerNode(NODENAME, NODEID, nodeCreator, nodeInitializer)
   except RuntimeError:
       sys.stderr.write("Failed to register node: %s" % NODENAME)


def uninitializePlugin(obj):
   plugin = ompx.MFnPlugin(obj)
   try:
       plugin.deregisterNode(NODEID)
   except Exception as err:
       sys.stderr.write("Failed to deregister node: %s\n%s" % (NODENAME, err))