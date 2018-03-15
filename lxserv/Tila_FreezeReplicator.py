import lx, modo
import lxifc
import lxu.command
import Tila_BatchExportModule as t


class CmdMyCustomCommand(lxu.command.BasicCommand):
	def __init__(self):
		lxu.command.BasicCommand.__init__(self)

		self.scn = modo.Scene()

	def cmd_Flags(self):
		return lx.symbol.fCMD_MODEL | lx.symbol.fCMD_UNDO

	def basic_Enable(self, msg):
		return True

	def cmd_Interact(self):
		pass

	def basic_Execute(self, msg, flags):

		for o in self.scn.selected:
			originalName = o.name
			lx.eval('replicator.freeze')
			lx.eval('select.item {}'.format(originalName))
			lx.eval('select.itemHierarchy')
			lx.eval('item.setType.mesh')
			lx.eval('layer.mergeMeshes true')
			self.scn.selected[0].name = originalName

	def cmd_Query(self, index, vaQuery):
		lx.notimpl()


lx.bless(CmdMyCustomCommand, t.TILA_FREEZE_REPLICATOR)

