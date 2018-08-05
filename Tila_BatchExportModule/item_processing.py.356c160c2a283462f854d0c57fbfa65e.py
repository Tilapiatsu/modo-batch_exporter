import lx
import modo
import sys
import random
import Tila_BatchExportModule as t
from Tila_BatchExportModule import helper
from Tila_BatchExportModule import dialog
# Item Processing


class ItemProcessing(helper.ModoHelper):
    mm = dialog.MessageManagement('ItemProcessing')

    def __init__(self, userValues=None):
        reload(helper)
        reload(dialog)

        super(ItemProcessing, self).__init__(userValues)

    # Progress bar
    def get_progression_message(self, message):
        return '%s / %s || %s' % (self.progression[0], self.progression[1], message)

    def increment_progress_bar(self, progress):
        if progress is not None:
            if not self.mm.increment_progress_bar(self, progress[0], self.progression, transform=True):
                sys.exit()

    # Item Processing
    def apply_morph(self, condition, name):
        if condition:
            message = 'Applying Morph Map : ' + name
            message = self.get_progression_message(message)
            self.increment_progress_bar(self.progress)
            self.mm.processing_log(message)

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
                message = self.get_progression_message(message)
                self.increment_progress_bar(self.progress)
                self.mm.processing_log(message)

            for o in self.scn.selected:
                if o.type == t.compatibleItemType['MESH'] and not self.item_have_deformers(o):
                    morph_maps = o.geometry.vmaps.morphMaps
                    for m in morph_maps:
                        self.mm.info('Delete {} morph map'.format(m.name))
                        lx.eval('!select.vertexMap {} morf replace'.format(m.name))
                        lx.eval('!!vertMap.delete morf')

    def smooth_angle(self):
        if self.smoothAngle_sw:
            message = "Harden edges witch are sharper than %s degrees" % self.smoothAngle
            message = self.get_progression_message(message)
            self.increment_progress_bar(self.progress)
            self.mm.processing_log(message)

            currAngle = lx.eval('user.value vnormkit.angle ?')
            lx.eval('user.value vnormkit.angle %s' % self.smoothAngle)
            lx.eval('vertMap.hardenNormals angle soften:true')
            lx.eval('user.value vnormkit.angle %s' % currAngle)
            lx.eval('vertMap.updateNormals')

    def harden_uv_border(self):
        if self.hardenUvBorder_sw:
            message = "HardenUvBorder = " + self.uvMapName
            message = self.get_progression_message(message)
            self.increment_progress_bar(self.progress)
            self.mm.processing_log(message)

            lx.eval('select.vertexMap {%s} txuv replace' % self.uvMapName)
            lx.eval('uv.selectBorder')
            lx.eval('vertMap.hardenNormals uv')
            lx.eval('vertMap.updateNormals')
            lx.eval('select.type item')

    def assign_material_per_udim(self, random_color):
        if self.assignMaterialPerUDIMTile_sw:
            message = "Assign Material per UDIM Tile = " + self.UDIMTextureName
            message = self.get_progression_message(message)
            self.increment_progress_bar(self.progress)
            self.mm.processing_log(message)

            selection = self.scn.selected

            for i in xrange(len(selection)):
                selection[i].select(replace=True)
                udim = self.get_udim_tile(selection[i], self.UDIMTextureName)

                if random_color:
                    color = [round(random.random(), 4), round(random.random(), 4), round(random.random(), 4)]
                else:
                    color = [1, 1, 1]
                self.assign_material_and_move_udim(selection[i], self.UDIMTextureName, udim, 1001, color)

            self.scn.select(selection)

    def triple(self):
        if self.triple_sw:
            message = "Triangulate"
            message = self.get_progression_message(message)
            self.increment_progress_bar(self.progress)
            self.mm.processing_log(message)

            try:
                lx.eval('!!poly.triple')
            except:
                pass

    def reset_pos(self):
        if self.resetPos_sw:
            message = "Reset Position"
            message = self.get_progression_message(message)
            self.increment_progress_bar(self.progress)
            self.mm.processing_log(message)

            lx.eval('!!transform.reset translation')

    def reset_rot(self):
        if self.resetRot_sw:
            message = "Reset Rotation"
            message = self.get_progression_message(message)
            self.increment_progress_bar(self.progress)
            self.mm.processing_log(message)

            lx.eval('!!transform.reset rotation')

    def reset_sca(self):
        if self.resetSca_sw:
            message = "Reset Scale"
            message = self.get_progression_message(message)
            self.increment_progress_bar(self.progress)
            self.mm.processing_log(message)

            lx.eval('!!transform.reset scale')

    def reset_she(self):
        if self.resetShe_sw:
            message = "Reset Shear"
            message = self.get_progression_message(message)
            self.increment_progress_bar(self.progress)
            self.mm.processing_log(message)

            lx.eval('!!transform.reset shear')

    def freeze_pos(self):
        if self.freezePos_sw:
            message = "Freeze Position"
            message = self.get_progression_message(message)
            self.increment_progress_bar(self.progress)
            self.mm.processing_log(message)

            lx.eval('!!transform.freeze translation')
            # lx.eval('vertMap.updateNormals')

    def freeze_rot(self):
        if self.freezeRot_sw:
            message = "Freeze Rotation"
            message = self.get_progression_message(message)
            self.increment_progress_bar(self.progress)
            self.mm.processing_log(message)

            lx.eval('!!transform.freeze rotation')
            # lx.eval('vertMap.updateNormals')

    def freeze_sca(self, force=False):
        if self.freezeSca_sw or force:
            if not force:
                message = "Freeze Scale"
                message = self.get_progression_message(message)
                self.increment_progress_bar(self.progress)
                self.mm.processing_log(message)

            lx.eval('!!transform.freeze scale')
            # lx.eval('vertMap.updateNormals')

    def freeze_she(self):
        if self.freezeShe_sw:
            message = "Freeze Shear"
            message = self.get_progression_message(message)
            self.increment_progress_bar(self.progress)
            self.mm.processing_log(message)

            lx.eval('!!transform.freeze shear')
            # lx.eval('vertMap.updateNormals')

    def freeze_geo(self):
        if self.freezeGeo_sw:
            message = "Freeze Geometry"
            message = self.get_progression_message(message)
            self.increment_progress_bar(self.progress)
            self.mm.processing_log(message)

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
                        # dialog.transform_log('Freeze Scaling after Instance Freeze')
                        self.freeze_sca(True)
                        lx.eval('vertMap.updateNormals')

                    if not self.exportFile_sw:
                        self.userSelection[first_index + i] = item
                    elif update_arr:
                        self.proceededMesh[first_index + i] = item

    def freeze_meshfusion(self, ctype):
        if ctype == t.itemType['MESH_FUSION']:

            message = "Freeze MeshFusion"
            message = self.get_progression_message(message)
            self.increment_progress_bar(self.progress)
            self.mm.processing_log(message)

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
        if (self.freezeMeshOp_sw or force) and ctype == t.itemType['MESH']:
            if not force:
                message = "Freeze Deformers"
                message = self.get_progression_message(message)
                self.increment_progress_bar(self.progress)
                self.mm.processing_log(message)

            selection = self.scn.selected
            for i in xrange(0, len(selection)):
                curr_item = selection[i]
                if self.item_have_deformers(curr_item):
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
            self.freeze_deformers(self, t.itemType['MESH'], force=True)

    def freeze_replicator(self, ctype, update_arr=True, force=False):
        if self.freezeReplicator_sw or force:
            if ctype == t.itemType['REPLICATOR']:
                first_index = 0

                message = "Freeze Replicator"
                message = self.get_progression_message(message)
                self.increment_progress_bar(self.progress)
                self.mm.processing_log(message)

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
                                            item_in_user_selection = item_name in self.get_name_arr(self.proceededMesh)
                                        else:
                                            item_in_user_selection = item_name in self.get_name_arr(self.proceededMesh[self.get_key_from_value(t.compatibleItemType, ctype)])

                                        if item_name not in self.replicatorSrcIgnoreList and not item_in_user_selection:
                                            self.scn.select(item)
                                            lx.eval('!!item.delete')
                                            self.mm.print_log('Delete replicator source : {}'.format(item_name))
                                            self.replicatorSrcIgnoreList = self.replicatorSrcIgnoreList + (item_name,)
                                    except:
                                        self.return_exception()

                if self.exportEach_sw:
                    self.replicatorSrcIgnoreList = ()

                self.scn.select(frozenItem_arr)

    def force_freeze_replicator(self):
        # Force Freeze replicator if the item use a group source replicator
        self.scn.deselect()
        self.select_compatible_item_type()
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
            self.freeze_replicator(self, t.itemType['REPLICATOR'], force=True)

        self.replicatorSrcIgnoreList = ()

    def position_offset(self):
        if (self.posX != 0.0 or self.posY != 0.0 or self.posZ != 0.0) and self.pos_sw:
            message = "Position offset = (%s, %s, %s)" % (self.posX, self.posY, self.posZ)
            message = self.get_progression_message(message)
            self.increment_progress_bar(self.progress)
            self.mm.processing_log(message)

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
            message = self.get_progression_message(message)
            self.increment_progress_bar(self.progress)
            self.mm.processing_log(message)

            selection = self.scn.selected

            for i in self.scn.selected:
                self.scn.select(i)
                currScale = i.scale

                self.freeze_sca(self)
                lx.eval('transform.channel scl.X %s' % str(float(self.scaX) * currScale.x.get()))
                lx.eval('transform.channel scl.Y %s' % str(float(self.scaY) * currScale.y.get()))
                lx.eval('transform.channel scl.Z %s' % str(float(self.scaZ) * currScale.z.get()))

            self.scn.select(selection)

    def rot_angle(self):
        if (self.rotX != 0.0 or self.rotY != 0.0 or self.rotZ != 0.0) and self.rot_sw:
            message = "Rotation Angle = (%s, %s, %s)" % (self.rotX, self.rotY, self.rotZ)
            message = self.get_progression_message(message)
            self.increment_progress_bar(self.progress)
            self.mm.processing_log(message)

            selection = self.scn.selected

            for i in self.scn.selected:
                self.scn.select(i)
                currRotation = i.rotation

                lx.eval('transform.freeze rotation')
                lx.eval('transform.channel rot.X "%s"' % str(float(self.rotX) + currRotation.x.get()))
                lx.eval('transform.channel rot.Y "%s"' % str(float(self.rotY) + currRotation.y.get()))
                lx.eval('transform.channel rot.Z "%s"' % str(float(self.rotZ) + currRotation.z.get()))

            self.scn.select(selection)
            # freeze_rot(self)

    def merge_meshes(self, item):
        message = 'Merging Meshes'
        message = self.get_progression_message(message)
        self.increment_progress_bar(self.progress)
        self.mm.processing_log(message)

        self.scn.select(item)

        name_arr = self.get_name_arr(item)

        for o in self.scn.selected:
            if o.type in [t.compatibleItemType['GROUP_LOCATOR'], t.compatibleItemType['LOCATOR']]:
                self.scn.select(o)
                lx.eval('item.setType.mesh')

        for o in name_arr:
            self.scn.select(o, add=True)

        self.select_hierarchy(self, force=True)
        lx.eval('layer.mergeMeshes true')


class ModoItem(ItemProcessing):

    def __init__(self, item):
        ItemProcessing.__init__()
        self._item = item
        self.item_name = item.name


class ModoReplicatorItem(ModoItem):
    def __init__(self, item):
        ModoItem.__init__(self, item)
        self._replicator = None
        self._source_group_name = self.source_group_name

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
        return self.get_name_arr(self.replicator_src_arr[0])

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
                lx.eval('replicator.source "{}"'.format(
                        self._source_group_name))
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


class ModoDeformerItem(ModoItem):
    # is Used by MOP Item
    def __init__(self, item):
        ModoItem.__init__(self, item)
        self.deformer_group = None
        self._deformer_item = None
        self._deformers = None
        if not self.is_deformer_item():
            self.mm.warning('The item {} has no deformer'.format(self.item_name))

    @property
    def deformer_item(self):
        self._deformer_item = modo.Item(self.item_name)
        return self._deformer_item

    @deformer_item.setter
    def deformer_item(self, item):
        self._deformer_item = item
        self.item_name = item.name

    @property
    def is_deformer_item(self):
        if len(self.deformer_item.deformers):
            return True
        else:
            return False

    @property
    def deformers(self):
        if self.is_deformer_item:
            self._deformers = self.deformer_item.deformers
            return self._deformers
        else:
            self.mm.warning('The item {} has no deformer'.format(self.item_name))
            return None

    def get_deformer_by_name(self, name, absolute=True):
        for d in self.deformers:
            if absolute:
                if name == d.name:
                    return d
            else:
                if name in d.name:
                    return d
        else:
            return None

    def rename_deformer_by_name(self, old_name, new_name):
        deformer = self.get_deformer_by_name(old_name)

        if deformer:
            deformer.name = new_name
            return True
        else:
            return False

    @property
    def deformer_names(self):
        return self.get_name_arr(self.deformers)

    def select_deformers(self):
        i = 0
        for o in self.deformers:
            if i == 0:
                lx.eval('select.deformer "{}" set'.format(o))
            else:
                lx.eval('select.deformer "{}" add'.format(o))
            i = i + 1

    def group_deformers(self):
        # Create a Deform Group
        if self.deformer_group is None:
            lx.eval('deformer.create deformFolder')
            self.deformer_group = self.scn.selected[0]
            self.deformer_group.name = self.item_name + '_DF'

        i = 0
        for d in self.deformers:
            lx.eval('deformer.setGroup "{}" "{}" {}'.format(d.name, self.deformer_group.name, i))

    def ungroup_deformers(self):  # It break The OoO ! Don't use tt as it is
        deformers_count = len(self.deformers)

        for d in self.deformers:
            lx.eval('deformer.setGroup "{}" seq:{}'.format(d.name, str(deformers_count - 1)))

        self.scn.removeItems(self.deformer_group, False)

    def reorder_deformers(self, new_order):
        for d in new_order:
            if d in self.deformer_names:
                index = self.deformer_names.index(d)
                lx.eval('deformer.setGroup "{}" seq:0'.format(self.deformers[index].name))
