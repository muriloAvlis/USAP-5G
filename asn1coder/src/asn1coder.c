//
// Created by Murilo Silva on 09/09/24.
//

#include "asn1coder.h"

// Just a test
void write_working(char ** str)
{
    free(*str);

    *str = calloc(1, sizeof(char *));

    strcpy(*str, "Working...");
}

