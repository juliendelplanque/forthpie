: esc
    0 EMIT
    $1B EMIT
;

: reset_esc
    esc
    ." [0m"
;

: bold_esc
    esc
    ." [1m"
;

: color_esc
    esc
    ." [3"
    0 .R
    ." m"
;

: black_esc
    0 color_esc
;

: red_esc
    1 color_esc
;

: green_esc
    2 color_esc
;

: yellow_esc
    3 color_esc
;

: blue_esc
    4 color_esc
;

: magenta_esc
    5 color_esc
;

: cyan_esc
    6 color_esc
;

: white_esc
    7 esc
;
