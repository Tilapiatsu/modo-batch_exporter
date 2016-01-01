# modo-batch_exporter
Simple python script to batch export mesh items out of modo
Tested in Modo 902. It's not fully functionnal and there is still some work to do to make it easy to integrate into Modo's pipeline.

Launch the script by running the command in Modo :

@<path_to_python_script> triple 0 resetPos 0 rotAngle 0 scaleAmount 1 exportEach 1 exportHierarchy 0 scanFiles 0 upAxis Y

(no matter the order of these parameters, if you put no parameter, the default one will be picked)

triple (0/1) : triangulate the mesh
resetPos (0/1) : reset position of the mesh
rotAngle (float) : rotate the mesh on the x axis (other axis comming soon)
scaleAmount (float) : scale the mesh uniformly
smoothAngle (0 -> 1 float) : set the global smoothing angle of the mesh
exportEach (0/1) : when 1 -> export each selected mesh on a separate file. otherwise, export all the selected mesh in the same file
exportHierarchy (0/1) : when 1 -> export all children of the selected mesh
scanFiles (0/1) : when 1 -> open file dialog pops, the selected files is exported instead of the selected mesh on the current scene (NOT WORKING)
upAxis (X/Y/Z) : defines the up axis of the world
