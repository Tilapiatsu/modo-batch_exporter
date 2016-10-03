import modo
import lx
import os
import sys
import subprocess
import dialog

def enum(*args):
    enums = dict(zip(args, range(len(args))))
    return type('Enum', (), enums)


class TilaBacthExport:
    def __init__(self,
                 userSelection,
                 userSelectionCount,
                 scn,
                 currScn,
                 currPath,
                 scnIndex,
                 upAxis,
                 iUpAxis,
                 fbxExportType,
                 fbxTriangulate,
                 exportFile_sw,
                 scanFiles_sw,
                 exportEach_sw,
                 exportHierarchy_sw,
                 triple_sw,
                 resetPos_sw,
                 resetRot_sw,
                 resetSca_sw,
                 resetShe_sw,
                 freezePos_sw,
                 freezeRot_sw,
                 freezeSca_sw,
                 freezeShe_sw,
                 freezeGeo_sw,
                 freezeInstance_sw,
                 posX,
                 posY,
                 posZ,
                 rotX,
                 rotY,
                 rotZ,
                 scaX,
                 scaY,
                 scaZ,
                 smoothAngle_sw,
                 smoothAngle,
                 hardenUvBorder_sw,
                 uvMapName,
                 exportFormatFbx_sw,
                 exportFormatObj_sw,
                 exportFormatLxo_sw,
                 exportFormatLwo_sw,
                 exportFormatAbc_sw,
                 exportFormatAbchdf_sw,
                 exportFormatDae_sw,
                 exportFormatDxf_sw,
                 exportFormat3dm_sw,
                 exportFormatGeo_sw,
                 exportCageMorph_sw,
                 cageMorphMapName,
                 applyMorphMap_sw,
                 morphMapName,
                 openDestFolder_sw):

        self.userSelection = userSelection
        self.userSelectionCount = userSelectionCount
        self.scn = scn
        self.currScn = currScn
        self.currPath = currPath
        self.scnIndex = scnIndex
        self.upAxis = upAxis
        self.iUpAxis = iUpAxis
        self.fbxExportType = fbxExportType
        self.fbxTriangulate = fbxTriangulate

        self.exportFile_sw = exportFile_sw
        self.scanFiles_sw = scanFiles_sw
        self.exportEach_sw = exportEach_sw
        self.exportHierarchy_sw = exportHierarchy_sw

        self.triple_sw = triple_sw

        self.resetPos_sw = resetPos_sw
        self.resetRot_sw = resetRot_sw
        self.resetSca_sw = resetSca_sw
        self.resetShe_sw = resetShe_sw

        self.freezePos_sw = freezePos_sw
        self.freezeRot_sw = freezeRot_sw
        self.freezeSca_sw = freezeSca_sw
        self.freezeShe_sw = freezeShe_sw

        self.freezeGeo_sw = freezeGeo_sw
        self.freezeInstance_sw = freezeInstance_sw

        self.posX = posX
        self.posY = posY
        self.posZ = posZ

        self.rotX = rotX
        self.rotY = rotY
        self.rotZ = rotZ

        self.scaX = scaX
        self.scaY = scaY
        self.scaZ = scaZ

        self.smoothAngle_sw = smoothAngle_sw
        self.smoothAngle = smoothAngle

        self.hardenUvBorder_sw = hardenUvBorder_sw
        self.uvMapName = uvMapName

        self.exportFormatFbx_sw = exportFormatFbx_sw
        self.exportFormatObj_sw = exportFormatObj_sw
        self.exportFormatLxo_sw = exportFormatLxo_sw
        self.exportFormatLwo_sw = exportFormatLwo_sw
        self.exportFormatAbc_sw = exportFormatAbc_sw
        self.exportFormatAbchdf_sw = exportFormatAbchdf_sw
        self.exportFormatDae_sw = exportFormatDae_sw
        self.exportFormatDxf_sw = exportFormatDxf_sw
        self.exportFormat3dm_sw = exportFormat3dm_sw
        self.exportFormatGeo_sw = exportFormatGeo_sw

        self.exportCageMorph_sw = exportCageMorph_sw
        self.cageMorphMapName = cageMorphMapName

        self.openDestFolder_sw = openDestFolder_sw

        self.applyMorphMap_sw = applyMorphMap_sw
        self.morphMapName = morphMapName

        self.meshItemToProceed = []
        self.meshInstToProceed = []
        self.sortedOriginalItems = []
        self.proceededMesh = []
        self.processingItemType = enum('MESHITEM', 'MESHINST')


    # Path Constructor

    def construct_file_path(self, output_dir, layer_name, ext):
        if self.scanFiles_sw:
            if self.exportEach_sw:
                sceneName = self.scn.name
                return [os.path.join(output_dir, sceneName + '_-_' + layer_name + '.' + ext),
                        os.path.join(output_dir, sceneName + '_-_' + layer_name
                                     + '_cage.' + ext)]
            else:
                return [os.path.join(output_dir, layer_name + '.' + ext),
                        os.path.join(output_dir, layer_name + '_cage.' + ext)]
        else:
            if self.exportEach_sw:
                return [os.path.join(output_dir, layer_name + '.' + ext),
                        os.path.join(output_dir, layer_name + '_cage.' + ext)]
            else:
                splited_path = os.path.splitext(output_dir)
                return [output_dir, splited_path[0] + '_cage' + splited_path[1]]

    # Loops methods

    def process_items(self):
        dialog.begining_log(self.exportFile_sw)

        if not self.exportFile_sw:  # Transform Selected
            if self.userSelectionCount == 0:  # No file Selected
                dialog.init_message('error', 'No item selected', 'Select at least one item')
                sys.exit()

            self.transform_loop()
            self.scn.select(self.userSelection)

        elif not self.scanFiles_sw:  # export selected mesh
            if self.userSelectionCount == 0:  # No file Selected
                dialog.init_message('error', 'No item selected', 'Select at least one item')
                sys.exit()

            if self.exportEach_sw:
                dialog.init_dialog("output", self.currPath)
            else:
                dialog.init_dialog("file_save", self.currPath)

            try:  # output folder dialog
                lx.eval('dialog.open')
            except:
                dialog.init_dialog('cancel', self.currPat)
            else:
                output_dir = lx.eval1('dialog.result ?')
                self.batch_export(output_dir)

        else:  # browse file to process
            dialog.init_dialog("input", self.currPat)
            try:  # mesh to process dialog
                lx.eval('dialog.open')
            except:
                dialog.init_dialog('cancel', self.currPat)
            else:
                files = lx.evalN('dialog.result ?')
                dialog.init_dialog("output", self.currPat)
                try:  # output folder dialog
                    lx.eval('dialog.open')
                except:
                    dialog.init_dialog('cancel', self.currPath)
                else:
                    output_dir = lx.eval1('dialog.result ?')

                    for f in files:
                        dialog.processing_log('.....................................   ' + os.path.basename(f) + '   .....................................')

                        lx.eval('!scene.open "%s" normal' % f)

                        # if ext == 'fbx'
                        lx.eval('select.itemType mesh')

                        scnIndex = lx.eval('query sceneservice scene.index ? current')
                        self.userSelection = self.scn.selected
                        self.userSelectionCount = len(self.userSelection)

                        dialog.print_log('.....................................   ' + str(self.userSelectionCount) + ' mesh item founded   .....................................')

                        self.batch_export(output_dir)
                        lx.eval('!scene.close')

                        dialog.init_message('info', 'Done', 'Operation completed successfully !')

        if self.exportFile_sw:
            if self.openDestFolder_sw:
                if self.scanFiles_sw:
                    dialog.open_folder(output_dir)
                if self.exportEach_sw:
                    dialog.open_folder(output_dir)
                else:
                    dialog.open_folder(os.path.split(output_dir)[0])

                dialog.ending_log(self.exportFile_sw)

    def batch_export(self, output_dir):
        if self.upAxis != lx.eval('pref.value units.upAxis ?'):
            lx.eval('pref.value units.upAxis %s' % self.upAxis)

        if self.exportFormatFbx_sw:
            #lx.eval('user.value sceneio.fbx.save.triangulate false')
            if self.exportHierarchy_sw:
                lx.eval('user.value sceneio.fbx.save.exportType FBXExportSelectionWithHierarchy')
            else:
                lx.eval('user.value sceneio.fbx.save.exportType FBXExportSelection')

        self.transform_loop()

        if self.exportEach_sw:
            for i in xrange(0, len(self.proceededMesh)):
                item_arr = []
                item_arr.append(self.proceededMesh[i])
                self.export_all_format(output_dir, item_arr, self.proceededMesh[i].name[:-2], i)
        else:
            self.export_all_format(output_dir, self.proceededMesh, self.scn.name)

        self.clean_scene()

    def transform_loop(self):
        self.items_to_proceed_constructor()

        if len(self.meshInstToProceed) > 0:
            self.scn.select(self.meshInstToProceed)
            self.transform_selected(type=self.processingItemType.MESHINST)

        if len(self.meshItemToProceed) > 0:
            self.scn.select(self.meshItemToProceed)
            self.transform_selected(type=self.processingItemType.MESHITEM)

    def transform_selected(self, type):
        self.export_hierarchy()

        if self.exportFile_sw:
            if type == self.processingItemType.MESHITEM:
                self.duplicate_rename(self.meshItemToProceed, '1')
            if type == self.processingItemType.MESHINST:
                self.duplicate_rename(self.meshInstToProceed, '1')

        self.freeze_instance(type=type)

        self.smooth_angle()
        self.harden_uv_border()

        self.freeze_geo()
        self.triple()

        self.apply_morph(self.applyMorphMap_sw, self.morphMapName)

        self.reset_pos()
        self.reset_rot()
        self.reset_sca()
        self.reset_she()

        self.position_offset()
        self.scale_amount()
        self.rot_angle()

        self.freeze_rot()
        self.freeze_sca()
        self.freeze_pos()
        self.freeze_she()

    def export_all_format(self, output_dir, duplicate, layer_name, index=0):

        originalItem = []
        if self.exportEach_sw:
            originalItem.append(self.sortedOriginalItems[index])
        else:
            originalItem = self.sortedOriginalItems

        self.set_name(originalItem, shrink=False, add=True, layer_name='_0')
        self.scn.select(duplicate)
        self.set_name(duplicate, shrink=True, add=True)

        if self.exportFormatFbx_sw:
            output_path = self.construct_file_path(output_dir, layer_name, 'fbx')
            self.export_selection(output_path, 'fbx')

        if self.exportFormatLxo_sw:
            output_path = self.construct_file_path(output_dir, layer_name, 'lxo')
            self.export_selection(output_path, '$LXOB')

        if self.exportFormatLwo_sw:
            output_path = self.construct_file_path(output_dir, layer_name, 'lwo')
            self.export_selection(output_path, '$NLWO2')

        if self.exportFormatObj_sw:
            output_path = self.construct_file_path(output_dir, layer_name, 'obj')
            self.export_selection(output_path, 'wf_OBJ')

        if self.exportFormatDxf_sw:
            output_path = self.construct_file_path(output_dir, layer_name, 'dxf')
            self.export_selection(output_path, 'DXF')

        if self.exportFormatDae_sw:
            output_path = self.construct_file_path(output_dir, layer_name, 'dae')
            self.export_selection(output_path, 'COLLADA_141')

        if self.exportFormat3dm_sw:
            output_path = self.construct_file_path(output_dir, layer_name, '3dm')
            self.export_selection(output_path, 'THREEDM')

        if self.exportFormatAbc_sw:
            output_path = self.construct_file_path(output_dir, layer_name, 'abc')
            self.export_selection(output_path, 'Alembic')

        if self.exportFormatAbchdf_sw:
            output_path = self.construct_file_path(output_dir, layer_name, 'abc')
            self.export_selection(output_path, 'AlembicHDF')

        if self.exportFormatGeo_sw:
            output_path = self.construct_file_path(output_dir, layer_name, 'geo')
            self.export_selection(output_path, 'vs_GEO')

        self.scn.select(duplicate)

        lx.eval('!!item.delete')

        self.set_name(originalItem, shrink=True, add=True)

    def export_selection(self, output_path, export_format):
        lx.eval('!scene.saveAs "%s" "%s" true' % (output_path[0], export_format))

        dialog.export_log(os.path.basename(output_path[0]))

        if self.exportCageMorph_sw:
            self.export_cage(output_path[1], export_format)

    def export_cage(self, output_path, export_format):
        # Smooth the mesh entirely
        lx.eval('vertMap.softenNormals connected:true')

        # Apply Cage Morph map
        self.apply_morph(True, self.cageMorphMapName)

        lx.eval('!scene.saveAs "%s" "%s" true' % (output_path, export_format))
        dialog.export_log(os.path.basename(output_path))

    def export_hierarchy(self):
        if self.exportHierarchy_sw:
            lx.eval('select.itemHierarchy')

    # Helpers, setter/getter, Selector

    def items_to_proceed_constructor(self):
        for item in self.userSelection:
            if item.type == 'meshInst':
                self.meshInstToProceed.append(item)
            if item.type == 'mesh':
                self.meshItemToProceed.append(item)
        self.sort_original_items()

    def sort_original_items(self):
        for i in self.meshInstToProceed:
            self.sortedOriginalItems.append(i)
        for i in self.meshItemToProceed:
            self.sortedOriginalItems.append(i)

    def duplicate_rename(self, arr, number):
        duplicate_arr = []
        for item in arr:
            layer_name = item.name
            duplicate = self.scn.duplicateItem(item)
            duplicate.name = '%s_%s' % (layer_name, number)
            duplicate_arr.append(duplicate)
            self.proceededMesh.append(duplicate)

        self.scn.select(duplicate_arr)

    def get_name(self, layer):
        if self.exportEach_sw:
            return layer.name
        else:
            return self.scn.name

    def set_name(self, arr, shrink, add, layer_name=''):
        for item in arr:
            currName = item.name

            if add:
                if shrink:
                    currName = currName[:-2]
                currName += layer_name
            else:
                currName = layer_name

            item.name = currName

    # Item Processing

    def apply_morph(self, condition, name):
        if condition:
            dialog.processing_log('Applying Morph Map : ' + name)
            lx.eval('vertMap.applyMorph %s 1.0' % name)

    def smooth_angle(self):
        if self.smoothAngle_sw:
            dialog.processing_log("Harden edges witch are sharper than %s degrees" % self.smoothAngle)
            currAngle = lx.eval('user.value vnormkit.angle ?')
            lx.eval('user.value vnormkit.angle %s' % self.smoothAngle)
            lx.eval('vertMap.hardenNormals angle soften:true')
            lx.eval('user.value vnormkit.angle %s' % currAngle)
            lx.eval('vertMap.updateNormals')

    def harden_uv_border(self):
        if self.hardenUvBorder_sw:
            dialog.processing_log("HardenUvBorder = " + self.uvMapName)
            lx.eval('select.vertexMap {%s} txuv replace' % self.uvMapName)
            lx.eval('uv.selectBorder')
            lx.eval('vertMap.hardenNormals uv')
            lx.eval('vertMap.updateNormals')
            lx.eval('select.type item')

    def triple(self):
        if self.triple_sw:
            dialog.processing_log("Triangulate")
            lx.eval('poly.triple')

    def reset_pos(self):
        if self.resetPos_sw:
            dialog.transform_log("Reset Position")
            lx.eval('transform.reset translation')

    def reset_rot(self):
        if self.resetRot_sw:
            dialog.transform_log("Reset Rotation")
            lx.eval('transform.reset rotation')

    def reset_sca(self):
        if self.resetSca_sw:
            dialog.transform_log("Reset Scale")
            lx.eval('transform.reset scale')

    def reset_she(self):
        if self.resetShe_sw:
            dialog.transform_log("Reset Shear")
            lx.eval('transform.reset shear')

    def freeze_pos(self):
        if self.freezePos_sw:
            dialog.transform_log("Freeze Position")

            lx.eval('transform.freeze translation')
            lx.eval('vertMap.updateNormals')

    def freeze_rot(self):
        if self.freezeRot_sw:
            dialog.transform_log("Freeze Rotation")

            lx.eval('transform.freeze rotation')
            lx.eval('vertMap.updateNormals')

    def freeze_sca(self, force=False):
        if self.freezeSca_sw or force:
            if not force:
                dialog.transform_log("Freeze Scale")

            lx.eval('transform.freeze scale')
            lx.eval('vertMap.updateNormals')

    def freeze_she(self):
        if self.freezeShe_sw:
            dialog.transform_log("Freeze Shear")

            lx.eval('transform.freeze shear')
            lx.eval('vertMap.updateNormals')

    def freeze_geo(self):
        if self.freezeGeo_sw:
            dialog.transform_log("Freeze Geometry")
            lx.eval('poly.freeze twoPoints false 2 true true true true 5.0 false Morph')

    def freeze_instance(self, type=0):
        if type == 1 and self.scn.selected[0].type == 'meshInst':
            if self.exportFile_sw or ((not self.exportFile_sw) and (self.freezeInstance_sw or self.freezePos_sw or self.freezeRot_sw or self.freezeSca_sw or self.freezeShe_sw)):
                dialog.transform_log("Freeze Instance")

                lx.eval('item.setType Mesh')

                for i in xrange(0, len(self.scn.selected)):
                    currScale = self.scn.selected[i].scale

                    if currScale.x.get() < 0 or currScale.y.get() < 0 or currScale.z.get() < 0:
                        self.freeze_sca(True)

                    if not self.exportFile_sw:
                        self.userSelection[i] = self.scn.selected[i]
                    else:
                        self.proceededMesh[i] = self.scn.selected[i]

    def position_offset(self):
        if self.posX != 0.0 or self.posY != 0.0 or self.posZ != 0.0:
            dialog.transform_log("Position offset = (%s, %s, %s)" % (self.posX, self.posY, self.posZ))

            currPosition = self.scn.selected[0].position

            lx.eval('transform.channel pos.X %s' % str(float(self.posX) + currPosition.x.get()))
            lx.eval('transform.channel pos.Y %s' % str(float(self.posY) + currPosition.y.get()))
            lx.eval('transform.channel pos.Z %s' % str(float(self.posZ) + currPosition.z.get()))

    def scale_amount(self):
        if self.scaX != 1.0 or self.scaY != 1.0 or self.scaZ != 1.0:
            dialog.transform_log("Scale amount = (%s, %s, %s)" % (self.scaX, self.scaY, self.scaZ))

            currScale = self.scn.selected[0].scale

            self.freeze_sca()
            lx.eval('transform.channel scl.X %s' % str(float(self.scaX) * currScale.x.get()))
            lx.eval('transform.channel scl.Y %s' % str(float(self.scaY) * currScale.y.get()))
            lx.eval('transform.channel scl.Z %s' % str(float(self.scaZ) * currScale.z.get()))

    def rot_angle(self):
        if self.rotX != 0.0 or self.rotY != 0.0 or self.rotZ != 0.0:
            dialog.transform_log("Rotation Angle = (%s, %s, %s)" % (self.rotX, self.rotY, self.rotZ))

            currRotation = self.scn.selected[0].rotation
            lx.eval('transform.freeze rotation')
            lx.eval('transform.channel rot.X "%s"' % str(float(self.rotX) + currRotation.x.get()))
            lx.eval('transform.channel rot.Y "%s"' % str(float(self.rotY) + currRotation.y.get()))
            lx.eval('transform.channel rot.Z "%s"' % str(float(self.rotZ) + currRotation.z.get()))
            self.freeze_rot()

    # Cleaning

    def clean_scene(self):
        self.scn.select(self.userSelection)

        # Put the user's original FBX Export setting back.

        if self.exportFormatFbx_sw:
            lx.eval('user.value sceneio.fbx.save.exportType %s' % self.fbxExportType)
            #lx.eval('user.value sceneio.fbx.save.triangulate %s' % self.fbxTriangulate)

        if self.upAxis != self.iUpAxis:
            lx.eval('pref.value units.upAxis %s' % self.iUpAxis)

