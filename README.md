# Batch Exporter for Modo
<p align="center"><img src="https://raw.githubusercontent.com/Tilapiatsu/modo_kit_assets/master/tila_batch_exporter/1.0.0/Tila_Batchexport_Overview.png" /></p>

Modo 10 Required

Tested on Windows only

This kit allows you to perform complex export tasks easily.
* Exporting mesh data from DCC to DCC can create sevral issues : Bad scaling, 90° rotation or in the case of objects away from world origin.
* When you need to export meshes for baking, you may want to triangulate it first, split vertex normal based on uv border or export a cage.
* When kit bashing, you may want to work with all items away from each other. When exporting you may want to put all items back to the world origin.
* You may want to process very dense meshes or hundreds. You can batch process files or directory on your drive without having to load them one by one or waiting for them to load.

This kit helps you with these tasks by **pre-processing mesh items before exporting without modifying the source meshes**. Your scene stays untoutched : it allows you to have a better iterative workflow and you will spend less time on conforming objects. In addition, you can save all your settings into a preset.

***

### Installation

Just copy the kit into your Modo's `User Script Folder` :  `System`&gt;`Open User Scripts Folder`

***

### Contact

Any suggestion or bug report, please contact me at support@tilapiatsu.fr

***