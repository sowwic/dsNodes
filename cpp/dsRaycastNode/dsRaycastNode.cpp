#include <maya/MObject.h>
#include <maya/MFnMesh.h>
#include <maya/MPxNode.h>
#include <maya/MDataBlock.h>
#include <maya/MFloatPoint.h>
#include <maya/MFloatVector.h>
#include <maya/MVector.h>
#include <maya/MPoint.h>
#include <maya/MFnPlugin.h>
#include <maya/MTypeId.h>
#include <maya/MString.h>
#include <maya/MPlug.h>
#include <maya/MDataHandle.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MUserData.h>
#include <maya/MIOStream.h>
#include <maya/MDagPath.h>

class Raycast : public MPxNode
{
public:
	Raycast();
	~Raycast() override;

	MStatus compute(const MPlug& plug, MDataBlock &data) override;

	static void* creator();
	static MStatus initialize();

public:
	static MTypeId id;
	static MObject inMesh;
	static MObject inSource;
	static MObject inAim;
	static MObject inDistance;
	static MObject inBothWays;
	static MObject outHitPoint;
	static MObject outNormal;
};

MTypeId Raycast::id(0x09833);
MObject Raycast::inMesh;
MObject Raycast::inSource;
MObject Raycast::inAim;
MObject Raycast::inDistance;
MObject Raycast::inBothWays;
MObject Raycast::outHitPoint;
MObject Raycast::outNormal;

Raycast::Raycast() {}
Raycast::~Raycast() {}


MStatus Raycast::compute(const MPlug &plug, MDataBlock &data)
{
	MStatus returnStatus;

	if (plug == outHitPoint | plug == outNormal)
	{
		MDataHandle inMeshHandle = data.inputValue(inMesh, &returnStatus);
		CHECK_MSTATUS(returnStatus);
		MDataHandle inSourceHandle = data.inputValue(inSource, &returnStatus);
		CHECK_MSTATUS(returnStatus);
		MDataHandle inAimHandle = data.inputValue(inAim, &returnStatus);
		CHECK_MSTATUS(returnStatus);
		MDataHandle inDistanceHandle = data.inputValue(inDistance, &returnStatus);
		CHECK_MSTATUS(returnStatus);
		MDataHandle inBotheWaysHandle = data.inputValue(inBothWays, &returnStatus);
		CHECK_MSTATUS(returnStatus);
		MDataHandle outHitHandle = data.outputValue(outHitPoint, &returnStatus);
		CHECK_MSTATUS(returnStatus);
		MDataHandle outNormalHandle = data.outputValue(outNormal, &returnStatus);
		CHECK_MSTATUS(returnStatus);

		//POINT
		//MDagPath pathTomesh;
		
		//MDagPath::getAPathTo(inMeshHandle.data(), pathTomesh);
		MFnMesh fnMesh(inMeshHandle.data());
		
		float fHitRayParams;
		int iaHitFaces;
		int iaHitTriangles;


		MFloatPoint inSource = MFloatPoint(inSourceHandle.asFloatVector());			MFloatVector inAim = MFloatVector(inAimHandle.asFloatVector());
		float distance = inDistanceHandle.asFloat();
		bool inBothWays = inBotheWaysHandle.asBool();
		MFloatPoint hitPoint = MFloatPoint();

		bool intersectStatus = fnMesh.closestIntersection(  inSource,
															inAim,
															NULL,
															NULL,
															false,
															MSpace::kWorld,
															distance,
															inBothWays,
															NULL,
															hitPoint,
															&fHitRayParams,
															&iaHitFaces,
															&iaHitTriangles,
															NULL,
															NULL,
															0.000001f
															);
			
		//NORMAL
		MVector normalVector = MVector();
		MPoint mHitPoint = MPoint(hitPoint);

		fnMesh.getClosestNormal(mHitPoint, normalVector, MSpace::kWorld);


		//OUTPUTS
		outHitHandle.setMFloatVector(MFloatVector(hitPoint));
		outNormalHandle.setMFloatVector(MFloatVector(normalVector));

		outHitHandle.setClean();
		outNormalHandle.setClean();

	}else{
		return MS::kUnknownParameter;
	}

	return MS::kSuccess;
}

void* Raycast::creator()
{
	return new Raycast();
}

MStatus Raycast::initialize()
{
	MFnNumericAttribute nAttr;
	MFnTypedAttribute tAttr;
	MStatus stat;

	//INPUT
	//Mesh
	inMesh = tAttr.create("targetMesh", "tm", MFnData::kMesh);
	tAttr.setReadable(false);

	//Source
	inSource = nAttr.createPoint("source", "src");
	
	//Aim
	inAim = nAttr.createPoint("aim", "a");

	//Distance
	inDistance = nAttr.create("distance", "d", MFnNumericData::kFloat, 100.0);

	//Test direction
	inBothWays = nAttr.create("bothWays", "bw", MFnNumericData::kBoolean, 1.0);


	//OUTPUT
	//Hit Point
	outHitPoint = nAttr.createPoint("hitPoint", "hit");
	nAttr.setWritable(false);
	
	//Normal vector
	outNormal = nAttr.createPoint("normal", "n");
	nAttr.setWritable(false);


	//ADDING ATTRIBUTES
	stat = addAttribute(inMesh);
		if (!stat) { stat.perror("addAttribute"); return stat;}
	stat = addAttribute(inSource);
		if (!stat) { stat.perror("addAttribute"); return stat;}
	stat = addAttribute(inAim);
		if (!stat) { stat.perror("addAttribute"); return stat;}
	stat = addAttribute(inDistance);
		if (!stat) { stat.perror("addAttribute"); return stat;}
	stat = addAttribute(inBothWays);
		if (!stat) { stat.perror("addAttribute"); return stat;}
	stat = addAttribute(outHitPoint);
		if (!stat) { stat.perror("addAttribute"); return stat; }
	stat = addAttribute(outNormal);
		if (!stat) { stat.perror("addAttribute"); return stat; }


	//ATTRIBUTE AFFECTS
	stat = attributeAffects(inMesh, outHitPoint);
		if (!stat) { stat.perror("attributeAffects"); return stat; }
	stat = attributeAffects(inSource, outHitPoint);
		if (!stat) { stat.perror("attributeAffects"); return stat; }
	stat = attributeAffects(inAim, outHitPoint);
		if (!stat) { stat.perror("attributeAffects"); return stat; }

	stat = attributeAffects(inMesh, outNormal);
		if (!stat) { stat.perror("attributeAffects"); return stat; }
	stat = attributeAffects(inSource, outNormal);
		if (!stat) { stat.perror("attributeAffects"); return stat; }
	stat = attributeAffects(inAim, outNormal);
		if (!stat) { stat.perror("attributeAffects"); return stat; }

		return MS::kSuccess;
}

MStatus initializePlugin(MObject obj)
{
	MStatus status;
	MFnPlugin plugin(obj, PLUGIN_COMPANY, "1.0", "Any");

	status = plugin.registerNode("dsRaycast", Raycast::id, Raycast::creator, Raycast::initialize);

	if (!status)
	{
		status.perror("registerNode");
		return status;
	}

	return status;
}

MStatus uninitializePlugin(MObject obj)
{
	MStatus status;
	MFnPlugin plugin(obj);

	status = plugin.deregisterNode(Raycast::id);
	if (!status)
	{
		status.perror("deregisterNode");
		return status;
	}

	return status;
}

