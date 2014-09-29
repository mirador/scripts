import sys, codecs
from miralib.utils import Log
from miralib.utils import Preferences
from miralib.utils import Project
from miralib.data import DataRanges
from miralib.data import DataSet
from miralib.data import Variable
from miralib.data import DataSlice2D
from miralib.shannon import Similarity

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
dataset = DataSet(project);
ranges = DataRanges();

count = dataset.getVariableCount()
output = [""] * (count + 1)
    
print "Calculating correlation matrix:"
scores = [[0 for x in xrange(count)] for x in xrange(count)] 
for i in range(0, count):
    print "  Row " + str(i) + "/" + str(count) + "..."
    for j in range(i, count):
        vi = dataset.getVariable(i)
        vj = dataset.getVariable(j)
        slice = dataset.getSlice(vi, vj, ranges)
        score = 0
        if i != j and slice.missing < project.missingThreshold():
            score = Similarity.calculate(slice, project.pvalue(), project)
        scores[i][j] = scores[j][i] = score        
print "Done."
    
header = "";
for i in range(0, count):
    vi = dataset.getVariable(i)
    vname = vi.getAlias().replace('"', '\'');
    header = header + ";\"" + vname + "\"";
output[0] = header;

for i in range(0, count):
    vi = dataset.getVariable(i)
    vname = vi.getAlias().replace('"', '\'')
    line = "\"" + vname + "\""
    for j in range(0, count):
        line = line + ";" + str(scores[i][j])
    output[1 + i] = line

file = codecs.open(outputFile, "w", "utf-8")
for line in output:
    file.write(line + "\n");
file.close()    

print "Saved to",outputFile
