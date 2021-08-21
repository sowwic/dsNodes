#pragma once
#include <maya/MFnMesh.h>
#include <maya/MPxNode.h>
#include <maya/MDataBlock.h>
#include <maya/MFloatPoint.h>
#include <maya/MFloatVector.h>
#include <maya/MMatrix.h>
#include <maya/MTransformationMatrix.h>
#include <maya/MEulerRotation.h>
#include <maya/MVector.h>
#include <maya/MAngle.h>
#include <maya/MPoint.h>
#include <maya/MTypeId.h>
#include <maya/MString.h>
#include <maya/MPlug.h>
#include <maya/MDataHandle.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MFnUnitAttribute.h>
#include <maya/MFnEnumAttribute.h>
#include <maya/MFnMatrixAttribute.h>
#include <maya/MUserData.h>
#include <maya/MNodeMessage.h>
#include <maya/MGlobal.h>

class Raycast : public MPxNode
{
public:
	Raycast();
	~Raycast() override;

	MStatus compute(const MPlug &plug, MDataBlock &data) override;

	static void *creator();
	static MStatus initialize();

public:
	//INPUTS
	static MTypeId id;
	static MString nodeName;
	static MObject inMesh;
	static MObject inMode;
	static MObject inSourceMatrix;
	static MObject inAim;
	static MObject inAimAxis;
	static MObject inUpVector;
	static MObject inDistance;
	static MObject inBothWays;
	static MObject inOffset;
	static MObject inOfsVectorEnum;
	//static MObject inDebug;

	//OUTPUTS
	static MObject outHitPoint;
	static MObject outNormal;
	static MObject outRotationX;
	static MObject outRotationY;
	static MObject outRotationZ;
	static MObject outRotation;
	static MObject outHitDistance;
	static MObject outSourcePt;

public:
	static MString AETemplate(MString);
};