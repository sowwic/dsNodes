#include "dsDrawVectorNode.h"

MStatus DrawVector::compute(const MPlug& plug/*plug*/, MDataBlock& dataBlock/*data*/)
{
	return MS::kSuccess;;
}

bool DrawVector::isBounded() const
{
	return false;
}


void* DrawVector::creator()
{
	return new DrawVector();
}

MStatus DrawVector::preEvaluation(
	const MDGContext& context,
	const MEvaluationNode& evaluationNode)
{
	if (context.isNormal())
	{
		MStatus status;
		if (evaluationNode.dirtyPlugExists(sourcePt, &status) && status)
		{
			MHWRender::MRenderer::setGeometryDrawDirty(thisMObject());
		}
	}

	return MStatus::kSuccess;
}


MStatus DrawVector::initialize()
{
	MFnUnitAttribute unitFn;
	MFnNumericAttribute numericFn;
	MFnMessageAttribute messageFn;
	MStatus stat;

	sourcePt = numericFn.createPoint("sourcePoint", "sourcePoint");
	aimPt = numericFn.createPoint("aimPoint", "aimPoint");
	drawMessage = messageFn.create("drawMessage", "drawMessage");
	lineColor = numericFn.createColor("lineColor", "lineColor");
	lineWidth = numericFn.create("lineWidth", "lineWidth", MFnNumericData::kFloat, 3.0);

	//ADD ATTRIBUTES
	stat = addAttribute(sourcePt);
		if (!stat) { stat.perror("addAttribute"); return stat; }
	stat = addAttribute(aimPt);
		if (!stat) { stat.perror("addAttribute"); return stat; }
	stat = addAttribute(drawMessage);
		if (!stat) { stat.perror("addAttribute"); return stat; }
	stat = addAttribute(lineColor);
		if (!stat) { stat.perror("addAttribute"); return stat; }
	stat = addAttribute(lineWidth);
		if (!stat) { stat.perror("addAttribute"); return stat; }
	
		return stat;
}

DrawVectorDrawOverride::DrawVectorDrawOverride(const MObject& obj)
	: MHWRender::MPxDrawOverride(obj, NULL, false)
{
	fModelEditorChangedCbId = MEventMessage::addEventCallback(
		"modelEditorChanged", OnModelEditorChanged, this);

	MStatus status;
	MFnDependencyNode node(obj, &status);
	fDrawVector = status ? dynamic_cast<DrawVector*>(node.userNode()) : NULL;
}

DrawVectorDrawOverride::~DrawVectorDrawOverride()
{
	fDrawVector = NULL;

	if (fModelEditorChangedCbId != 0)
	{
		MMessage::removeCallback(fModelEditorChangedCbId);
		fModelEditorChangedCbId = 0;
	}
}

void DrawVectorDrawOverride::OnModelEditorChanged(void *clientData)
{
	// Mark the node as being dirty so that it can update on display appearance
	// switch among wireframe and shaded.
	DrawVectorDrawOverride *ovr = static_cast<DrawVectorDrawOverride*>(clientData);
	if (ovr && ovr->fDrawVector)
	{
		MHWRender::MRenderer::setGeometryDrawDirty(ovr->fDrawVector->thisMObject());
	}
}

MHWRender::DrawAPI DrawVectorDrawOverride::supportedDrawAPIs() const
{
	// this plugin supports both GL and DX
	return (MHWRender::kOpenGL | MHWRender::kDirectX11 | MHWRender::kOpenGLCoreProfile);
}



MPointArray DrawVectorDrawOverride::getPoints(const MDagPath& objPath) const
{
	MPointArray points;
	MStatus status;
	MObject drawVectorNode = objPath.node(&status);
	if (status)
	{
		MPlug sourcePlug(drawVectorNode, DrawVector::sourcePt);
		MPlug aimPlug(drawVectorNode, DrawVector::aimPt);
		if (!sourcePlug.isNull())
		{
			MDataHandle sourcePtHandle = sourcePlug.asMDataHandle();
			MPoint sourcePt = MPoint(sourcePtHandle.asFloatVector());
			if (!aimPlug.isNull())
			{
				MDataHandle aimPtHandle = aimPlug.asMDataHandle();
				MPoint aimPt = MPoint(aimPtHandle.asFloatVector());
				MPoint srsArray[2] = { sourcePt, aimPt };
				points = MPointArray(srsArray, 2);
			}

			MPoint srsArray[1] = {sourcePt};
			points = MPointArray(srsArray, 1);
		}
		return points;
	}	
}

MColor DrawVectorDrawOverride::getColor(const MDagPath& objPath) const
{
	MColor color;
	MStatus status;
	MObject drawVectorNode = objPath.node(&status);
	if (status)
	{
		MPlug colorPlug(drawVectorNode, DrawVector::lineColor);
		if (!colorPlug.isNull())
		{
			MDataHandle colorHandle = colorPlug.asMDataHandle();
			color = MColor(colorHandle.asFloat3());
		}

		return color;
	}
}

float DrawVectorDrawOverride::getWidth(const MDagPath& objPath) const
{
	float width;
	MStatus status;
	MObject drawVectorNode = objPath.node(&status);
	if (status)
	{
		MPlug widthPlug(drawVectorNode, DrawVector::lineWidth);
		if (!widthPlug.isNull())
		{
			width = widthPlug.asFloat();
			return width;
		}

		return 1.0f;
	}
}

bool DrawVectorDrawOverride::isBounded(const MDagPath& /*objPath*/,
	const MDagPath& /*cameraPath*/) const
{
	return true;
}


MUserData* DrawVectorDrawOverride::prepareForDraw(
	const MDagPath& objPath,
	const MDagPath& cameraPath,
	const MHWRender::MFrameContext& frameContext,
	MUserData* oldData)
{
	DrawVectorData* data = dynamic_cast<DrawVectorData*>(oldData);
	if (!data)
	{
		data = new DrawVectorData();
	}

	MPointArray fPoints = getPoints(objPath);
	MColor fColor = getColor(objPath);
	float fWidth = getWidth(objPath);

	data->fSourcePt = fPoints[0];
	data->fAimPt = fPoints[1];
	data->fColor = fColor;
	data->fWidth = fWidth;

	return data;
}

void DrawVectorDrawOverride::addUIDrawables(
	const MDagPath& objPath,
	MHWRender::MUIDrawManager& drawManager,
	const MHWRender::MFrameContext& frameContext,
	const MUserData* data)
{
	DrawVectorData* pLocatorData = (DrawVectorData*)data;
	if (!pLocatorData)
	{
		return;
	}

	//DRAWING VECTOR
	drawManager.beginDrawable(MUIDrawManager::kNonSelectable);
	drawManager.setColor(pLocatorData->fColor);
	drawManager.setDepthPriority(5);
	drawManager.setLineWidth(pLocatorData->fWidth);
	drawManager.line(pLocatorData->fSourcePt, pLocatorData->fAimPt);
	drawManager.endDrawable();
}

MStatus initializePlugin(MObject obj)
{
	MStatus   status;
	MFnPlugin plugin(obj, "Dmitrii Shevchenko", "1.0", "2019");

	status = plugin.registerNode(
		"dsDrawVector",
		DrawVector::id,
		&DrawVector::creator,
		&DrawVector::initialize,
		MPxNode::kLocatorNode,
		&DrawVector::drawDbClassification);
	if (!status) {
		status.perror("registerNode");
		return status;
	}

	status = MHWRender::MDrawRegistry::registerDrawOverrideCreator(
		DrawVector::drawDbClassification,
		DrawVector::drawRegistrantId,
		DrawVectorDrawOverride::Creator);
	if (!status) {
		status.perror("registerDrawOverrideCreator");
		return status;
	}

	return status;
}

MStatus uninitializePlugin(MObject obj)
{
	MStatus   status;
	MFnPlugin plugin(obj);

	status = MHWRender::MDrawRegistry::deregisterDrawOverrideCreator(
		DrawVector::drawDbClassification,
		DrawVector::drawRegistrantId);

	if (!status) {
		status.perror("deregisterDrawOverrideCreator");
		return status;
	}

	status = plugin.deregisterNode(DrawVector::id);
	if (!status) {
		status.perror("deregisterNode");
		return status;
	}
	return status;
}