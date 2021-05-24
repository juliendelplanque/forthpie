\ -----------------------------------------------------------------------------
\ Memory block manipulation words
\ -----------------------------------------------------------------------------

: mblock_size@ ( addr - n )
    \ Reads the size of the memory block (header included).
    @
;

: mblock_size! ( n - )
    !
;

: mblock_is_free ( addr - addr )
    CELL+
;

: mblock_is_free@ ( addr - f )
    \ Determinate if the memory block is free or not and put a flag on the stack.
    mblock_is_free @
;

: mblock_is_free! ( f addr - )
    mblock_is_free !
;

: mblock_next ( addr - addr )
    CELL+ CELL+
;

: mblock_next@ ( addr - addr )
    \ Put address of next memory block on the stack.
    mblock_next @
;

: mblock_next@ ( addr - )
    \ Put address of next memory block on the stack.
    mblock_next @
;

: mblock_data ( addr - addr )
    \ Determinates the address of first bytes stored by this memory block.
    CELL+ CELL+ CELL+
;

: mblock_data_size ( addr - n )
    \ Returns the size of the data embedded by the memory block.
    DUP mblock_data SWAP -
;

: mblock_can_be_used ( n addr - f )
    mblock_size@ SWAP U<
;

: mblock_has_next ( addr - f )
    mblock_next 0 = NOT
;

\ : continue_mblock_search? ( n addr - f )
\     2DUP
\     mblock_can_be_used IF \ Guard clause, if block can be used, search can stop.
\         FALSE EXIT
\     THEN
\     SWAP DROP \ n is not needed.
\     mblock_has_next
\ ;

\ : find-mblock ( n - addr f | f )
\     heap_start@ \ n addr
\     BEGIN
\         2DUP
\         continue_mblock_search?
\     WHILE
\         mblock_next@
\     END
\     2DUP mblock_can_be_used
\     IF
\         SWAP DROP TRUE EXIT
\     THEN
\         2DROP FALSE
\ ;

\ -----------------------------------------------------------------------------
\ Public interface for the allocator.
\ -----------------------------------------------------------------------------

\ : block_allocate ( n - addr f )
\     \ First, search for a free block with enough space to fit n bytes.
\     DUP find-mblock
\     IF
\         TRUE EXIT
\     THEN
\     3 CELLS U+ bump_allocate
\     NOT IF
\         $" Bump allocation failed" THROW
\     THEN
\     \ TODO: setup block metadata and link previous block to this new block
\     \ TODO: also updated last block pointer variable
\ ;

\ : block_free ( addr - f )
\     TRUE mblock_is_free!
\ ;

\ : block_resize ( addr1 u - addr2 f | f )
\ ;
