#!/usr/bin/env python

import lx
import lxu.command
import lxu.select
import Tila_BatchExportModule as t
from Tila_BatchExportModule import user_value
from Tila_BatchExportModule import dialog
from Tila_BatchExportModule import file


class CmdBatchExport(lxu.command.BasicCommand):
    def __init__(self):
        lxu.command.BasicCommand.__init__(self)

        user_value.add_User_Values(self, t.userValues)

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

        userValues = user_value.query_User_Values(self, t.kit_prefix)

        if file.writePreset(userValues[53], userValues):
            dialog.init_message('info', 'Succeeded', 'Preset  \"%s\" saved successfully' % userValues[53])


    def cmd_Query(self, index, vaQuery):
        lx.notimpl()


lx.bless(CmdBatchExport, "tila.exportpreset.save")
