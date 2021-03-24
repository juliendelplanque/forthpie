\ requires ansi_escape_sequences

: colored_test_result_printer ( f - )
    0 = IF
        green_esc ." Passed"
    ELSE
        bold_esc red_esc ." Failed"
    THEN
    reset_esc
;

' colored_test_result_printer 'test_result_printer !
