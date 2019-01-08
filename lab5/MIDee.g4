grammar MIDee;

@header {
package cas.cs4tb3.parser;

import java.util.*;
import cas.cs4tb3.MIDIHelper;
}

@members {
/**
 * names: James You, Zichen Jiang
 */

private MIDIHelper midi = new MIDIHelper();

private long tick = 0;
private int tempo = 120;

private String[] notes = {"c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "b"};
private List notesmap = Arrays.asList(notes);

private ArrayList<Integer> notesList = new ArrayList<Integer>();

private int noteToNumber(String name, int octave) {
  if (octave > 10) {
    System.err.println("Octave exceeds max limit, rounding down...");
    octave = 10;
  }
  if (octave < 0) {
    System.err.println("Octave is below min limit, rounding up...");
    octave = 10;
  }
  return notesmap.indexOf(name) + octave*12;
}

}

//Start rule
program
    :   instrumentBlock* EOF {midi.saveSequence();}
    ;

scopeHeader
    :   (INSTRUMENT ('@' NUMBER)?) {
            int t = 120;
            int instrument = midi.getInstrumentId($INSTRUMENT.text);
            if (instrument == -1)
                throw new RuntimeException("Invalid Instrument Name");
            if ($NUMBER != null) {
                t = Integer.parseInt($NUMBER.text);
                if (t <= 0)
                    throw new RuntimeException("Invalid Tempo");
            }
            midi.setInstrument(instrument, tick);
            if (t != tempo) {
                midi.setTempo(t, tick);
                tempo = t;
            }
        }
    ;

instrumentBlock
    :   scopeHeader '{' (playStatement | waitStatement)* '}'
    ;

playStatement
    :   'play' note {notesList.add($note.number);} (',' note {notesList.add($note.number);} )* 'for' duration ';' {
            long duration = midi.getDurationInTicks(Double.parseDouble($duration.text));
            for (Integer note_: notesList) {
                midi.play(note_, tick, tick+duration);
            }
            tick += duration;
            notesList.clear();
        }
    ;

waitStatement
    :   'wait' 'for' duration ';' {
            long duration = midi.getDurationInTicks(Double.parseDouble($duration.text));
            tick += duration;
        }
    ;

duration
    :   NUMBER
    |   FLOATING_NUMBER
    ;

note returns [int number]
    :   (NOTENAME symbol=('#' | '_')? NUMBER) {
            String name = "";
            name = $NOTENAME.text;
            if ($symbol != null)
              if ($symbol.text.equals("#"))
                name += $symbol.text;
            int octave = Integer.parseInt($NUMBER.text);
            $number = noteToNumber(name, octave);
        }
    ;

NOTENAME
    :   [a-g]
    ;

NUMBER
    :   [0-9]+
    ;

FLOATING_NUMBER
    :   [0-9]+'.'[0-9]+
    ;

INSTRUMENT
    : [a-z]+
    ;

WS: [ \n\t\r]+ -> skip;
