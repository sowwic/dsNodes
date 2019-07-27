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

class Raycast : public MPxNode
{
public:
	Raycast();
	~Raycast() override;

	MStatus compute(const MPlug& plug, MDataBlock data);

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



MStatus Raycast::compute(const MPlug & plug, MDataBlock data)
{
	MStatus returnStatus;

	if (plug == outHitPoint)
	{
		MDataHandle inMeshHandle = data.inputValue(inMesh, &returnStatus);
		MDataHandle inSourceHAndle = data.inputValue(inSource, &returnStatus);

		if (returnStatus != MS::kSuccess)
			cerr << "ERROR getting data" << endl;
		else
		{	
			inMesh = inMeshHandle.asMeshTransformed();
			MFnMesh fnMesh = MFnMesh(inMesh);
		}

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

	inMesh = tAttr.create("targetMesh", 'tm', MFnData::kMesh, 0.0);
	tAttr.setReadable(false);




}

MStatus initializePlugin(MObject obj)
{
	
}

MStatus uninitializePlugin(MObject obj)
{

}

