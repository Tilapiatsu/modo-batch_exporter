#!/usr/bin/env python

import modo
import sys
import subprocess
import lx
import lxifc
import lxu.command
import lxu.select
import traceback


class TilaBacthExport ():
    global debug_log
    global debug_mode

    debug_log = True

    debug_mode = False

    def __init__(self, exportFile_sw, scanFiles_sw, triple_sw, resetPos_sw, resetRot_sw, resetSca_sw, resetShe_sw):
        self.exportFile_sw = exportFile_sw
        self.scanFiles_sw = scanFiles_sw
        self.triple_sw = triple_sw
        self.resetPos_sw = resetPos_sw
        self.resetRot_sw = resetRot_sw
        self.resetSca_sw = resetSca_sw
        self.resetShe_sw = resetShe_sw

    def print_log(self, message):
        lx.out("TILA_BATCH_EXPORT : " + message)

    def print_debug_log(self, message):
        if debug_log:
            TilaBacthExport.print_log(self, 'Debug : ' + message)

    def transform_log(self, message):
        TilaBacthExport.print_log(self, "Transform_Item : " + message)

    def processing_log(self, message):
        TilaBacthExport.print_log(self, "Processing_Item : " + message)

    def debug(self, message):
        if debug_mode:
            TilaBacthExport.print_debug_log(self, message)

    def export_log(self, message):
        TilaBacthExport.print_log(self, "Exporting_File : " + message)


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
            tbe = TilaBacthExport
            tbe.processing_log(tbe(1, 1, 1, 1, 1, 1, 1), str(self.attr_GetFlt(0)))
        except:
            lx.out(traceback.format_exc())

    def cmd_Query(self, index, vaQuery):
        lx.notimpl()


lx.bless(CmdBatchExport, "tila.batchexport")