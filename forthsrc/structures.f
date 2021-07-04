: CELL
    CELLS
;

: LITERAL_STRING ( n - n )
    1+
;

: field
    CREATE OVER , +
    DOES> @ +
;

: with-allot ( n - n )
    CREATE DUP ,
    DOES> @ ALLOT HERE
;

: struct 0 ;

: end-struct ( n - )
    DROP
;
