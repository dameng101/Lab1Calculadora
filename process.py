
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

## SSP Components
implemented_components = []
control_implementation = ssp.control_implementation
ssp_components = control_implementation.implemented_requirement[0].by_component
for comp in ssp_components:
    implemented_components += [comp.component_uuid.prose]
# sys.exit()

## find assessment links 
references = {}
bm = cdef.back_matter
for resource in bm.resource:
    for rlink in resource.rlink:
        references[resource.uuid.prose] = rlink.href.prose