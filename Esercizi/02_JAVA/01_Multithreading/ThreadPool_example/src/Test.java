import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class Test {
 
    public static void main(String[] args) {
     
        //executor è come il thread che prende in carico la funzione in Python, 
        //in questo caso la claase Runnable è la funzione ed ExecutorService è il thread.
        ExecutorService executor = Executors.newFixedThreadPool(5);
        
     for (int i = 0; i < 10; i++) {
            Runnable worker = new WorkerThread("" + i);
            // target = worker
            executor.execute(worker);
          }
        //ogni thread che ritorna si chiude
        executor.shutdown();
        while (!executor.isTerminated()) {
        }
        System.out.println("Finished all threads");
    }
 
}
