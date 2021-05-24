: previous_name
    CELL- CELL- @
;

: name_length ( ca - n )
    C@ LEXICON_MASK AND
;

: extended_name_token_lex ( - n )
    $020
;

: is_extended ( ca - F )
    C@ extended_name_token_lex AND extended_name_token_lex =
;

: meta_data_byte_address ( ca - addr )
    DUP is_extended NOT
    IF
        ABORT" Not an extended word!"
    THEN
    name_length ALIGNED
;

: meta_data_byte ( ca - value )
    meta_data_byte_address C@
;

\ Format 1 --------------------------------------------------------------------

: ensure_format_1 ( ca - )
    meta_data_byte 1 = NOT
    IF
        ABORT" Word format 1 is expected."
    THEN
;

: last_xt_address ( ca - addr )
    DUP ensure_format_1
    meta_data_byte_address CELL+ @
;

\ -----------------------------------------------------------------------------
