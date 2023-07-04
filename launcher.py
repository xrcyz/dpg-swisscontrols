# i have no idea what i'm doing
# this sets the current working directory to the project folder
# so that relative paths work properly
# which apparently isn't a native feature of python? 

import subprocess

subprocess.run(["python", "./controls/PivotCtrl/demo_PivotCtrl.py"])

# import runpy

# runpy.run_module(mod_name='controls.PivotCtrl.demo_PivotCtrl', run_name="__main__")
