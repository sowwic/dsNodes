#pragma once
#include <maya/MPxLocatorNode.h>
#include <maya/MString.h>
#include <maya/MTypeId.h>
#include <maya/MPlug.h>
#include <maya/MVector.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MColor.h>
#include <maya/MFnPlugin.h>
#include <maya/MDistance.h>
#include <maya/MFnUnitAttribute.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnEnumAttribute.h>
#include <maya/MFnMessageAttribute.h>
#include <maya/MArrayDataBuilder.h>
#include <maya/MEvaluationNode.h>

#include <maya/MPoint.h>
#include <maya/MPointArray.h>
#include <maya/MGlobal.h>
#include <maya/MFnPlugin.h>
#include <maya/MObject.h>


// Viewport 2.0 includes
#include <maya/MDrawRegistry.h>
#include <maya/MPxDrawOverride.h>
#include <maya/MUserData.h>
#include <maya/MDrawContext.h>
#include <maya/MHWGeometryUtilities.h>
#include <maya/MPointArray.h>
#include <maya/MGlobal.h>
#include <maya/MEventMessage.h>
#include <maya/MFnDependencyNode.h>


class DrawVector : public MPxLocatorNode
{
public:
	DrawVector();
	~DrawVector() override;

	MStatus  compute(const MPlug& plug, MDataBlock& data) override;

	bool isBounded() const override;

	MStatus preEvaluation(const MDGContext& context, const MEvaluationNode& evaluationNode) override;

	static void* creator();
	static MStatus initialize();

	static MObject sourcePt;
	static MObject aimPt;
	static MObject vector;
	static MObject distance;
	static MObject lineColor;
	static MObject lineWidth;
	static MObject drawMessage;

public:
	static MTypeId id;
	static MString drawDbClassification;
	static MString drawRegistrantId;
};

MTypeId DrawVector::id(0x09834);
MString	DrawVector::drawDbClassification("drawdb/geometry/drawVector");
MString	DrawVector::drawRegistrantId("drawVectorPlugin");
MObject DrawVector::sourcePt;
MObject DrawVector::aimPt;
MObject DrawVector::vector;
MObject DrawVector::distance;
MObject DrawVector::lineColor;
MObject DrawVector::lineWidth;
MObject DrawVector::drawMessage;

DrawVector::DrawVector() {}
DrawVector::~DrawVector() {}

class DrawVectorData : public MUserData
{
public:
	DrawVectorData() : MUserData(false) {} //don't delete afer draw
	~DrawVectorData() override {}

	MColor fColor;
	MPoint fSourcePt;
	MPoint fAimPt;
	float fWidth;
};

class DrawVectorDrawOverride : public MHWRender::MPxDrawOverride
{
public:
	static MHWRender::MPxDrawOverride* Creator(const MObject& obj)
	{
		return new DrawVectorDrawOverride(obj);
	}

	~DrawVectorDrawOverride() override;

	MHWRender::DrawAPI supportedDrawAPIs() const override;

	bool isBounded(
		const MDagPath& objPath,
		const MDagPath& cameraPath) const override;

	/*
	MBoundingBox boundingBox(
		const MDagPath& objPath,
		const MDagPath& cameraPath) const override;
	*/

	MUserData* prepareForDraw(
		const MDagPath& objPath,
		const MDagPath& cameraPath,
		const MHWRender::MFrameContext& frameContext,
		MUserData* oldData) override;

	bool hasUIDrawables() const override { return true; }

	void addUIDrawables(
		const MDagPath& objPath,
		MHWRender::MUIDrawManager& drawManager,
		const MHWRender::MFrameContext& frameContext,
		const MUserData* data) override;

	bool traceCallSequence() const override
	{
		// Return true if internal tracing is desired.
		return false;
	}
	void handleTraceMessage(const MString &message) const override
	{
		MGlobal::displayInfo("drawVectorDrawOverride: " + message);

		// Some simple custom message formatting.
		fputs("drawVectorDrawOverride: ", stderr);
		fputs(message.asChar(), stderr);
		fputs("\n", stderr);
	}

public:
	DrawVectorDrawOverride(const MObject& obj);
	MPointArray getPoints(const MDagPath& objPath) const;
	static void OnModelEditorChanged(void *clientData);
	MColor getColor(const MDagPath& objPath) const;
	float getWidth(const MDagPath& objPath) const;
	DrawVector* fDrawVector;
	MCallbackId fModelEditorChangedCbId;
};