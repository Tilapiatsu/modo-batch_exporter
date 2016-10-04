import lx
import dialog

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

        freeze_sca(self)
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
        freeze_rot(self)
