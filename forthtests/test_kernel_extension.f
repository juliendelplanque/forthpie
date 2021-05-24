: clear_testing_memory
    0 $4001 !
    0 $4003 !
    0 $4005 !
    0 $4007 !
    0 $4009 !
    0 $4011 !
    0 $4013 !
    0 $4015 !
;

: test_shift_cell_right
    clear_testing_memory
    42 $4001 !
    43 $4003 !

    $4005 @ 0 assert_equals

    $4001 shift_cell_right

    $4001 @ 42 assert_equals
    $4003 @ 42 assert_equals
    $4005 @ 0 assert_equals
; TEST

: test_1-
    42 1- 41 assert_equals
    0 1- -1 assert_equals
    1 1- 0 assert_equals
; TEST

: test_U<=
    1 1 U<= assert_true
    1 2 U<= assert_true
    2 1 U<= assert_false
    0 -1 U<= assert_true
    $3FFF $4001 U<= assert_true
    $4001 $4001 U<= assert_true
    $3FFF $3FFF U<= assert_true
    $4001 $3FFF U<= assert_false
; TEST

: test_last_cell_address
    $4001 1 last_cell_address $4003 assert_equals
    $4001 0 last_cell_address $4001 assert_equals
    $4001 4 last_cell_address $4009 assert_equals
; TEST

: test_shift_cells_right_odd
    clear_testing_memory
    42 $4001 !
    43 $4003 !
    44 $4005 !

    $4007 @ 0 assert_equals
    $4009 @ 0 assert_equals

    $4001 3 shift_cells_right

    $4003 @ 42 assert_equals
    $4005 @ 43 assert_equals
    $4007 @ 44 assert_equals
    $4009 @ 0 assert_equals
; TEST

: test_shift_cells_right_even
    clear_testing_memory
    42 $4001 !
    43 $4003 !
    0 $4005 !

    $4005 @ 0 assert_equals
    $4007 @ 0 assert_equals

    $4001 2 shift_cells_right

    $4003 @ 42 assert_equals
    $4005 @ 43 assert_equals
    $4007 @ 0 assert_equals
    $4009 @ 0 assert_equals
; TEST

: test_shift_cells_right_twice
    clear_testing_memory
    42 $4001 !
    43 $4003 !
    44 $4005 !

    $4007 @ 0 assert_equals
    $4009 @ 0 assert_equals
    $4011 @ 0 assert_equals

    $4001 3 shift_cells_right_twice

    $4005 @ 42 assert_equals
    $4007 @ 43 assert_equals
    $4009 @ 44 assert_equals
    $4011 @ 0 assert_equals
; TEST

: test_replace_doVAR_by_doDOES>
    clear_testing_memory
    5 $4001 !
    [ ' doVAR ] LITERAL $4003 !
    $4001 replace_doVAR_by_doDOES>
    $4003 @ [ ' doDOES> ] LITERAL assert_equals
; TEST

: replace_doVAR_by_doDOES>_f
    clear_testing_memory
    5 $4001 !
    [ ' DUP ] LITERAL $4003 !
    fail \ TODO
    \ $4001 [ ' replace_doVAR_by_doDOES> ] LITERAL should_raise_any
; TEST

run_tests
