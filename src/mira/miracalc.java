/* COPYRIGHT (C) 2014 Fathom Information Design. All Rights Reserved. */

package mira;

import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.io.UnsupportedEncodingException;

import mira.data.DataRanges;
import mira.data.DataSet;
import mira.data.DataSlice2D;
import mira.data.Variable;
import mira.shannon.Similarity;
import mira.utils.Log;
import mira.utils.Preferences;
import mira.utils.Project;

/**
 * Simple command line application to run Mirador-related calculations.
 *
 * @author Andres Colubri
 */


public class miracalc {
  static public String inputFile = "config.mira";
  static public String outputFile = "network.csv";
  
  static Preferences preferences;
  static Project project;
  static DataSet dataset;
  static DataRanges ranges;
  
  public static void init(String args[]) {
    Log.init();
    
    // Load preferences
    try {
      preferences = new Preferences(".mirador");
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
    float[][] scores = new float[count][count];     
    for (int i = 0; i < count; i++) {
      Variable vi = dataset.getVariable(i);
      for (int j = i; j < count; j++) {
        Variable vj = dataset.getVariable(j);
        DataSlice2D slice = dataset.getSlice(vi, vj, ranges);
        float score = i == j ? 1f : 0f;
        if (slice.missing < 0.2f) {
          score = Similarity.calculate(slice, 0.05f, project);
        }
        scores[i][j] = scores[j][i] = score;        
      }
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
  
//protected ThreadPoolExecutor scorematPool;

//public void calculateScoreMatrix() {
//if (!sorted()) return;
//
//cancelMatrixCalculation();    
//
//int proc = Runtime.getRuntime().availableProcessors();
//scorematPool = (ThreadPoolExecutor)Executors.newFixedThreadPool(PApplet.min(1, proc - 1));
//
//int size = 0;
//for (int i = 0; i < columns.size(); i++) {
//if (0 < scores.get(i)) size++;
//else break;
//}
//if (!sortVar.column) size++; 
//scoreMatrix = new float[size][size];
//for (int i = 0; i < size; i++) {
//Arrays.fill(scoreMatrix[i], -1);  
//}
//
//size = scoreMatrix.length;
//for (int i = 0; i < size; i++) {
//final int col = i;
//for (int j = i + 1; j < size; j++) {        
//  final int row = j;
//  scorematPool.execute(new Runnable() {
//    public void run() {
//      Variable vx = getScoreMatrixCol(col);            
//      Variable vy = getScoreMatrixRow(row);
//      DataSlice2D slice = getSlice(vx, vy, sortRanges);
//      float score = 0f;
//      if (slice.missing < sortMissingThreshold) {
//        score = Similarity.calculate(slice, sortPValue, project);
//      }            
//      scoreMatrix[col][row] = scoreMatrix[row][col] = score;
//    }
//  });        
//}      
//}
//scorematPool.shutdown();
//}
//
//public float matrixProgress() { 
//if (scorematPool != null && !scorematPool.isTerminated()) {
//return (float)scorematPool.getCompletedTaskCount() / (scorematPool.getTaskCount());
//} else {
//return 1;
//}
//} 
//
//public boolean matrixCompleted() {
//return scorematPool != null && scorematPool.isTerminated();
//}
//
//public void cancelMatrixCalculation() {
//if (scorematPool != null && !scorematPool.isTerminated()) {
//Log.message("Suspending score matrix calculation...");
//scorematPool.shutdownNow();
//while (!scorematPool.isTerminated()) {
//  Thread.yield();
//}      
//Log.message("Done.");
//}
//}
//
//public boolean calculatingMatrix() {
//return scorematPool != null && !scorematPool.isTerminated();
//}

//public Variable getScoreMatrixRow(int i) {
//return getScoreMatrixCol(i);
//}
//
//public Variable getScoreMatrixCol(int i) {
//if (sortVar.column) {
//return getColumn(i);
//} else {
//return i == 0 ? sortVar : getColumn(i + 1);
//}    
//} 
//
//public int getScoreMatrixSize() {
//return scoreMatrix.length;    
//}
  
//public float getScore(int i, int j) {
//return scoreMatrix[i][j];
//}
  
}


