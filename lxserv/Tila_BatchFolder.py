#!/usr/bin/env python

import modo
import lx
import lxu.command
import lxu.select
import traceback
import Tila_BatchExportModule as t
from Tila_BatchExportModule import user_value
from Tila_BatchExportModule import batch_export

############## TODO ###################
'''
 - find a way to keep last output folder in memory
 - Create a progress bar https://gist.github.com/tcrowson/e3d401055739d1a72863
 - Implement a log windows to see exactly what's happening behind ( That file is exporting to this location 9 / 26 )
 - Add "Export Visible" Feature
 - Add "Merge Mesh" feature
 - Add "Create UDIM UV From Material Set" Feature
 - polycount limit to avoid crash : select the first 1 M polys and transform them then select the next 1 M Poly etc ...

'''


class CmdBatchExport(lxu.command.BasicCommand):
    def __init__(self):
        lxu.command.BasicCommand.__init__(self)

        self.dyna_Add('exportEach_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(2, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('exportHierarchy_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(3, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('triple_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(4, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('resetPos_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(5, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('resetRot_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(6, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('resetSca_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(7, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('resetShe_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(8, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('freezePos_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(9, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('freezeRot_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(10, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('freezeSca_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(11, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('freezeShe_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(12, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('freezeGeo_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(13, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('freezeInstance_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(14, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('posX', lx.symbol.sTYPE_FLOAT)
        self.basic_SetFlags(15, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('posY', lx.symbol.sTYPE_FLOAT)
        self.basic_SetFlags(16, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('posZ', lx.symbol.sTYPE_FLOAT)
        self.basic_SetFlags(17, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('rotX', lx.symbol.sTYPE_FLOAT)
        self.basic_SetFlags(18, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('rotY', lx.symbol.sTYPE_FLOAT)
        self.basic_SetFlags(19, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('rotZ', lx.symbol.sTYPE_FLOAT)
        self.basic_SetFlags(20, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('scaX', lx.symbol.sTYPE_FLOAT)
        self.basic_SetFlags(21, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('scaY', lx.symbol.sTYPE_FLOAT)
        self.basic_SetFlags(22, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('scaZ', lx.symbol.sTYPE_FLOAT)
        self.basic_SetFlags(23, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('smoothAngle_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(24, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('smoothAngle', lx.symbol.sTYPE_FLOAT)
        self.basic_SetFlags(25, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('hardenUvBorder_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(26, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('uvMapName', lx.symbol.sTYPE_STRING)
        self.basic_SetFlags(27, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('exportFormatFbx_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(28, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('exportFormatObj_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(29, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('exportFormatLxo_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(30, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('exportFormatLwo_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(31, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('exportFormatAbc_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(32, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('exportFormatAbchdf_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(33, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('exportFormatDae_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(34, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('exportFormatDxf_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(35, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('exportFormat3dm_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(36, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('exportFormatGeo_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(37, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('exportCageMorph_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(38, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('cageMorphMapName', lx.symbol.sTYPE_STRING)
        self.basic_SetFlags(39, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('openDestFolder_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(40, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('applyMorphMap_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(41, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('morphMapName', lx.symbol.sTYPE_STRING)
        self.basic_SetFlags(42, lx.symbol.fCMDARG_OPTIONAL)

    def cmd_Flags(self):
        return lx.symbol.fCMD_MODEL | lx.symbol.fCMD_UNDO

    def basic_Enable(self, msg):
        return True

    def cmd_Interact(self):
        pass

    def basic_Execute(self, msg, flags):
        reload(t)
        reload(batch_export)
        try:
            scn = modo.Scene()
            currScn = modo.scene.current()

            userSelection = scn.selected
            userSelectionCount = len(userSelection)

            currPath = currScn.filename

            if currPath is None:
                currPath = ""

            fbxExportType = lx.eval1('user.value sceneio.fbx.save.exportType ?')
            fbxTriangulate = False

            scnIndex = lx.eval('query sceneservice scene.index ? current')

            upAxis = lx.eval('pref.value units.upAxis ?')
            iUpAxis = upAxis

            userValues = user_value.query_User_Values(self, 'tilaBExp.')

            tbe = batch_export.TilaBacthExport

            tbe.process_items(tbe(userSelection, userSelectionCount, scn, currScn, currPath, scnIndex, upAxis, iUpAxis, fbxExportType, fbxTriangulate, self.dyna_Bool(0), self.dyna_Bool(1), bool(userValues[2]), bool(userValues[3]), bool(userValues[4]), bool(userValues[5]), bool(userValues[6]), bool(userValues[7]), bool(userValues[8]), bool(userValues[9]), bool(userValues[10]), bool(userValues[11]), bool(userValues[12]), bool(userValues[13]), bool(userValues[14]), userValues[15], userValues[16], userValues[17], userValues[18], userValues[19], userValues[20], userValues[21], userValues[22], userValues[23], bool(userValues[24]), userValues[25], bool(userValues[26]), userValues[27], bool(userValues[28]), bool(userValues[29]), bool(userValues[30]), bool(userValues[31]), bool(userValues[32]), bool(userValues[33]), bool(userValues[34]), bool(userValues[35]), bool(userValues[36]), bool(userValues[37]), bool(userValues[38]), userValues[39], bool(userValues[40]), bool(userValues[41]), userValues[42]))
        except:
            lx.out(traceback.format_exc())

    def cmd_Query(self, index, vaQuery):
        lx.notimpl()


lx.bless(CmdBatchExport, "tila.batchfolder")