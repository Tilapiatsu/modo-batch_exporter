import modo
import lx
import os
from os.path import isfile
import sys
import Tila_BatchExportModule as t
import dialog
import item_processing
import helper
import renamer
from Tila_BatchExportModule import file

############## TODO ###################
'''
 - Sometime the XML Tila_Config\tila_batchexport.cfg is corrupded and the file wont export
 - add a checkbox to vertMap.updateNormals at export
 - Expose some settings ( Freeze Geometry, Export/Import settings )
 - Add Mesh Cleanup
 - check export for procedural geometry and fusion item
 - polycount limit to avoid crash : select the first 1 M polys and transform them then select the next 1 M Poly etc ...
 - Implement a log windows to see exactly what's happening behind ( That file is exporting to this location 9 / 26 )
'''

class TilaBacthExport:
	def __init__(self,userValues):

		reload(dialog)
		reload(item_processing)
		reload(helper)
		reload(file)
		reload(renamer)

		self.cmd_svc = lx.service.Command()
		self.scn = modo.Scene()
		self.scnName = modo.scene.current().name
		self.userSelection = self.scn.selected
		self.userSelectionCount = len(self.userSelection)

		self.currPath = modo.scene.current().filename
		if self.currPath is None:
			self.currPath = ''

		self.scnIndex = lx.eval('query sceneservice scene.index ? current')
		self.tempScnID = None

		index = 0
		self.exportVisible_sw = bool(userValues[index])
		if self.exportVisible_sw:
			self.userSelection = self.select_visible_items()
		index += 1
		self.exportFile_sw = bool(userValues[index])
		index += 1
		self.scanFiles_sw = bool(userValues[index])
		index += 1
		self.scanFolder_sw = bool(userValues[index])
		index += 1
		self.exportEach_sw = bool(userValues[index])
		index += 1
		self.exportHierarchy_sw = bool(userValues[index])
		index += 1

		self.triple_sw = bool(userValues[index])
		index += 1
		self.mergeMesh_sw = bool(userValues[index])
		index += 1
		self.askBeforeOverride_sw = bool(userValues[index])
		index += 1

		self.assignMaterialPerUDIMTile_sw = bool(userValues[index])
		index += 1
		self.UDIMTextureName = userValues[index]
		index += 1

		self.resetPos_sw = bool(userValues[index])
		index += 1
		self.resetRot_sw = bool(userValues[index])
		index += 1
		self.resetSca_sw = bool(userValues[index])
		index += 1
		self.resetShe_sw = bool(userValues[index])
		index += 1

		self.freezePos_sw = bool(userValues[index])
		index += 1
		self.freezeRot_sw = bool(userValues[index])
		index += 1
		self.freezeSca_sw = bool(userValues[index])
		index += 1
		self.freezeShe_sw = bool(userValues[index])
		index += 1

		self.freezeGeo_sw = bool(userValues[index])
		index += 1
		self.freezeInstance_sw = bool(userValues[index])
		index += 1
		self.freezeMeshOp_sw = bool(userValues[index])
		index += 1
		self.freezeReplicator_sw = bool(userValues[index])
		index += 1

		self.pos_sw = bool(userValues[index])
		index += 1
		self.posX = userValues[index]
		index += 1
		self.posY = userValues[index]
		index += 1
		self.posZ = userValues[index]
		index += 1

		self.rot_sw = bool(userValues[index])
		index += 1
		self.rotX = userValues[index]
		index += 1
		self.rotY = userValues[index]
		index += 1
		self.rotZ = userValues[index]
		index += 1

		self.sca_sw = bool(userValues[index])
		index += 1
		self.scaX = userValues[index]
		index += 1
		self.scaY = userValues[index]
		index += 1
		self.scaZ = userValues[index]
		index += 1

		self.smoothAngle_sw = bool(userValues[index])
		index += 1
		self.smoothAngle = userValues[index]
		index += 1

		self.hardenUvBorder_sw = bool(userValues[index])
		index += 1
		self.uvMapName = userValues[index]
		index += 1

		self.exportCageMorph_sw = bool(userValues[index])
		index += 1
		self.cageMorphMapName = userValues[index]
		index += 1

		self.exportMorphMap_sw = bool(userValues[index])
		index += 1
		self.applyMorphMap_sw = bool(userValues[index])
		index += 1
		self.morphMapName = userValues[index]
		index += 1

		self.openDestFolder_sw = bool(userValues[index])
		index += 1

		self.createFormatSubfolder_sw = bool(userValues[index])
		index += 1
		self.processSubfolder_sw = bool(userValues[index])
		index += 1
		self.subfolderDepth = userValues[index]
		index += 1
		self.formatFilter = userValues[index]
		index += 1

		self.filenamePattern = userValues[index]
		index += 1

		self.exportFormatLxo_sw = bool(userValues[index])
		index += 1
		self.exportFormatLwo_sw = bool(userValues[index])
		index += 1
		self.exportFormatFbx_sw = bool(userValues[index])
		index += 1
		self.exportFormatObj_sw = bool(userValues[index])
		index += 1
		self.exportFormatAbc_sw = bool(userValues[index])
		index += 1
		self.exportFormatAbchdf_sw = bool(userValues[index])
		index += 1
		self.exportFormatDae_sw = bool(userValues[index])
		index += 1
		self.exportFormatDxf_sw = bool(userValues[index])
		index += 1
		self.exportFormat3dm_sw = bool(userValues[index])
		index += 1
		self.exportFormatGeo_sw = bool(userValues[index])
		index += 1
		self.exportFormatStl_sw = bool(userValues[index])
		index += 1
		self.exportFormatX3d_sw = bool(userValues[index])
		index += 1
		self.exportFormatSvg_sw = bool(userValues[index])
		index += 1
		self.exportFormatPlt_sw = bool(userValues[index])

		self.itemToProceed = helper.init_ctype_dict_arr()

		if self.exportEach_sw:
			self.proceededMesh = []
		else:
			self.proceededMesh = helper.init_ctype_dict_arr()

		self.sortedItemToProceed = []

		self.replicatorSrcIgnoreList = ()
		self.replicator_dict = {}
		self.replicator_group_source = {}
		self.replicator_multiple_source = {}
		self.replicator_non_group_source = {}
		self.UDIMMaterials = set([])
		self.proceededMeshIndex = 0
		self.progress = None
		self.progression = [0, 0]
		self.filename = ''
		self.firstIndex = helper.init_ctype_dict_arr()

		self.exportedFileCount = 0
		self.overrideFiles = ''

		self.defaultExportSettings = t.defaultExportSettings
		self.defaultImportSettings = t.defaultImportSettings

	def export_at_least_one_format(self):
		if not (self.exportFormatFbx_sw
				or self.exportFormatObj_sw
				or self.exportFormatLxo_sw
				or self.exportFormatLwo_sw
				or self.exportFormatAbc_sw
				or self.exportFormatAbchdf_sw
				or self.exportFormatDae_sw
				or self.exportFormatDxf_sw
				or self.exportFormat3dm_sw
				or self.exportFormatGeo_sw
				or self.exportFormatStl_sw
				or self.exportFormatX3d_sw
				or self.exportFormatSvg_sw
				or self.exportFormatPlt_sw):
			dialog.init_message('info', 'No export format selected', 'Select at least one export fromat in the form')
			sys.exit()

	def at_least_one_compatible_item_selected(self, exit=True):
		helper.items_to_proceed_constructor(self)

		totalLength = 0
		for arr in self.itemToProceed.keys():
			totalLength += len(arr)
		if totalLength == 0:
			if exit:
				message = ''
				separator = ' or '
				for i in xrange(len(t.compatibleItemType)):
					if i < len(t.compatibleItemType) - 1:
						message += t.compatibleItemType.keys()[i] + separator
					else:
						message += t.compatibleItemType.keys()[i]
				dialog.init_message('info', 'No compatible item selected', 'Select at least one item of this type : \n \n {} '.format(message))
				sys.exit()
			else:
				return True

	# Loops methods

	def batch_export(self):
		# check if at least one item is selected
		helper.check_selection_count(self)
		# check if within this selection, at least one item is compatible with by this script referenced by t.compatibleItemType
		# Construct the queue of item to proceed self.itemToProceed_dict, filtered them and exclude all incompatible types
		self.at_least_one_compatible_item_selected()

		dialog.begining_log(self)

		self.currPath = file.getLatestPath(t.config_export_path)

		path = os.path.join(self.currPath, os.path.splitext(self.scn.name)[0])
		dialog.init_dialog("filesave", path, dialog.dialogFormatType[helper.get_first_export_type(self)])

		try:  # output folder dialog
			lx.eval('dialog.open')
		except:
			dialog.init_dialog('cancel', self.currPath)
		else:
			output_dir = lx.eval1('dialog.result ?')

			self.filename = os.path.splitext(os.path.split(output_dir)[1])[0]
			output_dir = os.path.split(output_dir)[0]

			file.updateExportPath(output_dir, '', '')

			self.batch_process(output_dir, self.filename)

			helper.revert_initial_parameter(self)

		helper.open_destination_folder(self, output_dir)
		dialog.ending_log(self)

	def batch_files(self):
		self.currPath = file.getLatestPath(t.config_browse_src_path)
		dialog.init_dialog("input", self.currPath)

		try:  # mesh to process dialog
			lx.eval('dialog.open')
		except:
			dialog.init_dialog('cancel', self.currPath)
		else:
			files = lx.evalN('dialog.result ?')
			file.updateExportPath('', os.path.split(files[0])[0], '')
			self.currPath = file.getLatestPath(t.config_browse_dest_path)
			dialog.init_dialog("output", self.currPath)
			try:  # output folder dialog
				lx.eval('dialog.open')
			except:
				dialog.init_dialog('cancel', self.currPath)
			else:
				output_dir = lx.eval1('dialog.result ?')
				file.updateExportPath('', '', output_dir)

				file_count = len(files)

				self.progress = dialog.init_progress_bar(file_count, 'Exporting files...')

				self.progression[1] = file_count
				self.progression[0] = 0

				t.set_import_setting()

				for f in files:
					dialog.processing_log('.....................................   ' + os.path.basename(
						f) + '   .....................................')

					lx.eval('!scene.open "%s" normal' % f)

					self.scnIndex = lx.eval('query sceneservice scene.index ? current')

					helper.select_compatible_item_type()

					self.userSelection = self.scn.selected
					self.userSelectionCount = len(self.userSelection)

					dialog.print_log('.....................................   ' + str(
						self.userSelectionCount) + ' mesh item founded   .....................................')

					if self.at_least_one_compatible_item_selected(exit=False):
						lx.eval('!scene.close')
						continue

					self.filename = os.path.splitext(os.path.basename(f))[0]

					self.batch_process(output_dir, self.filename)

					dialog.increment_progress_bar(self, self.progress[0], self.progression)

					helper.revert_initial_parameter(self)

					lx.eval('!scene.close')

				helper.reset_import_settings(self)

		dialog.init_message('info', 'Done', 'Operation completed successfully ! %s file(s) exported' % self.exportedFileCount)

		helper.open_destination_folder(self, output_dir)

		dialog.ending_log(self)

	def batch_folder(self):
		self.currPath = file.getLatestPath(t.config_browse_src_path)
		dialog.init_dialog("input_path", self.currPath)

		try:  # mesh to process dialog
			lx.eval('dialog.open')
		except:
			dialog.init_dialog('cancel', self.currPath)
		else:
			input_dir = lx.eval1('dialog.result ?')
			file.updateExportPath('', input_dir, '')
			self.currPath = file.getLatestPath(t.config_browse_dest_path)
			dialog.init_dialog("output", self.currPath)
			try:  # output folder dialog
				lx.eval('dialog.open')
			except:
				dialog.init_dialog('cancel', self.currPath)
			else:
				output_dir = lx.eval1('dialog.result ?')
				file.updateExportPath('', '', output_dir)

				if not self.processSubfolder_sw:
					format = helper.filter_string(self.formatFilter, t.compatibleImportFormat)
					files = helper.get_files_of_type(input_dir, format)
					dialog.print_log('{} files found'.format(len(files)))
				else:
					input_subdir = helper.get_recursive_subdir([input_dir], self.subfolderDepth)
					files = []
					format = helper.filter_string(self.formatFilter, t.compatibleImportFormat)
					for subdir in input_subdir:
						subfiles = helper.get_files_of_type(subdir, format)

						for f in subfiles:
							files.append(f)
					dialog.print_log('{} files found'.format(len(files)))

				file_count = len(files)

				self.progress = dialog.init_progress_bar(file_count, 'Exporting files...')

				self.progression[1] = file_count
				self.progression[0] = 0

				t.set_import_setting()

				for f in files:
					dialog.processing_log('.....................................   ' + os.path.basename(
						f) + '   .....................................')

					lx.eval('!scene.open "%s" normal' % f)

					self.scnIndex = lx.eval('query sceneservice scene.index ? current')

					helper.select_compatible_item_type()

					self.userSelection = self.scn.selected
					self.userSelectionCount = len(self.userSelection)

					dialog.print_log('.....................................   ' + str(
						self.userSelectionCount) + ' mesh item founded   .....................................')

					if self.at_least_one_compatible_item_selected(exit=False):
						lx.eval('!scene.close')
						continue

					input_relative_dir_root = os.path.split(f)[0].split(input_dir)[1][1:]
					output_subdir = os.path.join(output_dir, input_relative_dir_root)

					helper.create_folder_if_necessary(output_subdir)

					self.filename = os.path.splitext(os.path.basename(f))[0]

					self.batch_process(output_subdir, self.filename)

					dialog.increment_progress_bar(self, self.progress[0], self.progression)

					helper.revert_initial_parameter(self)

					lx.eval('!scene.close')

				helper.reset_import_settings(self)

				#dialog.deallocate_dialog_svc(self.progress[1])

		dialog.init_message('info', 'Done', 'Operation completed successfully ! %s file(s) exported' % self.exportedFileCount)

		helper.open_destination_folder(self, output_dir)

		dialog.ending_log(self)

	def batch_transform(self):
		helper.check_selection_count(self)
		self.at_least_one_compatible_item_selected()

		self.proceededMesh = self.itemToProceed
		dialog.begining_log(self)

		helper.construct_replicator_dict(self)

		self.transform_loop()
		dialog.ending_log(self)

	def batch_process(self, output_dir, filename):
		# helper.select_hierarchy(self)

		helper.construct_replicator_dict(self)

		item_count = len(self.sortedItemToProceed)

		self.progress = dialog.init_progress_bar(item_count, 'Exporting ...')
		self.progression[1] = item_count
		self.progression[0] = 0

		if self.exportEach_sw:
			for tcount in xrange(item_count):
				currItem = [self.sortedItemToProceed[tcount]]

				helper.copy_arr_to_temporary_scene(self, currItem)

				currItem = [self.proceededMesh[tcount]]

				for ctype, type in t.compatibleItemType.iteritems():
					if type == currItem[0].type:
						self.transform_arr(currItem, ctype)
						break

				self.proceededMeshIndex = tcount
				dialog.increment_progress_bar(self, self.progress[0], self.progression)

				layername = currItem[0].name

				self.export_all_format(output_dir, layername, tcount)

				lx.eval('scene.set {}'.format(self.tempScnID))
				lx.eval('!!scene.close')

				self.tempScnID = None

		else:  # export all in one file
			tcount = len(t.compatibleItemType)
			for ctype, type in t.compatibleItemType.iteritems():
				items = self.itemToProceed[ctype]
				if len(items) > 0:
					self.firstIndex[ctype] = helper.copy_arr_to_temporary_scene(self, items, ctype)
				if tcount > 1:  # for the last type, we don't want to go back to the original scene
					lx.eval('scene.set {}'.format(self.scnIndex))
				else:
					lx.eval('scene.set {}'.format(self.tempScnID))
				tcount -= 1

			self.transform_loop()

			self.export_all_format(output_dir, filename)
			dialog.increment_progress_bar(self, self.progress[0], self.progression)

			lx.eval('scene.set {}'.format(self.tempScnID))
			lx.eval('!!scene.close')
			self.tempScnID = None

		# helper.set_name(self.sortedOriginalItems, shrink=len(t.TILA_BACKUP_SUFFIX))

		helper.revert_scene_preferences(self)

	def transform_loop(self):

		transformed = []

		for ctype in t.compatibleItemType.keys():
			if len(self.proceededMesh[ctype]) > 0:
				dialog.print_log('Processing item of type : ' + ctype)
				# dialog.print_list_item_name(self.proceededMesh[ctype])
				transformed += self.transform_arr(self.proceededMesh[ctype], ctype)

		if self.mergeMesh_sw:
			item_processing.merge_meshes(self, transformed)
			self.proceededMesh = [self.scn.selected[0]]

			print self.filename
			print self.filenamePattern

			layer_name = renamer.construct_filename(self, '', self.filenamePattern, self.filename, '', 0)
			layer_name = os.path.splitext(layer_name)[0]
			self.proceededMesh[0].name = layer_name

	def transform_arr(self, item_arr, ctype):
		if len(item_arr) > 0:
			self.scn.select(item_arr)
			self.transform_selected(ctype=ctype)

		return self.scn.selected

	def transform_selected(self, ctype):
		self.progression = [1, helper.get_transformation_count(self)]
		self.progress = dialog.init_progress_bar(self.progression[1], 'Processing item(s) ...')

		helper.select_hierarchy(self)

		item_processing.freeze_instance(self, ctype=t.compatibleItemType[ctype], first_index=self.firstIndex[ctype])
		item_processing.freeze_replicator(self, ctype=t.compatibleItemType[ctype])
		item_processing.freeze_meshop(self, ctype=t.compatibleItemType[ctype])

		item_processing.smooth_angle(self)
		item_processing.harden_uv_border(self)

		item_processing.freeze_geo(self)
		item_processing.triple(self)

		item_processing.assign_material_per_udim(self, True)
		item_processing.apply_morph(self, self.applyMorphMap_sw, self.morphMapName)
		item_processing.export_morph(self)

		item_processing.reset_pos(self)
		item_processing.reset_rot(self)
		item_processing.reset_sca(self)
		item_processing.reset_she(self)

		item_processing.position_offset(self)
		item_processing.scale_amount(self)
		item_processing.rot_angle(self)

		item_processing.freeze_rot(self)
		item_processing.freeze_sca(self)
		item_processing.freeze_pos(self)
		item_processing.freeze_she(self)

		dialog.deallocate_dialog_svc(self.progress[1])

	def export_all_format(self, output_dir, layer_name, increment=0):

		if self.exportFormatLxo_sw:
			output_path = helper.construct_file_path(self, output_dir, layer_name, t.exportTypes[0][0], increment)
			self.export_selection(output_path, t.exportTypes[0][1])

		if self.exportFormatLwo_sw:
			output_path = helper.construct_file_path(self, output_dir, layer_name, t.exportTypes[1][0], increment)
			self.export_selection(output_path, t.exportTypes[1][1])

		if self.exportFormatFbx_sw:
			item_processing.force_freeze_replicator(self)
			output_path = helper.construct_file_path(self, output_dir, layer_name, t.exportTypes[2][0], increment)
			lx.eval('user.value sceneio.fbx.save.exportType FBXExportAll')
			lx.eval('user.value sceneio.fbx.save.surfaceRefining subDivs')
			lx.eval('user.value sceneio.fbx.save.format FBXLATEST')
			self.export_selection(output_path, t.exportTypes[2][1])

		if self.exportFormatObj_sw:
			item_processing.force_freeze_replicator(self)
			output_path = helper.construct_file_path(self, output_dir, layer_name, t.exportTypes[3][0], increment)
			self.export_selection(output_path, t.exportTypes[3][1])

		if self.exportFormatAbc_sw:
			output_path = helper.construct_file_path(self, output_dir, layer_name, t.exportTypes[4][0], increment)
			self.export_selection(output_path, t.exportTypes[4][1])

		if self.exportFormatAbchdf_sw:
			output_path = helper.construct_file_path(self, output_dir, layer_name, t.exportTypes[5][0], increment)
			self.export_selection(output_path, t.exportTypes[5][1])

		if self.exportFormatDae_sw:
			output_path = helper.construct_file_path(self, output_dir, layer_name, t.exportTypes[6][0], increment)
			self.export_selection(output_path, t.exportTypes[6][1])

		if self.exportFormatDxf_sw:
			output_path = helper.construct_file_path(self, output_dir, layer_name, t.exportTypes[7][0], increment)
			self.export_selection(output_path, t.exportTypes[7][1])

		if self.exportFormat3dm_sw:
			output_path = helper.construct_file_path(self, output_dir, layer_name, t.exportTypes[8][0], increment)
			self.export_selection(output_path, t.exportTypes[8][1])

		if self.exportFormatGeo_sw:
			output_path = helper.construct_file_path(self, output_dir, layer_name, t.exportTypes[9][0], increment)
			self.export_selection(output_path, t.exportTypes[9][1])

		if self.exportFormatStl_sw:
			output_path = helper.construct_file_path(self, output_dir, layer_name, t.exportTypes[10][0], increment)
			self.export_selection(output_path, t.exportTypes[10][1])

		if self.exportFormatX3d_sw:
			output_path = helper.construct_file_path(self, output_dir, layer_name, t.exportTypes[11][0], increment)
			self.export_selection(output_path, t.exportTypes[11][1])

		if self.exportFormatSvg_sw:
			output_path = helper.construct_file_path(self, output_dir, layer_name, t.exportTypes[12][0], increment)
			self.export_selection(output_path, t.exportTypes[12][1])

		if self.exportFormatPlt_sw:
			output_path = helper.construct_file_path(self, output_dir, layer_name, t.exportTypes[13][0], increment)
			self.export_selection(output_path, t.exportTypes[13][1])

		helper.select_arr(self.UDIMMaterials)
		# lx.eval('!!item.delete')

	def export_selection(self, output_path, export_format):

		self.save_file(output_path[0], export_format)

		if self.exportCageMorph_sw:
			self.export_cage(output_path[1], export_format)



	def export_cage(self, output_path, export_format):
		# Smooth the mesh entirely
		lx.eval('vertMap.softenNormals connected:true')

		# Apply Cage Morph map
		helper.select_compatible_item_type()
		item_processing.apply_morph(self, True, self.cageMorphMapName)

		self.save_file(output_path, export_format)

	def save_file(self, output_path, export_format):
		if self.file_conflict(output_path) and self.askBeforeOverride_sw:
			if self.overrideFiles != 'yesToAll' and self.overrideFiles != 'noToAll':
				self.overrideFiles = dialog.ask_before_override(os.path.split(output_path)[1])
				if self.overrideFiles == 'cancel':
					helper.clean_duplicates(self)

			if self.overrideFiles == 'ok' or self.overrideFiles == 'yesToAll':
				self.save_command(output_path, export_format)
		else:
			self.save_command(output_path, export_format)

	def save_command(self, output_path, export_format):
		try:
			# lx.eval('!!tila.exportselected {} {} "{}"'.format(export_format, 'false', output_path))
			lx.eval('!scene.saveAs {%s} %s true' % (output_path, export_format))
			message = helper.get_progression_message(self, os.path.basename(output_path))
			dialog.export_log(message)
			self.exportedFileCount += 1

		except RuntimeError:
			dialog.print_log('Failed to export {}'.format(output_path))

	def select_visible_items(self):
		mesh = self.scn.items(t.itemType['MESH'])
		meshInstance = self.scn.items(t.itemType['MESH_INSTANCE'])
		meshFusion = self.scn.items(t.itemType['MESH_FUSION'])
		meshReplicator = self.scn.items(t.itemType['REPLICATOR'])

		compatible = mesh + meshInstance + meshFusion + meshReplicator

		visible = []

		for item in compatible:
			visible_channel = item.channel('visible').get()
			if visible_channel == 'default' or visible_channel == 'on':
				visible.append(item)

		self.scn.select(visible)
		return visible

	@staticmethod
	def file_conflict(path):
		return os.path.isfile(path)
