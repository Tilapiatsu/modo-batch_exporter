import lx
import modo
import os
from os.path import isfile
import dialog
import sys
import math
import Tila_BatchExportModule as t
import renamer
import lxu


# Path Constructor

def construct_file_path(self, output_dir, layer_name, ext, increment):
	sceneName = os.path.splitext(modo.Scene().name)[0]

	if self.createFormatSubfolder_sw:
		output_dir = os.path.join(output_dir, ext)
		create_folder_if_necessary(output_dir)

	layer_name = renamer.construct_filename(self, layer_name, self.filenamePattern, self.filename, ext, increment)

	layer_name = os.path.splitext(layer_name)[0]

	return [os.path.join(output_dir, layer_name + '.' + ext),
			os.path.join(output_dir, layer_name + '_cage.' + ext)]


# Helpers, setter/getter, Selector

def items_to_proceed_constructor(self):
	for item in self.userSelection:
		for type in t.compatibleItemType.keys():
			if item.type == t.compatibleItemType[type]:
				self.itemToProceed[type].append(item)

	self.sortedItemToProceed = sort_items_dict_arr(self.itemToProceed)


# sort Item per compatible types
def sort_items_dict_arr(dict):
	result_arr = []

	for type in t.compatibleItemType.keys():
		result_arr += dict[type]

	return result_arr


def construct_proceededMesh(self, arr, ctype):
	for o in arr:
		self.proceededMesh[ctype].append(o)

	return len(self.proceededMesh) - len(arr)


def get_name_arr(arr):
	name_arr = []
	for o in arr:
		name_arr.append(o.name)

	return name_arr


def get_generic_name_dict(arr):
	dict = {}
	for o in arr:
		for k in t.genericNameDict.keys():
			if k in o.name:
				dict[o.name] = [k, t.genericNameDict[k], o.name.lower()]

	return dict


def get_key_from_value(dict, value):
	for key in dict.keys():
		if dict[key] == value:
			return key
	else:
		return None


def copy_arr_to_temporary_scene(self, arr, ctype=None):
	try:
		srcscene = lx.eval('query sceneservice scene.index ? current')

		if self.exportEach_sw:
			reference_item = ''
			for name in t.genericName:
				if name in arr[0].name:  # hack to enable replicator item to be layer.import to the temporary scene
					reference_item = arr[0].name.lower()
			else:
				reference_item = arr[0].name

		original_selection_name_arr = []
		modified_selection_name_arr = []
		genericName_arr = []

		for item in arr:  # Gather selection Original Names
			original_selection_name_arr.append(item.name)

		if self.tempScnID is None:  # Create a new Scene and Store tmpScnID
			self.cmd_svc.ExecuteArgString(-1, lx.symbol.iCTAG_NULL, 'scene.new')
			self.tempScnID = lx.eval('query sceneservice scene.index ? current')

			clearitems()

			for o in arr:
				if o.type == t.compatibleItemType['REPLICATOR']:
					if o.name in self.replicator_group_source.keys():
						if len(modo.Scene().groups) == 0:
							lx.eval('!group.create "{}" mode:empty'.format(self.replicator_group_source[o.name][0]))
						elif self.replicator_group_source[o.name][0] not in [grp.name for grp in modo.Scene().groups]:
							lx.eval('!group.create "{}" mode:empty'.format(self.replicator_group_source[o.name][0]))


			self.cmd_svc.ExecuteArgString(-1, lx.symbol.iCTAG_NULL, 'scene.set %s' % srcscene)

		self.scn.select(arr)

		for item in arr:  # Select all item related to the user selection
			if item.type == t.compatibleItemType['REPLICATOR']:  # Select Replicator Soucres and Particles
				for o in self.replicator_dict[item.name].source:
					lx.eval('select.item "{}" mode:add'.format(o.name))  # add the source to the selection

				lx.eval('select.item "{}" mode:add'.format(self.replicator_dict[item.name].particle.name))  # add the particle to the selection
		for item in self.scn.selected:  # Dealing with generic Names
			itemType = item.type
			original_name = item.name
			for gen in t.genericName:
				if gen in item.name:
					if itemType == t.compatibleItemType['REPLICATOR']:
						replicator = self.replicator_dict[original_name]

						genericName_arr.append([item.name])
						item.name = item.name.replace(gen, t.genericNameDict[gen])
						genericName_arr[-1].append(item.name)

						self.replicator_dict.pop(original_name, None)
						self.replicator_dict[item.name] = replicator
					else:
						genericName_arr.append([item.name])
						item.name = item.name.replace(gen, t.genericNameDict[gen])
						genericName_arr[-1].append(item.name)
			modified_selection_name_arr.append(item.name)

		# Move all selected items to temporary scene
		self.cmd_svc.ExecuteArgString(
			-1, lx.symbol.iCTAG_NULL,
			'!layer.import {}'.format(self.tempScnID) + ' {} ' + 'childs:{} shaders:true move:false position:0'.format(self.exportHierarchy_sw))

		self.scn = modo.Scene()

		for i in xrange(len(modified_selection_name_arr)):  # revert Generic Name
			for val in t.genericNameDict.values():
				if val in modified_selection_name_arr[i]:
					old_name = modified_selection_name_arr[i]
					item = modo.Item(old_name)
					itemType = item.type
					initial_name = get_key_from_value(t.genericNameDict, val)
					if initial_name is None:
						continue
					modified_selection_name_arr[i] = old_name.replace(val, initial_name)
					item.name = modified_selection_name_arr[i]

					lx.eval('scene.set {}'.format(self.scnIndex))  # switch to original Scene to revert name
					self.scn = modo.Scene()

					if itemType == t.compatibleItemType['REPLICATOR']:
						replicator = self.replicator_dict[old_name]
						replicator.item_name = old_name
						replicator.replicator_item.name = modified_selection_name_arr[i]
						self.replicator_dict.pop(old_name, None)
						self.replicator_dict[item.name] = replicator
					else:
						self.scn.select(item.name.replace(get_key_from_value(t.genericNameDict, val), val))
						lx.eval('!item.name "{}" "{}"'.format(item.name, itemType))

					lx.eval('scene.set {}'.format(self.tempScnID))
					self.scn = modo.Scene()

		replicator_group_source_ignored = {}
		for o in arr:  # Assign Replicator source item to their proper group if needed
			if o.type == t.compatibleItemType['REPLICATOR']:
				if o.name in self.replicator_group_source.keys():
					group_name = self.replicator_group_source[o.name][0]
					self.scn.deselect()
					lx.eval('select.item "{}" set'.format(self.replicator_group_source[o.name][0]))
					for source in self.replicator_group_source[o.name][1]:
						if group_name not in replicator_group_source_ignored.keys():
							self.scn.select(source.name, add=True)
							replicator_group_source_ignored[group_name] = [source]
						else:
							if source not in replicator_group_source_ignored[group_name]:
								self.scn.select(source.name, add=True)
								replicator_group_source_ignored[group_name].append(source)

					if len(self.scn.selected) > 1:
						lx.eval('!group.edit add item')

					self.scn.select(o.name)
					lx.eval('replicator.source {}'.format(self.replicator_group_source[o.name][0]))
		self.scn.deselect()

		for i in xrange(len(original_selection_name_arr)):  # Select items that were imported to the temporary scene
			if i == 0:
				lx.eval('select.item {}'.format(original_selection_name_arr[i]))
			else:
				lx.eval('select.item {} mode:add'.format(original_selection_name_arr[i]))

		if self.exportEach_sw:
			self.proceededMesh.append(self.scn.item(reference_item))
		else:
			for o in self.scn.selected:
				self.proceededMesh[ctype].append(o)
		return len(self.proceededMesh) - len(original_selection_name_arr)

	except:
		return_exception()


def return_exception():
	lx.out('Exception "{}" on line {} in file {}'.format(sys.exc_value, sys.exc_traceback.tb_lineno,os.path.basename(__file__)))


def duplicate_rename(self, arr, suffix):
	duplicate_arr = []
	for item in arr:
		layer_name = item.name
		if item.type == t.itemType['MESH_FUSION']:
			select_hierarchy(self, force=True)
		if self.exportHierarchy_sw:
			self.scn.select(item)
			lx.eval('item.duplicate false all:true')
			duplicate = self.scn.selected[0]
		else:
			duplicate = self.scn.duplicateItem(item)
		duplicate.name = '%s%s' % (layer_name, suffix)
		duplicate_arr.append(duplicate)
		self.proceededMesh.append(duplicate)

	self.scn.select(duplicate_arr)
	return len(self.proceededMesh) - len(duplicate_arr)


def get_name(self, layer):
	if self.exportEach_sw:
		return layer.name
	else:
		return self.scn.name


def set_name(arr, shrink=0, suffix=''):
	for item in arr:
		currName = item.name

		if shrink:
			currName = currName[:-shrink]
		currName = '%s%s' % (currName, suffix)

		item.name = currName


def open_destination_folder(self, output_dir):
	if self.exportFile_sw:
		if self.openDestFolder_sw:
			dialog.open_folder(output_dir)


def check_selection_count(self):
	if self.userSelectionCount == 0:  # No file Selected
		if self.exportVisible_sw:
			dialog.init_message('error', 'No item visible', 'At least one item has to be visible')
		else:
			dialog.init_message('error', 'No item selected', 'Select at least one item')
		sys.exit()


def getIteratorTemplate(i):
	i = str(i)
	iterator = ''

	if lx.eval('pref.value application.indexStyle ?') == t.indexStyle[0]:
		iterator = ' (' + i + ')'

	elif lx.eval('pref.value application.indexStyle ?') == t.indexStyle[1]:
		iterator = '(' + i + ')'

	elif lx.eval('pref.value application.indexStyle ?') == t.indexStyle[2]:
		iterator = ' ' + i

	elif lx.eval('pref.value application.indexStyle ?') == t.indexStyle[3]:
		iterator = '_' + i

	return iterator


def getLatestItemCreated(name):
	i = 1
	item = None
	while True:
		try:
			if i == 1:
				item = modo.Item(name)
			else:
				item = modo.Item('%s%s' % (name, getIteratorTemplate(i)))
			i += 1
		except:
			break

	return item


def get_transformation_count(self):
	count = 0
	if self.triple_sw:
		count += 1
	if self.resetPos_sw:
		count += 1
	if self.resetRot_sw:
		count += 1
	if self.resetSca_sw:
		count += 1
	if self.resetShe_sw:
		count += 1
	if self.freezePos_sw:
		count += 1
	if self.freezeRot_sw:
		count += 1
	if self.freezeSca_sw:
		count += 1
	if self.freezeShe_sw:
		count += 1
	if self.freezeGeo_sw:
		count += 1
	if self.scn.selected[0].type == t.itemType['MESH_INSTANCE'] and (self.exportFile_sw or ((not self.exportFile_sw) and (self.freezeInstance_sw or self.freezePos_sw or self.freezeRot_sw or self.freezeSca_sw or self.freezeShe_sw))):
		count += 1
	if self.scn.selected[0].type == t.itemType['REPLICATOR']:
		count += 1
	if (self.posX != 0 or self.posY != 0 or self.posZ != 0) and self.pos_sw:
		count += 1
	if (self.rotX != 0 or self.rotY != 0 or self.rotZ != 0) and self.rot_sw:
		count += 1
	if (self.scaX != 1 or self.scaY != 1 or self.scaZ != 1) and self.sca_sw:
		count += 1
	if self.smoothAngle_sw:
		count += 1
	if self.hardenUvBorder_sw:
		count += 1
	if self.applyMorphMap_sw:
		count += 1

	return count


def get_progression_message(self, message):
	return 'Item %s / %s || %s' % (self.progression[0], self.progression[1], message)


def safe_select(tuple):
	first = False
	for i in tuple:
		if isItemTypeCompatibile(i):
			if not first:
				first = True
				modo.item.Item.select(i, True)
			else:
				modo.item.Item.select(i)


def select_arr(arr, replace=False):
	first = True
	for o in arr:
		if replace and first:
			first = False
			modo.item.Item.select(o, True)
		else:
			modo.item.Item.select(o)


def isItemTypeCompatibile(item):
	for type in t.itemType.values():
		try:
			if str(item.type) == type:
				return True
		except AttributeError:
			break
	return False


def construct_dict_from_arr(arr, keySubIndex):
	d = {}

	for i in arr:
		d[i[0]] = i[keySubIndex]

	return d


def select_hierarchy(self, force=False):
	if self.exportHierarchy_sw or force:
		lx.eval('select.itemHierarchy')


def get_replicator_source(self, replicator_arr):
	result_dict = {}
	selection = self.scn.selected

	for i in replicator_arr:
		replicator = ModoReplicator(i)
		result_dict[i.name] = replicator

	self.scn.select(selection)

	return result_dict


def concatetate_string_arr(arr, separator):
	string = ''
	for i in xrange(len(arr)):
		if i == 0:
			string += arr[i]
		else:
			string += separator + arr[i]

	return string


def get_recursive_subdir(path, depth):
	if depth == 0:
		return path

	else:
		subdir = set([])

		for p in path:
			if os.path.isdir(p):
				subdir.add(p)
				sub = get_immediate_subdir(p)

				for s in sub:
					subdir.add(s)

				rec = get_recursive_subdir(sub, depth - 1)

				for r in rec:
					subdir.add(r)

		return list(subdir)


def get_immediate_subdir(path):
	return [os.path.join(path, subdir) for subdir in os.listdir(path)
			if os.path.isdir(os.path.join(path, subdir))]


def get_files_of_type(path, type):
	files = [os.path.join(path, f) for f in os.listdir(path) if isfile(os.path.join(path, f))]
	return [f for f in files if os.path.splitext(f)[1][1:] in type]


def filter_string(string, filter):
	format_arr = string.split(',')
	return [f.lower() for f in format_arr if f.lower() in filter]


def create_folder_if_necessary(path):
	if not os.path.exists(path):
		os.makedirs(path)


def select_compatible_item_type():
	for type in list(t.compatibleItemType.viewvalues()):
		 lx.eval('select.itemType %s mode:add' % type)


def init_ctype_dict_arr():
	arr = {}
	for type in list(t.compatibleItemType.viewkeys()):
		arr[type] = []

	return arr



def get_first_export_type(self):
	if self.exportFormatLxo_sw:
		return 'LXO'
	if self.exportFormatLwo_sw:
		return 'LWO'
	if self.exportFormatFbx_sw:
		return 'FBX'
	if self.exportFormatObj_sw:
		return 'OBJ'
	if self.exportFormatStl_sw:
		return 'STL'
	if self.exportFormatAbc_sw:
		return 'ABC'
	if self.exportFormatAbchdf_sw:
		return 'ABC-HDF'
	if self.exportFormatDae_sw:
		return 'DAE'
	if self.exportFormatDxf_sw:
		return 'DXF'
	if self.exportFormat3dm_sw:
		return '3DM'
	if self.exportFormatGeo_sw:
		return 'GEO'
	if self.exportFormatX3d_sw:
		return 'X3D'
	if self.exportFormatSvg_sw:
		return 'SVG'
	if self.exportFormatPlt_sw:
		return 'PLT'


def select_item_materials(self, items):
	sel = []
	for item in items:
		for matname in get_material_list_from_item(self,item):
			mat = modo.Item(matname + ' (Material)')
			sel.append(mat)

	self.scn.select(sel+items)


def get_material_list_from_item(self, item):
	tag = set([])

	for i in xrange(len(item.geometry.polygons)):
		tag.add(item.geometry.polygons[i].materialTag)

	return list(tag)


def get_udim_value(self, uv):
	x = math.ceil(uv[0])
	y = math.ceil(uv[1])

	if x>10 or x<1 or y<1:
		raise ValueError('invalid uv value')

	udim_value = x + 10*(y-1)
	return int(udim_value), int(1000 + udim_value)


def get_udim_tile(self, item, uvmap):
	udim = set([])
	for i in xrange(len(item.geometry.polygons)):
		vert = item.geometry.polygons[i].vertices
		for v in vert:
			uv = item.geometry.polygons[i].getUV(v, uvmap)
			udim.add(get_udim_value(self, uv)[1])

	return udim


def offset_uv(self, uv):
	lx.eval('tool.viewType uv')
	lx.eval('tool.set xfrm.transform on')
	lx.eval('tool.reset')
	lx.eval('tool.setAttr xfrm.transform U %s' % uv[0])
	lx.eval('tool.setAttr xfrm.transform V %s' % uv[1])
	lx.eval('tool.doApply')
	lx.eval('tool.set xfrm.transform off')


def get_normalize_uv_offset(self, uv):
	x = uv[0]
	y = uv[1]
	return [ - math.floor(x), - math.floor(y)]


def assign_material_and_move_udim(self, item, uvmap, udim, destination, color):
	main_layer = lx.eval1('query layerservice layer.index ? main')

	udim_dict = {}
	uv_offset_dict = {}

	for u in udim:
		udim_dict[u] = set([])
		uv_offset_dict[u] = []

	for i in xrange(len(item.geometry.polygons)):
		vert = item.geometry.polygons[i].vertices

		for v in vert:
			uv = item.geometry.polygons[i].getUV(v, uvmap)

			current_udim = get_udim_value(self, uv)[1]

			uv_offset_dict[current_udim] = get_normalize_uv_offset(self, uv)

			if current_udim in udim:
				udim_dict[current_udim].add(v.index)

	lx.eval('vertMap.list txuv %s' % uvmap)

	for u in udim_dict:
		lx.eval('select.type vertex')
		for v in udim_dict[u]:
			lx.eval('select.element %s vertex add index:%s' % (main_layer, v))

		lx.eval('select.convert polygon')
		offset_uv(self, uv_offset_dict[u])

		lx.eval('poly.setMaterial %s {%s %s %s} 0.8 0.04 true false' % (str(u), color[0], color[1], color[2]))

		lx.eval('select.drop vertex')
		lx.eval('select.drop polygon')
		lx.eval('select.drop item')
		lx.eval('select.drop item mask')
		lx.eval('select.drop item advancedMaterial')

		self.UDIMMaterials.add(modo.Item(str(u) + ' (Material)'))

	lx.eval('vertMap.list txuv _____n_o_n_e_____')

	lx.eval('select.type item')


def construct_replicator_dict(self):
	if len(self.itemToProceed['REPLICATOR']) > 0:
		self.replicator_dict = get_replicator_source(self, self.itemToProceed['REPLICATOR'])
		for o in self.replicator_dict.keys():  # Generate self.replicator_group_source
			if self.replicator_dict[o].source_is_group:
				self.replicator_group_source[o] = [self.replicator_dict[o].source_group_name, self.replicator_dict[o].source]
			elif len(self.replicator_dict[o].source) > 1:
				self.replicator_multiple_source[o] = self.replicator_dict[o].source
			else:
				self.replicator_non_group_source[o] = self.replicator_dict[o].source

# Cleaning


def revert_scene_preferences(self):
	# lx.eval('scene.set {}'.format(self.currScn))
	self.scn.select(self.userSelection)

	# Put the user's original Export setting back.
	if self.exportFormatFbx_sw:
		lx.eval('user.value sceneio.fbx.save.exportType %s' % self.defaultExportSettings['FBX_EXPORT_TYPE'])
		lx.eval('user.value sceneio.fbx.save.surfaceRefining %s' % self.defaultExportSettings['FBX_SURFACE_REFINING'])
		lx.eval('user.value sceneio.fbx.save.format %s' % self.defaultExportSettings['FBX_FORMAT'])


def clean_duplicates(self, closeScene=False):
	if closeScene:
		lx.eval('scene.set %s' % self.tempScnID)
		lx.eval('!scene.close')
	revert_scene_preferences(self)
	sys.exit()


def revert_initial_parameter(self):
	self.itemToProceed = init_ctype_dict_arr()
	self.sortedItemToProceed = []
	if self.exportEach_sw:
		self.proceededMesh = []
	else:
		self.proceededMesh = init_ctype_dict_arr()
	self.replicator_dict = {}
	self.proceededMeshIndex = 0
	self.progress = None
	self.progression = [0, 0]
	self.tempScnID = None
	self.replicatorSrcIgnoreList = ()
	self.firstIndex = init_ctype_dict_arr()


def reset_import_settings(self):
	# Put the user's original Import setting back.
	lx.eval('user.value sceneio.obj.import.static %s' % self.defaultImportSettings['OBJ_STATIC'])
	lx.eval('user.value sceneio.obj.import.separate.meshes %s' % self.defaultImportSettings['OBJ_SEPARATE_MESH'])
	lx.eval('user.value sceneio.obj.import.suppress.dialog %s' % self.defaultImportSettings['OBJ_SUPRESS_DIALOG'])
	lx.eval('user.value sceneio.obj.import.units %s' % self.defaultImportSettings['OBJ_UNIT'])


def clearitems():
	try:
		lx.eval('select.itemType mesh')
		lx.eval('select.itemType camera mode:add')
		lx.eval('select.itemType light super:true mode:add')
		lx.eval('select.itemType renderOutput mode:add')
		lx.eval('select.itemType defaultShader mode:add')
		lx.eval('!!item.delete')
	except:
		return_exception()


class ModoReplicator():
	def __init__(self, item):
		self._item = item
		self.item_name = item.name
		self._replicator = None
		self._source_group_name = self.source_group_name
		self.scn = modo.Scene()


	@property
	def replicator_item(self):
		self._item = modo.Item(self.item_name)
		return self._item

	@property
	def replicator_src_arr(self):
		self.scn = modo.Scene()
		selection = self.scn.selected

		lx.eval('select.item {}'.format(self._item.name))
		source = lx.eval('replicator.source ?')
		particle = lx.eval('replicator.particle ?')

		if 'group' in source:
			lx.eval('select.item {}'.format(source))
			lx.eval('group.scan sel item')
			source = self.scn.selected
			replicator = [source, self.scn.item(particle)]
			self.scn.select(selection)
			self._replicator = replicator
			return replicator
		elif isinstance(source, tuple) or isinstance(source, list):
			source_arr = []
			for o in source:
				source_arr.append(modo.Item(o))
			replicator = [source_arr, self.scn.item(particle)]
			self._replicator = replicator
			self.scn.select(selection)
			return replicator
		elif modo.Item(source).type in [t.itemType['MESH'], t.itemType['MESH_INSTANCE'], t.itemType['GROUP_LOCATOR'], t.itemType['LOCATOR']]:
			replicator = [[self.scn.item(source)], self.scn.item(particle)]
			self._replicator = replicator
			self.scn.select(selection)
			return replicator

		self.scn.select(selection)

	@property
	def source(self):
		return self.replicator_src_arr[0]

	@property
	def source_name(self):
		return get_name_arr(self.replicator_src_arr[0])

	@property
	def particle(self):
		return self.replicator_src_arr[1]

	def select_src_arr(self):
		self.scn = modo.Scene()
		self.scn.deselect()
		for o in self.replicator_src_arr[0]:
			self.scn.select(o, add=True)

		self.scn.select(self.replicator_src_arr[1], add=True)

	@property
	def source_is_group(self):
		if self._item.type == t.compatibleItemType['REPLICATOR']:
			self.scn = modo.Scene()
			selection = self.scn.selected

			lx.eval('select.item {}'.format(self._item.name))
			source = lx.eval('replicator.source ?')

			result = 'group' in source

			self.scn.select(selection)

			return result
		else:
			return False

	@property
	def source_group_name(self):
		if self.source_is_group:
			self.scn = modo.Scene()
			selection = self.scn.selected

			lx.eval('select.item {}'.format(self._item.name))
			source = lx.eval('replicator.source ?')

			group = modo.Item(source)

			self.scn.select(selection)

			return group.name

		else:
			return None

	@property
	def source_group(self):
		name = self.source_group_name
		if name is not None:
			for grp in self.scn.groups:
				if grp.name == name:
					return grp
		else:
			return None

	def set_source(self, source_arr):
		if self.replicator_item is not None:
			selection = self.scn.selected

			self.scn.select(self.replicator_item)

			if self.source_is_group:
				lx.eval('replicator.source "{}"'.format(self._source_group_name))
				group = modo.item.Group(self._source_group_name)
				for o in source_arr:
					if not group.hasItem(o):
						group.addItems(o)
			elif len(source_arr) == 1:
				lx.eval('replicator.source "{}"'.format(source_arr[0].name))
			else:
				for o in source_arr:
					# Need to link with multiple item
					lx.eval('item.link particle.proto {} {} replace:false'.format(o, self.replicator_item.name))
					# lx.eval('replicator.source "{}"'.format(o.name))

			self.scn.select(selection)
