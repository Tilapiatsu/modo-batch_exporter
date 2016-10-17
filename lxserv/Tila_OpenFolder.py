#!/usr/bin/env python

import modo
import lx
import lxu.command
import lxu.select
import Tila_BatchExportModule as t
from Tila_BatchExportModule import dialog
from Tila_BatchExportModule import file


class CmdBatchExport(lxu.command.BasicCommand):
    def __init__(self):
        lxu.command.BasicCommand.__init__(self)

        self.dyna_Add('bExpFolderIndex', lx.symbol.sTYPE_INTEGER)

    def cmd_Flags(self):
        return lx.symbol.fCMD_MODEL | lx.symbol.fCMD_UNDO

    def basic_Enable(self, msg):
        return True

    def cmd_Interact(self):
        pass

    def basic_Execute(self, msg, flags):
        reload(t)
        reload(file)
        reload(dialog)

        if self.dyna_Int(0) == 0:
            dialog.open_folder(file.getLatestPath(t.config_export_path))
        if self.dyna_Int(0) == 1:
            dialog.open_folder(file.getLatestPath(t.config_browse_dest_path))

    def cmd_Query(self, index, vaQuery):
        lx.notimpl()


lx.bless(CmdBatchExport, t.TILA_OPEN_EXPORT_FOLDER)
