: test_reset_heap
    reset_heap
    heap_start@ heap_top@ assert-equals
; TEST

: test_bump_allocate
    heap_top@ 42 + \ expected new heap top
    heap_top@ \ expected address returned by allocate
    42 bump_allocate
    assert-true
    assert-equals
    heap_top@ assert-equals
; TEST

: test_bump_free
    heap_top@ \ backup heap top address
    bump_free 0 assert-equals
    heap_top@ assert-equals \ ensure heap_top did not change.
; TEST

: test_bump_resize
    heap_top@ \ backup heap top address
    bump_resize 0 assert-equals
    heap_top@ assert-equals \ ensure heap_top did not change.
; TEST

run_tests
BYE
