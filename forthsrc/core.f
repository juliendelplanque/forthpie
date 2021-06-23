\ Arithmetic

: 1+ 1 + ;

: 1- 1 - ;

\ Arithmetic tests

: x_or_eq_macro
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

\ Setting forthpie boot message

: forthpie_hi
    !IO CR
    ." Welcome to forthpie. Press BYE to quit."
;

' forthpie_hi 'BOOT !
