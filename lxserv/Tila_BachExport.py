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

			userValues = user_value.query_User_Values(self, t.kit_prefix)
			userValues[1] = True
			userValues[2] = False

			tbe = batch_export.TilaBacthExport

			tbe.export_at_least_one_format(tbe(userValues))

			if bool(userValues[0]):
				olderSelection = scn.selected

			tbe.batch_export(tbe(userValues))

			if bool(userValues[0]):
				scn.select(olderSelection)

		except:
			lx.out(traceback.format_exc())

	def cmd_Query(self, index, vaQuery):
		lx.notimpl()


lx.bless(CmdBatchExport, t.TILA_BATCH_EXPORT)