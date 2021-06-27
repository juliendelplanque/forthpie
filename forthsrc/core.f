\ Arithmetic

: 1+ 1 + ;

: 1- 1 - ;

: [']
    R> DUP CELL+ >R @
;

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

: 0= 0 = ;

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
: :noname HERE 5 , ] ;

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

: is_lowercase_alpha ( c - f )
    \ is the char between a and z code ?
    97 122 WITHIN
;

: char_to_uppercase ( c - c )
    DUP is_lowercase_alpha
    IF
        32 - \ Convert to capital letter
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
    65 90 WITHIN
;

: char_to_lowercase ( c - c )
    DUP is_lowercase_alpha
    IF
        32 + \ Convert to lowercase letter
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
    [ CHAR " ] LITERAL PARSE

    temp_str @
    PACK$
    COUNT
;
