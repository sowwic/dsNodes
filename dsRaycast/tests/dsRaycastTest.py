import maya.cmds as mc
from rigging.functions import *


mc.file(new=1,f=1)
mc.unloadPlugin("dsRaycast")

mc.loadPlugin('C:\Users\dmitris\Documents\maya\scripts\dsNodes\dsRaycast\plugins\dsRaycast.py')

###### Test #########
#Basic test

mesh = mc.polyPlane()[0]
mc.move(0, 4, 0, mesh)
mc.scale(50, 50, 50, mesh)
source = create.locator(name='sourse')
source.translate = [0, 10, 0]
aim = create.locator(name='aim')
aim.translate = [0, 1, 0]

dsRaycast = mc.createNode('dsRaycast')

mc.connectAttr(mesh + '.worldMesh', dsRaycast + '.tm')
source.translate > dsRaycast + '.srs'
aim.translate > dsRaycast + '.aim'

testObj = mc.polyCone(n='testBoi00')

mc.connectAttr(dsRaycast + ".hitPoint", testObj[0] + ".t")

'''
#Wheel test
mesh = mc.polyPlane()
srsLocs =[]
wheelGeo =[]
meshShape = mc.listRelatives(mesh, type='shape')[0]
mc.move(0, 2, 0, mesh[0])
mc.setAttr(mesh[1] + '.width', 50)
mc.setAttr(mesh[1] + '.height', 50)
mc.setAttr(mesh[1] + '.subdivisionsWidth', 50)
mc.setAttr(mesh[1] + '.subdivisionsHeight', 50)

body = mc.polyCube(n='C_body_PLY', w=7, h=5, d=15)
mc.move(0, 7.5, 0, body)



x = 5
y = 8
z = 5
    
for side in ['L', 'R']:
    frontWheelSource = create.locator(side=side, name='frontWheelSource')
    srsLocs.append(frontWheelSource)
    frontWheelAim = create.locator(parent=frontWheelSource, side=side, name='frontWheelAim')
    hit = create.transform(side=side, name='frontHitPt')
    frontWheelGeo = mc.polyCylinder(n='{}_frontWheel_PLY'.format(side), r=2.5)
    wheelGeo.append(frontWheelGeo[0])
    mc.setAttr(frontWheelGeo[0] +'.rz', 90)
    mc.setAttr(frontWheelGeo[0] +'.ty', 2.559)
    mc.setAttr(frontWheelGeo[1] +'.h', 1)
    mc.parent(frontWheelGeo[0], hit)
    frontWheelAim.translateY = -7

    if side == 'L':
        x = 5
    else:
        x=-5
    
    frontWheelSource.translate = [x, y, z]

    #Connections
    dsRaycast = mc.createNode('dsRaycast')
    frontWheelSource.translate > dsRaycast + '.srs'
    frontWheelAim.translate > dsRaycast + '.aim'
    mc.connectAttr(meshShape + '.worldMesh', dsRaycast + '.tm')
    dsRaycast + '.hit' > hit.translate

    
z = -5
for side in ['L', 'R']:
    backWheelSource = create.locator(side=side, name='backWheelSource')
    srsLocs.append(backWheelSource)
    backWheelAim = create.locator(parent=backWheelSource, side=side, name='backWheelAim',)
    hit = create.transform(side=side, name='backHitPt')
    backWheelGeo = mc.polyCylinder(n='{}_backWheel_PLY'.format(side), r=2.5)
    wheelGeo.append(backWheelGeo[0])
    mc.setAttr(backWheelGeo[0] +'.rz', 90)
    mc.setAttr(backWheelGeo[0] +'.ty', 2.559)
    mc.setAttr(backWheelGeo[1] +'.h', 1)
    mc.parent(backWheelGeo[0], hit)
    backWheelAim.translateY = -7

    if side == 'L':
        x = 5
    else:
        x=-5
    
    backWheelSource.translate = [x, y, z]

    #Connections
    dsRaycast = mc.createNode('dsRaycast')
    backWheelSource.translate > dsRaycast + '.srs'
    backWheelAim.translate > dsRaycast + '.aim'
    mc.connectAttr(meshShape + '.worldMesh', dsRaycast + '.tm')
    dsRaycast + '.hit' > hit.translate

for loc in srsLocs:
    constraintFn.parentConstraint(body[0], loc, mo=1)

for geo in wheelGeo:
    constraintFn.orientConstraint(body[0], geo, mo=1)
'''