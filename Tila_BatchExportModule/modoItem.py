import lx
import modo
import Tila_BatchExportModule as t
from Tila_BatchExportModule import dialog


class ModoItem(modo.item.Item):
    mm = dialog.MessageManagement('ModoItem')
    _key = None

    def __init__(self, item, **kwargs):
        modo.item.Item.__init__(self, item)
        self.scn = modo.Scene()
        self.name = item.name
        self.cmd_svc = lx.service.Command()

        # store scene source scene ID
        self.srcScnID = lx.eval('query sceneservice scene.index ? current')
        self.dstScnID = None
        self.dstItem = None
        self.extraItems = []

        self.previouslySelected = None

        self.originalName = []
        self.modifiedName = []

        self.set_kwargs(kwargs)

    @staticmethod
    def get_name_arr(arr):
        name_arr = []
        for o in arr:
            name_arr.append(o.name)

        return name_arr

    @property
    def type(self):
        if self._key is None:
            return self._item.type
        else:
            return t.itemType[self._key]

    @property
    def typeKey(self):
        return t.get_key_from_value(t.compatibleItemType, self.type)

    @property
    def position(self):
        return modo.item.LocatorSuperType(self._item).position

    @property
    def rotation(self):
        return modo.item.LocatorSuperType(self._item).rotation

    @property
    def scale(self):
        return modo.item.LocatorSuperType(self._item).scale

    def set_kwargs(self, kwargs):
        for key, value in kwargs.items():
            if key == 'scn':
                self.scn = value
            if key == 'name':
                self.name = value
            if key == 'srcScnID':
                self.srcScnID = value
            if key == 'dstScnID':
                self.dstScnID = value
            if key == 'dstItem':
                self.dstItem = value
            if key == 'extraItems':
                self.extraItems = value

    def get_src_parameters_dict(self):
        return {'scn': self.scn,
                'name': self.name,
                'srcScnID': self.srcScnID,
                'dstScnID': self.dstScnID,
                'dstItem': self.dstItem,
                'extraItems': self.extraItems}

    def get_dst_parameters_dict(self):
        return {'scn': self.scn,
                'name': self.dstItem.name,
                'srcScnID': self.dstScnID,
                'extraItems': self.extraItems}

    def create_dstItem(self):
        kwargs = self.get_dst_parameters_dict()
        return convert_to_modoItem(self.dstItem,
                                   scn=kwargs.get('scn'),
                                   name=kwargs.get('name'),
                                   srcScnID=kwargs.get('srcScnID'),
                                   extraItems=kwargs.get('extraItems'))

    def updated_item(self):
        kwargs = self.get_src_parameters_dict()
        self.mm.breakPoint('before update')
        return convert_to_modoItem(modo.Item(self.name),
                                   scn=kwargs.get('scn'),
                                   name=kwargs.get('name'),
                                   srcScnID=kwargs.get('srcScnID'),
                                   dstScnID=kwargs.get('dstScnID'),
                                   dstItem=kwargs.get('dstItem'),
                                   extraItems=kwargs.get('extraItems'))

    def have_deformers(self):
        if len(self._item.deformers):
            return True
        else:
            return False

    def clearitems(self):
        try:
            lx.eval('select.itemType mesh')
            lx.eval('select.itemType camera mode:add')
            lx.eval('select.itemType light super:true mode:add')
            lx.eval('select.itemType renderOutput mode:add')
            lx.eval('select.itemType defaultShader mode:add')
            lx.eval('!!item.delete')
        except:
            t.return_exception()

    def copy_to_scene(self, dstScnID=None, getExtraItems_func=None):
        # store the original name of the item
        self.originalName.append(self._item.name)

        if getExtraItems_func is not None:
            self.originalName = getExtraItems_func(self.originalName)

        # create a new temporary scene if no one scene is specified
        if dstScnID is None:
            self.cmd_svc.ExecuteArgString(-1, lx.symbol.iCTAG_NULL, 'scene.new')
            self.dstScnID = lx.eval('query sceneservice scene.index ? current')

            self.clearitems()

            self.cmd_svc.ExecuteArgString(-1, lx.symbol.iCTAG_NULL, 'scene.set %s' % self.srcScnID)
        else:
            self.dstScnID = dstScnID

        # rename item if it is contains a generic name
        self.rename_generic_name()

        self.scn.deselect()
        for name in self.modifiedName:
            self.scn.select(name, add=True)

        # Move all selected items to temporary scene
        self.cmd_svc.ExecuteArgString(-1, lx.symbol.iCTAG_NULL, '!layer.import {}'.format(self.dstScnID) + ' {} ' + 'childs:{} shaders:true move:false position:0'.format(False))

        self.scn = modo.Scene()

        self.revert_generic_name()

        self.store_dstItem(self.originalName[0])
        if len(self.originalName) > 1:
            self.store_extraItems(self.originalName[1:])

    def rename_generic_name(self):
        for name in self.originalName:
            isGenericName = False
            for gen in t.genericName:
                if gen in name:
                    item = modo.Item(name)
                    item.name = name.replace(gen, t.genericNameDict[gen])
                    self.modifiedName.append(item.name)
                    isGenericName = True
            else:
                if not isGenericName:
                    self.modifiedName.append(name)

    def revert_generic_name(self):
        if self.srcScnID is None or self.dstScnID is None:
            self.mm.error('Temporary scene not found. \n can\'t revert name', dialog=True)
            return False

        # rename item in destination scene
        lx.eval('scene.set {}'.format(self.dstScnID))
        self.scn = modo.Scene()

        i = 0
        for modifiedName in self.modifiedName:
            item = modo.Item(modifiedName)

            item.name = self.originalName[i]
            i += 1

        # switch to source Scene to revert name
        lx.eval('scene.set {}'.format(self.srcScnID))
        self.scn = modo.Scene()

        i = 0
        for modifiedName in self.modifiedName:
            item = modo.Item(modifiedName)

            item.name = self.originalName[i]
            i += 1

        lx.eval('scene.set {}'.format(self.dstScnID))
        self.scn = modo.Scene()

        return True

    def store_dstItem(self, name):
        curr_scnID = lx.eval('query sceneservice scene.index ? current')

        lx.eval('scene.set {}'.format(self.dstScnID))
        self.scn = modo.Scene()

        self.dstItem = modo.Item(name)

        lx.eval('scene.set {}'.format(curr_scnID))
        self.scn = modo.Scene()

    def store_extraItems(self, names):
        curr_scnID = lx.eval('query sceneservice scene.index ? current')

        lx.eval('scene.set {}'.format(self.dstScnID))
        self.scn = modo.Scene()

        for name in names:
            self.extraItems.append(convert_to_modoItem(modo.Item(name)))

        lx.eval('scene.set {}'.format(curr_scnID))
        self.scn = modo.Scene()

    def remove_extraItems(self):
        if len(self.extraItems):
            curr_scnID = lx.eval('query sceneservice scene.index ? current')

            lx.eval('scene.set {}'.format(self.dstScnID))
            self.scn = modo.Scene()

            self.scn.removeItems(self.extraItems)

            lx.eval('scene.set {}'.format(curr_scnID))
            self.scn = modo.Scene()

            self.extraItems = []

    def store_previouslySelected(self):
        self.previouslySelected = self.scn.selected

    def select_previouslySeleced(self):
        self.scn.select(self.previouslySelected)
        self.previouslySelected = None

    # item transform

    def apply_morph(self, morph_map_name):
        morph_maps = morph_map_name.split(',')
        for maps in morph_maps:
            lx.eval('vertMap.applyMorph %s 1.0' % maps)

    def reset_pos(self):
        self.store_previouslySelected()
        self._item.select()
        lx.eval('!!transform.reset translation')
        self.select_previouslySeleced()

    def reset_rot(self):
        self.store_previouslySelected()
        self._item.select()
        lx.eval('!!transform.reset rotation')
        self.select_previouslySeleced()

    def reset_sca(self):
        self.store_previouslySelected()
        self._item.select()
        lx.eval('!!transform.reset scale')
        self.select_previouslySeleced()

    def reset_she(self):
        self.store_previouslySelected()
        self._item.select()
        lx.eval('!!transform.reset shear')
        self.select_previouslySeleced()

    def freeze_pos(self):
        self.store_previouslySelected()
        self._item.select()
        lx.eval('!!transform.freeze translation')
        # lx.eval('vertMap.updateNormals')
        self.select_previouslySeleced()

    def freeze_rot(self):
        self.store_previouslySelected()
        self._item.select()
        lx.eval('!!transform.freeze rotation')
        # lx.eval('vertMap.updateNormals')
        self.select_previouslySeleced()

    def freeze_sca(self, test=False):
        self.store_previouslySelected()
        self._item.select()

        if test:
            currScale = self.scale
            if currScale.x.get() > 0 or currScale.y.get() > 0 or currScale.z.get() > 0:
                self.select_previouslySeleced()
                return

        lx.eval('!!transform.freeze scale')

        if test:
            lx.eval('vertMap.updateNormals')

        self.select_previouslySeleced()

    def freeze_she(self):
        self.store_previouslySelected()
        self._item.select()
        lx.eval('!!transform.freeze shear')
        # lx.eval('vertMap.updateNormals')
        self.select_previouslySeleced()

    def freeze_geo(self):
        self.store_previouslySelected()
        self._item.select()
        lx.eval('poly.freeze polyline true 2 true true true false 4.0 true Morph')
        self.select_previouslySeleced()


class ModoMeshItem(ModoItem):

    def __init__(self, item, **kwargs):
        ModoItem.__init__(self, item, **kwargs)


class ModoMeshInstance(ModoItem):

    def __init__(self, item, **kwargs):
        ModoItem.__init__(self, item, **kwargs)

    @property
    def source(self):
        self.store_previouslySelected()

        self._item.select()

        lx.eval('select.itemSourceSelected')

        source = convert_to_modoItem(self.scn.selected[0])
        self.select_previouslySeleced()

        return source

    def copy_to_scene(self, dstScnID=None):
        ModoItem.copy_to_scene(self, dstScnID, getExtraItems_func=self.getExtraItems)

    def getExtraItems(self, originalName):
        originalName.append(self.source.name)
        return originalName

    # Item Processing

    def freeze_instance(self):

        self._item.select(replace=True)
        lx.eval('item.setType.mesh')


class ModoGroupLocatorItem(ModoItem):

    def __init__(self, item, **kwargs):
        ModoItem.__init__(self, item, **kwargs)


class ModoLocatorItem(ModoItem):

    def __init__(self, item, **kwargs):
        ModoItem.__init__(self, item, **kwargs)


class ModoMeshFusionItem(ModoItem):
    _key = 'MESH_FUSION'

    def __init__(self, item, **kwargs):
        ModoItem.__init__(self, item, **kwargs)


class ModoReplicatorItem(ModoItem):
    _key = 'REPLICATOR'

    def __init__(self, item, **kwargs):
        ModoItem.__init__(self, item, **kwargs)
        self._replicator = None
        self._source_group_name = self.source_group_name

    @property
    def replicator_item(self):
        self._item = modo.Item(self.name)
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
    _key = 'MESH_OPERATOR'

    # is Used by MOP Item
    def __init__(self, item, **kwargs):
        ModoItem.__init__(self, item, **kwargs)
        self.deformer_group = None
        self._deformer_item = None
        self._deformers = None
        if not self.is_deformer_item:
            self.mm.warning('The item {} has no deformer'.format(self.name))

    @property
    def deformer_item(self):
        self._deformer_item = modo.Item(self.name)
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
            self.mm.warning('The item {} has no deformer'.format(self.name))
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
            self.deformer_group.name = self.name + '_DF'

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


modoItemTypes = {'MESH': ModoMeshItem,
                 'MESH_INSTANCE': ModoMeshInstance,
                 'REPLICATOR': ModoReplicatorItem,
                 'GROUP_LOCATOR': ModoGroupLocatorItem,
                 'LOCATOR': ModoLocatorItem,
                 'MESH_FUSION': ModoMeshFusionItem,
                 'DEFORMER': ModoDeformerItem}


def convert_to_modoItem(item, **kwargs):
    if item.type in t.compatibleItemType.values():
        key = t.get_key_from_value(t.compatibleItemType, item.type)
        mItem = modoItemTypes[key](item, **kwargs)
        if mItem.have_deformers():
            mItem = modoItemTypes['DEFORMER'](item, **kwargs)

        return mItem
    else:
        mm = dialog.MessageManagement('ModoItem')
        mm.info('The item {} can\'t be converted to modo Item'.format(item.name))
        return item
