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

        reload(user_value)
        reload(t)

        user_value.add_User_Values(self, t.userValues)

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

            scnIndex = lx.eval('query sceneservice scene.index ? current')

            userValues = user_value.query_User_Values(self, 'tilaBExp.')

            tbe = batch_export.TilaBacthExport

            userValues[0] = True
            userValues[1] = True

            tbe.batch_folder(tbe(userSelection,
                                 userSelectionCount,
                                 scn,
                                 currScn,
                                 currPath,
                                 scnIndex,
                                 userValues))
        except:
            lx.out(traceback.format_exc())

    def cmd_Query(self, index, vaQuery):
        lx.notimpl()


lx.bless(CmdBatchExport, "tila.batchfolder")