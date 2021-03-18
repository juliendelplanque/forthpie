: true ( - f ) -1 ;

: false ( - f ) 0 ;

: assert-true
    NOT \ If TOS is false, raise exception.
    ABORT" Assertion error"
;

: assert-false
    NOT assert-true
;

: assert-equals
    = assert-true
;

: assert-not-equals
    = assert-false
;

: should_raise_any
    CATCH
    0 assert-not-equals
;

: sould_not_raise
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

: print_test_name
    ( na - )
    \ Prints the name of the test to run.
    DUP
    C@ $1F AND \ name-length
    SWAP 1 + \ name-length str-addr
    SWAP
    TYPE
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
        CATCH
        0 =
        IF ." Passed"
        ELSE
            ." Failed"
        THEN
    REPEAT
;
