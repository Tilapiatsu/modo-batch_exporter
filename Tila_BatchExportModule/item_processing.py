import lx
import dialog
import sys

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
        lx.eval('vertMap.applyMorph %s 1.0' % name)


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
        lx.eval('transform.reset translation')


def reset_rot(self):
    if self.resetRot_sw:
        message = "Reset Rotation"
        message = get_progression_message(self, message)
        increment_progress_bar(self, self.progress)
        dialog.transform_log(message)
        lx.eval('transform.reset rotation')


def reset_sca(self):
    if self.resetSca_sw:
        message = "Reset Scale"
        message = get_progression_message(self, message)
        increment_progress_bar(self, self.progress)
        dialog.transform_log(message)
        lx.eval('transform.reset scale')


def reset_she(self):
    if self.resetShe_sw:
        message = "Reset Shear"
        message = get_progression_message(self, message)
        increment_progress_bar(self, self.progress)
        dialog.transform_log(message)
        lx.eval('transform.reset shear')


def freeze_pos(self):
    if self.freezePos_sw:
        message = "Freeze Position"
        message = get_progression_message(self, message)
        increment_progress_bar(self, self.progress)
        dialog.transform_log(message)

        lx.eval('transform.freeze translation')
        #lx.eval('vertMap.updateNormals')


def freeze_rot(self):
    if self.freezeRot_sw:
        message = "Freeze Rotation"
        message = get_progression_message(self, message)
        increment_progress_bar(self, self.progress)
        dialog.transform_log(message)

        lx.eval('transform.freeze rotation')
        #lx.eval('vertMap.updateNormals')


def freeze_sca(self, force=False):
    if self.freezeSca_sw or force:
        if not force:
            message = "Freeze Scale"
            message = get_progression_message(self, message)
            increment_progress_bar(self, self.progress)
            dialog.transform_log(message)

        lx.eval('transform.freeze scale')
        #lx.eval('vertMap.updateNormals')


def freeze_she(self):
    if self.freezeShe_sw:
        message = "Freeze Shear"
        message = get_progression_message(self, message)
        increment_progress_bar(self, self.progress)
        dialog.transform_log(message)

        lx.eval('transform.freeze shear')
        lx.eval('vertMap.updateNormals')


def freeze_geo(self):
    if self.freezeGeo_sw:
        message = "Freeze Geometry"
        message = get_progression_message(self, message)
        increment_progress_bar(self, self.progress)
        dialog.transform_log(message)
        lx.eval('poly.freeze twoPoints false 2 true true true true 5.0 false Morph')


def freeze_instance(self, type=0):
    if type == 1 and self.scn.selected[0].type == 'meshInst':
        if self.exportFile_sw or ((not self.exportFile_sw) and (self.freezeInstance_sw or self.freezePos_sw or self.freezeRot_sw or self.freezeSca_sw or self.freezeShe_sw)):
            message = "Freeze Instance"
            message = get_progression_message(self, message)
            increment_progress_bar(self, self.progress)
            dialog.transform_log(message)

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
