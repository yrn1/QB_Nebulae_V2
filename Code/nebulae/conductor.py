import filehandler as fh
import instrparser
import os

class Conductor(object):
    def __init__(self):
        self.instrparser = instrparser.InstrParser()
        self.source = "factory"
        self.instr = "granular_test"
        self.dir = "/home/alarm/audio/"

    def generate_orc(self, instr, instr_bank):
        self.refreshFileHandler()
        self.instr = instr
        self.orcheader = """
; File-Looping Orc
nchnls=2
0dbfs=1
; primary controls
gkpitch chnexport "pitch", 1
gkspeed chnexport "speed", 1
gkloopstart chnexport "start", 1
gkloopsize chnexport "size", 1
gkdensity chnexport "density", 1
gkoverlap chnexport "overlap", 1
gkwindow chnexport "window", 1
gkfilesel chnexport "file", 1
gkfreeze chnexport "freeze", 1
gkreset chnexport "reset", 1
gkblend chnexport "blend", 1
gkrecord chnexport "record", 1
gkfilestate chnexport "filestate", 1
gksource chnexport "source", 1
gksourcegate chnexport "sourcegate", 1
gksourcebuttonstate chnexport "source_state", 1
gkeol chnexport "eol", 2
gksizestatus chnexport "sizestatus", 2
gkrecordstatus chnexport "recordstatus", 2
gkbufferlength chnexport "bufferlength", 2
; secondary controls
gkloopstart_alt chnexport "start_alt", 1
gkloopsize_alt chnexport "size_alt", 1
gkdensity_alt chnexport "density_alt", 1
gkoverlap_alt chnexport "overlap_alt", 1
gkwindow_alt chnexport "window_alt", 1
gkfreeze_alt chnexport "freeze_alt", 1
gkrecord_alt chnexport "record_alt", 1
gkfile_alt chnexport "file_alt", 1
gkreset_alt chnexport "reset_alt", 1
gksource_alt chnexport "source_alt", 1
gkpitch_alt chnexport "pitch_alt", 1
gkblend_alt chnexport "blend_alt", 1
; added by danishfurniture
gkinsttype1 chnexport "instype1", 2
gkinsttype2 chnexport "instype2", 2
gkinsttype3 chnexport "instype3", 2
gkoption1 chnexport "option1", 2
gkoption2 chnexport "option2", 2
gkoption3 chnexport "option3", 2
gkoption4 chnexport "option4", 2
gkoption5 chnexport "option5", 2
gkoption6 chnexport "option6", 2
gkoption7 chnexport "option7", 2
; data buffers -- 100 Files maximum
gilen[] init 100
gichn[] init 100
gSname[] init 100
gisr[] init 100
gipeak[] init 100
            """

        self.source = instr_bank
        if self.source == "user": # Changed "is" to "==" (danishfurniture)
            self.instr_dir = "/home/alarm/instr/"
        else: #if self.source is "factory":
            self.instr_dir = "/home/alarm/QB_Nebulae_V2/Code/instr/"
        self.instrparser.parse(self.instr, self.instr_dir)
        if self.instrparser.configEntry("ksmps") is not None:
            self.preamble = "ksmps = " + str(self.instrparser.configEntry("ksmps")[0]) + "\n"
        else:
            self.preamble = "ksmps = 128\n"
        if self.instrparser.configEntry("sr") is not None:
            self.preamble += "sr = " + str(self.instrparser.configEntry("sr")[0]) + "\n"
        else:
            self.preamble += "sr = 48000\n"
        isco = "f 0 2147483641\n" + "i1 1 -10\n" #Start the longest possible score, and force i1 to run for length of score
        fsco_lines = []
        glen_arrayinit = []
        stereo_ftgen = []
        glen_arrayinit.append('\n')
        for i,f in enumerate(self.filehandler.files):
            #fsco_lines.append("f " + str(i + 1) + " 0 0 1 \"" + f + "\" 0 0 0\n")
            fsco_lines.append("f " + str(400 + i) + " 0 0 1 \"" + f + "\" 0 0 1\n") # 'f' in a Csound score is an 'ftgen' command
            glen_arrayinit.append("gSname[" + str(i) +"] = \"" + f + "\"\n")
            glen_arrayinit.append("gilen[" + str(i) +"] filelen \"" + f + "\"\n")
            glen_arrayinit.append("gichn[" + str(i) +"] filenchnls \"" + f + "\"\n")
            glen_arrayinit.append("gisr[" + str(i) +"] filesr \"" + f + "\"\n")
            glen_arrayinit.append("gipeak[" + str(i) +"] filepeak \"" + f + "\"\n")
        glen_arrayinit.append("ginumfiles init " + str(self.numFiles()) + "\n")
        fsco = ''.join(fsco_lines)
        self.arrayinitlines = ''.join(glen_arrayinit)
        sco = isco + fsco   # This is the score?
        self.curOrc = self.preamble + self.orcheader + self.arrayinitlines + self.instrparser.getInstrString() # This builds the orchestra?
        self.curSco = sco   # This is the score?
        try:
            if neb_globals.remount_fs is True:
                os.system("sh /home/alarm/QB_Nebulae_V2/Code/scripts/mountfs.sh rw")
            if os.path.isdir("/home/alarm/QB_Nebulae_V2/Code/log") != True:
                os.system("mkdir -p /home/alarm/QB_Nebulae_V2/Code/log")
            with open('/home/alarm/QB_Nebulae_V2/Code/log/formattedcsd.txt', 'w') as f:
                f.write("Beginning of generated CSOUND Score/Orchestra")
                f.write(self.curSco + self.curOrc)
                f.write("End of generated CSOUND Score/Orchestra")
            if neb_globals.remount_fs is True:
                os.system("sh /home/alarm/QB_Nebulae_V2/Code/scripts/mountfs.sh ro")
        except:
            print "Could not write log of current csd"

    def numFiles(self):
        # return self.filehandler.numFiles() # there was a ";" at the end of this line
        print self.instrparser.configEntry("typeInst")
        if self.instrparser.configEntry("typeInst") is not None:
	        print self.instrparser.configEntry("typeInst")[0]
	        print self.instrparser.configEntry("typeInst")[1]
	        print self.filehandler.numFiles()
        #     return self.instrparser.configEntry("typeInst")[0]
        # else:
        #     return self.filehandler.numFiles() # there was a ";" at the end of this line
        return self.filehandler.numFiles() # there was a ";" at the end of this line

    def getConfigDict(self):
        return self.instrparser.getConfigDict()

    def refreshFileHandler(self):
        self.filehandler = fh.FileHandler(self.dir,[".wav",".aif", ".aiff", ".flac"])
