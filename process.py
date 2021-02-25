
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

## find components 
inspec_jobs = []
components = cdef.component 
for component in components:
    if component.uuid.prose in implemented_components:
        for contimp in component.control_implementation:
            for impreq in contimp.implemented_requirement:
                for prop in impreq.prop:
                    if prop.name.prose.startswith('inspec'):
                        if not isinstance(prop.remarks, list):
                            prop.remarks = [prop.remarks]
                        for control in prop.remarks:
                            inspect_job = {
                                'requirement': impreq.uuid.prose,
                                'profile': references[prop.value.prose],
                                'definition': yaml.safe_load(control.prose)
                            }
                            inspec_jobs += [inspect_job]
results = {}

for job in inspec_jobs:
    inputs = ""
    for control in job['definition']:
        for inp in control['inputs']:
            inputs += " --input {}={}".format(inp,control['inputs'][inp])
        # print (
        #     "inspec exec {0} {1} --controls {2}".format(
        #         job['profile'],
        #         inputs,
        #         control['control']
        #     )
        # )
        output = subprocess.check_output(
            "inspec exec {0} {1} --controls {2}".format(
                job['profile'],
                inputs,
                control['control']
            ), shell=True
        ).decode('utf-8')
        results[job['requirement']] =  re.sub(u'[^\u0020-\uD7FF\u0009\u000A\u000D\uE000-\uFFFD\U00010000-\U0010FFFF]+', '', output)

output
print (results)

## Create Plan
title = oscal_metadata.Title.Title(prose="Assessment Plan")
last_modified = oscal_metadata.Last_Modified.Last_Modified(prose=str(datetime.now().isoformat()))
version = oscal_metadata.Version.Version(prose=str(datetime.now().strftime('%Y%m%d')))
oscal_version = oscal_metadata.Oscal_Version.Oscal_Version(prose=str(datetime.now().isoformat()))
uuid = oscal_metadata.Uuid.Uuid(prose=str(uuid4()))
metadata = oscal_metadata.Metadata.Metadata(
            title=title,
            last_modified=last_modified,
            version=version,
            oscal_version=oscal_version,
        )
import_ssp = oscal_assessment_common.Import_Ssp.Import_Ssp(
    href=oscal_assessment_common.Href.Href(prose='./ssp.xml')
)
control_selection = oscal_assessment_common.Control_Selection.Control_Selection(
    include_all=oscal_assessment_common.Include_All.Include_All(),
    include_control=None
)
reviewed_controls = oscal_assessment_common.Reviewed_Controls.Reviewed_Controls(
    control_selection=control_selection
)
ap = oscal_ap.Assessment_Plan.Assessment_Plan(
    uuid=uuid,
    metadata=metadata,
    import_ssp=import_ssp,
    reviewed_controls=reviewed_controls
)
oscal.add_model(ap)


## Create Result
title = oscal_metadata.Title.Title(prose="Assessment Results")
last_modified = oscal_metadata.Last_Modified.Last_Modified(prose=str(datetime.now().isoformat()))
version = oscal_metadata.Version.Version(prose=str(datetime.now().strftime('%Y%m%d')))
oscal_version = oscal_metadata.Oscal_Version.Oscal_Version(prose=str(datetime.now().isoformat()))
uuid = oscal_metadata.Uuid.Uuid(prose=str(uuid4()))
metadata = oscal_metadata.Metadata.Metadata(
    title=title,
    last_modified=last_modified,
    version=version,
    oscal_version=oscal_version,
)

import_ap = oscal_ar.Import_Ap.Import_Ap(
    href=oscal_ar.Href.Href(prose='./ap.xml')
)
control_selection = oscal_assessment_common.Control_Selection.Control_Selection(
    include_all=oscal_assessment_common.Include_All.Include_All(),
    include_control=None
)
reviewed_controls = oscal_assessment_common.Reviewed_Controls.Reviewed_Controls(
    control_selection=control_selection
)

finding = oscal_ar.Finding.Finding(
    uuid=oscal_metadata.Uuid.Uuid(prose=str(uuid4())),
    title=oscal_metadata.Title.Title(prose="Result"),
    description=oscal_ar.Description.Description(prose="N/A"),
)

observations = []
for result in results:
    relevant_evidence = oscal_assessment_common.Relevant_Evidence.Relevant_Evidence(
        href=oscal_ar.Href.Href(prose='N/A'),
        description=oscal_ar.Description.Description(prose=results[result]),
    )
    observations += [
        oscal_assessment_common.Observation.Observation(
            uuid=oscal_metadata.Uuid.Uuid(prose=str(uuid4())),
            description=oscal_ar.Description.Description(prose="N/A"),
            method=oscal_assessment_common.Method.Method(prose="Inspec"),
            collected=oscal_assessment_common.Collected.Collected(prose=str(datetime.now().isoformat())),
            relevant_evidence=relevant_evidence
        )
    ]

result = oscal_ar.Result.Result(
    uuid=oscal_ar.Uuid.Uuid(prose=str(uuid4())),
    title=oscal_ar.Title.Title(prose=str('Assessment Results')),
    description=oscal_ar.Description.Description(prose=str('Assessment Results')),
    start=oscal_ar.Start.Start(prose=str(datetime.now().isoformat())),
    reviewed_controls=reviewed_controls,
    finding=finding,
    observation=observations
)

ar = oscal_ar.Assessment_Results.Assessment_Results(
    uuid=uuid,
    metadata=metadata,
    import_ap=import_ap,
    result=result
)
oscal.add_model(ar)