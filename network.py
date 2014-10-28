import sys, os, codecs
from miralib.utils import Log
from miralib.utils import Preferences
from miralib.utils import Project
from miralib.data import DataRanges
from miralib.data import DataSet
from miralib.data import Variable
from miralib.data import DataSlice2D
from miralib.shannon import Similarity

Log.init()


inputFile = "./25-44/profile-config.mira";
outputFile = "./25-44/network.csv";

if 1 < len(sys.argv):
    inputFile = sys.argv[1]
    outputFile = os.path.join(os.path.split(inputFile)[0], 'network.csv')
    if 2 < len(sys.argv):
        outputFile = sys.argv[2]

print "Input Mirador project file:",inputFile
print "Output network file       :",outputFile

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