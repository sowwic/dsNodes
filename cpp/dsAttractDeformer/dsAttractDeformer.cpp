#include "dsAttractDeformer.h"


MStatus DsAttractDeformer::initialize()
{
	MFnNumericAttribute numericFn;
	MFnGenericAttribute genericFn;
	MFnMatrixAttribute matrixFn;
	MRampAttribute rampFn;
	MFnEnumAttribute enumFn;
	MStatus stat;

	//CREATE ATTRIBUTES
	// warnings
	warnings = numericFn.create("warnings", "warnings", MFnNumericData::kBoolean, true);
	numericFn.setChannelBox(true);

	// max distance
	maxDistance = numericFn.create("maximumDistance", "maxDist", MFnNumericData::kFloat, 1.0);
	numericFn.setKeyable(true);
	numericFn.setMin(0.0);

	//falloff
	falloff = rampFn.createCurveRamp("falloff", "falloff");

	// max distance uv
	maxDistanceUV = rampFn.createCurveRamp("maxDistanceUV", "maxDistanceUV");

	// project on normal
	projectOnNormal = numericFn.create("projectOnNormal", "projectOnNormal", MFnNumericData::kFloat, 0.0);
	numericFn.setKeyable(true);
	numericFn.setMin(0.0);
	numericFn.setMax(1.0);

	// normal direction limit
	normalDirectionLimit = enumFn.create("normalDirectionLimit", "normalDirectionLimit", 0);
	enumFn.setKeyable(true);
	enumFn.addField("Off", 0);
	enumFn.addField("Only positive", 1);
	enumFn.addField("Only negative", 2);

	// input shape
	inputShape = genericFn.create("inputShape", "inputShape");
	genericFn.setWritable(true);
	genericFn.setReadable(false);
	genericFn.addDataAccept(MFnNurbsCurveData::kNurbsCurve);
	genericFn.addDataAccept(MFnNurbsCurveData::kNurbsSurface);

	// input matrix
	inputMatrix = matrixFn.create("inputMatrix", "inputMatrix");
	matrixFn.setWritable(true);
	matrixFn.setReadable(false);

	//paintable
	//MGlobal::executeCommand("makePaintable -attrType multiFloat -shapeMode deformer dsAttract weights;");

	
	
	//ADD ATTRIBUTES
	stat = addAttribute(maxDistance);
		if (!stat) { stat.perror("addAttribute"); return stat;}
	stat = addAttribute(projectOnNormal);
		if (!stat) { stat.perror("addAttribute"); return stat; }
	stat = addAttribute(warnings);
		if (!stat) { stat.perror("addAttribute"); return stat; }
	stat = addAttribute(inputShape);
		if (!stat) { stat.perror("addAttribute"); return stat; }
	stat = addAttribute(inputMatrix);
		if (!stat) { stat.perror("addAttribute"); return stat; }
	stat = addAttribute(maxDistanceUV);
		if (!stat) { stat.perror("addAttribute"); return stat; }
	stat = addAttribute(falloff);
		if (!stat) { stat.perror("addAttribute"); return stat; }
	stat = addAttribute(normalDirectionLimit);
		if (!stat) { stat.perror("addAttribute"); return stat; }

	//ATTRIBUTE AFFECTS
	stat = attributeAffects(maxDistance, DsAttractDeformer::outputGeom);
		if (!stat) { stat.perror("attributeAffects"); return stat; }
	stat = attributeAffects(inputShape, DsAttractDeformer::outputGeom);
		if (!stat) { stat.perror("attributeAffects"); return stat; }
	stat = attributeAffects(inputMatrix, DsAttractDeformer::outputGeom);
		if (!stat) { stat.perror("attributeAffects"); return stat; }
	stat = attributeAffects(maxDistanceUV, DsAttractDeformer::outputGeom);
		if (!stat) { stat.perror("attributeAffects"); return stat; }
	stat = attributeAffects(falloff, DsAttractDeformer::outputGeom);
		if (!stat) { stat.perror("attributeAffects"); return stat; }
	stat = attributeAffects(projectOnNormal, DsAttractDeformer::outputGeom);
		if (!stat) { stat.perror("attributeAffects"); return stat; }
	stat = attributeAffects(normalDirectionLimit, DsAttractDeformer::outputGeom);
		if (!stat) { stat.perror("attributeAffects"); return stat; }

	return MS::kSuccess;
}

MStatus DsAttractDeformer::deform(MDataBlock& block,
	                              MItGeometry& iter,
	                              const MMatrix& worldMatrix,
	                              unsigned int multiIndex)
{	
	//-------------------------------
	MStatus returnStatus;
	MObject thisNode = thisMObject();

	//-------------------------------
	// get attributes
	// envelope
	MDataHandle envelopeHandle = block.inputValue(envelope, &returnStatus);
	CHECK_MSTATUS(returnStatus);
	float fEnvelope = envelopeHandle.asFloat();
	if (fEnvelope == 0.0)
		return returnStatus;

	// max distance
	MDataHandle maxDistanceHandle = block.inputValue(maxDistance, &returnStatus);
	CHECK_MSTATUS(returnStatus);
	float fMaxDistance = maxDistanceHandle.asFloat();
	if (fMaxDistance == 0.0)
		return returnStatus;
	
	// warnings
	MDataHandle warningsHandle = block.inputValue(warnings, &returnStatus);
	CHECK_MSTATUS(returnStatus);
	bool bWarnings = warningsHandle.asBool();

	// project on normal
	MDataHandle projectOnNormalHandle = block.inputValue(projectOnNormal, &returnStatus);
	CHECK_MSTATUS(returnStatus);
	float fProjectOnNormal = projectOnNormalHandle.asFloat();

	//inputGeom for fProjectOnNormal
	MFnMesh mfInputGeom;
	if (fProjectOnNormal > 0.0)
	{
		MArrayDataHandle hInput = block.outputArrayValue(input, &returnStatus);
		if (returnStatus != MS::kSuccess) return returnStatus;
		hInput.jumpToElement(multiIndex);
		MDataHandle hInputGeom = hInput.outputValue().child(inputGeom);
		MObject oInputGeom = hInputGeom.asMesh();
		mfInputGeom.setObject(oInputGeom);
	}

	// normal direction limit
	MDataHandle normalDirectionLimitHandle = block.inputValue(normalDirectionLimit, &returnStatus);
	CHECK_MSTATUS(returnStatus);
	short sNormalDirectionLimit = normalDirectionLimitHandle.asShort();

	// input matrix
	MDataHandle inputMatrixHandle = block.inputValue(inputMatrix, &returnStatus);
	CHECK_MSTATUS(returnStatus);
	MMatrix mInputMatrix = inputMatrixHandle.asMatrix();
	MPlug plugInputMatrix(thisNode, inputMatrix);
	if (plugInputMatrix.isConnected() == false)
	{
		if (bWarnings)
			MGlobal::displayInfo("Missing incoming connection to InputMatrix");
		return returnStatus;
	}

	// input shape
	MDataHandle inputShapeHandle = block.inputValue(inputShape, &returnStatus);
	CHECK_MSTATUS(returnStatus);
	MPlug plugInputShape(thisNode, inputShape);
	if (plugInputShape.isConnected() == false)
	{
		if (bWarnings)
			MGlobal::displayInfo("Missing incoming connection to InputShape");
		return returnStatus;
	}
	
	// ramp UV and falloff
	MRampAttribute rampMaxDistanceUV(thisNode, maxDistanceUV, &returnStatus);
	CHECK_MSTATUS(returnStatus);
	MRampAttribute rampFalloff(thisNode, falloff, &returnStatus);
	CHECK_MSTATUS(returnStatus);

	

	//--------------------------------------------------------------------------------------
	//DEFORM
	
	//Get dag 
	MPlugArray plugArInputShape;
	plugInputShape.connectedTo(plugArInputShape, true, false, &returnStatus);
	CHECK_MSTATUS(returnStatus);
	MPlug plugDagInputShape = plugArInputShape[0];
	MObject oDagInputShape = plugDagInputShape.node();
	MFnDagNode fnDagInputShape(oDagInputShape);
	MDagPath dagPathInputShape;
	fnDagInputShape.getPath(dagPathInputShape);

	//Identify inputShape type
	MFnData::Type typeInputShape = inputShapeHandle.type();
	MString strInputShapeType;
	MFnNurbsCurve fnTargetNurbsCurve; //curve
	MFnNurbsSurface fnTargetNurbsSurface; //surface
	if (typeInputShape == MFnNurbsCurveData::kNurbsCurve)
	{
		strInputShapeType = "curve";
		returnStatus = fnTargetNurbsCurve.setObject(dagPathInputShape);
		CHECK_MSTATUS(returnStatus);
	}

	else if (typeInputShape == MFnNurbsCurveData::kNurbsSurface)
	{
		strInputShapeType = "nurbs";
		returnStatus = fnTargetNurbsCurve.setObject(dagPathInputShape);
		CHECK_MSTATUS(returnStatus);
	}

	
	//--------------------------------------
	// store indices (for case of removed verticies)
	MIntArray iaIterIndices;
	while (! iter.isDone())
	{
		iaIterIndices.append(iter.index());
		iter.next();
	}
	iter.reset();

	//--------------------------------------
	// loop variables

	const MMatrix matInverse = worldMatrix.inverse();
	const double dCurveTolerance = 0.000001;

	float wPt, fRampMaxDist, fRampFallof;
	double dUValue, dPercent, dVecDotProduct;
	MPoint ptClosest, pt, loopPt;
	MPointOnMesh ptomMesh;
	MVector loopVec, closestVector, vecMove;
	MIntArray faceVerticies;
	bool failed = false; // OpenMP

	// store all verticies
	MPointArray verts;
	iter.allPositions(verts);
	int nPoints = verts.length();


	//--------------------------------------
	// loop

	for (int i = 0; i < nPoints; i++)
	{
		if (failed) continue;
		// weight, skip if zero
		wPt = weightValue(block, multiIndex, iaIterIndices[i]);
		if (wPt == 0.0) continue;
		pt = verts[i];
		//set to worldspace
		pt *= worldMatrix;

		// NURBS curve
		if (strInputShapeType == "curve")
		{
			// get closest point on curve and u value
			ptClosest = fnTargetNurbsCurve.closestPoint(pt, &dUValue, dCurveTolerance, MSpace::kWorld, &returnStatus);
			if (returnStatus != MS::kSuccess) { failed = true; continue; }
		}
		else if (strInputShapeType == "nurbs")
		{
			// get closest point and u value
			ptClosest = fnTargetNurbsSurface.closestPoint(pt, &dUValue, NULL, false, dCurveTolerance, MSpace::kWorld, &returnStatus);
			if (returnStatus != MS::kSuccess) { failed = true; continue; }
		}
		// move vector
		vecMove = ptClosest - pt;
		rampMaxDistanceUV.getValueAtPosition((float)dUValue, fRampMaxDist, &returnStatus);
		if (returnStatus!=MS::kSuccess){failed=true; continue; }
		//max distance each 
		float fMaxDistanceEach = fMaxDistance * fRampMaxDist;
		if (vecMove.length() < fMaxDistanceEach)
		{
			dPercent = vecMove.length() / fMaxDistanceEach;
			rampFalloff.getValueAtPosition((float)(1.0 - dPercent), fRampFallof, &returnStatus);
			if (returnStatus != MS::kSuccess) { failed = true; continue; }
			vecMove *= fRampFallof;

			if (fProjectOnNormal > 0.0)
			{
				//get normal
				#pragma omp critical
				returnStatus = mfInputGeom.getVertexNormal(iaIterIndices[i], false, loopVec, MSpace::kWorld);
				if (returnStatus != MS::kSuccess) { failed = true; continue; }
				//normalize
				loopVec.normalize();
				//project move vector on normal
				dVecDotProduct = vecMove * loopVec;
				loopVec *= dVecDotProduct;
				if (sNormalDirectionLimit == 1 && dVecDotProduct <= 0)
				{
					loopVec *= 0;
				}
				else if (sNormalDirectionLimit == 2 && dVecDotProduct > 0)
				{
					loopVec *= 0;
				}
				//blend
				vecMove = vecMove * (1.0 - fProjectOnNormal) + loopVec * fProjectOnNormal;
			}

			// adjust with envelope and painted weight
			vecMove *= fEnvelope * wPt;
			// new position
			pt += vecMove;
			//back to object space
			pt *= matInverse;
			verts[i] = pt;
		}
	}

	//set new positions
	iter.setAllPositions(verts);
	return returnStatus;
}

MStatus DsAttractDeformer::accessoryNodeSetup(MDagModifier& cmd)
{
	//initialize ramps
	MStatus stat;
	MObject thisNode = thisMObject();

	// falloff
	MRampAttribute rampFalloff(thisNode, DsAttractDeformer::falloff, &stat);

	MFloatArray f1, f2; //position, value;
	MIntArray i1;// interpolation

	f1.append(float(0.0));
	f1.append(float(1.0));

	f2.append(float(0.0));
	f2.append(float(1.0));

	i1.append(MRampAttribute::kSmooth);
	i1.append(MRampAttribute::kSmooth);

	rampFalloff.addEntries(f1, f2, i1);

	// max distance UV
	MRampAttribute rampMaxDistUv(thisNode, DsAttractDeformer::maxDistanceUV);

	f1.clear();
	f2.clear();
	i1.clear();

	f1.append(float(0.5));
	f2.append(float(1.0));
	i1.append(MRampAttribute::kSmooth);

	rampMaxDistUv.addEntries(f1, f2, i1);

	return stat;
}


MString DsAttractDeformer::AETemplate(MString nodeName)
{
	MString AEStr = "";
	AEStr += "global proc AE" + nodeName + "Template(string $nodeName)\n";
	AEStr += "{\n";
	AEStr += "AEswatchDisplay $nodeName;\n";
	AEStr += "editorTemplate -beginScrollLayout;\n";
	AEStr += "        AEgeometryFilterCommon $nodeName;\n";
	AEStr += "        editorTemplate -beginLayout \"Attract attributes\" -collapse 0 ;";
	AEStr += "            editorTemplate -addControl \"maximumDistance\";\n";
	AEStr += "            AEaddRampControl ($nodeName + \".falloff\");\n";
	AEStr += "            AEaddRampControl($nodeName + \".maxDistanceUV\");\n"; 
	AEStr += "        editorTemplate -endLayout;";

	AEStr += "        editorTemplate -beginLayout \"Normal vector\" -collapse 0 ;";
	AEStr += "            editorTemplate -addControl \"projectOnNormal\";\n";
	AEStr += "            editorTemplate -addControl \"normalDirectionLimit\";\n";
	AEStr += "        editorTemplate -endLayout;";

	AEStr += "		  editorTemplate -addExtraControls;";
	AEStr += "        AEgeometryFilterInclude $nodeName;\n";
	AEStr += "        editorTemplate -suppress \"weightList\";";
	AEStr += "        editorTemplate -suppress \"inputShape\";";
	AEStr += "        editorTemplate -suppress \"inputMatrix\";";
	AEStr += "editorTemplate -endScrollLayout;\n";
	AEStr += "};\n";
	return AEStr;
}


void dsAttractCreate()
{
	MString cr("");
	//
	cr += "global proc dsAttract()";
	cr += "{ \n";
	cr += "string $sel[] = `ls -sl -type \"transform\"`; \n";
	cr += "if( size($sel) != 2 ) \n";
	cr += " error \"Script requires two transforms to be selected.\"; \n";
	cr += "string $driverShapes[] = `listRelatives -children $sel[0]`; \n";
	cr += "string $drivenShapes[] = `listRelatives -children $sel[1]`; \n";
	cr += "string $drivenShapeType = objectType($driverShapes[0]); \n";
	cr += "if($drivenShapeType != \"nurbsCurve\" && \n";
	cr += "	  $drivenShapeType != \"nurbsSurface\" ) \n";
	cr += "	    error (\"Invalid driver shape type. Should be nurbsCurve/nurbsSurface, but got: \"+objectType($driverShapes[0])); \n";
	cr += "if( objectType($drivenShapes[0]) != \"mesh\" ) \n";
	cr += " error (\"Invalid driven shape type. Should be mesh. Instead got: \"+objectType($drivenShapes[0])); \n";
	cr += "string $def[] = `deformer -type dsAttract $sel[1]`; \n";
	cr += "connectAttr( $sel[0]+\".matrix\", $def[0]+\".inputMatrix\" ); \n";
	cr += "if( $drivenShapeType == \"mesh\" ) \n";
	cr += " connectAttr( $driverShapes[0]+\".outMesh\", $def[0]+\".inputShape\" ); \n";
	cr += "else \n";
	cr += " connectAttr( $driverShapes[0]+\".local\", $def[0]+\".inputShape\" ); \n";
	cr += "};";
	//
	MGlobal::executeCommand(cr);
}




// Plugin Registration
MStatus initializePlugin(MObject obj)
{
	MStatus status;
	MFnPlugin plugin(obj, "Dmitrii Shevchenko", "1.0", "2020");

	status = plugin.registerNode(DsAttractDeformer::nodeName,
								 DsAttractDeformer::id,
								 DsAttractDeformer::creator,
								 DsAttractDeformer::initialize,
								 MPxNode::kDeformerNode);
	MGlobal::executeCommand(DsAttractDeformer::AETemplate(DsAttractDeformer::nodeName));
	//MGlobal::executeCommand("refreshEditorTemplates; refreshAE;");
	dsAttractCreate();
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

	status = plugin.deregisterNode(DsAttractDeformer::id);
	if (!status)
	{
		status.perror("deregisterNode");
		return status;
	}

	return status;
}