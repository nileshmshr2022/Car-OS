#
# Created on Sun Oct 02 2022 10:10:10 AM
#
# The MIT License (MIT)
# Copyright (c) 2022 Aananth C N
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial
# portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

# This tool takes *.oil file generated by OSEK-Builder tool as input and 
# generates .c/.h/.mk files as output.
import sys
import os
import traceback

from os_builder.scripts.common import import_or_install, print_info
from os_builder.scripts.ob_globals import TaskParams, CntrParams, AlarmParams, ISR_Params, TNMI, FreeOSEK_Params, OSEK_Params, STSZ

import os_builder.scripts.sg_counter as sg_counter
import os_builder.scripts.sg_tasks as sg_tasks
import os_builder.scripts.sg_alarms as sg_alarms
import os_builder.scripts.sg_appmodes as sg_appmodes
import os_builder.scripts.sg_events as sg_events
import os_builder.scripts.sg_messages as sg_messages
import os_builder.scripts.sg_resources as sg_resources
import os_builder.scripts.sg_os_param as sg_os_param
import os_builder.scripts.sg_isrs as sg_isrs

import colorama
from colorama import init, Fore, Back, Style
init(convert=True)


from gui.os.os_view import Counters
from gui.os.os_view import Alarms
from gui.os.os_view import Tasks
from gui.os.os_view import AppModes
from gui.os.os_view import ISRs
from gui.os.os_view import OS_Cfgs


# Functions
def print_usage(prog):
    print("Usage:\n\t python " + prog + " output/oil-files/*.oil")



def parse_alarm_autostart(oil_lines, line_num, alarms):
    line = oil_lines[line_num]
    alarms[AlarmParams[5]] = line.replace('=', '{').split('{')[1].strip()
    line_num += 1
    while "};" not in oil_lines[line_num]:
        line = oil_lines[line_num]
        if "ALARMTIME" in line.split():
            alarms[AlarmParams[6]] = line.replace('=', ';').split(';')[1].strip()
        if "CYCLETIME" in line.split():
            alarms[AlarmParams[7]] = line.replace('=', ';').split(';')[1].strip()
        if "APPMODE" in line.split():
            try:
                alarms[AlarmParams[8]].append(line.replace('=', ';').split(';')[1].strip())
            except KeyError:
                alarms[AlarmParams[8]] = []
                alarms[AlarmParams[8]].append(line.replace('=', ';').split(';')[1].strip())
        line_num += 1

    return line_num, alarms



def parse_alarm_action(oil_lines, line_num, alarms):
    line = oil_lines[line_num]
    alarms[AlarmParams[2]] = line.replace('=', '{').split('{')[1].strip()
    line_num += 1
    while "};" not in oil_lines[line_num]:
        line = oil_lines[line_num]
        if "TASK" in line.split():
            alarms[AlarmParams[3]] = line.replace('=', ';').split(';')[1].strip()
        if "EVENT" in line.split():
            alarms[AlarmParams[4]] = line.replace('=', ';').split(';')[1].strip()
        if "ALARMCALLBACKNAME" in line.split():
            alarms[AlarmParams[3]] = line.replace('=', ';').split(';')[1].strip()
        line_num += 1

    return line_num, alarms



def parse_alarms(oil_lines, line_num):
    alarms = {}
    alarms[AlarmParams[0]] = oil_lines[line_num].split()[1]
    line_num += 1
    while "};" not in oil_lines[line_num]:
        line = oil_lines[line_num]
        if AlarmParams[1] in line:
            alarms[AlarmParams[1]] = line.replace('=', ';').split(';')[1].strip()
        if "ACTION" in line.split() and "{" in line:
            line_num, alarms = parse_alarm_action(oil_lines, line_num, alarms)
        if "AUTOSTART" in line.split() and "{" in line:
            line_num, alarms = parse_alarm_autostart(oil_lines, line_num, alarms)
        elif "AUTOSTART" in line.split() and "FALSE" in line:
            alarms[AlarmParams[5]] = line.replace('=', ';').split(';')[1].strip()

        line_num += 1

    return line_num, alarms



def parse_task_autostart(oil_lines, line_num, task):
    line = oil_lines[line_num]
    task[TaskParams[4]] = line.replace('=', '{').split('{')[1].strip()
    line_num += 1
    while "};" not in oil_lines[line_num]:
        line = oil_lines[line_num]
        if "APPMODE" in line.split():
            app_mode = line.replace('=', ';').split(';')[1].strip()
            if app_mode not in AppModes:
                AppModes.append(app_mode)
            try:
                task["AUTOSTART_APPMODE"].append(app_mode)
            except KeyError:
                task["AUTOSTART_APPMODE"] = []
                task["AUTOSTART_APPMODE"].append(app_mode)
        line_num += 1

    return line_num, task



def parse_tasks_item_list(line, task, param):
    if TaskParams[param] in line.split():
        try:
            task[TaskParams[param]].append(line.replace('=', ';').split(';')[1].strip())
        except KeyError:
            task[TaskParams[param]] = []
            task[TaskParams[param]].append(line.replace('=', ';').split(';')[1].strip())
    return task



def parse_tasks(oil_lines, line_num):
    tasks = {}
    tasks[TaskParams[TNMI]] = oil_lines[line_num].split()[1]
    line_num += 1
    while "};" not in oil_lines[line_num]:
        line = oil_lines[line_num]
        if TaskParams[1] in line:
            tasks[TaskParams[1]] = line.replace('=', ';').split(';')[1].strip()
        if TaskParams[2] in line:
            tasks[TaskParams[2]] = line.replace('=', ';').split(';')[1].strip()
        if TaskParams[3] in line:
            tasks[TaskParams[3]] = line.replace('=', ';').split(';')[1].strip()
        if "AUTOSTART" in line.split() and "{" in line:
            line_num, tasks = parse_task_autostart(oil_lines, line_num, tasks)
        elif "AUTOSTART" in line.split() and "FALSE" in line:
            tasks[TaskParams[4]] = line.replace('=', ';').split(';')[1].strip()
        tasks = parse_tasks_item_list(line, tasks, 5)
        tasks = parse_tasks_item_list(line, tasks, 6)
        tasks = parse_tasks_item_list(line, tasks, 7)
        if TaskParams[STSZ] in line:
            tasks[TaskParams[STSZ]] = line.replace('=', ';').split(';')[1].strip()
        line_num += 1

    return line_num, tasks



def parse_counter(oil_lines, line_num):
    cntr = {}
    cntr[CntrParams[0]] = oil_lines[line_num].split()[1]
    line_num += 1
    while "};" not in oil_lines[line_num]:
        line = oil_lines[line_num]
        if CntrParams[1] in line:
            cntr[CntrParams[1]] = int(line.replace('=', ';').split(';')[1])
        if CntrParams[2] in line:
            cntr[CntrParams[2]] = line.replace('=', ';').split(';')[1].strip()
        if CntrParams[3] in line:
            cntr[CntrParams[3]] = int(line.replace('=', ';').split(';')[1])
        if "TICKDURATION" in line:
            cntr[CntrParams[2]] = int(line.replace('=', ';').split(';')[1]) # treat OSMAXALLOWEDVALUE as TICKDURATION
        line_num += 1
    # following line is added as AUTOSAR spec doesn't support TICKDURATION, hence it is replaced with OsCounterType
    if "OsCounterType" not in cntr:
        cntr["OsCounterType"] = "HARDWARE"
    return line_num, cntr



def parse_os_params(oil_lines, line_num, par_list):
    os_params = {}
    line_num += 1
    while "};" not in oil_lines[line_num]:
        line = oil_lines[line_num]
        for osp in par_list:
            if osp in line:
                os_params[osp] = line.replace('=', ';').split(';')[1].strip()
        line_num += 1
    return line_num, os_params



def parse_isr(oil_lines, line_num):
    isrs = {}
    isrs[ISR_Params[0]] = oil_lines[line_num].split()[1]
    line_num += 1
    while "};" not in oil_lines[line_num]:
        line = oil_lines[line_num]
        for isr in ISR_Params:
            if isr in line:
                isrs[isr] = line.replace('=', ';').split(';')[1].strip()
 
        line_num += 1

    # Add ARXML elements to OIL file extracts
    if "OsIsrInterruptPriority" not in isrs:
        isrs["OsIsrInterruptPriority"] = '0'
    if "OsIsrStackSize" not in isrs:
        isrs["OsIsrStackSize"] = 0

    return line_num, isrs



def set_source_file_path(path):
    global SrcFilePath
    SrcFilePath = path


def parse(oilfile):
    global Counters, Alarms, Tasks, AppModes, ISRs, OS_Cfgs

    # Validate and open OIL file
    print_info("Opening " + oilfile)
    if "oil" != oilfile.split(".")[-1]:
        print(Fore.RED + "Error: Input file is not an OIL file!", Style.RESET_ALL)
        return -1
    
    if not os.path.exists(oilfile):
        print(Fore.RED + "Error: Can't open OIL file: \""+oilfile+"\"!", Style.RESET_ALL)
        return -1
    
    of = open(oilfile, "r")
    print(Style.RESET_ALL, "\033[F")
    
    # Generate source in src folder under tools, else create it in current directory
    if oilfile.split("/")[-2] == "oil-files" and oilfile.split("/")[-3] == "output":
        path = "/".join(oilfile.split("/")[0:-3]) + "/tools/src"
    else:
        path = "/".join(oilfile.split("/")[0:-1]) + "/src"
    set_source_file_path(path)
    if not os.path.exists(path):
        print_info("Creating source file directory " + path)
        os.mkdir(path)
    
    # Parse the OIL file
    print_info("Parsing " + oilfile)
    oil_lines = of.readlines()
    total_lines = len(oil_lines)
    line_num = 1
    while line_num < total_lines:
        words = oil_lines[line_num].split()
        if "COUNTER" in words and "{" in oil_lines[line_num]:
            line_num, cntr = parse_counter(oil_lines, line_num)
            Counters.append(cntr)
        if "ALARM" in words and "{" in oil_lines[line_num]:
            line_num, alrms = parse_alarms(oil_lines, line_num)
            Alarms.append(alrms)
        if "TASK" in words and "{" in oil_lines[line_num]:
            line_num, task = parse_tasks(oil_lines, line_num)
            Tasks.append(task)
        if "ISR" in words and "{" in oil_lines[line_num]:
            line_num, isr = parse_isr(oil_lines, line_num)
            ISRs.append(isr)
        if "FreeOSEK_PARAMS" in words and "{" in oil_lines[line_num]:
            line_num, os_params = parse_os_params(oil_lines, line_num, FreeOSEK_Params)
            OS_Cfgs.update(os_params)
        if "OS" in words and "{" in oil_lines[line_num]:
            OS_Cfgs["OS"] = words[1]
            line_num, os_params = parse_os_params(oil_lines, line_num, OSEK_Params)
            OS_Cfgs.update(os_params)
        line_num += 1
        
    # Get CPU / Target name
    OS_Cfgs["CPU"] = oil_lines[0].split(" ")[1]

    return path



if __name__ == '__main__':
    cmd_args = len(sys.argv)
    if cmd_args < 2:
        print(Fore.RED + "Error: Input OIL file not passed as argument!", Style.RESET_ALL)
        print_usage(sys.argv[0])
        exit(-1)
    
    # check and import pre-requisites
    import_or_install("colorama")

    oilfile = sys.argv[1]
    parse(oilfile)
    generate_code()
