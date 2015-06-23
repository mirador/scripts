import sys, codecs, os

os.environ['CLASSPATH'] = "../miralib/dist/*" # Need this to load the classes from the jar files

# in pyjnius 1.4+ we can use:
#import jnius_config
#jnius_config.add_options('-Xrs', '-Xmx4096')
#jnius_config.set_classpath('.', '../miralib/dist/*')

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
ranges = DataRanges();
dataset = DataSet(project);

# Example of how to set ranges programmatically:
age = dataset.getVariable("AGE")
gender = dataset.getVariable("SEX")
adults = age.createRange(10, 50, False)
females = gender.createRange("Female")
ranges.update(age, adults)
ranges.update(gender, females)

# Setting selection of columns to use in the calculations
dataset.selectAllColumns()
dataset.getGroup("GWAS").deselectAllColumns()
dataset.getGroup("Treatment").deselectAllColumns()
dataset.getTable("Maximum Values of Lab Results").deselectAllColumns()
dataset.getTable("Last Day of Lab Results").deselectAllColumns()
dataset.updateColumnSelection()

count = dataset.getColumnCount()
output = [""] * (count + 1)
print "Number of selected variables",count

print "Calculating correlation matrix:"
scores = [[0 for x in xrange(count)] for x in xrange(count)] 
for i in range(0, count):
    vi = dataset.getColumn(i)
    print "  Variable: " + vi.getAlias() + " - " + str(i) + "/" + str(count) + "..."
    for j in range(i, count):
        vj = dataset.getColumn(j)
        slice = dataset.getSlice(vi, vj, ranges)
        score = 0
        if i != j and slice.missing < project.missingThreshold():
            score = Similarity.calculate(slice, project.pvalue(), project)
        scores[i][j] = scores[j][i] = score        
print "Done."

header = "";
for i in range(0, count):
    vi = dataset.getColumn(i)
    vname = vi.getAlias().replace('"', '\'');
    header = header + ";\"" + vname + "\"";
output[0] = header;

for i in range(0, count):
    vi = dataset.getColumn(i)
    vname = vi.getAlias().replace('"', '\'')
    line = "\"" + vname + "\""
    for j in range(0, count):
        line = line + ";" + str(scores[i][j])
    output[1 + i] = line

file = codecs.open(outputFile, "w", "utf-8")
for line in output:
    file.write(line + "\n");
file.close()  