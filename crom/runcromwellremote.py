#!/usr/bin/env python

import requests
import json
import os
import sys
import time
import atexit
import subprocess

# Note - requests.post and .get calls could be replaced via swagger library

#curl -X POST "http://35.193.85.62:8000/api/workflows/v1" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "workflowSource=@taskdef.btl_gatk_indexref.wdl;type=" -F "workflowInputs=@inputtest.btl_gatk_indexref.json;type=application/json"


global submission_id
global running
running = False
base_url = 'http://35.193.85.62:8000'


def killjob():
    if not running:
        # no work to do
        return 
    # curl -X POST "http://35.193.85.62:8000/api/workflows/v1/ee447739-8953-4c76-b47c-bdc1d95df03f/abort" -H "accept: application/json"
    abort_url = base_url + '/api/workflows/v1/' + submission_id + '/abort'
    headers = {"accept":"application/json"}
    print (abort_url)
    r = requests.post(abort_url, headers=headers, timeout=10 )
    print ("abort request sent")

atexit.register(killjob)


def get_metadata():

    # curl -X GET "http://35.193.85.62:8000/api/workflows/v1/05184cf6-432c-4901-bdf8-8768abee2862/metadata?expandSubWorkflows=false" -H "accept: application/json"

    metadata_url = base_url + '/api/workflows/v1/' + submission_id + '/metadata'
    data = {'expandSubWorkflows':'false'}
    headers = {"accept":"application/json"}
    r = requests.get(metadata_url, headers=headers, data=data, timeout=10)

    metadata = {}
    try:
        metadata['status_code'] = r.status_code
        metadata['struct'] = json.loads(r.text)
        metadata['outputs'] = metadata['struct']['outputs']
        metadata['inputs'] =  json.loads(metadata['struct']['submittedFiles']['inputs'])
        metadata['failures'] = json.dumps(metadata['struct'].get('failures'))
        workflow_dirs = []
        workflow_urls = []
        #print(metadata['struct']['calls'])
        for task in metadata['struct']['calls']:
            #print(task)
            num_calls = len(metadata['struct']['calls'][task])
            for call in range(num_calls):
                #print(call)
                workflow_dir = metadata['struct']['calls'][task][call]['callRoot']
                workflow_url = 'https://console.cloud.google.com/storage/browser/' + workflow_dir[5:] 
                workflow_dirs.append(workflow_dir)
                workflow_urls.append(workflow_url)
        metadata['workflow_dirs'] = workflow_dirs
        metadata['workflow_urls'] = workflow_urls
    except:
        pass
    return metadata


def run_wdl(wdl_path, inputs_dict):
    global submission_id
    global running

    running = False
    submit_url = base_url + '/api/workflows/v1'
    headers = {"accept":"application/json"}


    input_json = json.dumps(inputs_dict)
    files = { 'workflowSource': (os.path.basename(wdl_path),open(wdl_path,'rb'),""),
            'workflowInputs': ('input.json', input_json, "application/json")}
    # TODO add option to disable caching for this submission, via  data fields: {"read_from_cache": false}


    r = requests.post(submit_url, headers=headers, files=files, timeout=10 )

    print(r.status_code)
    print(r.text)


    if r.status_code != 201:
        sys.exit(1)

    # {'id': '9bdc4d55-d551-4608-80b0-6a86e57bd2a0', 'status': 'Submitted'}

    submission_response = json.loads(r.text)

    if submission_response['status'] != "Submitted":
        raise exception('status is %s'%submission_response['status'])

    submission_id = submission_response['id']
    running = True

    # curl -X GET "http://35.193.85.62:8000/api/workflows/v1/9bdc4d55-d551-4608-80b0-6a86e57bd2a0/status" -H "accept: application/json"

    status_url = base_url + '/api/workflows/v1/' + submission_id + '/status'
    headers = {"accept":"application/json"}

    import datetime 
    startTime= datetime.datetime.now()  

    workflow_status = None
    workflow_urls = []
    while workflow_status not in ['Failed','Aborted','Succeeded']:
        timeElapsed=datetime.datetime.now()-startTime 
        #print('{}'.format(timeElapsed))

        r = requests.get(status_url, headers = headers, timeout=10 )
    #{
    #  "status": "fail",
    #  "message": "Unrecognized workflow ID: 4824df01-ee6b-46c9-ab1d-bd9e3bd12f9d"
    #}

    #{'id': '4824df01-ee6b-46c9-ab1d-bd9e3bd12f9d', 'status': 'Failed'}

        print(r.status_code, r.text, timeElapsed)
        status_dict = json.loads(r.text)
        workflow_status = status_dict['status']

        if len(workflow_urls) < 1:
            # Fetch detailed metadata until directory first shows up, then stop updating it. May need to fix if more than one directory.
            m = get_metadata()
            #print(json.dumps(m['struct'],indent=4))
            workflow_urls = m.get('workflow_urls',[])
        for workflow_url in workflow_urls:
            print(workflow_url)
        print('')


        if timeElapsed < datetime.timedelta(seconds=10):
            sleep_time = 1
        else:
            sleep_time = 5
        time.sleep(sleep_time)


    running = False
    metadata = get_metadata()
    print (metadata['status_code'])
    print (json.dumps(metadata['struct'], indent=4))
    outputs = metadata['outputs']
    inputs = metadata['inputs']


    print('')
    print('inputs:')
    for key in inputs:
        print (key)
        print('     ', repr(inputs[key]).replace("'",'"'))
        print('')
    print('')
    print("outputs:")
    for key in outputs:
        print(key)
        print('     ', repr(outputs[key]).replace("'",'"'))
        print('')
    if workflow_status == "Failed":
        print('')
        print('failures:')
        failure_struct = json.loads(metadata['failures'])
        failure_string = json.dumps(failure_struct,indent=4)
        failure_string2 = failure_string.replace(r'\\n','\n\n')
        print(failure_string2)

    try:
        first_workflow_url = metadata['workflow_urls'][0]
        first_workflow_dir = metadata['workflow_dirs'][0]
        print ('listing of one output bucket:\n  %s\n  %s\n'%(first_workflow_url,first_workflow_dir))
        subprocess.call('gsutil ls -l %s'%first_workflow_dir, shell=True)
    except:
        print('no bucket location found')

    print("")
    print("total time: %s"%timeElapsed)
    print(workflow_status)
    print("")

    passed = workflow_status == 'Succeeded'

    return passed, outputs

if __name__ == "__main__":

    inputs_json_path = '/home/gsaksena/dev/btl_firecloud_gatk/workflows/btl_gatk_bqsr/inputtest.btl_gatk_bqsr.json'
    inputs_dict = {'foo':'bar'}
    inputs_dict = {
        'gatk_bqsr.indelrealigner_bam':'gs://broad-cil-devel-bucket/input_data/Candida_Auris.tcir.bam',
        'gatk_bqsr.indelrealigner_bam_index':'gs://broad-cil-devel-bucket/input_data/Candida_Auris.tcir.bam.bai',
        'gatk_bqsr.gatk_bqsr_task.debug_dump_flag':'onfail',
        'gatk_bqsr.gatk_bqsr_task.output_disk_gb':'10',
        'gatk_bqsr.gatk_bqsr_task.known_sites_vcf_tbis':["gs://broad-cil-devel-bucket/input_data/7g8_gb4.combined.final.vcf.gz.tbi","gs://broad-cil-devel-bucket/input_data/hb3_dd2.combined.final.vcf.gz.tbi","gs://broad-cil-devel-bucket/input_data/3d7_hb3.combined.final.vcf.gz.tbi"],
        'gatk_bqsr.gatk_bqsr_task.reference_tgz':'gs://broad-cil-devel-bucket/input_data/minion_illumina_hybrid_clean_MT.tgz',
        'gatk_bqsr.gatk_bqsr_task.known_sites_vcfs':["gs://broad-cil-devel-bucket/input_data/7g8_gb4.combined.final.vcf.gz","gs://broad-cil-devel-bucket/input_data/hb3_dd2.combined.final.vcf.gz","gs://broad-cil-devel-bucket/input_data/3d7_hb3.combined.final.vcf.gz"],
        'gatk_bqsr.gatk_bqsr_task.sample_name':'Candida_Auris',
    }

    wdl_path = '/home/gsaksena/dev/btl_firecloud_gatk/workflows/btl_gatk_bqsr/taskdef.btl_gatk_bqsr.wdl'


    passed, outputs_dict = run_wdl(wdl_path, inputs_dict)



# TODO enable call caching/job avoidance on server
#     call-caching {

#   enabled = true
#   invalidate-bad-cache-results = true
# }
# filesystems {
#   gcs{
#     caching {
#        duplication-strategy = "reference"
#     }
#   }
# }