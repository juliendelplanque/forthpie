\ Forth Compiler

: COMPILE_ONLY_bit
    64
;

: COMPILE_ONLY
    COMPILE_ONLY_bit LAST @ @ OR
    LAST @ !
;

: IMMEDIATE_bit
    128
;

: IMMEDIATE
    IMMEDIATE_bit LAST @ @ OR
    LAST @ !
;

: POSTPONE
    ' ,
; IMMEDIATE

: [CHAR]
    CHAR POSTPONE LITERAL
; IMMEDIATE COMPILE_ONLY

: [']
    R> DUP CELL+ >R @
; COMPILE_ONLY

\ Arithmetic

: 1+ 1 + ;

: 1- 1 - ;

\ Arithmetic tests

: x_or_eq_macro ( xt - )
    COMPILE 2DUP
    ,
    COMPILE >R
    COMPILE =
    COMPILE R>
    COMPILE OR
; IMMEDIATE

: <=
    [ ' < ] x_or_eq_macro
;

: >
    <= NOT
;

: >=
    [ ' > ] x_or_eq_macro
;

: <>
    = NOT
;

: 0= 0 = ;

: 0<>
    0 <>
;

: U<=
    [ ' U< ] x_or_eq_macro
;

: U>
    U<= NOT
;

: U>=
    [ ' U> ] x_or_eq_macro
;

\ Stack manipulation

: NIP ( w1 w2 -- w2 )
    SWAP DROP
;

: -ROT SWAP >R SWAP R> ;

\ Anonymous word
: :noname
    HERE ['] doLIST @ , ]
;

\ Memory manipulation

: cell_map ( addr n xt - )
    SWAP \ addr xt n
    FOR
        2DUP EXECUTE
        SWAP CELL+ SWAP
    NEXT
    2DROP
;

: char_map ( addr n xt - )
    SWAP \ addr xt n
    FOR
        2DUP EXECUTE
        SWAP 1+ SWAP
    NEXT
    2DROP
;

\ Strings support

VARIABLE temp_str

: lower_upper_diff
    COMPILE doLIT
    [ CHAR a CHAR A - ] LITERAL ,
; IMMEDIATE COMPILE_ONLY

: is_lowercase_alpha ( c - f )
    \ is the char between a and z code ?
    [CHAR] a [CHAR] z WITHIN
;

: char_to_uppercase ( c - c )
    DUP is_lowercase_alpha
    IF
        lower_upper_diff - \ Convert to capital letter
    THEN
;

: char@_to_uppercase ( addr - )
    DUP C@ \ addr c
    char_to_uppercase \ addr C
    SWAP C!
;

: to_uppercase ( addr n - )
    \ MODIFIES the string provided as parameter to be uppercase.
    ['] char@_to_uppercase char_map
;

: is_uppercase_alpha ( c - f )
    \ is the char between A and Z code ?
    [CHAR] A [CHAR] Z WITHIN
;

: char_to_lowercase ( c - c )
    DUP is_uppercase_alpha
    IF
        lower_upper_diff + \ Convert to lowercase letter
    THEN
;

: char@_to_lowercase ( addr - )
    DUP C@ \ addr c
    char_to_lowercase \ addr C
    SWAP C!
;

: to_lowercase ( addr n - )
    \ MODIFIES the string provided as parameter to be uppercase.
    ['] char@_to_lowercase char_map
;

0 temp_str !

: allocate_temp_str_if_needed
    temp_str @ 0=
    IF
        256 ALLOT HERE temp_str !
    THEN
;

: s"
    allocate_temp_str_if_needed
    [CHAR] " PARSE

    temp_str @
    PACK$
    COUNT
;

\ DOES>

: shift_cell_right ( addr - )
    \ Move the value of the cell at addr to the cell at addr+1 in memory.
    DUP @ SWAP CELL+ !
;

: last_cell_address ( addr cells-count - end-address )
    CELLS +
;

: shift_cells_right ( addr cells-count - )
    \ Move the values of the cells-count cells starting at addr to the next
    \ cell in memory.
    SWAP DUP ROT \ addr addr cells-count
    last_cell_address \ addr end-addr
    BEGIN
        2DUP U<=
    WHILE
        DUP shift_cell_right
        CELL-
    REPEAT
    2DROP
;

: shift_cells_right_twice ( addr cells-count - )
    \ Move the values of the cells-count cells starting at addr to the next
    \ cell in memory. Then move the values of the cells-count cells starting at
    \ addr+CELL_SIZE to the next cell in memory.
    2DUP
    shift_cells_right
    SWAP CELL+ SWAP
    shift_cells_right
;

: LASTXT
    LAST @ NAME>
;

: doDOES> ( xt - )
    R> DUP
    @ >R
    CELL+
;

: last_word_xt_len
    \ Computes the number of cells required by the last word xt.
    HERE LASTXT - \ size in byte
    1 CELLS / \ size in cells
;

: DOES>
    LASTXT CELL+ CELL+ last_word_xt_len shift_cells_right
    HERE 2 CELLS + CP !
    ['] doDOES> LASTXT CELL+ !
    R> LASTXT CELL+ CELL+ !
; COMPILE_ONLY
