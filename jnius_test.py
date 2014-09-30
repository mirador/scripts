# Test using JNIus, not functional yet.

import sys, codecs, os
os.environ['CLASSPATH'] = "./*" # Need this to load the classes from the jar files

from jnius import autoclass
Log = autoclass("miralib.utils.Log")
Preferences = autoclass("miralib.utils.Preferences")
Project = autoclass("miralib.utils.Project")
DataRanges = autoclass("miralib.data.DataRanges")
DataSet = autoclass("miralib.data.DataSet")
Variable = autoclass("miralib.data.Variable")
DataSlice2D = autoclass("miralib.data.DataSlice2D")
Similarity = autoclass("miralib.shannon.Similarity")

Log.init()

inputFile = "./config.mira";
outputFile = "./network.csv";

len = len(sys.argv)
if len == 2:
    inputFile = sys.argv[1];
else:
    for i in range(1, len):    
        if sys.argv[i] == "-in" and i + 1 < len:
            inputFile = sys.argv[i + 1];
        elif sys.argv[i] == "-out" and i + 1 < len:
            outputFile = sys.argv[i + 1];
        elif sys.argv[i] == "-miss" and i + 1 < len:
            preferences.missingString = sys.argv[i + 1];
        elif sys.argv[i] == "-mist" and i + 1 < len:
            preferences.missingThreshold = Project.stringToMissing(sys.argv[i + 1]); 
        elif sys.argv[i] == "-pval" and i + 1 < len:
            preferences.pValue = Project.stringToPValue(sys.argv[i + 1]);
        elif sys.argv[i] == "-algo" and i + 1 < len:
            preferences.depTest = Similarity.stringToAlgorithm(sys.argv[i + 1]);
        elif sys.argv[i] == "-surr" and i + 1 < len:
            preferences.surrCount = int(sys.argv[i + 1]);
        elif sys.argv[i] == "-chtr" and i + 1 < len:
            preferences.threshold = float(sys.argv[i + 1]);

preferences = Preferences()
project = Project(inputFile, preferences)
# This hangs the script, bc of calls to PApplet
# dataset = DataSet(project);
ranges = DataRanges();
