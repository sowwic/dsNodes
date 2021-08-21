#pragma once
// plug-in classes
#include <maya/MTypeId.h>
#include <maya/MPxDeformerNode.h>
// attributes
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnGenericAttribute.h>
#include <maya/MFnMatrixAttribute.h>
#include <maya/MFnEnumAttribute.h>
#include <maya/MRampAttribute.h>
// variables
#include <maya/MFnMesh.h>
#include <maya/MMatrix.h>
#include <maya/MFloatArray.h>
#include <maya/MIntArray.h>
#include <maya/MGlobal.h>
#include <maya/MString.h>
#include <maya/MDagPath.h>
#include <maya/MPlugArray.h>
#include <maya/MFnMeshData.h>
#include <maya/MMeshIntersector.h>
#include <maya/MFnNurbsCurve.h>
#include <maya/MFnNurbsSurface.h>
#include <maya/MFnNurbsCurveData.h>
#include <maya/MFnNurbsSurfaceData.h>
#include <maya/MItGeometry.h>
// openMP
#include <maya/MThreadUtils.h>
#include <maya/MPointArray.h>

class DsAttractDeformer : public MPxDeformerNode
{
public:
	DsAttractDeformer();
	~DsAttractDeformer() override;

	static void *creator();
	static MStatus initialize();

	//Deformation function
	virtual MStatus deform(MDataBlock &block,
						   MItGeometry &iter,
						   const MMatrix &worldMatrix,
						   unsigned int multiIndex);

	virtual MStatus accessoryNodeSetup(MDagModifier &cmd);

	//when the accessory is deleted, this node will clean itself up
	//virtual MObject& accessoryAttribute() const;

	//create accessory nodes whne the node is created
	//virtual MStatus accessoryNodeSetup(MDagModifier& cmd);

	//LOCAL NODE ATTRIBUTES
	//Inputs
	static MTypeId id;
	static MString nodeName;
	static MObject maxDistance;
	static MObject projectOnNormal;
	static MObject warnings;
	static MObject inputShape;
	static MObject inputMatrix;
	static MObject maxDistanceUV;
	static MObject falloff;
	static MObject normalDirectionLimit;

public:
	static MString AETemplate(MString);
	static void defineMelCreateCommand();
};