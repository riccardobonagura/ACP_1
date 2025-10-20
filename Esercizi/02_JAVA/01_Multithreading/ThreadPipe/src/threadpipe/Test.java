package threadpipe;

//modulo per la comunicazione inter-thread
import java.io.PipedOutputStream;

public class Test {
	
	public static void main(String[] args)  {
	
		//istanzio un oggetto 'pipe'
		PipedOutputStream pipeOut = new PipedOutputStream();

		//consegno il 'pipe' ai thread che dovranno comunicare
		WriterThread w = new WriterThread (pipeOut);
		ReaderThread r = new ReaderThread (pipeOut);
		
		w.start();
		r.start();
		
		
	}

}
