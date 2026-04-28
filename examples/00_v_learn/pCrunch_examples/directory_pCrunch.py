# main directory where pCrunch is installed (depr. coz method 2. used for each script)
# - this would be inside the virtual environment being used here (weis-env)
#
# 1. direct copy
# dir_pcrunch = "C:\\Users\\vasudevg\\.conda\\envs\\weis-env\\Lib\\site-packages\\pCrunch"
#
# 2. using __file__ attribute of pCrunch
from pCrunch import __file__
import os
dir_pcrunch = os.path.dirname(os.path.abspath(__file__))