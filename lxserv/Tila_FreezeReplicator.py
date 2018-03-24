import lx, modo
import lxifc
import lxu.command
import Tila_BatchExportModule as t
from Tila_BatchExportModule import dialog, helper


class CmdMyCustomCommand(lxu.command.BasicCommand):
	def __init__(self):
		lxu.command.BasicCommand.__init__(self)

		self.scn = modo.Scene()
		self.replicator_dict = {}

	def cmd_Flags(self):
		return lx.symbol.fCMD_MODEL | lx.symbol.fCMD_UNDO

	def basic_Enable(self, msg):
		return True

	def cmd_Interact(self):
		pass

	def basic_Execute(self, msg, flags):

		selection = self.scn.selected

		self.scn.deselect()
		lx.eval('select.itemType {} mode:add'.format(t.compatibleItemType['REPLICATOR']))
		arr = self.scn.selected

		self.replicator_dict = helper.get_replicator_source(self, arr)
		self.scn.select(selection)

		group_source = []
		for replicator in self.replicator_dict.values():  # Construct group_source
			if replicator.source_is_group:
				group_source.append(replicator.source_group)

		source_arr = {}

		for key in self.replicator_dict.keys():
			source_arr[key] = self.replicator_dict[key].source

		for o in selection:
			originalName = o.name
			self.scn.deselect()

			lx.eval('select.item {}'.format(originalName))
			lx.eval('replicator.freeze')
			lx.eval('select.item {}'.format(originalName))
			lx.eval('select.itemHierarchy')
			lx.eval('item.setType.mesh')
			lx.eval('layer.mergeMeshes true')
			self.scn.selected[0].name = originalName

			self.replicator_dict.pop(originalName, None)

			frozenItem = modo.Item(originalName)

			for g in group_source:  # Clean frozenItems in source_group
				g.removeItems(frozenItem)

			for key, rep in self.replicator_dict.iteritems():  # reassign source for all other replicator in the scene
				rep.set_source(source_arr[key])

	def cmd_Query(self, index, vaQuery):
		lx.notimpl()


lx.bless(CmdMyCustomCommand, t.TILA_FREEZE_REPLICATOR)

