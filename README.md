## Calculation scripts

Miralib is the Java library that contains all the data handling and calculation algorithms
used in Mirador. It is possible to run miralib calculations in a Python script by using 
[PyJNIus](https://github.com/kivy/pyjnius). This allows to perform batch operations from the 
command line, in combination with any standard Python library (numpy, matplotlib).

The only requirement to run miralib scripts is to install the PyJNIus package, for example 
using pip:

```bash
pip install pyjnius
```

Installation of PyJNIus on Windows is slightly more involved, please see this brief wiki
entry for more details.

One PyJNIus is installet, then the miralib classes can be accessed from Python as follows:

```
os.environ['CLASSPATH'] = "../miralib/dist/*"

from jnius import autoclass
Preferences = autoclass("miralib.utils.Preferences")
Project = autoclass("miralib.utils.Project")
DataRanges = autoclass("miralib.data.DataRanges")
DataSet = autoclass("miralib.data.DataSet")
```

The os.environ['CLASSPATH'] assignment is important so PyJNIus is able to locate the jar files 
containing the classes. The two dependencies of miralib, common-math3 and joda-time, need to
be in the classpath folder as well.
