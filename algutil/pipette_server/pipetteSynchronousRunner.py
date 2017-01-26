import pipetteServer
import sys
import os
import subprocess

def pipetteSynchronousRunner(args):
    full_script_path = os.path.abspath(args[0])
    scriptDir = os.path.dirname(full_script_path)    

    communicationDirBase = args[1]
    fh_outdir = args[2]
    pipelineCmdStr = ' '.join(args[3:])
    
    if os.path.exists(communicationDirBase):
        fns = os.listdir(communicationDirBase)
        if len(fns)>0:
            raise Exception('For running single pipelines, comm_dir must start empty')
    if communicationDirBase not in pipelineCmdStr:
        raise Exception('Pipeline script must accept the comm_dir as an argument')
    
    os.symlink(fh_outdir,os.path.join(communicationDirBase,'firehose_outdir'))
        
    # run the pipeline, write its description to communicationDirBase/launch
    subprocess.check_call(pipelineCmdStr,shell=True)
    
    runMode = 'runone'
    retryMode = 'False'
    main = pipetteServer.Main()
    main.run_server(communicationDirBase, scriptDir, runMode, retryMode)
    # if one or more pipelines fail, an exception will be thrown once all that can be run has been attempted.
    


if __name__ == '__main__':
    args = sys.argv
    pipetteSynchronousRunner(args)
