# makefile for reader/writer programs for Initiating Message

include ../../../platform.mk

# include directories
OSROOTDIR = ../../../..
AAROOTDIR = ../../debug
LIBDIR  = $(AAROOTDIR)/lib
RTLIBDIR  = $(OSROOTDIR)/c$(RTDIRSFX)/lib
RTSRCDIR = $(OSROOTDIR)/rtsrc
PERSRCDIR = $(OSROOTDIR)/rtpersrc
SRCDIR = $(AAROOTDIR)/src
HFILESDIR = $(AAROOTDIR)/src
HFILES = $(RTSRCDIR)/asn1type.h $(PERSRCDIR)/asn1per.h 
# compiler defs
CFLAGS = -c $(CVARS_) $(CFLAGS_) $(CBLDTYPE_) -D_TRACE
IPATHS = -I$(SRCDIR) -I$(OSROOTDIR) -I$(RTSRCDIR) -I$(PERSRCDIR) $(IPATHS_)
LINKOPT = $(LINKOPT_)

# run-time libraries
LIBS = $(LIBDIR)/$(LIBPFX)ngap$(A) \
   $(RTLIBDIR)/$(PERLIBNAME) $(RTLIBDIR)/$(RTLIBNAME)

LLIBS = $(LLPFX)ngap$(LLAEXT) $(LLPER) $(LLRT) $(LLSYS)
LPATHS = $(LPPFX)$(LIBDIR) $(LPPFX)$(RTLIBDIR)

all : writer$(EXE) reader$(EXE)

WRITEROBJ = writer$(OBJ)

writer$(EXE) : $(WRITEROBJ) $(LIBS)
	$(LINK) $(WRITEROBJ) $(LINKOPT) $(LPATHS) $(LLIBS)

READEROBJ = reader$(OBJ)

reader$(EXE) : $(READEROBJ) $(LIBS)
	$(LINK) $(READEROBJ) $(LINKOPT) $(LPATHS) $(LLIBS)

RWHFILES = $(HFILESDIR)/NGAP-CommonDataTypes.h  \
$(HFILESDIR)/NGAP-Constants.h $(HFILESDIR)/NGAP-IEs.h \
$(HFILESDIR)/NGAP-PDU-Contents.h $(HFILESDIR)/NGAP-PDU-Descriptions.h \
$(HFILESDIR)/rtkey.h $(HFILES)

writer$(OBJ) : writer.c $(RWHFILES)
	$(CC) -c $(CFLAGS) $(IPATHS) writer.c

reader$(OBJ) : reader.c $(RWHFILES)
	$(CC) -c $(CFLAGS) $(IPATHS) reader.c

clean:
	$(RM) *$(OBJ)
	$(RM) *~
	$(RM) reader$(EXE)
	$(RM) writer$(EXE)
	$(RM) *.pdb
	$(RM) *.map
	$(RM) message.dat
