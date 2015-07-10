import sys, codecs, os, time
from scipy.stats import chi2_contingency
from scipy.stats import fisher_exact
import numpy as np

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
Histogram = autoclass("miralib.data.ContingencyTable")
Similarity = autoclass("miralib.shannon.Similarity")
PValue = autoclass("miralib.shannon.PValue")

def getContingency(slice, proj):
    table = slice.getContingencyTable(proj)
    if not table.empty():
        rows = []
        for r in range(0, table.rowCount):
            row = table.getRow(r)
            if 0 in row: return None
            rows.append(row)
        return np.array(rows)
    else: 
        return None

Log.init()

# inputFile = "./data_nhanes/config.mira";
inputFile = "./data_lassa/config.mira";

preferences = Preferences()
project = Project(inputFile, preferences)
ranges = DataRanges();
data = DataSet(project);

print "Total number of data points:", data.getRowCount(ranges)
age = data.getVariableByAlias("Age at admission")
# age = data.getVariableByAlias("Age at Screening Adjudicated - Recode")
adults = age.createRange(18, 50)
ranges.update(age, adults)
print "Number of data points matching ranges:", data.getRowCount(ranges)

print "Total number of variables", data.getColumnCount()

data.removeColumns(data.getGroup("GWAS"))
data.removeColumns(data.getGroup("Treatment"))
data.removeColumns(data.getTable("Maximum Values of Lab Results"))
data.removeColumns(data.getTable("Last Day of Lab Results"))

# data.removeColumns(data.getGroup("Examination"))

count = data.getColumnCount()
output = [""] * (count + 1)
print "Number of selected variables", count

t0 = time.time()
print "*************************************"
total = 0
diff = 0
for i in range(0, count):
    vari = data.getColumn(i)
    if vari.categorical():
#     if True:
       print vari.getAlias()
       for j in range(0, count):
           varj = data.getColumn(j)
#            if True:
           if varj.categorical():
               slice = data.getSlice(vari, varj, ranges)
               if project.missingThreshold() <= slice.missing: continue
               obs = getContingency(slice, project)
               if obs == None: continue
               if vari.getCount() == 2 and varj.getCount() == 2:
                   odds, p = fisher_exact(obs)
               else:    
                   chi2, p, dof, ex = chi2_contingency(obs, correction=False)
               score = Similarity.calculate(slice, project.pvalue(), project)
               m, p2 = PValue.calculate(slice, project)
               chi2_res = p < project.pvalue()
               simil_res = p2 < project.pvalue()
               total += 1
               if chi2_res != simil_res: 
                   mark = "<----"
                   diff += 1
               else: mark = ""
               print vari.getAlias(), varj.getAlias(), p, p2, chi2_res, simil_res, vari.getCount(), varj.getCount(), mark
t1 = time.time()

print "differences:", diff, "/" , total, "=",(100.0*diff/total), "%"
print "time:",t1-t0
