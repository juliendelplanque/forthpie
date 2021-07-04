\ This file contains words that allow one to manipulate the various format
\ used to represent words in the name dictionary.
\ By convention, an entry is referenced by the address of the meta-data byte.
\ This address is called the name address (na) in the rest of the code.
\
\  1cell  1cell    1byte
\  <--> <--------> <---->
\ +----+----------+------+ - - -
\ | xt | previous | meta |
\ +----+----------+------+ - - -
\                   ^ na is a pointer to the address of this byte
\

: previous_entry ( na - na )
    CELL- @
;

: code_address ( na - xt )
    CELL- CELL- @
;

: extended_name_token_lex ( - n )
    $020
;

: is_extended ( ca - F )
    C@ extended_name_token_lex AND extended_name_token_lex =
;

: meta_data_byte ( ca - value )
    C@
;

\ Default format (format 0) ---------------------------------------------------

: fmt0_name_length ( ca - length )
    meta_data_byte LEXICON_MASK AND
;

: fmt0_name ( ca - addr u-count )
    DUP 1+ SWAP fmt0_name_length
;

: fmt0_>NAME ( ca -- na, F )
    CURRENT
    BEGIN CELL+ @ ?DUP WHILE 2DUP
        BEGIN @ DUP WHILE 2DUP NAME> XOR
        WHILE 1 CELLS -
        REPEAT THEN NIP ?DUP
    UNTIL NIP NIP EXIT THEN 0 NIP
;

\ Format 1 --------------------------------------------------------------------

: fmt1_name_length ( ca - length )
    1+ CELL+ @
;

: fmt1_name ( ca - addr u-count )
    DUP 1+ CELL+ CELL+ SWAP
;

: fmt1_code_end ( ca - addr )
    1+ CELL+ @
;
