: :noname HERE 5 , ] ;

: shift_cell_right ( addr - )
    \ Move the value of the cell at addr to the cell at addr+1 in memory.
    DUP @ SWAP CELL+ !
;

: 1- ( n - n-1 )
    \ Substract 1 from top of stack.
    1 -
;

: U<=
    2DUP U< >R = R> OR
;

: U>
    U<= NOT
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
    R>
    CELL+ CELL+
;

: replace_doVAR_by_doDOES> ( xt - )
    \ Overwrite doVAR previously compiled by CREATE with doDOES>
    \ for xt provided on the stack.
    [ ' doDOES> ] LITERAL
    SWAP \ doDoes>_xt xt
    CELL+
    DUP @ [ ' doVAR ] LITERAL = NOT IF
        ABORT" Second bytecode of the xt provided is not doVAR."
    THEN
    !
;

: last_word_xt_len
    \ Computes the number of cells required by the last word xt.
    LASTXT CP @ - \ size in byte
    1 CELLS / \ size in cells
;

: DOES>
    replace_doVAR_by_doDOES>
    \ Inject branch top-of-return-stack between doDOES> and the cells allocated
    \ after CREATE.
    LASTXT CELL+ CELL+ \ Compute address of first cell to shift
    DUP DUP
    CP @ - 1 CELLS / \ Compute number of cells to shift
    shift_cells_right_twice
    HERE 2 CELLS + CP ! \ Update CP
    [ ' branch ] LITERAL LASTXT CELL+ !
    R> LASTXT CELL+ CELL+ !
;
