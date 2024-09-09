//
// Created by Murilo Silva on 09/09/24.
//

#include <asn1coder.h>
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

int main()
{
    char * strTest = NULL;
    write_working(&strTest);

    // compare strings
    assert(strcmp(strTest, "Working...") == 0);

    free(strTest);
    return EXIT_SUCCESS;
}
