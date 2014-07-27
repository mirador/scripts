/* COPYRIGHT (C) 2014 Fathom Information Design. All Rights Reserved. */

package miracalc;

import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.io.UnsupportedEncodingException;
import java.util.concurrent.Executors;
import java.util.concurrent.ThreadPoolExecutor;

import miralib.data.DataRanges;
import miralib.data.DataSet;
import miralib.data.DataSlice2D;
import miralib.data.Variable;
import miralib.shannon.Similarity;
import miralib.utils.Log;
import miralib.utils.Preferences;
import miralib.utils.Project;

/**
 * Simple command line application to run Mirador-related calculations.
 *
 */

public class miracalc {
  static public String inputFile = "config.mira";
  static public String outputFile = "network.csv";
  
  static Preferences preferences;
  static Project project;
  static DataSet dataset;
  static DataRanges ranges;
  static float[][] scores;
  
  public static void init(String args[]) {
    Log.init();
    
    // Load preferences
    try {
      preferences = new Preferences();
    } catch (IOException e) {
      e.printStackTrace();
      System.exit(0);
    }
    
    if (0 < args.length) {
      if (args.length == 1) {
        inputFile = args[0];
      } else {
        for (int i = 0; i < args.length; i++) {
          if (args[i].equals("-in") && i + 1 < args.length) {
            inputFile = args[i + 1];
          } else if (args[i].equals("-out") && i + 1 < args.length) {
            outputFile = args[i + 1];
          } else if (args[i].equals("-miss") && i + 1 < args.length) {
            preferences.missingString = args[i + 1];
          } else if (args[i].equals("-mist") && i + 1 < args.length) {
            preferences.missingThreshold = Project.stringToMissing(args[i + 1]); 
          } else if (args[i].equals("-pval") && i + 1 < args.length) {
            preferences.pValue = Project.stringToPValue(args[i + 1]);
          } else if (args[i].equals("-algo") && i + 1 < args.length) {
            preferences.depTest = Similarity.stringToAlgorithm(args[i + 1]);
          } else if (args[i].equals("-surr") && i + 1 < args.length) {
            preferences.surrCount = Integer.parseInt(args[i + 1]);
          } else if (args[i].equals("-cthr") && i + 1 < args.length) {
            preferences.threshold = Float.parseFloat(args[i + 1]);
          }
        }        
      }
    }
    
    // Load project
    try {
      project = new Project(inputFile, preferences);
    } catch (IOException e) {
      e.printStackTrace();
      System.exit(0);
    }
    
    // Load data
    dataset = new DataSet(project);
    ranges = new DataRanges();
  }
  
  public static void run() {    
    int count = dataset.getVariableCount();
    String[] output = new String[count + 1];
    
    System.out.println("Calculating correlation matrix...");
    
    ThreadPoolExecutor pool;
    int proc = Runtime.getRuntime().availableProcessors();
    pool = (ThreadPoolExecutor)Executors.newFixedThreadPool(proc);
        
    scores = new float[count][count];    
    for (int i = 0; i < count; i++) {
      final int row = i;
      for (int j = i; j < count; j++) {
        final int col = j;
        pool.execute(new Runnable() { 
          public void run() {
            Variable vi = dataset.getVariable(row);
            Variable vj = dataset.getVariable(col);
            DataSlice2D slice = dataset.getSlice(vi, vj, ranges);
            float score = row == col ? 1f : 0f;
            if (slice.missing < project.missingThreshold()) {
              score = Similarity.calculate(slice, project.pvalue(), project);
            }
            scores[row][col] = scores[col][row] = score;     
          }
        });
      }
    }
    pool.shutdown();
    
    int perc0 = 0;
    while (!pool.isTerminated()) {      
      int perc = (int)(100 * (float)pool.getCompletedTaskCount() / (float)pool.getTaskCount());
      if (perc0 + 5 <= perc) {
        System.out.println("  " + perc + "% completed...");
        perc0 = perc;
      }
      Thread.yield();      
    }        
    System.out.println("Done.");
    
    String header = "";
    for (int i = 0; i < count; i++) {
      Variable vi = dataset.getVariable(i);
      String vname = vi.getAlias().replace('"', '\'');
      header += ";\"" + vname + "\"";
    }
    output[0] = header;
    
    for (int i = 0; i < count; i++) {
      Variable vi = dataset.getVariable(i);
      String vname = vi.getAlias().replace('"', '\'');
      String line = "\"" + vname + "\"" ;
      for (int j = 0; j < count; j++) {
        line += ";" + scores[i][j];
      }
      output[1 + i] = line;
    }
        
    File file = new File(outputFile);
    FileOutputStream fos = null;
    try {
      fos = new FileOutputStream(file);
    } catch (FileNotFoundException e) {
      e.printStackTrace();
      System.exit(1);
    }
    
    BufferedOutputStream bos = new BufferedOutputStream(fos, 8192);
    OutputStreamWriter osw = null;
    try {
      osw = new OutputStreamWriter(bos, "UTF-8");
    } catch (UnsupportedEncodingException e) {
      e.printStackTrace();
      System.exit(1);
    }
    PrintWriter writer = new PrintWriter(osw);
    
    for (int i = 0; i < output.length; i++) {
      writer.println(output[i]);
    }
    writer.flush();
    writer.close();
    
    System.out.println("Saved to " + outputFile);
  }
  
  public static void main(String args[]) {
    init(args);
    run();
  }  
}