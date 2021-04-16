: true ( - f ) -1 ;

: false ( - f ) 0 ;

: assert_true
    NOT \ If TOS is false, raise exception.
    ABORT" Assertion error"
;

: assert-true \ deprecated
    assert_true
;

: assert_false
    NOT assert-true
;

: assert-false  \ deprecated
    assert_false
;

: assert_equals
    = assert_true
;

: assert-equals \ deprecated
    assert_equals
;

: assert_not_equals
    = assert_false
;

: assert-not-equals \ deprecated
    assert_not_equals
;

: should_raise_any
    CATCH
    0 assert-not-equals
;

: should_not_raise
    CATCH
    0 assert-equals
;

: test_lex
    $020
;

: TEST
    \ Make the last compiled word a test word.
    test_lex LAST @ @ OR LAST @ !
;

: is_test_word ( na - f )
    C@ test_lex AND test_lex =
;

: next_test ( na - na f | f )
    CELL- @
    BEGIN
        DUP
        is_test_word NOT
    WHILE
        CELL- @
        DUP 0 = \ end of linked list
        IF
            false EXIT
        THEN
    REPEAT
    true
;

VARIABLE 'test_name_printer

: default_test_name_printer
    ( na - )
    \ Prints the name of the test to run.
    DUP
    C@ $1F AND \ name-length
    SWAP 1 + \ name-length str-addr
    SWAP
    TYPE
;

' default_test_name_printer 'test_name_printer !

: print_test_name
    'test_name_printer @EXECUTE
;

VARIABLE 'test_result_printer

: default_test_result_printer ( f - )
    0 = IF
        ." Passed"
    ELSE
        ." Failed"
    THEN
;

' default_test_result_printer 'test_result_printer !

: print_test_result
    'test_result_printer @EXECUTE
;

: run_tests ( - )
    \ Runs all the tests reachable starting from LAST.
    LAST CELL+
    BEGIN
        next_test true =
    WHILE
        \ Print test name.
        CR DUP print_test_name SPACE
        \ Get execution token of test.
        DUP NAME> \ na ca
        CATCH \ na exception_occured?
        print_test_result \ na
    REPEAT
;
