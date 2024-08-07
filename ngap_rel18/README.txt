NGAP 3GPP LTE Protocol API, Release 18.0

This distribution contains the software for the 5G NG Application
Protocol (NGAP) Specification as defined by the Third Generation 
Partnership Program (3GPP).  The ASN.1 files were extracted 
from 3GPP specification TS 38.413.

INSTALLATION

The extended sample program is saved as an archive which 
is to be installed within an existing ASN1C installation (either 
evaluation or licensed).

The package should be unzipped in the c - or c_64 for 64-bit
Windows - subdirectory of the ASN1C installation. The following
directory tree will be created: 

ngap_<rel>
  +- debug
     +- build
     +- lib
     +- src
  +- release
     +- build
     +- lib
     +- src
  +- sample
     +- initiatingMessage
  +- specs

where <rel> would be replaced with the supported NGAP release version.
For example, ngap_rel18 would correspond to NGAP release 18.

BUILD PROCEDURE

The debug and release subdirectories contain debug and release versions
of the API respectively.  The source code generated for each of these 
configurations is different; thus the need for two separate directories.

To build the NGAP library, change directory to the debug/build or 
release/build subdirectory and execute the Visual Studio nmake command.  
This will cause the ASN1C compiler to be invoked to compile the ASN.1 
specification file(s) in the specs subdirectory.  The C compiler will then 
be invoked to compile the C source files.  The result will be a static 
archive library file created in the lib subdirectory.

The library may also be built using the Visual Studio IDE by 
double-clicking on the src.vcproj file located in the debug/src or
release/src subdirectory.  Visual Studio 2019 or higher is required.

For Linux, run "make" in the main directory of the package.

To build and run the sample programs, go to the sample subdirectory. 
You can then go to each of the sample subdirectories within and invoke 
nmake to compile and link the writer and reader programs.  The writer 
and reader programs can then be invoked from a command-line prompt 
to demonstrate the encoding and decoding of PER messages.

INCLUDED FILES

The following is a listing and description of important files 
included in this package.  Note that the files listed are what 
is present after a build is completed:

debug/build/makefile - This is the makefile for building the debug 
version of the NGAP library.

debug/lib/ngap_a.lib - Object library containing compiled NGAP C source 
file objects.  The default compiled configured configuration is a 
static library.  This should be linked with the lib/asn1per_a.lib and 
lib/asn1rt_a.lib libraries to produce an executable (see the sample 
programs).

debug/src/* - This directory contains the standard generated NGAP source 
code.  This code is generated with the -trace command-line option which 
adds additional diagnostic messages for PER bit-field tracing.

release/build/makefile - This is the makefile for building the release 
(optimized) version of the NGAP library.

release/lib/ngap_a.lib - Object library containing compiled NGAP C 
source file objects.  The default compiled configured configuration is 
a static library.  This should be linked with the optimized run-time 
libraries (lib_opt/asn1per_a.lib and lib_opt/asn1rt_a.lib) libraries 
to produce an executable (see the sample programs).

release/src/* - This directory contains the standard generated NGAP source 
code.  The code in this case is generated with the -compact command-line 
option which removes diagnostic and error messages and does additional 
optimizations.

sample/initiatingMessage - This directory contains a sample program 
showing how an NGAP message is populated, encoded, and decoded.  The 
writer program encodes a test message and writes it to a file 
(message.dat).  The reader will read this file and decode and display 
the message contents.

specs/* - ASN.1 specifications extracted and pretty-printed from the 
3GPP NGAP TS 38.413 standards document.

GETTING STARTED

The best way to begin using the software is by executing the sample 
program.  Go to the sample/initiatingMessage directory and execute the 
makefile using nmake from a Visual Studio command prompt or other 
command shell, or using make from a Linux terminal:

  nmake (Windows)
   OR
  make (Linux)

This will build the writer and reader programs.  You can then 
execute the writer as follows:

  writer

It will encode a PER message corresponding to one of the PDU types in 
the specification and write it to the message.dat file.  A trace dump 
of the message will be done do that you can observe the bit-pattern of 
what was encoded.

You can then issue the reader program to read the message:

  reader

This will read and decode the message.  The contents of the decoded 
structure will be displayed.  You can verify these contents with the 
code in the writer program to ensure you got back what originally was 
encoded.

This can then be used as a template for further development.  The most 
time consuming task in developing an API is poulating data structures for 
encoding.  ASN1C provides some assistance in this area through the test 
code generation command-line option (-genTest).  This will populate a test 
instance of a generated type with random test data.  This can then be used
as a model for populating structures with real data.

REPORTING PROBLEMS

Report problems you encounter by sending E-mail to support@obj-sys.com.  
The preferred format of example programs is the same as the sample 
programs.  Please provide a writer and reader and indicate where in 
the code the problem occurs.

If you have any further questions or comments on what you would like to 
see in the product or what is difficult to use or understand, please 
communicate them to us.  Your feedback is important to us.  Please let 
us know how it works out for you - either good or bad.
