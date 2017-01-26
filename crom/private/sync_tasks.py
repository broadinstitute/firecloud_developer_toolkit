#!/usr/bin/env python

import sys
import os
import glob
from six import print_

def scopes_from_wdl(scope, wdl):
    """
    Return a dictionary of top-level scopes contained in a .wdl file. 
    A scope is either a task or workflow, and associated block
    """
    D = dict()
    with open(wdl, "r") as wdl_file:
        contents=wdl_file.read()

    scope_start = contents.find(scope)

    ##Handle case where workflow contains no scope
    if scope_start == -1: 
        return D

    while (scope_start != -1):
        ###Now loop through to find the first open bracket. 
        ##The task's name is whatever is obtained by splitting the 
        ##string between task and the first "{" 
        ##E.g: "task consensus_cluster_plus {" -> "consensus_cluster_plus"
        first_bracket = contents.find("{", scope_start)
        scope_name = contents[scope_start:first_bracket+1].split()[1]

        ##Now loop through counting left and right brackets, once we hit 0, we have found the end of the task
        stack = 1
        pos = first_bracket + 1
        while stack > 0:
            if contents[pos] == "{":
                stack += 1
            elif contents[pos] == "}":
                stack -= 1
            pos += 1

        ##pos is one ahead of the end of the last bracket, so this is the splice point
        scope_definition = contents[scope_start:pos]

        D[scope_name] = scope_definition

        #Keep searching past this task
        scope_start=contents.find(scope, pos)

    return D

def tasks_from_wdl(wdl):
    """
    Return a dictionary of tasks contained in a .wdl file. 
    The values are task definitions within the wdl
    """
    return scopes_from_wdl("task", wdl)

def workflow_from_wdl(wdl):
    """
    Return the first workflow name and definition in a .wdl file
    .wdl files should have one or zero workflows
    """
    D = scopes_from_wdl("workflow", wdl)
    assert len(D) <= 1
    if len(D) == 1:
        return D.itervalues().next()
    else:
        return None

def read_sync_files(*sync_files):
    paths = []
    for sync_file in sync_files:
        with open(sync_file, "r") as sf:
            paths.extend(sf.read().split())
    return paths

def get_tasks_from_files(*files):
    master_dict = dict()
    for wdl in files:
        tasks = tasks_from_wdl(wdl)
        for k,v in tasks.iteritems():
            if k in master_dict:
                raise ValueError("Task {0} defined in multiple files, aborting sync".format(k))
            else:
                master_dict[k] = v
    return master_dict

def sync_tasks(workflow, tasks):
    """
    Upserts task definitions defined in tasks into the workflow, 
    overwriting the contents of workflow 

    tasks -> Dictionary of task names and definitions
    workflow -> a .wdl file
    """
    workflow_tasks = tasks_from_wdl(workflow)
    workflow_def = workflow_from_wdl(workflow)
    print_("Syncing tasks for {0}:".format(workflow))
    ##Overwrite or add the task_definition
    for task_name, task_definition in tasks.iteritems():
        print("\t{0}".format(task_name))
        workflow_tasks[task_name] = task_definition


    ##Now write out the file, sort tasks in alphabetical order (to try to minimize git impact of repeated syncs)
    with open(workflow, "w") as out:
        for task_name in sorted(workflow_tasks):
            out.write(workflow_tasks[task_name] + "\n\n")
        #Write the workflow_def, if it exists
        if workflow_def is not None:
            out.write(workflow_def + "\n\n")
    print_("{0} task(s) synced".format(len(tasks)))

def glob_list_wdl(*args):
    """
    Joins several globs together into one list of .wdl files.
    Any folder name is converted to "folder_name/*.wdl"

    Raises ValueError if any of the resulting files are not .wdl files
    """
    g = []
    for arg in args:
        path = os.path.join(arg, "*.wdl") if os.path.isdir(arg) else arg
        files = glob.glob(path)
        if len(files) == 0:
            print_("Warning: '{0}'' did not match any files, ignoring".format(arg))
        g.extend(glob.glob(path))

    for f in g:
        if os.path.splitext(f)[1] != ".wdl":
            raise ValueError("{0} is not a .wdl file".format(f)) 
    return g

def main():
    if len(sys.argv) == 1:
        usage()
    else:
        SYNC_MODE=False
        if sys.argv[2] == "-s": 
            SYNC_MODE = True
        paths = glob_list_wdl(*sys.argv[2:]) if not SYNC_MODE else glob_list_wdl(*read_sync_files(*sys.argv[3:]))
        tasks_to_sync = get_tasks_from_files(*paths)
        sync_tasks(sys.argv[1], tasks_to_sync)


def usage():
    print_("sync_tasks.py -- Sync tasks from task folders into a workflow\n")
    print_("You can pass in WDLs and folders directly or use Sync mode (-s), which treats")
    print_("all arguments as SYNC_FILES, which themselves are lists of WDLs\n")
    print_("Usage: python sync_tasks.py workflow [-s] Path [Path ...]\n")

if __name__ == '__main__':
    main()
