#!/usr/bin/env python
#   Copyright (c) 2001-2016, The Foundry Group LLC
#   All Rights Reserved. Patents granted and pending.

################################################################################
#
# export_selected.py
#
# Version: 1.000
#
# Author: Gwynne Reddick
#
# Description: Command plugin to export selected mesh layers to any supported
#              output format.
#
# Parameters:  format - output file format
#              allLayers - export all mesh layers or just selected?
#              separateFiles - export layers to separate files or one file?
#              justLayers - export just the mesh layers or scene items too?
#
# Last Update: 13:00 13/10/15
#
################################################################################

import sys, traceback
import lx
import lxifc
import lxu.command
import lxu.select
from os.path import join, dirname
from os import sep

import Tila_BatchExportModule as t


def dirdialog(path=None):
	cmd_svc = lx.service.Command()

	cmd_svc.ExecuteArgString(-1, lx.symbol.iCTAG_NULL, 'dialog.setup dir')
	cmd_svc.ExecuteArgString(-1, lx.symbol.iCTAG_NULL, 'dialog.title {Export To:}')
	if path:
		cmd_svc.ExecuteArgString(-1, lx.symbol.iCTAG_NULL, 'dialog.result {%s}' % path)
	try:
		cmd_svc.ExecuteArgString(-1, lx.symbol.iCTAG_NULL, 'dialog.open')
	except:
		return

	command = cmd_svc.Spawn(lx.symbol.iCTAG_NULL, 'dialog.result')
	val_arr = cmd_svc.Query(command, 0)

	if val_arr.Count() < 1:
		return

	return val_arr.GetString(0)


def customFileDialog(fformat, uname, ext, path=None):
	cmd_svc = lx.service.Command()

	cmd_svc.ExecuteArgString(-1, lx.symbol.iCTAG_NULL, 'dialog.setup fileSave')
	cmd_svc.ExecuteArgString(-1, lx.symbol.iCTAG_NULL, 'dialog.title {Save File}')
	cmd_svc.ExecuteArgString(-1, lx.symbol.iCTAG_NULL,
							 'dialog.fileTypeCustom {%s} {%s} "" {%s}' % (fformat, uname, ext))
	if path:
		cmd_svc.ExecuteArgString(-1, lx.symbol.iCTAG_NULL, 'dialog.result {%s}' % path)
	try:
		cmd_svc.ExecuteArgString(-1, lx.symbol.iCTAG_NULL, 'dialog.open')
	except:
		return

	command = cmd_svc.Spawn(lx.symbol.iCTAG_NULL, "dialog.result")
	val_arr = cmd_svc.Query(command, 0)

	if val_arr.Count() < 1:
		return

	return val_arr.GetString(0)

class CmdExportSelected(lxu.command.BasicCommand):

	def __init__(self):
		lxu.command.BasicCommand.__init__(self)
		# output format
		self.dyna_Add('format', lx.symbol.sTYPE_STRING)
		# output path
		self.dyna_Add('path', lx.symbol.sTYPE_STRING)


		self.cmd_svc = None
		self.item_sel = None

	def cmd_Flags(self):
		return lx.symbol.fCMD_MODEL | lx.symbol.fCMD_UNDO

	def basic_ButtonName(self):
		return 'Export Selected'

	def basic_Execute(self, msg, flags):
		self.outputFormat = self.dyna_String(0)
		self.outputPath = self.dyna_String(1)

		print self.outputPath

		scn_sel = lxu.select.SceneSelection()
		self.item_sel = lxu.select.ItemSelection()
		scn_svc = lx.service.Scene()
		sel_svc = lx.service.Selection()
		self.cmd_svc = lx.service.Command()

		# look up some item types we're going to use.
		scenetype = scn_svc.ItemTypeLookup(lx.symbol.sITYPE_SCENE)
		scn_seltype = sel_svc.LookupType(lx.symbol.sSELTYP_SCENE)
		meshtype = scn_svc.ItemTypeLookup(lx.symbol.sITYPE_MESH)

		src_scn = scn_sel.current()
		selLyrs = self.item_sel.current()

		# can't currently walk scenes from the new API so we'll need
		# to use sceneservice to get the source and destination scene indices
		srcscene = lx.eval('query sceneservice scene.index ? current')
		scenefile = src_scn.Filename()

		# create destination scene
		self.cmd_svc.ExecuteArgString(-1, lx.symbol.iCTAG_NULL, 'scene.new')
		# can't currently walk scenes from the new API so we'll need
		# to use sceneservice to get the source and destination scene indices
		newscene = lx.eval('query sceneservice scene.index ? current')
		self.clearlyrs()

		outpath = self.savelyrs(selLyrs, srcscene, newscene)
		if outpath is None:
			# user cancelled file dialog
			msg.SetCode(lx.symbol.e_ABORT)
			return
		self.cmd_svc.ExecuteArgString(-1, lx.symbol.iCTAG_NULL, '!!scene.close')

		self.cmd_svc.ExecuteArgString(-1, lx.symbol.iCTAG_NULL,
									  'user.value Lux_ExportLayersAs_outpath {%s%s}' % (outpath, sep))

	def clearlyrs(self):
		try:
			lx.eval('select.itemType mesh')
			lx.eval('!!item.delete')
		except:
			lx.out('Exception "%s" on line: %d' % (sys.exc_value, sys.exc_traceback.tb_lineno))

	def clearitems(self):
		try:
			lx.eval('select.itemType camera')
			lx.eval('select.itemType light super:true mode:add')
			lx.eval('select.itemType renderOutput mode:add')
			lx.eval('select.itemType defaultShader mode:add')
			lx.eval('!!item.delete')
		except:
			lx.out('Exception "%s" on line: %d' % (sys.exc_value, sys.exc_traceback.tb_lineno))

	def savelyrs(self, selected, srcscene, newscene):
		'''Export a muliple layers to the shosen format

		'''
		try:
			if not self.outputPath:
				return
			self.cmd_svc.ExecuteArgString(-1, lx.symbol.iCTAG_NULL, 'scene.set %s' % srcscene)
			for item in selected:
				self.item_sel.select(item.Ident(), True)


			self.cmd_svc.ExecuteArgString(
				-1, lx.symbol.iCTAG_NULL,
				'layer.import %s {} childs:true shaders:true move:false position:0' % newscene)

			self.cmd_svc.ExecuteArgString(
				-1, lx.symbol.iCTAG_NULL,
				'scene.saveAs {%s} %s true' % (self.outputPath, self.outputFormat))

			self.clearlyrs()
			return dirname(self.outputPath)
		except:
			lx.out('Exception "%s" on line: %d' % (sys.exc_value, sys.exc_traceback.tb_lineno))


lx.bless(CmdExportSelected, t.TILA_EXPORT_SELECTED)

