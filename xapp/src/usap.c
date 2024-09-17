//
// Created by murilo on 17/09/24.
//

#include "usap.h"

void start_kpm_monitor(char * configPath)
{
    char * argv[] = {"xapp_usap", "-c", configPath};
    int argc = sizeof(argv)/sizeof(char *);
}