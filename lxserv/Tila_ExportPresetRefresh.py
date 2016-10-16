#!/usr/bin/env python

import os
from os.path import isfile
import lx
import lxu.command
import lxu.select

from Tila_BatchExportModule import file
import Tila_BatchExportModule as t


class CmdBatchExport(lxu.command.BasicCommand):
    def __init__(self):
        lxu.command.BasicCommand.__init__(self)

        self.presets = [f for f in os.listdir(t.preset_path) if isfile(os.path.join(t.preset_path, f))]

    def cmd_Flags(self):
        return lx.symbol.fCMD_MODEL | lx.symbol.fCMD_UNDO

    def basic_Enable(self, msg):
        return True

    def cmd_Interact(self):
        pass

    def basic_Execute(self, msg, flags):
        reload(file)

        file.refreshPresetForm(t.preset_hash, self.presets)


    def cmd_Query(self, index, vaQuery):
        lx.notimpl()


lx.bless(CmdBatchExport, "tila.exportpreset.refresh")
