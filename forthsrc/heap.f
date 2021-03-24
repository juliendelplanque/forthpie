VARIABLE heap_start

: heap_start@
    heap_start @
;

: heap_start!
    heap_start !
;

$4001 heap_start!

VARIABLE heap_direction

: heap_direction@
    heap_direction @
;

: heap_direction!
    heap_direction !
;

1 heap_direction!

VARIABLE heap_top

: heap_top@
    \ Get the address of top of heap.
    heap_top @
;

: heap_top! ( addr - )
    \ Set the address for top of heap.
    heap_top !
;

: reset_heap
    heap_start@ heap_top!
;

reset_heap

\ -----------------------------------------------------------------------------
\ Simple bump allocator
\ -----------------------------------------------------------------------------

: bump_allocate ( n - addr f )
    heap_top@ SWAP    \ heap-addr, n
    heap_direction@ * \ Change sign of n according to direction
    heap_top@ +       \ Compute the new address
    heap_top!         \ Store new heap address.
    -1                \ true flag to say alloc was ok.
;

: bump_free ( addr - f )
    \ One can not free memory with a bump allocator.
    0
;

: bump_resize ( addr1 u - addr2 f | f )
    \ One can not resize with a bump allocator.
    0
;

\ -----------------------------------------------------------------------------
\ Public interface for the allocator.
\ -----------------------------------------------------------------------------

VARIABLE 'allocate
VARIABLE 'free
VARIABLE 'resize

: 'allocate!
    'allocate !
;

' bump_allocate 'allocate!

' bump_free 'free !
' bump_resize 'resize !

: allocate
    'allocate @EXECUTE
;

: free
    'free @EXECUTE
;

: resize
    'resize @EXECUTE
;
