#!/usr/bin/env python

import lx
import os
from Tila_BatchExportModule import dialog


def enum(*args):
    enums = dict(zip(args, range(len(args))))
    return type('Enum', (), enums)


def get_default_settings(self):
    if self.exportFormatFbx_sw:
        self.fbxExportType = lx.eval('user.value sceneio.fbx.save.exportType ?')
        self.fbxTriangulate = lx.eval('user.value sceneio.fbx.save.surfaceRefining ?')
        self.fbxFormat = lx.eval('user.value sceneio.fbx.save.format ?')

TILA_BATCH_EXPORT = "tila.batchexport"
TILA_BATCH_TRANSFORM = "tila.batchtransform"
TILA_BATCH_FOLDER = "tila.batchfolder"
TILA_OPEN_EXPORT_FOLDER = "tila.openexportfolder"
TILA_EXPORT_PRESET = "tila.exportpreset"

TILA_PRESET_NAME = 'presetName'
TILA_EXPORT_VISIBLE = 'exportVisible_sw'

TILA_DUPLICATE_SUFFIX = '_tila_duplicate'
TILA_BACKUP_SUFFIX = '_tila_backup'

REFRESH_ASTERISK_NOTIFIER = "tila.export.refreshAsteriskNotifier"


userValues = [
    [TILA_EXPORT_VISIBLE, lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['exportFile_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['scanFiles_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['scanFolder_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['exportEach_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['exportHierarchy_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['triple_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['mergeMesh_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['askBeforeOverride_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['resetPos_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['resetRot_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['resetSca_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['resetShe_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['freezePos_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['freezeRot_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['freezeSca_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['freezeShe_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['freezeGeo_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['freezeInstance_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['freezeMeshOp_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['pos_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['posX', lx.symbol.sTYPE_FLOAT, True, 0],
    ['posY', lx.symbol.sTYPE_FLOAT, True, 0],
    ['posZ', lx.symbol.sTYPE_FLOAT, True, 0],
    ['rot_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['rotX', lx.symbol.sTYPE_FLOAT, True, 0],
    ['rotY', lx.symbol.sTYPE_FLOAT, True, 0],
    ['rotZ', lx.symbol.sTYPE_FLOAT, True, 0],
    ['sca_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['scaX', lx.symbol.sTYPE_FLOAT, True, 1],
    ['scaY', lx.symbol.sTYPE_FLOAT, True, 1],
    ['scaZ', lx.symbol.sTYPE_FLOAT, True, 1],
    ['smoothAngle_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['smoothAngle', lx.symbol.sTYPE_FLOAT, True, 40],
    ['hardenUvBorder_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['uvMapName', lx.symbol.sTYPE_STRING, True, 'Texture'],
    ['exportCageMorph_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['cageMorphMapName', lx.symbol.sTYPE_STRING, True, 'Cage'],
    ['applyMorphMap_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['morphMapName', lx.symbol.sTYPE_STRING, True, 'Exploded'],
    ['openDestFolder_sw', lx.symbol.sTYPE_BOOLEAN, True, 1],
    ['createFormatSubfolder_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['processSubfolder_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['subfolderDepth', lx.symbol.sTYPE_INTEGER, True, 1],
    ['formatFilter', lx.symbol.sTYPE_STRING, True, 'fbx,obj'],
    ['filenamePattern', lx.symbol.sTYPE_STRING, True, '<file>_<item>'],
    ['exportFormatLxo_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['exportFormatLwo_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['exportFormatFbx_sw', lx.symbol.sTYPE_BOOLEAN, True, 1],
    ['exportFormatObj_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['exportFormatAbc_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['exportFormatAbchdf_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['exportFormatDae_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['exportFormatDxf_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['exportFormat3dm_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['exportFormatGeo_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['exportFormatStl_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['exportFormatX3d_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['exportFormatSvg_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    ['exportFormatPlt_sw', lx.symbol.sTYPE_BOOLEAN, True, 0],
    [TILA_PRESET_NAME, lx.symbol.sTYPE_STRING, True, 'default']
    ]

exportTypes = [
    ['lxo', '$LXOB'],
    ['lwo', '$NLWO2'],
    ['fbx', 'fbx'],
    ['obj', 'wf_OBJ'],
    ['abc', 'Alembic'],
    ['abc', 'AlembicHDF'],
    ['dae', 'COLLADA_141'],
    ['dxf', 'DXF'],
    ['3dm', 'THREEDM'],
    ['geo', 'vs_GEO'],
    ['stl', 'pySTLScene2'],
    ['x3d', '$X3D'],
    ['svg', 'SVG_SceneSaver'],
    ['plt', 'HPGL_PLT']
]

compatibleImportFormat = [exportTypes[i][0] for i in xrange(len(exportTypes))]

itemType = {'MESH': 'mesh',
            'MESH_INSTANCE': 'meshInst',
            'MESH_FUSION': 'sdf.item',
            'CAMERA': 'camera',
            'LIGHT': 'light',
            'TEXTURE_LOCATOR': 'txtrLocator',
            'BACKDROP': 'backdrop',
            'GROUP_LOCATOR': 'groupLocator',
            'REPLICATOR': 'replicator',
            'SURFACE_GENERATOR': 'surfGen',
            'LOCATOR': 'locator',
            'DEFORM': 'deform',
            'LOCATOR_DEFORM': 'locdeform',
            'DEFORM_GROUP': 'deformGroup',
            'DEFORM_MDD2': 'deformMDD2',
            'MORPH_DEFORM': 'morphDeform',
            'ITEM_INFLUENCE': 'itemInfluence',
            'GEN_INFLUENCE': 'genInfluence',
            'DEFORM_PUSH': 'deform.push',
            'DEFORM_WARP': 'deform.wrap',
            'SOFT_LAG': 'softLag',
            'ABC_CURVE_DEFORM': 'ABCCurvesDeform.sample',
            'ABC_DEFORM': 'ABCdeform.sample',
            'FORCE_ROOT': 'force.root',
            'BASE_VOLUME': 'baseVolume',
            'CHANNEL_MODIFY': 'chanModify',
            'ITEM_MODIFY': 'itemModify',
            'MESH_OPERATION': 'meshoperation',
            'CHANNEL_EFFECT': 'chanEffect',
            'DEFAULT_SHADER': 'defaultShader',
            'ADVANCED_MATERIAL': 'advancedMaterial'}

compatibleItemType = {'MESH': 'mesh',
                      'MESH_INSTANCE': 'meshInst',
                      'REPLICATOR': 'replicator'}

indexStyle = ['brak-sp', 'brak', 'sp', 'uscore', 'none']

g_dialog_svc = lx.service.StdDialog()
g_msg_svc    = lx.service.Message ()
g_msg        = lx.object.Message (g_msg_svc.Allocate ())

kit_prefix = 'tilaBExp.'
preset_hash = '70945661220'

curr_path = os.path.dirname(os.path.realpath(__file__))
root_path = dialog.parentPath(curr_path)
config_path = os.path.join(root_path, "Tila_Config")
preset_path = os.path.join(root_path, "Tila_Preset")


config_filename = 'tila_batchexport.cfg'
config_root = 'configuration'
config_sub_element = 'atom'
config_last_directory = 'LastDirectory'
config_export_path = 'ExportPath'
config_browse_src_path = 'BrowseSrcPath'
config_browse_dest_path = 'BrowseDestPath'
config_export_settings = 'ExportSettings'

config_file_path = os.path.join(config_path, config_filename)
