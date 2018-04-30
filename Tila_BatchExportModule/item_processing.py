import lx
import modo
import dialog
import sys
import random
import time
import Tila_BatchExportModule as t
from Tila_BatchExportModule import helper

# Item Processing


def get_progression_message(self, message):
	return '%s / %s || %s' % (self.progression[0], self.progression[1], message)


def increment_progress_bar(self, progress):
	if progress is not None:
		if not dialog.increment_progress_bar(self, progress[0], self.progression, transform=True):
			sys.exit()


def apply_morph(self, condition, name):
	if condition:
		message = 'Applying Morph Map : ' + name
		message = get_progression_message(self, message)
		increment_progress_bar(self, self.progress)
		dialog.processing_log(message)

		morph_maps = name.split(',')
		selection = self.scn.selected
		ignore_source_list = ()
		for o in selection:
			self.scn.deselect()
			lx.eval('select.item {}'.format(o.name))
			if o.type == t.compatibleItemType['GROUP_LOCATOR'] or o.type == t.compatibleItemType['LOCATOR']:
				sub_selection = self.scn.selected
				for i in xrange(0, len(sub_selection)):
					if i > 0:
						for maps in morph_maps:
							lx.eval('vertMap.applyMorph %s 1.0' % maps)
			elif o.type == t.compatibleItemType['MESH']:
				for maps in morph_maps:
					lx.eval('vertMap.applyMorph %s 1.0' % maps)
			elif o.type == t.compatibleItemType['REPLICATOR']:
				for s in self.replicator_dict[o.name].source:
					if s not in ignore_source_list:
						ignore_source_list = ignore_source_list + (s,)
						self.scn.deselect()
						lx.eval('select.item "{}"'.format(s.name))
						for maps in morph_maps:
							lx.eval('vertMap.applyMorph %s 1.0' % maps)
			else:
				continue
		self.scn.select(selection)


def export_morph(self, force=False):
	if not self.exportMorphMap_sw or force:
		if not force:
			message = 'Cleaning Morph Map'
			message = get_progression_message(self, message)
			increment_progress_bar(self, self.progress)
			dialog.processing_log(message)

		for o in self.scn.selected:
			if o.type == t.compatibleItemType['MESH'] and not helper.item_have_deformers(o):
				morph_maps = o.geometry.vmaps.morphMaps
				for m in morph_maps:
					dialog.print_log('Delete {} morph map'.format(m.name))
					lx.eval('!select.vertexMap {} morf replace'.format(m.name))
					lx.eval('!!vertMap.delete morf')


def smooth_angle(self):
	if self.smoothAngle_sw:
		message = "Harden edges witch are sharper than %s degrees" % self.smoothAngle
		message = get_progression_message(self, message)
		increment_progress_bar(self, self.progress)
		dialog.processing_log(message)
		currAngle = lx.eval('user.value vnormkit.angle ?')
		lx.eval('user.value vnormkit.angle %s' % self.smoothAngle)
		lx.eval('vertMap.hardenNormals angle soften:true')
		lx.eval('user.value vnormkit.angle %s' % currAngle)
		lx.eval('vertMap.updateNormals')


def harden_uv_border(self):
	if self.hardenUvBorder_sw:
		message = "HardenUvBorder = " + self.uvMapName
		message = get_progression_message(self, message)
		increment_progress_bar(self, self.progress)
		dialog.processing_log(message)
		lx.eval('select.vertexMap {%s} txuv replace' % self.uvMapName)
		lx.eval('uv.selectBorder')
		lx.eval('vertMap.hardenNormals uv')
		lx.eval('vertMap.updateNormals')
		lx.eval('select.type item')


def assign_material_per_udim(self, random_color):
	if self.assignMaterialPerUDIMTile_sw:
		message = "Assign Material per UDIM Tile = " + self.UDIMTextureName
		message = get_progression_message(self, message)
		increment_progress_bar(self, self.progress)
		dialog.processing_log(message)

		selection = self.scn.selected

		for i in xrange(len(selection)):
			selection[i].select(replace=True)
			udim = helper.get_udim_tile(self, selection[i], self.UDIMTextureName)

			if random_color:
				color = [round(random.random(),4), round(random.random(),4), round(random.random(),4)]
			else:
				color = [1, 1, 1]
			helper.assign_material_and_move_udim(self, selection[i], self.UDIMTextureName, udim, 1001, color)

		self.scn.select(selection)


def triple(self):
	if self.triple_sw:
		message = "Triangulate"
		message = get_progression_message(self, message)
		increment_progress_bar(self, self.progress)
		dialog.processing_log(message)
		try:
			lx.eval('!!poly.triple')
		except:
			pass


def reset_pos(self):
	if self.resetPos_sw:
		message = "Reset Position"
		message = get_progression_message(self, message)
		increment_progress_bar(self, self.progress)
		dialog.transform_log(message)
		lx.eval('!!transform.reset translation')


def reset_rot(self):
	if self.resetRot_sw:
		message = "Reset Rotation"
		message = get_progression_message(self, message)
		increment_progress_bar(self, self.progress)
		dialog.transform_log(message)
		lx.eval('!!transform.reset rotation')


def reset_sca(self):
	if self.resetSca_sw:
		message = "Reset Scale"
		message = get_progression_message(self, message)
		increment_progress_bar(self, self.progress)
		dialog.transform_log(message)
		lx.eval('!!transform.reset scale')


def reset_she(self):
	if self.resetShe_sw:
		message = "Reset Shear"
		message = get_progression_message(self, message)
		increment_progress_bar(self, self.progress)
		dialog.transform_log(message)
		lx.eval('!!transform.reset shear')


def freeze_pos(self):
	if self.freezePos_sw:
		message = "Freeze Position"
		message = get_progression_message(self, message)
		increment_progress_bar(self, self.progress)
		dialog.transform_log(message)

		lx.eval('!!transform.freeze translation')
		#lx.eval('vertMap.updateNormals')


def freeze_rot(self):
	if self.freezeRot_sw:
		message = "Freeze Rotation"
		message = get_progression_message(self, message)
		increment_progress_bar(self, self.progress)
		dialog.transform_log(message)

		lx.eval('!!transform.freeze rotation')
		#lx.eval('vertMap.updateNormals')


def freeze_sca(self, force=False):
	if self.freezeSca_sw or force:
		if not force:
			message = "Freeze Scale"
			message = get_progression_message(self, message)
			increment_progress_bar(self, self.progress)
			dialog.transform_log(message)

		lx.eval('!!transform.freeze scale')
		#lx.eval('vertMap.updateNormals')


def freeze_she(self):
	if self.freezeShe_sw:
		message = "Freeze Shear"
		message = get_progression_message(self, message)
		increment_progress_bar(self, self.progress)
		dialog.transform_log(message)

		lx.eval('!!transform.freeze shear')
		#lx.eval('vertMap.updateNormals')


def freeze_geo(self):
	if self.freezeGeo_sw:
		message = "Freeze Geometry"
		message = get_progression_message(self, message)
		increment_progress_bar(self, self.progress)
		dialog.transform_log(message)
		lx.eval('poly.freeze polyline true 2 true true true false 4.0 true Morph')


def freeze_instance(self, ctype=t.itemType['MESH_INSTANCE'], update_arr=True, first_index=0):
	compatibleType = [t.itemType['MESH_INSTANCE']]
	if ctype in compatibleType and self.scn.selected[0].type in compatibleType:
		if self.exportFile_sw or ((not self.exportFile_sw) and (self.freezeInstance_sw or self.freezePos_sw or self.freezeRot_sw or self.freezeSca_sw or self.freezeShe_sw)):
			#
			# message = "Freeze Instance"
			# message = get_progression_message(self, message)
			# increment_progress_bar(self, self.progress)
			# dialog.transform_log(message)

			lx.eval('item.setType.mesh')

			selection = self.scn.selected
			for i in xrange(0, len(selection)):

				item = selection[i]
				item.select(replace=True)

				currScale = item.Item.scale

				if currScale.x.get() < 0 or currScale.y.get() < 0 or currScale.z.get() < 0:
					#dialog.transform_log('Freeze Scaling after Instance Freeze')
					freeze_sca(self, True)
					lx.eval('vertMap.updateNormals')

				if not self.exportFile_sw:
					self.userSelection[first_index + i] = item
				elif update_arr:
					self.proceededMesh[first_index + i] = item


def freeze_meshfusion(self, ctype):
	if ctype == t.itemType['MESH_FUSION']:

		message = "Freeze MeshFusion"
		message = get_progression_message(self, message)
		increment_progress_bar(self, self.progress)
		dialog.transform_log(message)

		selection = self.scn.selected
		for i in xrange(0, len(selection)):
			self.scn.select(selection[i])
			name = self.scn.selected[0].name
			lx.eval('item.channel OutputMeshMode outModeFinalParts')
			lx.eval('user.value sdf.outDup false')
			lx.eval('user.value sdf.meshOutName "%s"' % name)
			lx.eval('!!@tila.meshout')
			selection[i] = self.scn.item(name)
			self.scn.select(selection)


def freeze_deformers(self, ctype, force=False):
	if (self.freezeMeshOp_sw or force) and ctype == t.itemType['MESH'] :
		if not force:
			message = "Freeze Deformers"
			message = get_progression_message(self, message)
			increment_progress_bar(self, self.progress)
			dialog.transform_log(message)

		selection = self.scn.selected
		for i in xrange(0, len(selection)):
			curr_item = selection[i]
			if helper.item_have_deformers(curr_item):
				self.scn.select(curr_item)
				lx.eval('deformer.freeze false')
				self.scn.select(selection)


def force_freeze_deformers(self):
	selection = self.scn.selected
	self.scn.deselect()

	for o in selection:
		if o.name in self.deformer_item_dict.keys():
			self.scn.select(o.name, add=True)

	if len(self.scn.selected):
		freeze_deformers(self, t.itemType['MESH'], force=True)


def freeze_replicator(self, ctype, update_arr=True, force=False):
	if self.freezeReplicator_sw or force:
		if ctype == t.itemType['REPLICATOR']:
			first_index = 0

			message = "Freeze Replicator"
			message = get_progression_message(self, message)
			increment_progress_bar(self, self.progress)
			dialog.transform_log(message)

			frozenItem_arr = []
			source_dict = {}

			selection = self.scn.selected

			i = 0
			for o in selection:
				originalName = o.name
				self.scn.deselect()
				self.scn.select(originalName)

				source_dict[originalName] = self.replicator_dict[originalName].replicator_src_arr

				lx.eval(t.TILA_FREEZE_REPLICATOR)

				frozenItem = modo.Item(originalName)

				selection[i] = frozenItem

				frozenItem_arr.append(frozenItem)

				if not self.exportFile_sw:
					self.userSelection[first_index + i] = frozenItem
				elif update_arr:
					if self.exportEach_sw:
						self.proceededMesh[first_index + i] = frozenItem
					else:
						self.proceededMesh['REPLICATOR'][first_index + i] = frozenItem

				i += 1

			for o in selection:  # remove replicator source and particle
				if self.exportFile_sw:
					for k, source in source_dict.iteritems():
						if o.name == k:
							# Construct source arr
							source_arr = []
							for i in source[0]:
								source_arr.append(i)
							source_arr.append(source[1])

							for item in source_arr:
								item_name = item.name
								try:
									if self.exportEach_sw:
										item_in_user_selection = item_name in helper.get_name_arr(self.proceededMesh)
									else:
										item_in_user_selection = item_name in helper.get_name_arr(self.proceededMesh[helper.get_key_from_value(t.compatibleItemType, ctype)])

									if item_name not in self.replicatorSrcIgnoreList and not item_in_user_selection:
										self.scn.select(item)
										lx.eval('!!item.delete')
										dialog.print_log('Delete replicator source : {}'.format(item_name))
										self.replicatorSrcIgnoreList = self.replicatorSrcIgnoreList + (item_name,)
								except:
									helper.return_exception()

			if self.exportEach_sw:
				self.replicatorSrcIgnoreList = ()

			self.scn.select(frozenItem_arr)


def force_freeze_replicator(self):
	# Force Freeze replicator if the item use a group source replicator
	self.scn.deselect()
	helper.select_compatible_item_type()
	selection = self.scn.selected
	self.scn.deselect()

	# Feed self.replicatorSrcIgnoreList
	for key in self.replicator_non_group_source.keys():
		for o in self.replicator_non_group_source[key]:
			self.replicatorSrcIgnoreList = self.replicatorSrcIgnoreList + (o.name,)

	for o in selection:  # Select Replicator Objects to force freeze
		if o.type == t.compatibleItemType['REPLICATOR']:
			if o.name in self.replicator_group_source.keys() or o.name in self.replicator_multiple_source.keys():
				self.scn.select(o.name, add=True)

	if len(self.scn.selected):
		freeze_replicator(self, t.itemType['REPLICATOR'], force=True)

	self.replicatorSrcIgnoreList = ()


def position_offset(self):
	if (self.posX != 0.0 or self.posY != 0.0 or self.posZ != 0.0) and self.pos_sw:
		message = "Position offset = (%s, %s, %s)" % (self.posX, self.posY, self.posZ)
		message = get_progression_message(self, message)
		increment_progress_bar(self, self.progress)
		dialog.transform_log(message)

		selection = self.scn.selected

		for i in self.scn.selected:
			self.scn.select(i)
			currPosition = i.position

			lx.eval('transform.channel pos.X %s' % str(float(self.posX) + currPosition.x.get()))
			lx.eval('transform.channel pos.Y %s' % str(float(self.posY) + currPosition.y.get()))
			lx.eval('transform.channel pos.Z %s' % str(float(self.posZ) + currPosition.z.get()))

		self.scn.select(selection)


def scale_amount(self):
	if (self.scaX != 1.0 or self.scaY != 1.0 or self.scaZ != 1.0) and self.sca_sw:
		message = "Scale amount = (%s, %s, %s)" % (self.scaX, self.scaY, self.scaZ)
		message = get_progression_message(self, message)
		increment_progress_bar(self, self.progress)
		dialog.transform_log(message)

		selection = self.scn.selected

		for i in self.scn.selected:
			self.scn.select(i)
			currScale = i.scale

			freeze_sca(self)
			lx.eval('transform.channel scl.X %s' % str(float(self.scaX) * currScale.x.get()))
			lx.eval('transform.channel scl.Y %s' % str(float(self.scaY) * currScale.y.get()))
			lx.eval('transform.channel scl.Z %s' % str(float(self.scaZ) * currScale.z.get()))

		self.scn.select(selection)


def rot_angle(self):
	if (self.rotX != 0.0 or self.rotY != 0.0 or self.rotZ != 0.0) and self.rot_sw:
		message = "Rotation Angle = (%s, %s, %s)" % (self.rotX, self.rotY, self.rotZ)
		message = get_progression_message(self, message)
		increment_progress_bar(self, self.progress)
		dialog.transform_log(message)

		selection = self.scn.selected

		for i in self.scn.selected:
			self.scn.select(i)
			currRotation = i.rotation

			lx.eval('transform.freeze rotation')
			lx.eval('transform.channel rot.X "%s"' % str(float(self.rotX) + currRotation.x.get()))
			lx.eval('transform.channel rot.Y "%s"' % str(float(self.rotY) + currRotation.y.get()))
			lx.eval('transform.channel rot.Z "%s"' % str(float(self.rotZ) + currRotation.z.get()))

		self.scn.select(selection)
		#freeze_rot(self)


def merge_meshes(self, item):
	message = 'Merging Meshes'
	message = get_progression_message(self, message)
	increment_progress_bar(self, self.progress)
	dialog.processing_log(message)
	self.scn.select(item)

	name_arr = helper.get_name_arr(item)

	for o in self.scn.selected:
		if o.type in [t.compatibleItemType['GROUP_LOCATOR'], t.compatibleItemType['LOCATOR']]:
			self.scn.select(o)
			lx.eval('item.setType.mesh')

	for o in name_arr:
		self.scn.select(o, add=True)

	helper.select_hierarchy(self, force=True)
	lx.eval('layer.mergeMeshes true')
