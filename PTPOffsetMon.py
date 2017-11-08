#!/isan/bin/nxpython

################################################################
# File:   PTPOffseMon.py
#
# Description:
#    This application monitors the PTP offset from master every
#    2 minutes.  Depending on the amount of drift from offset
#    will generate a syslog message (1. Alert, 2. Critical,
#    3. Error).
#
#    Thresholds for alerts are configurable
#
#
#
# $Id: $
# $Source: $
# $Author: Simon Hart
##################################################################


import time
import threading
import sys
import json

### Imports NX-OS SDK package
import nx_sdk_py

###
# Timer thread to showcase that native python threads can also
# run along with sdkThread which is also listening for NX-OS 
# specific events.
###
def timerThread(name,val):
    global cliP, sdk, tmsg
    count = 0
    while True:
        count += 1
        if sdk and cliP:
            print "timer kicked - sdk"

            #Check for offset
            offset()

        else:
            print "timer ticked - not sdk"
        if tmsg:
           ### Logs a event log everytime timer is kicked once tmsg
           ### is initialized.
           tmsg.event("PTPOffsetMon Timer ticked - %d" % count)

        time.sleep(120)


'''Checking to see if any violations of PTP Offset'''

def offset():
    x=0
    global cliP, sdk, current_upper_threshold, current_lower_threshold, tmsg

    resp_str = cliP.execShowCmd("show ptp clock", nx_sdk_py.R_JSON)
    clckd = json.loads(resp_str)
    off_set_val = int(clckd["offset-from-master"])
    if off_set_val >= current_threshold and off_set_val < current_threshold_2 \
            or off_set_val <= -current_threshold and off_set_val > -current_threshold_2:

        offset = str(clckd["offset-from-master"])

        msg = "PTP VIOLATION - offset now at " + offset
        tmsg.syslog(tmsg.ALERT, str(msg))
        print('offset warning ' + offset)

    elif off_set_val >= current_threshold_2 and off_set_val < current_threshold_3 \
            or off_set_val <= -current_threshold_2 and off_set_val > -current_threshold_3:

        offset = str(clckd["offset-from-master"])

        msg = "PTP VIOLATION - offset now at " + offset
        tmsg.syslog(tmsg.CRITICAL, str(msg))
        print('offset warning ' + offset)

    elif off_set_val >= current_threshold_3 or off_set_val <= -current_threshold_3:
        offset = str(clckd["offset-from-master"])

        msg = "PTP VIOLATION - offset now at " + offset
        tmsg.syslog(tmsg.ERROR, str(msg))
        print('offset warning ' + offset)


###
# Inherit from the NxCmdHandler class, define the application
# callback in 'postCliCb'. Handler Callback for Custom Cli execution.
# Returns True if the action was successful. False incase of failure.
###

class pyCmdHandler(nx_sdk_py.NxCmdHandler):


        def postCliCb(self,clicmd):
           
            ### To access the global Cli Parser Obj
            global cliP, current_threshold, current_threshold_2, current_threshold_3

            if "set_ptp_upper_threshold_1" in clicmd.getCmdName():

            ### Create Int Pointer to get the integer Value
                int_p = nx_sdk_py.new_intp()
                int_p = nx_sdk_py.void_to_int(clicmd.getParamValue("<threshold1>"))

            ### Get the value of int * in python
                if int_p:
                    current_threshold = int(nx_sdk_py.intp_value(int_p))

            if "set_ptp_upper_threshold_2" in clicmd.getCmdName():
                int_p = nx_sdk_py.new_intp()
                int_p = nx_sdk_py.void_to_int(clicmd.getParamValue("<threshold2>"))

                if int_p:
                    current_threshold_2 = int(nx_sdk_py.intp_value(int_p))


            elif "set_ptp_upper_threshold_3" in clicmd.getCmdName():
                int_p = nx_sdk_py.new_intp()
                int_p = nx_sdk_py.void_to_int(clicmd.getParamValue("<threshold3>"))

                if int_p:
                    current_threshold_3 = int(nx_sdk_py.intp_value(int_p))


            if "show_ptp" in clicmd.getCmdName():

                ptpclock = cliP.execShowCmd("show ptp clock", nx_sdk_py.R_JSON)
                jsonclock = json.loads(ptpclock)
                printstr = str(jsonclock["offset-from-master"])
                clicmd.printConsole("\nThe current ptp offset from master is at %s \n\n" % printstr)

            elif "show_threshold_1" in clicmd.getCmdName():


                clicmd.printConsole("Upper Threshold Sev 1 is set to %s " % current_threshold)

                clicmd.printConsole("\nLower Threshold Sev 1 is set to %s \n\n" % -current_threshold)
                clicmd.printConsole("Upper Threshold Sev 2 is set to %s " % current_threshold_2)

                clicmd.printConsole("\nLower Threshold Sev 2 is set to %s \n\n" % -current_threshold_2)
                clicmd.printConsole("Upper Threshold Sev 3 is set to %s " % current_threshold_3)

                clicmd.printConsole("\nLower Threshold Sev 3 is set to %s \n\n" % -current_threshold_3)

            return True

### Perform all SDK related initializations in one thread.  
### All SDK related activities happen here, while the main thread
### may continue to do other work.  The call to startEventLoop will
### block until we break out of it by calling stopEventLoop. 
def sdkThread(name,val):
    global cliP, sdk, event_hdlr, tmsg, int_attr

    ###
    # getSdkInst is the first step for any custom Application
    # wanting to gain access to NXOS Infra. Without this 
    # NXOS infra cannot be used.
    #
    # NOTE: 
    #   Perform all SDK related initializations and startEventLoop in one
    #   thread. The call to startEventLoop will block the thread until we 
    #   break out of it by calling stopEventLoop.  
    #
    #   Perform other actions in a different thread.   
    ###
    sdk = nx_sdk_py.NxSdk.getSdkInst(len(sys.argv), sys.argv)
    if not sdk:
       return

    ### Set a short Application description.
    sdk.setAppDesc('BOA PTP Python App')

    ###
    # To Create & Manage Custom syslogs one must do
    # getTracer() which loads the plugin to NXOS Syslog
    # Infra Functionalities. 
    ###
    tmsg = sdk.getTracer()

    ### To log some Trace events
    tmsg.event("[%s] Started service" % sdk.getAppName())

    ###
    # To Create & Manage Custom CLI commands one must do
    # getCliParser() which loads the plugin to NXOS CLI
    # Infra Functionalities. 
    ###
    cliP = sdk.getCliParser()

    ### Construct Custom show Port Bandwidth Utilization commands
    nxcmd = cliP.newShowCmd("show_ptp", "ptp_offset")
    nxcmd.updateKeyword("ptp_offset", "offset from master")

    nxcmd = cliP.newShowCmd("show_threshold_1", "values")
    nxcmd.updateKeyword("values", "Upper and Lower threshold values for all Severity levels")


    myranges = [0,1001,2001,1000,2000,5000]


    for i in range(1,4):

        threshstr = "set_ptp_upper_threshold_" + str(i)
        newstr = "Threshold_%s <threshold%s>" % (str(i), str(i))

        nxcmd = cliP.newConfigCmd(threshstr, newstr)
        nxcmd.updateKeyword(newstr[:11], "Offset Severity %s for upper & lower threshold for monitoring" % (str(i)))
        int_attr = nx_sdk_py.cli_param_type_integer_attr()
        int_attr.min_val = myranges[i-1];
        int_attr.max_val = myranges[i+2];
        nxcmd.updateParam(newstr[12:], \
                           "Upper threshold value in nanoseconds", \
                           nx_sdk_py.P_INTEGER, int_attr, len(int_attr))



    ###
    # Add the command callback Handler.
    # When the respective CLI commands gets configured 
    # the overloaded postCliCb callback will be instantiated.
    ###
    mycmd = pyCmdHandler()
    cliP.setCmdHandler(mycmd)

    ###
    # This is important as it Adds the constructed custom configs 
    # to NXOS CLI Parse tree.
    ###
    cliP.addToParseTree()

    ###
    # startEventLoop will block the thread until we break out
    # of it by calling stopEventLoop.
    ###
    sdk.startEventLoop()

    ### Got here either by calling stopEventLoop() or when App 
    ### is removed from VSH.
    tmsg.event("Service Quitting...!")

    ### [Required] Needed for graceful exit.
    nx_sdk_py.NxSdk.__swig_destroy__(sdk)

### main thread
### Global Variables
cliP = 0
sdk  = 0
tmsg = 0
current_threshold = 1000
current_threshold_2 = 2000
current_threshold_3 = 5000
heartbeat_interval = 60

### create a new sdkThread to setup SDK service and handle events.
sdk_thread = threading.Thread(target=sdkThread, args=("sdkThread",0))
sdk_thread.start()


timer_thread = threading.Thread(target=timerThread, args=("timerThread",0))
timer_thread.daemon = True

### 
# Starting timer thread. Start it after sdkThread is started so that
# any SDK specific APIs will work without any issues in timerThread.  
###
timer_thread.start()

### Main thread is blocked until sdkThread exits. This keeps the
### App running and listening to NX-OS events. 
sdk_thread.join()

