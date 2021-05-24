: test_assert_true
    true assert-true
; TEST

: test_assert_false
    false assert-false
; TEST

: test_assert_equals
    1 1 assert-equals
; TEST

: test_assert_not_equals
    1 2 assert-not-equals
; TEST

run_tests
