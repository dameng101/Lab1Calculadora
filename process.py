
from pyoscal import oscal_metadata, oscal_assessment_common, oscal_ap, oscal_ar
import yaml
import subprocess
import sys
from uuid import uuid4
from datetime import datetime
import re


## Load files 
oscal = OSCAL()
oscal.parse_file('component-def.xml')
oscal.parse_file('ssp.xml')
cdef = oscal.objects['Component_Definition'][0]
ssp = oscal.objects['System_Security_Plan'][0]