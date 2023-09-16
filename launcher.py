# import subprocess

# subprocess.run(["python", "-m", "./controls/PivotCtrl/demo_PivotCtrl.py"])

"""
https://stackoverflow.com/questions/14132789/relative-imports-for-the-billionth-time

"Relative imports use a module's name attribute to determine that module's 
position in the package hierarchy. If the module's name does not contain any 
package information (e.g. it is set to 'main') then relative imports are 
resolved as if the module were a top level module, regardless of where the 
module is actually located on the file system."

So if `my_file.py` imports a file from a sister folder, the location is _not_ 
relative to `my_file.py`, it is relative to wherever the process was initiated. 

"""

# import src.swisscontrols.examples.demo_ListEdtCtrl
# import src.swisscontrols.examples.demo_CheckListCtrl

# import src.swisscontrols.controls.PivotCtrl.demo_PivotCtrl

import src.swisscontrols.controls.FileOpenDialog.FileOpenDialog
