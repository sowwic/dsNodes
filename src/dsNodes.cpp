#include "dsAttractDeformer.cpp"
#include "dsRaycast.cpp"

MStatus initializePlugin(MObject obj)
{
    MStatus status;
    MFnPlugin plugin(obj, "Dmitrii Shevchenko", "1.0", "2020");
    status = DsAttractDeformer::registerAsPartOfPlugin(plugin);
    if (!status)
        return status;
    status = Raycast::registerAsPartOfPlugin(plugin);
    if (!status)
        return status;

    return status;
}

MStatus uninitializePlugin(MObject obj)
{
    MStatus status;
    MFnPlugin plugin(obj);
    status = DsAttractDeformer::deregisterAsPartOfPlugin(plugin);
    if (!status)
        return status;
    status = Raycast::deregisterAsPartOfPlugin(plugin);
    if (!status)
        return status;

    return status;
}