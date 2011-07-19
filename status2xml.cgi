#!/usr/bin/env python
""" This takes the nagios realtime status dada and outputs as XML. """

import re
import sys
import datetime

# config local access control permission to enable the file to be readbale by this script
status_file="/usr/local/nagios/var/status.dat"

# fixme - the following token change dependiong on the version of Nagios 
hosttoken='hoststatus'
servicetoken='servicestatus'
programtoken='programstatus'

def GetDefinitions(filename,obj):
    """ Parse the status.dat file and extract matching object definitions """
    file=open(filename)
    content=file.read().replace("\t"," ")
    file.close
    pat=re.compile(obj +' \{([\S\s]*?)\}',re.DOTALL)
    finds=pat.findall(content)
    return finds


def GetDirective(item,directive):
    """ parse an object definition, return the directives """
    pat=re.compile(' '+directive + '[\s= ]*([\S, ]*)\n')
    m=pat.search(item)
    if m:
        return m.group(1)



def xmlattr(definition,directive):
    """ returns directive='value' """
    return "%s='%s' " % (directive,GetDirective(definition,directive).strip())


def main():
    """ Parse and output """
    print "Content-type: text/plain\n\n"
    output="<?xml version='1.0'?>\n"
    output+="<nagios name='nagios' "

    # Information about Nagios running state
    prog=GetDefinitions(status_file,programtoken)
    for progdef in prog:
        output+=xmlattr(progdef,"last_command_check")+" >\n"
    output+="  <hosts>\n"

    # each host
    hosts=GetDefinitions(status_file,hosttoken)
    for hostdef in hosts:
        output+="    <host"
        output+="   "+xmlattr(hostdef,"host_name")
        output+="   "+xmlattr(hostdef,"current_state")
        output+="   "+xmlattr(hostdef,"current_attempt")
        output+="   "+xmlattr(hostdef,"last_check")	
        output+="   >\n"

        services=GetDefinitions(status_file,servicetoken)
        for servicedef in services:
            if(GetDirective(servicedef,"host_name").strip()==GetDirective(hostdef,"host_name").strip()):
                output+="      <service"
                output+=" "+xmlattr(servicedef,"service_description")
                output+=" "+xmlattr(servicedef,"current_state")
                output+=" "+xmlattr(servicedef,"current_attempt")
                output+=" "+xmlattr(servicedef,"last_check")
                output+="/>\n"
        output+="    </host>\n"
    output+="  </hosts>\n"
    output+="</nagios>\n"
    print output

if __name__ == "__main__":
    sys.exit(main())

