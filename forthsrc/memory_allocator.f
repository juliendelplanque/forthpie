
\ Block manipulation words.

VARIABLE HEAPSTART

$4001 HEAPSTART ! \ Modify to fit memory layout.

: memblock-size ( addr - n ) @ ;

: memblock-next ( addr - addr ) CELL+ @ ;

: memblock-used ( addr - f ) CELL+ CELL+ @ ;

: memblock-data ( addr - addr ) CELL+ CELL+ CELL+ ;

: memblock-find ( n addr - addr f | f )
    WHILE
        DUP 0 =
    BEGIN
        2DUP memblock-size =
        IF SWAP DROP TRUE EXIT
        THEN
    REPEAT
    2DROP FALSE
;

\ Allocator public interface.

: allocate (u - a-addr wior) ; \ TODO

: free (a-addr - wior) ; \ TODO

; resize (a-addr1 u - a-addr2 wior) ; \ TODO