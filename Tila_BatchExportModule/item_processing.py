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
		for o in selection:
			self.scn.select(o)
			if o.type == t.compatibleItemType['GROUP_LOCATOR'] or o.type == t.compatibleItemType['LOCATOR']:
				sub_selection = self.scn.selected
				for i in xrange(0, len(sub_selection)):
					if i > 0:
						for maps in morph_maps:
							lx.eval('vertMap.applyMorph %s 1.0' % maps)
			else:
				for maps in morph_maps:
					lx.eval('vertMap.applyMorph %s 1.0' % maps)
		self.scn.select(selection)


def clean_morph(self):
	if self.cleanMorphMap_sw:
		message = 'Cleaning Morph Map '
		message = get_progression_message(self, message)
		increment_progress_bar(self, self.progress)
		dialog.processing_log(message)
		for o in self.scn.selected:
			if o.type == t.compatibleItemType['MESH']:
				morph_maps = o.geometry.vmaps.morphMaps
				for m in morph_maps:
					lx.eval('select.vertexMap {} morf replace'.format(m.name))
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
		lx.eval('poly.triple')


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

def freeze_instance(self, type='meshInst', update_arr=True, first_index=0):
	compatibleType = [t.itemType['MESH_INSTANCE']]
	if type in compatibleType and self.scn.selected[0].type in compatibleType:
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

				currScale = item.scale

				if currScale.x.get() < 0 or currScale.y.get() < 0 or currScale.z.get() < 0:
					#dialog.transform_log('Freeze Scaling after Instance Freeze')
					freeze_sca(self, True)
					lx.eval('vertMap.updateNormals')

				if not self.exportFile_sw:
					self.userSelection[first_index + i] = item
				elif update_arr:
					self.proceededMesh[first_index + i] = item


def freeze_meshfusion(self, type):
	if type == t.itemType['MESH_FUSION']:

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


def freeze_meshop(self, type):
	if self.freezeMeshOp_sw and type == t.itemType['MESH']:

		message = "Freeze MeshOp"
		message = get_progression_message(self, message)
		increment_progress_bar(self, self.progress)
		dialog.transform_log(message)

		selection = self.scn.selected
		for i in xrange(0, len(selection)):
			self.scn.select(selection[i])
			lx.eval('deformer.freeze false')
			self.scn.select(selection)


def freeze_replicator(self, type, update_arr=True, first_index=0):
	if type == t.itemType['REPLICATOR']:

		message = "Freeze Replicator"
		message = get_progression_message(self, message)
		increment_progress_bar(self, self.progress)
		dialog.transform_log(message)

		frozenItem_arr = []

		selection = self.scn.selected
		for i in xrange(0, len(selection)):
			selection[i].select(replace=True)
			originalName = self.scn.selected[0].name

			lx.eval('replicator.freeze')

			item = modo.Item(originalName)
			children = item.children()

			self.scn.select(children)

			lx.eval('item.setType.mesh')
			lx.eval('layer.mergeMeshes true')

			trimed_selection = selection[i:]
			#print trimed_selection
			helper.replace_replicator_source(self, trimed_selection)

			frozenItem = modo.Item(self.scn.selected[0].name)
			frozenItem.setParent()

			self.scn.select(item)

			lx.eval('!!item.delete')

			frozenItem.name = originalName

			frozenItem_arr.append(frozenItem)

			if not self.exportFile_sw:
				self.userSelection[first_index + i] = frozenItem
			elif update_arr:
				self.proceededMesh[first_index + i] = frozenItem

		self.scn.select(frozenItem_arr)


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
	lx.eval('layer.mergeMeshes true')
