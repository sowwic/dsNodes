from maya import cmds as mc, mel
import os

MAYA_APP_DIR = mel.eval('getenv ("MAYA_APP_DIR")')


mc.file(new=1,f=1)
mc.unloadPlugin("dsGhosting")
mc.loadPlugin(os.path.join(MAYA_APP_DIR, 'scripts\dsNodes\dsGhosting\plugins\dsGhosting.py'))
