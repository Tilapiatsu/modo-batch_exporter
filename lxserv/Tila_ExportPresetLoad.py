#!/usr/bin/env python

import os
import lx
import lxu.command
import lxu.select
from os.path import isfile
import Tila_BatchExportModule as t
from Tila_BatchExportModule import dialog
from Tila_BatchExportModule import file



class CmdBatchExport(lxu.command.BasicCommand):
    def __init__(self):
        lxu.command.BasicCommand.__init__(self)

        self.dyna_Add('presetIndex', lx.symbol.sTYPE_INTEGER)

        self.presets = [f for f in os.listdir(t.preset_path) if isfile(os.path.join(t.preset_path, f))]

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

        index = self.dyna_Int(0)
        name = os.path.splitext(self.presets[index])[0]

        if not file.loadPreset(name):
            dialog.init_message('error', 'Error', 'Error while loading Preset \"%s\"' % name)

    def cmd_Query(self, index, vaQuery):
        lx.notimpl()


lx.bless(CmdBatchExport, "tila.exportpreset.load")

