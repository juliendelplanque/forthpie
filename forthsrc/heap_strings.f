\ requires heap.f

: h" ( - addr ; <string> )
    \ Reads a string from the terminal input buffer up to next " character,
    \ allocate the heap and stores it on the heap.
    \ Returns the address of the allocated string on the heap.
    [ CHAR " ] LITERAL PARSE
    255 allocate
    NOT IF
        abort" Heap exhausted."
    THEN
    PACK$
;
