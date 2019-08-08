import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMayaRender as OpenMayaRender
import maya.cmds as mc


def setCamera(*args):
    view = OpenMayaUI.M3dView.active3dView()

    # Get a renderer, then a function table
    glRenderer = OpenMayaRender.MHardwareRenderer.theRenderer()
    glFT = glRenderer.glFunctionTable()

    view.beginGL()

    glFT.glPushAttrib(OpenMayaRender.MGL_LINE_BIT)
    glFT.glLineWidth(5.0)

    glFT.glBegin(OpenMayaRender.MGL_LINES)

    glFT.glColor3f(1.0, 0.0, 0.0)
    glFT.glVertex3f(0.0, 0.0, 0.0)
    glFT.glVertex3f(3.0, 0.0, 0.0)

    glFT.glColor3f(0.0, 1.0, 0.0)
    glFT.glVertex3f(0.0, 0.0, 0.0)
    glFT.glVertex3f(0.0, 3.0, 0.0)

    glFT.glColor3f(0.0, 0.0, 1.0)
    glFT.glVertex3f(0.0, 0.0, 0.0)
    glFT.glVertex3f(0.0, 0.0, 3.0)

    glFT.glEnd()

    glFT.glPopAttrib()

    view.endGL()

if __name__ == '__main__':

    panel = mc.getPanel(withFocus=True)
    callBack = OpenMayaUI.MUiMessage.add3dViewPostRenderMsgCallback(
        panel, setCamera)

    view = OpenMayaUI.M3dView.active3dView()
    view.refresh(True, True)