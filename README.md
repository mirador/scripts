## Calculation scripts

Miralib is the Java library that contains all the data handling and calculation algorithms
used in Mirador. It is possible to run miralib calculations in a Python script by using 
[Jython](http://www.jython.org/). This allows to perform batch operations from the command line.

This repository includes an [stand-alone](https://wiki.python.org/jython/JythonFaq/DistributingJythonScripts) 
Jython jar, which is generated with the following steps:

```bash
cd <JYTHON_FOLDER>
cp jython.jar jythonlib.jar
zip -r jythonlib.jar Lib
mv jythonlib.jar <SCRIPTS_FOLDER>
jar ufm jythonlib.jar manifest-miralib.mf
```

A Python script using miralib can be then run as follows:

```bash
java -jar jythonlib.jar <script> <arguments>
```

## Under testing: PyJNIus

A disadvantage of Jython is Cython-based modules, like numpy, cannot be imported into the Python code.
[PyJNIus](https://github.com/kivy/pyjnius) removes this limitation, as it is Cython based and calls 
the Java code using JNI. However, it has an incompatibility with PApplet in Processing core, 
which is used indirectly used by Miralib due to its dependency on Processing's Table class. Any call
to a PApplet method will hang the script. 
