#!/usr/bin/env python

import modo
import lx
import lxu.command
import lxu.select
import traceback
import Tila_BatchExportModule as t
from Tila_BatchExportModule import user_value
from Tila_BatchExportModule import batch_export


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
            olderSelection = []

            currPath = currScn.filename

            if currPath is None:
                currPath = ""

            scnIndex = lx.eval('query sceneservice scene.index ? current')

            userValues = user_value.query_User_Values(self, t.kit_prefix)

            tbe = batch_export.TilaBacthExport

            userValues[1] = False
            userValues[2] = False

            if bool(userValues[0]):
                olderSelection = userSelection
                userSelection = tbe.select_visible_items(tbe(userSelection,
                                                         userSelectionCount,
                                                         scn,
                                                         currScn,
                                                         currPath,
                                                         scnIndex,
                                                         userValues))
                userSelectionCount = len(userSelection)

            tbe.batch_transform(tbe(userSelection,
                                    userSelectionCount,
                                    scn,
                                    currScn,
                                    currPath,
                                    scnIndex,
                                    userValues))

            if bool(userValues[0]):
                scn.select(olderSelection)

        except:
            lx.out(traceback.format_exc())

    def cmd_Query(self, index, vaQuery):
        lx.notimpl()


lx.bless(CmdBatchExport, "tila.batchtransform")