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


userValues = [
    ['exportVisible_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['exportFile_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['scanFiles_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['exportEach_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['exportHierarchy_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['triple_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['mergeMesh_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['askBeforeOverride_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['resetPos_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['resetRot_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['resetSca_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['resetShe_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['freezePos_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['freezeRot_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['freezeSca_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['freezeShe_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['freezeGeo_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['freezeInstance_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['pos_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['posX', lx.symbol.sTYPE_FLOAT, True],
    ['posY', lx.symbol.sTYPE_FLOAT, True],
    ['posZ', lx.symbol.sTYPE_FLOAT, True],
    ['rot_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['rotX', lx.symbol.sTYPE_FLOAT, True],
    ['rotY', lx.symbol.sTYPE_FLOAT, True],
    ['rotZ', lx.symbol.sTYPE_FLOAT, True],
    ['sca_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['scaX', lx.symbol.sTYPE_FLOAT, True],
    ['scaY', lx.symbol.sTYPE_FLOAT, True],
    ['scaZ', lx.symbol.sTYPE_FLOAT, True],
    ['smoothAngle_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['smoothAngle', lx.symbol.sTYPE_FLOAT, True],
    ['hardenUvBorder_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['uvMapName', lx.symbol.sTYPE_STRING, True],
    ['exportCageMorph_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['cageMorphMapName', lx.symbol.sTYPE_STRING, True],
    ['applyMorphMap_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['morphMapName', lx.symbol.sTYPE_STRING, True],
    ['openDestFolder_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['exportFormatLxo_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['exportFormatLwo_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['exportFormatFbx_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['exportFormatObj_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['exportFormatAbc_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['exportFormatAbchdf_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['exportFormatDae_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['exportFormatDxf_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['exportFormat3dm_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['exportFormatGeo_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['exportFormatStl_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['exportFormatX3d_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['exportFormatSvg_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['exportFormatPlt_sw', lx.symbol.sTYPE_BOOLEAN, True],
    ['presetName', lx.symbol.sTYPE_STRING, True]
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

processingItemType = enum('MESHITEM', 'MESHINST')

compatibleItemType = ['mesh',
                      'meshInst',
                      'camera',
                      'light',
                      'txtrLocator',
                      'backdrop',
                      'groupLocator',
                      'replicator',
                      'surfGen',
                      'locator',
                      'deform',
                      'locdeform',
                      'deformGroup',
                      'deformMDD2',
                      'morphDeform',
                      'itemInfluence',
                      'genInfluence',
                      'deform.push',
                      'deform.wrap',
                      'softLag',
                      'ABCCurvesDeform.sample',
                      'ABCdeform.sample',
                      'force.root',
                      'baseVolume',
                      'chanModify',
                      'itemModify',
                      'meshoperation',
                      'chanEffect',
                      'defaultShader',
                      'defaultShader']

indexStyle = ['brak-sp', 'brak', 'sp', 'uscore', 'none']

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
