#include "dsRaycastNode.h"

MString Raycast::AETemplate(MString nodeName)
{
	MString AEStr = "";
	AEStr += "global proc AE" + nodeName + "Template(string $nodeName)\n";
	AEStr += "{\n";
	AEStr += "editorTemplate -beginScrollLayout;\n";
	AEStr += "        editorTemplate -beginLayout \"Ray Attributes\" -collapse 0 ;";
	AEStr += "            editorTemplate -addControl \"mode\";\n";
	AEStr += "            editorTemplate -addControl \"aimAxis\";\n";
	AEStr += "            editorTemplate -addControl \"sourceMatrix\";\n";
	AEStr += "            editorTemplate -addControl \"aimMatrix\";\n";
	AEStr += "        editorTemplate -endLayout;";

	AEStr += "        editorTemplate -beginLayout \"Casting Attributes\" -collapse 0 ;";
	AEStr += "            editorTemplate -addControl \"castDistance\";\n";
	AEStr += "            editorTemplate -addControl \"bothWays\";\n";
	AEStr += "        editorTemplate -endLayout;";

	AEStr += "        editorTemplate -beginLayout \"Hitpoint Attributes\" -collapse 0 ;";
	AEStr += "            editorTemplate -addControl \"upVector\";\n";
	AEStr += "            editorTemplate -addControl \"rotate\";\n";
	AEStr += "            editorTemplate -addControl \"offsetVector\";\n";
	AEStr += "            editorTemplate -addControl \"offset\";\n";
	AEStr += "        editorTemplate -endLayout;";
	AEStr += "		  editorTemplate -addExtraControls;";
	AEStr += "editorTemplate -suppress \"targetMesh\";";
	AEStr += "editorTemplate -endScrollLayout;\n";
	AEStr += "}\n";
	return AEStr;
}


MStatus Raycast::compute(const MPlug &plug, MDataBlock &data)
{
	MStatus returnStatus;

	if ((plug == outHitPoint) || (plug == outNormal) || (plug == outHitDistance) || (plug == outRotation))
	{	
		//INPUT HANDLES
		MDataHandle inMeshHandle = data.inputValue(inMesh, &returnStatus);
		CHECK_MSTATUS(returnStatus);
		MDataHandle inModeHandle = data.inputValue(inMode, &returnStatus);
		CHECK_MSTATUS(returnStatus);
		MDataHandle inSourceMatrixHandle = data.inputValue(inSourceMatrix, &returnStatus);
		CHECK_MSTATUS(returnStatus);
		MDataHandle inAimHandle = data.inputValue(inAim, &returnStatus);
		CHECK_MSTATUS(returnStatus);
		MDataHandle inAimAxisHandle = data.inputValue(inAimAxis, &returnStatus);
		CHECK_MSTATUS(returnStatus);
		MDataHandle inUpVectorHandle = data.inputValue(inUpVector, &returnStatus);
		CHECK_MSTATUS(returnStatus);
		MDataHandle inDistanceHandle = data.inputValue(inDistance, &returnStatus);
		CHECK_MSTATUS(returnStatus);
		MDataHandle inBotheWaysHandle = data.inputValue(inBothWays, &returnStatus);
		CHECK_MSTATUS(returnStatus);
		MDataHandle inOffsetHandle = data.inputValue(inOffset, &returnStatus);
		CHECK_MSTATUS(returnStatus);
		MDataHandle inOfsVectorEnumHandle = data.inputValue(inOfsVectorEnum, &returnStatus);
		CHECK_MSTATUS(returnStatus);
		//MDataHandle inDebugHandle = data.inputValue(inDebug, &returnStatus);
		//CHECK_MSTATUS(returnStatus);
		
		//OUTPUT HANDLES
		MDataHandle outHitHandle = data.outputValue(outHitPoint, &returnStatus);
		CHECK_MSTATUS(returnStatus);
		MDataHandle outNormalHandle = data.outputValue(outNormal, &returnStatus);
		CHECK_MSTATUS(returnStatus);
		MDataHandle outRotationXHandle = data.outputValue(outRotationX, &returnStatus);
		CHECK_MSTATUS(returnStatus);
		MDataHandle outRotationYHandle = data.outputValue(outRotationY, &returnStatus);
		CHECK_MSTATUS(returnStatus);
		MDataHandle outRotationZHandle = data.outputValue(outRotationZ, &returnStatus);
		CHECK_MSTATUS(returnStatus);
		MDataHandle outHitDistanceHandle = data.outputValue(outHitDistance, &returnStatus);
		CHECK_MSTATUS(returnStatus);
	

		//GET DATA OFF HANDLES
		//bool inDebug = inDebugHandle.asBool();
		MFnMesh fnMesh(inMeshHandle.data());
		MMatrix inAim = inAimHandle.asMatrix();
		MVector inUpVector = inUpVectorHandle.asVector();
		float inDistance = inDistanceHandle.asFloat();
		bool inBothWays = inBotheWaysHandle.asBool();
		short inMode = inModeHandle.asShort();
		float inOffset = inOffsetHandle.asFloat();
		bool inOfsVectorEnum = inOfsVectorEnumHandle.asBool();
		MFloatPoint hitpoint = MFloatPoint();
		MMatrix inSourceMatrix = inSourceMatrixHandle.asMatrix();
		short inAimAxis = inAimAxisHandle.asShort();

		//GET AXIS VECTORS FROM SOURCE MATRIX
		double sourceAxisX[] = { inSourceMatrix(0, 0), inSourceMatrix(0,1), inSourceMatrix(0,2) };
		double sourceAxisY[] = { inSourceMatrix(1, 0), inSourceMatrix(1,1), inSourceMatrix(1,2) };
		double sourceAxisZ[] = { inSourceMatrix(2, 0), inSourceMatrix(2,1), inSourceMatrix(2,2) };

		//GET SOURCE POINT FROM MATRIX
		double sourceTranslate[] = { inSourceMatrix(3, 0), inSourceMatrix(3,1), inSourceMatrix(3,2) };
		MFloatPoint sourcePoint = MFloatPoint(sourceTranslate[0], sourceTranslate[1], sourceTranslate[2]);

		//GET AIM POINT FROM MATRIX
		double aimTranslate[] = { inAim(3, 0), inAim(3, 1), inAim(3, 2)};
		MFloatPoint aimPoint = MFloatPoint(aimTranslate[0], aimTranslate[1], aimTranslate[2]);

		//GET AIM VECTOR
		MFloatVector aimVector;
		if (inMode == 0)
		{
			aimVector = MFloatVector(aimPoint.x - sourcePoint.x , aimPoint.y - sourcePoint.y, aimPoint.z - sourcePoint.z); //Relative vector
		}
		else if (inMode == 1)
		{
			if (inAimAxis == 0)
			{
				aimVector = MFloatVector(sourceAxisX[0], sourceAxisX[1], sourceAxisX[2]);
			}
			else if (inAimAxis == 1)
			{
				aimVector = MFloatVector(sourceAxisY[0], sourceAxisY[1], sourceAxisY[2]);
			}
			else if (inAimAxis == 2)
			{
				aimVector = MFloatVector(sourceAxisZ[0], sourceAxisZ[1], sourceAxisZ[2]);
			}
		}

		//GET HIT POINT
		float fHitRayParams;
		int iaHitFaces;
		int iaHitTriangles;

		bool intersectStatus = fnMesh.closestIntersection(  sourcePoint,
															aimVector,
															NULL,
															NULL,
															false,
															MSpace::kWorld,
															inDistance,
															inBothWays,
															NULL,
															hitpoint,
															&fHitRayParams,
															&iaHitFaces,
															&iaHitTriangles,
															NULL,
															NULL,
															0.000001f
															);
			
		//NORMAL
		MVector normalVector = MVector();
		MPoint mHitPoint = MPoint(hitpoint);

		fnMesh.getClosestNormal(mHitPoint, normalVector, MSpace::kWorld);

		//APPLY OFFSET
		MFloatPoint offsetPoint;
		if (inOfsVectorEnum)
		{
			MFloatVector fNormalVector = MFloatVector(normalVector);
			offsetPoint = MFloatPoint(inOffset * fNormalVector.x, inOffset * fNormalVector.y, inOffset * fNormalVector.z);
		}
		else
		{
			offsetPoint = MFloatPoint(inOffset * aimVector.x, inOffset * aimVector.y, inOffset * aimVector.z);
		}
		hitpoint.x += offsetPoint.x;
		hitpoint.y += offsetPoint.y;
		hitpoint.z += offsetPoint.z;

		//CREATING ROTATION
		
		MVector crossVector = normalVector ^ inUpVector;
		inUpVector = normalVector ^ crossVector;
		double vectorArray[4][4] = {{normalVector.x, normalVector.y, normalVector.z, 0.0},
									{inUpVector.x, inUpVector.y, inUpVector.z, 0.0},
									{crossVector.x, crossVector.y, crossVector.z, 0.0},
									{0.0, 0.0, 0.0, 0.0}
									};
		MMatrix baseMatrix = MMatrix(vectorArray);
		MTransformationMatrix transformMatrix = MTransformationMatrix(baseMatrix);
		MEulerRotation eulerRot = transformMatrix.eulerRotation();
		MAngle eulerRotX = MAngle(eulerRot.x);
		MAngle eulerRotY = MAngle(eulerRot.y);
		MAngle eulerRotZ = MAngle(eulerRot.z);


		//SET OUTPUT HANDLES
		outHitHandle.setMFloatVector(MFloatVector(hitpoint));
		outNormalHandle.setMFloatVector(MFloatVector(normalVector));
		outRotationXHandle.setMAngle(eulerRotX);
		outRotationYHandle.setMAngle(eulerRotY);
		outRotationZHandle.setMAngle(eulerRotZ);
		outHitDistanceHandle.setFloat(fHitRayParams);

		outHitHandle.setClean();
		outNormalHandle.setClean();
		outRotationXHandle.setClean();
		outRotationYHandle.setClean();
		outRotationZHandle.setClean();
		outHitDistanceHandle.setClean();

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
//Init raycast node attributes
{
	
	MFnTypedAttribute typedAttributeFn;
	MFnNumericAttribute numericAttributeFn;
	MFnUnitAttribute unitAttributeFn;
	MFnEnumAttribute enumAttributeFn;
	MFnMatrixAttribute matrixAttributeFn;
	MStatus stat;

	//INPUT
	//Debug
	//inDebug = numericAttributeFn.create("debugRay", "debugRay", MFnNumericData::kBoolean, 0);

	//Mesh
	inMesh = typedAttributeFn.create("targetMesh", "tm", MFnData::kMesh);
	typedAttributeFn.setReadable(false);

	//Mode
	inMode = enumAttributeFn.create("mode", "mode", 0);
	enumAttributeFn.addField("Between two", 0);
	enumAttributeFn.addField("From single", 1);

	//Aim axis
	inAimAxis = enumAttributeFn.create("aimAxis", "aimAxis", 0);
	enumAttributeFn.addField("X", 0);
	enumAttributeFn.addField("Y", 1);
	enumAttributeFn.addField("Z", 2);

	//Source matrix
	inSourceMatrix = matrixAttributeFn.create("sourceMatrix", "sourceMtx");
	
	//Aim matrix
	inAim = matrixAttributeFn.create("aimMatrix", "aimMtx");

	//Up vector
	inUpVector = numericAttributeFn.createPoint("upVector", "upVector");

	//Distance
	inDistance = numericAttributeFn.create("castDistance", "castDistance", MFnNumericData::kFloat, 100.0);

	//Test direction
	inBothWays = numericAttributeFn.create("bothWays", "bw", MFnNumericData::kBoolean, 1.0);

	//Offset
	inOffset = numericAttributeFn.create("offset", "offs", MFnNumericData::kFloat, 0.0);

	//Offset vector enum
	inOfsVectorEnum = enumAttributeFn.create("offsetVector", "offsetVector", 0);
	enumAttributeFn.addField("Aim", 0);
	enumAttributeFn.addField("Normal", 1);


	//OUTPUT
	//Hit Point
	outHitPoint = numericAttributeFn.createPoint("hitPoint", "hit");
	numericAttributeFn.setWritable(false);
	
	//Normal vector
	outNormal = numericAttributeFn.createPoint("normal", "n");
	numericAttributeFn.setWritable(false);

	//Rotation
	outRotationX = unitAttributeFn.create("rotateX", "rx", MFnUnitAttribute::kAngle);
	outRotationY = unitAttributeFn.create("rotateY", "ry", MFnUnitAttribute::kAngle);
	outRotationZ = unitAttributeFn.create("rotateZ", "rz", MFnUnitAttribute::kAngle);
	outRotation = numericAttributeFn.create("rotate", "r", outRotationX, outRotationY, outRotationZ);

	//Hit distance
	outHitDistance = numericAttributeFn.create("hitDistance", "hitDistance", MFnNumericData::kFloat);
	numericAttributeFn.setWritable(false);




	//ADD ATTRIBUTES
	//Input
	//stat = addAttribute(inDebug);
		//if (!stat) { stat.perror("addAttribute"); return stat;}
	stat = addAttribute(inMesh);
		if (!stat) { stat.perror("addAttribute"); return stat;}
	stat = addAttribute(inMode);
		if (!stat) { stat.perror("addAttribute"); return stat;}
	stat = addAttribute(inAimAxis);
		if (!stat) { stat.perror("addAttribute"); return stat;}
	stat = addAttribute(inSourceMatrix);
		if (!stat) { stat.perror("addAttribute"); return stat;}
	stat = addAttribute(inAim);
		if (!stat) { stat.perror("addAttribute"); return stat;}
	stat = addAttribute(inUpVector);
		if (!stat) { stat.perror("addAttribute"); return stat;}
	stat = addAttribute(inDistance);
		if (!stat) { stat.perror("addAttribute"); return stat;}
	stat = addAttribute(inBothWays);
		if (!stat) { stat.perror("addAttribute"); return stat;}
	stat = addAttribute(inOffset);
		if (!stat) { stat.perror("addAttribute"); return stat;}
	stat = addAttribute(inOfsVectorEnum);
		if (!stat) { stat.perror("addAttribute"); return stat;}

	//Output
	stat = addAttribute(outHitPoint);
		if (!stat) { stat.perror("addAttribute"); return stat;}
	stat = addAttribute(outNormal);
		if (!stat) { stat.perror("addAttribute"); return stat;}
	stat = addAttribute(outRotation);
		if (!stat) { stat.perror("addAttribute"); return stat;}
	stat = addAttribute(outHitDistance);
		if (!stat) { stat.perror("addAttribute"); return stat;}


	//ATTRIBUTE AFFECTS
	stat = attributeAffects(inMesh, outHitPoint);
		if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects(inAim, outHitPoint);
		if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects(inAimAxis, outHitPoint);
		if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects(inSourceMatrix, outHitPoint);
		if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects(inOffset, outHitPoint);
		if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects(inOfsVectorEnum, outHitPoint);
		if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects(inMode, outHitPoint);
		if (!stat) { stat.perror("attributeAffects"); return stat;}
	

	stat = attributeAffects(inMesh, outNormal);
		if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects(inSourceMatrix, outNormal);
		if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects(inAimAxis, outNormal);
		if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects(inAim, outNormal);
		if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects(inUpVector, outNormal);
		if (!stat) { stat.perror("attributeAffects"); return stat;}
	stat = attributeAffects(inMode, outNormal);
		if (!stat) { stat.perror("attributeAffects"); return stat;}

	stat = attributeAffects(inMesh, outRotation);
		if (!stat) { stat.perror("attributeAffects"); return stat; }
	stat = attributeAffects(inSourceMatrix, outRotation);
		if (!stat) { stat.perror("attributeAffects"); return stat; }
	stat = attributeAffects(inAimAxis, outRotation);
		if (!stat) { stat.perror("attributeAffects"); return stat; }
	stat = attributeAffects(inAim, outRotation);
		if (!stat) { stat.perror("attributeAffects"); return stat; }
	stat = attributeAffects(inUpVector, outRotation);
		if (!stat) { stat.perror("attributeAffects"); return stat; }
	stat = attributeAffects(inMode, outRotation);
		if (!stat) { stat.perror("attributeAffects"); return stat; }

	stat = attributeAffects(inMesh, outHitDistance);
		if (!stat) { stat.perror("attributeAffects"); return stat; }
	stat = attributeAffects(inSourceMatrix, outHitDistance);
		if (!stat) { stat.perror("attributeAffects"); return stat; }
	stat = attributeAffects(inAimAxis, outHitDistance);
		if (!stat) { stat.perror("attributeAffects"); return stat; }
	stat = attributeAffects(inAim, outHitDistance);
		if (!stat) { stat.perror("attributeAffects"); return stat; }
	stat = attributeAffects(inUpVector, outHitDistance);
		if (!stat) { stat.perror("attributeAffects"); return stat; }
	stat = attributeAffects(inMode, outHitDistance);
		if (!stat) { stat.perror("attributeAffects"); return stat; }


	return MS::kSuccess;
}


//---------------------------------------------------------------------------
//---------------------------------------------------------------------------
// Plugin Registration
//---------------------------------------------------------------------------
//---------------------------------------------------------------------------

MStatus initializePlugin(MObject obj)
{
	MStatus status;
	MFnPlugin plugin(obj, "Dmitrii Shevchenko", "1.0", "2020");
	MGlobal::executeCommand(Raycast::AETemplate(Raycast::nodeName));
	
	status = plugin.registerNode("dsRaycast", 
								Raycast::id, 
								Raycast::creator, 
								Raycast::initialize);

	//MGlobal::executeCommand("refreshEditorTemplates; refreshAE;");

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

