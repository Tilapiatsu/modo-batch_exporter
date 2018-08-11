import lx
import modo
import sys
import random
import Tila_BatchExportModule as t
from Tila_BatchExportModule import helper
from Tila_BatchExportModule import dialog
from Tila_BatchExportModule import modoItem
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

    def conditionTesting(func):
        def func_wrapper(self, condition, items, **kwargs):
            force = False
            for key, value in kwargs.items():
                if key == 'force':
                    force = value
            if condition or force:
                return func(self, condition, items, **kwargs)
        return func_wrapper
    # Item Processing

    @conditionTesting
    def apply_morph(self, condition, items, name=""):
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

    @conditionTesting
    def export_morph(self, condition, items, force=False):
        if not force:
            message = 'Cleaning Morph Map'
            message = self.get_progression_message(message)
            self.increment_progress_bar(self.progress)
            self.mm.processing_log(message)

        for o in self.scn.selected:
            o = modoItem.convert_to_modoItem(o)
            if o.type == t.compatibleItemType['MESH'] and not o.have_deformers():
                morph_maps = o.geometry.vmaps.morphMaps
                for m in morph_maps:
                    self.mm.info('Delete {} morph map'.format(m.name))
                    lx.eval('!select.vertexMap {} morf replace'.format(m.name))
                    lx.eval('!!vertMap.delete morf')

    @conditionTesting
    def smooth_angle(self, condition, items):
        message = "Harden edges witch are sharper than %s degrees" % self.smoothAngle
        message = self.get_progression_message(message)
        self.increment_progress_bar(self.progress)
        self.mm.processing_log(message)

        currAngle = lx.eval('user.value vnormkit.angle ?')
        lx.eval('user.value vnormkit.angle %s' % self.smoothAngle)
        lx.eval('vertMap.hardenNormals angle soften:true')
        lx.eval('user.value vnormkit.angle %s' % currAngle)
        lx.eval('vertMap.updateNormals')

    @conditionTesting
    def harden_uv_border(self, condition, items):
        message = "HardenUvBorder = " + self.uvMapName
        message = self.get_progression_message(message)
        self.increment_progress_bar(self.progress)
        self.mm.processing_log(message)

        lx.eval('select.vertexMap {%s} txuv replace' % self.uvMapName)
        lx.eval('uv.selectBorder')
        lx.eval('vertMap.hardenNormals uv')
        lx.eval('vertMap.updateNormals')
        lx.eval('select.type item')

    @conditionTesting
    def assign_material_per_udim(self, condition, items, random_color=True):
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

    @conditionTesting
    def triple(self, condition, items):
        message = "Triangulate"
        message = self.get_progression_message(message)
        self.increment_progress_bar(self.progress)
        self.mm.processing_log(message)

        try:
            lx.eval('!!poly.triple')
        except:
            pass

    @conditionTesting
    def reset_pos(self, condition, items):
        message = "Reset Position"
        message = self.get_progression_message(message)
        self.increment_progress_bar(self.progress)
        self.mm.processing_log(message)

        lx.eval('!!transform.reset translation')

    @conditionTesting
    def reset_rot(self, condition, items):
        message = "Reset Rotation"
        message = self.get_progression_message(message)
        self.increment_progress_bar(self.progress)
        self.mm.processing_log(message)

        lx.eval('!!transform.reset rotation')

    @conditionTesting
    def reset_sca(self, condition, items):
        message = "Reset Scale"
        message = self.get_progression_message(message)
        self.increment_progress_bar(self.progress)
        self.mm.processing_log(message)

        lx.eval('!!transform.reset scale')

    @conditionTesting
    def reset_she(self, condition, items):
        message = "Reset Shear"
        message = self.get_progression_message(message)
        self.increment_progress_bar(self.progress)
        self.mm.processing_log(message)

        lx.eval('!!transform.reset shear')

    @conditionTesting
    def freeze_pos(self, condition, items):
        message = "Freeze Position"
        message = self.get_progression_message(message)
        self.increment_progress_bar(self.progress)
        self.mm.processing_log(message)

        lx.eval('!!transform.freeze translation')
        # lx.eval('vertMap.updateNormals')

    @conditionTesting
    def freeze_rot(self, condition, items):
        message = "Freeze Rotation"
        message = self.get_progression_message(message)
        self.increment_progress_bar(self.progress)
        self.mm.processing_log(message)

        lx.eval('!!transform.freeze rotation')
        # lx.eval('vertMap.updateNormals')

    @conditionTesting
    def freeze_sca(self, condition, items, force=False):
        if not force:
            message = "Freeze Scale"
            message = self.get_progression_message(message)
            self.increment_progress_bar(self.progress)
            self.mm.processing_log(message)

        lx.eval('!!transform.freeze scale')
        # lx.eval('vertMap.updateNormals')

    @conditionTesting
    def freeze_she(self, condition, items):
        message = "Freeze Shear"
        message = self.get_progression_message(message)
        self.increment_progress_bar(self.progress)
        self.mm.processing_log(message)

        lx.eval('!!transform.freeze shear')
        # lx.eval('vertMap.updateNormals')

    @conditionTesting
    def freeze_geo(self, condition, items):
        message = "Freeze Geometry"
        message = self.get_progression_message(message)
        self.increment_progress_bar(self.progress)
        self.mm.processing_log(message)

        lx.eval('poly.freeze polyline true 2 true true true false 4.0 true Morph')

    @conditionTesting
    def freeze_instance(self, condition, items):
        for o in items:
            if o.type == t.itemType['MESH_INSTANCE']:
                #
                # message = "Freeze Instance"
                # message = get_progression_message(self, message)
                # increment_progress_bar(self, self.progress)
                # dialog.transform_log(message)
                o.select(replace=True)
                lx.eval('item.setType.mesh')

                currScale = o.scale

                if currScale.x.get() < 0 or currScale.y.get() < 0 or currScale.z.get() < 0:
                    # dialog.transform_log('Freeze Scaling after Instance Freeze')
                    self.freeze_sca(True)
                    lx.eval('vertMap.updateNormals')

    @conditionTesting
    def freeze_meshfusion(self, condition, items):
        selection = self.scn.selected
        for o in self.currentlyProcessing:
            if o.type == t.itemType['MESH_FUSION']:
                message = "Freeze MeshFusion"
                message = self.get_progression_message(message)
                self.increment_progress_bar(self.progress)
                self.mm.processing_log(message)

                self.scn.select(o)
                name = o.name
                lx.eval('item.channel OutputMeshMode outModeFinalParts')
                lx.eval('user.value sdf.outDup false')
                lx.eval('user.value sdf.meshOutName "%s"' % name)
                lx.eval('!!@tila.meshout')
                o = self.scn.item(name)

        self.scn.select(selection)

    @conditionTesting
    def freeze_deformers(self, condition, items, force=False):
        selection = self.scn.selected
        for o in self.currentlyProcessing:
            if not force:
                message = "Freeze Deformers"
                message = self.get_progression_message(message)
                self.increment_progress_bar(self.progress)
                self.mm.processing_log(message)

            self.scn.select(o)
            lx.eval('deformer.freeze false')
        self.scn.select(selection)

    @conditionTesting
    def force_freeze_deformers(self, condition, items):
        selection = self.scn.selected
        self.scn.deselect()

        for o in selection:
            if o.name in self.deformer_item_dict.keys():
                self.scn.select(o.name, add=True)

        if len(self.scn.selected):
            self.freeze_deformers(condition, items, force=True)

    @conditionTesting
    def freeze_replicator(self, condition, items, update_arr=True, force=False):  # Need to be reworked
        if self.currentlyProcessing[0].type == t.itemType['REPLICATOR']:
            first_index = 0

            message = "Freeze Replicator"
            message = self.get_progression_message(message)
            self.increment_progress_bar(self.progress)
            self.mm.processing_log(message)

            frozenItem_arr = []
            source_dict = {}

            i = 0
            for o in self.currentlyProcessing:
                originalName = o.name
                self.scn.deselect()
                self.scn.select(originalName)

                source_dict[originalName] = self.replicator_dict[originalName].replicator_src_arr

                lx.eval(t.TILA_FREEZE_REPLICATOR)

                frozenItem = modoItem.convert_to_modoItem(modo.Item(originalName))

                self.currentlyProcessing[i] = frozenItem

                frozenItem_arr.append(frozenItem)

                if not self.exportFile_sw:
                    self.userSelection[first_index + i] = frozenItem
                elif update_arr:
                    if self.exportEach_sw:
                        self.proceededMesh[first_index + i] = frozenItem
                    else:
                        self.proceededMesh['REPLICATOR'][first_index + i] = frozenItem

                i += 1

            for o in self.currentlyProcessing:  # remove replicator source and particle
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
                                        item_in_user_selection = item_name in self.get_name_arr(self.proceededMesh[t.get_key_from_value(t.compatibleItemType, ctype)])

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

    @conditionTesting
    def force_freeze_replicator(self, condition, items):
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
            self.freeze_replicator(condition, items, force=True)

        self.replicatorSrcIgnoreList = ()

    @conditionTesting
    def position_offset(self, condition, items):
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

    @conditionTesting
    def scale_amount(self, condition, items):
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

    @conditionTesting
    def rot_angle(self, condition, items):
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

    @conditionTesting
    def merge_meshes(self, condition, items):
        message = 'Merging Meshes'
        message = self.get_progression_message(message)
        self.increment_progress_bar(self.progress)
        self.mm.processing_log(message)

        self.scn.select(items)

        name_arr = self.get_name_arr(items)

        for o in self.scn.selected:
            if o.type in [t.compatibleItemType['GROUP_LOCATOR'], t.compatibleItemType['LOCATOR']]:
                self.scn.select(o)
                lx.eval('item.setType.mesh')

        for o in name_arr:
            self.scn.select(o, add=True)

        self.select_hierarchy(self, force=True)
        lx.eval('layer.mergeMeshes true')
