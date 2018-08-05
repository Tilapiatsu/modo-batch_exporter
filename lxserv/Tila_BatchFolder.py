#!/usr/bin/env python

import modo
import lx
import lxu.command
import lxu.select
import traceback
import Tila_BatchExportModule as t
from Tila_BatchExportModule import user_value, batch_export


class CmdBatchExport(lxu.command.BasicCommand):
    def __init__(self):
        lxu.command.BasicCommand.__init__(self)

        reload(t)
        reload(user_value)
        reload(batch_export)

        user_value.add_User_Values(self, t.userValues)

    def cmd_Flags(self):
        return lx.symbol.fCMD_MODEL | lx.symbol.fCMD_UNDO

    def basic_Enable(self, msg):
        return True

    def cmd_Interact(self):
        pass

    def basic_Execute(self, msg, flags):
        reload(t)
        try:
            tbe = batch_export.TilaBacthExport

            userValues = user_value.query_User_Values(self, t.kit_prefix)
            userValues[1] = True

            if userValues[3]:
                tbe.batch_folder(tbe(userValues))
            elif userValues[2]:
                tbe.batch_files(tbe(userValues))
        except:
            lx.out(traceback.format_exc())

    def cmd_Query(self, index, vaQuery):
        lx.notimpl()


lx.bless(CmdBatchExport, t.TILA_BATCH_FOLDER)
