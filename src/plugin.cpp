#include <maya/MFnPlugin.h>
#include "dsAttractDeformer.h"
#include "dsRaycast.h"

MStatus initializePlugin(MObject obj)
{
    MStatus status;
    MFnPlugin plugin(obj, "Dmitrii Shevchenko", "1.0", "2020");

    // Raycast
    status = plugin.registerNode("dsRaycast",
                                 Raycast::id,
                                 Raycast::creator,
                                 Raycast::initialize);
    if (!status)
    {
        status.perror("Failed to register dsRaycast node");
        return status;
    }
    MGlobal::executeCommand(Raycast::AETemplate(Raycast::nodeName));

    // Attract deformer
    status = plugin.registerNode(DsAttractDeformer::nodeName,
                                 DsAttractDeformer::id,
                                 DsAttractDeformer::creator,
                                 DsAttractDeformer::initialize,
                                 MPxNode::kDeformerNode);
    if (!status)
    {
        status.perror("Failed to register dsAttractDeformer node");
        return status;
    }
    MGlobal::executeCommand(DsAttractDeformer::AETemplate(DsAttractDeformer::nodeName));
    DsAttractDeformer::defineMelCreateCommand();

    return status;
}

MStatus uninitializePlugin(MObject obj)
{
    MStatus status;
    MFnPlugin plugin(obj);

    // Raycast
    status = plugin.deregisterNode(Raycast::id);
    if (!status)
    {
        status.perror("Failed to deregister dsRaycast node.");
        return status;
    }

    // Attract deformer
    status = plugin.deregisterNode(DsAttractDeformer::id);
    if (!status)
    {
        status.perror("Failed to deregister dsAttract deformer node.");
        return status;
    }

    return status;
}