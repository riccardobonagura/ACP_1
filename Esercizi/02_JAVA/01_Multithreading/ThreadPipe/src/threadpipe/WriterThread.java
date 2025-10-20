package threadpipe;

import java.io.*;

/*
 * WriterThread: legge una stringa da System.in e 
 * fa output sulla pipe
 */

//classe che eredita da Thread
public class WriterThread extends Thread {

	//oggetto 'Stream' generico di comunicazione
	private DataOutputStream dataOut;
	
	//costruttore 
	public WriterThread ( PipedOutputStream pipeOut ){
		dataOut  = new DataOutputStream ( pipeOut );	
	}
	
	
	public void run (){
		
		// BufferedReader: oggetto incaricato della lettura da System.in
		BufferedReader keyboardBuf = new BufferedReader ( new InputStreamReader ( System.in ) );
		String s;
		
		while ( true ){
			try{				
				// lettura stringa
				s = keyboardBuf.readLine();
				// output su pipe
				dataOut.writeUTF(s);
				
			}catch ( IOException e ){
				e.printStackTrace();
			}
		}	
	}
}
