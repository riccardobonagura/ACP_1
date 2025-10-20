package threadpipe;

import java.io.*;

/*
 * ReaderThread: legge il contenuto 
 * della pipe
 */


public class ReaderThread extends Thread {
	//oggetto per il passaggio
	private DataInputStream dataIn; 
	
	//costruttore
	public ReaderThread ( PipedOutputStream pipeOut ){
		try{ //perchè qui serve il try-catch?
			dataIn = new DataInputStream ( new PipedInputStream ( pipeOut )  ) ;
		}catch ( IOException e ){
			e.printStackTrace();
		}
	}	
	public void run (){
		
		String s;
		
		while ( true ){
			
			try{
				System.out.println ( "						[READER] waiting for new input ... " );
				// input da pipe
				s= dataIn.readUTF() ;
				System.out.println ( "						[READER] input form pipe: " + s );
			}catch ( IOException e ){
				e.printStackTrace();
			}
		}
		
	}

}
