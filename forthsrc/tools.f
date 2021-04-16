: _TYPE ( b u -- ) FOR AFT COUNT >CHAR EMIT THEN NEXT DROP ;

: dm+ ( b u -- b )
  OVER 4 U.R SPACE FOR AFT COUNT 3 U.R THEN NEXT ;

: .S ( -- ) CR DEPTH FOR AFT R@ PICK . THEN NEXT ."  <tos" ;

: -ROT SWAP >R SWAP R> ;

: 0= 0 = ;

\ : DUMP ( b u -- )
\   BASE @ >R HEX  16 /
\   FOR CR 16 2DUP dm+ -ROT 2 SPACES _TYPE NUF? 0= WHILE
\   NEXT ELSE R> DROP THEN DROP  R> BASE ! ;

: NIP ( w w -- w ) SWAP DROP ;

: !CSP ( -- ) SP@ CSP ! ;

: ?CSP ( -- ) SP@ CSP @ XOR ABORT" stack depth" ;

: >NAME ( ca -- na, F )
  CURRENT
  BEGIN CELL+ @ ?DUP WHILE 2DUP
    BEGIN @ DUP WHILE 2DUP NAME> XOR
    WHILE 1 CELLS -
    REPEAT      THEN NIP ?DUP
  UNTIL NIP NIP EXIT THEN 0 NIP ;

: .ID ( na -- )
  ?DUP IF COUNT LEXICON_MASK AND TYPE EXIT THEN ." {noName}" ;

: SEE ( -- ; <string> )
 ' CR
 BEGIN CELL+ DUP @ DUP
   IF >NAME THEN ?DUP
    IF SPACE .ID ELSE DUP @ U. THEN 1
 UNTIL DROP ;

: WORDS ( -- )
  CR  CONTEXT @
  BEGIN @ ?DUP
  WHILE DUP SPACE .ID 1 CELLS -
  REPEAT ;
