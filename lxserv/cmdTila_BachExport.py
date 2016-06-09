#!/usr/bin/env python

import modo
import sys
import subprocess
import lx
import lxifc
import lxu.command
import lxu.select
import traceback

class CmdBatchExport(lxu.command.BasicCommand):
    def __init__(self):
        lxu.command.BasicCommand.__init__(self)

        self.dyna_Add('exportFile_sw', lx.symbol.sTYPE_BOOLEAN)
        self.dyna_Add('scanFiles_sw', lx.symbol.sTYPE_BOOLEAN)

        self.dyna_Add('triple_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(2, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('resetPos_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(3, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('resetRot_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(4, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('resetSca_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(5, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('resetShe_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(6, lx.symbol.fCMDARG_OPTIONAL)

    def cmd_Flags(self):
        return lx.symbol.fCMD_MODEL | lx.symbol.fCMD_UNDO

    def basic_Enable(self, msg):
        return True

    def cmd_Interact(self):
        pass

    def basic_Execute(self, msg, flags):
        try:
            print self.attr_GetFlt(0)
        except:
            lx.out(traceback.format_exc())

    def cmd_Query(self, index, vaQuery):
        lx.notimpl()


lx.bless(CmdBatchExport, "tila.batchexport")