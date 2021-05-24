: test_mblock_size@!
    $4001 mblock_size@ 0 assert-equals
    42 $4001 mblock_size!
    $4001 mblock_size@ 42 assert-equals
; TEST

: test_mblock_is_free@!
    $4001 mblock_is_free@ assert-false
    ." foo"
    true $4001 mblock_is_free!
    ." bar"
    $4001 mblock_is_free@ assert-true
; TEST

\ run_tests
