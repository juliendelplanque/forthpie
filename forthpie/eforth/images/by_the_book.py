from ...model import Image, WordsSet, Primitive, ColonWord, UserVariable, WR, code, L, LR, Byte, Align

def by_the_book_primitives():
    """ Builds and returns a WordsSet that contains EForth primitives as
    described in the book.
    """
    return WordsSet("primitives",
        Primitive("BYE"),
        Primitive("?RX"),
        Primitive("TX!"),
        Primitive("!IO"),
        Primitive("doLIT", compile_only=True),
        Primitive("doLIST", compile_only=True),
        Primitive("EXIT"),
        Primitive("EXECUTE"),
        Primitive("next", compile_only=True),
        Primitive("?branch", compile_only=True),
        Primitive("branch", compile_only=True),
        Primitive("!"),
        Primitive("@"),
        Primitive("C!"),
        Primitive("C@"),
        Primitive("RP@"),
        Primitive("RP!", compile_only=True),
        Primitive("R>"),
        Primitive("R@"),
        Primitive(">R", compile_only=True),
        Primitive("SP@"),
        Primitive("SP!"),
        Primitive("DROP"),
        Primitive("DUP"),
        Primitive("SWAP"),
        Primitive("OVER"),
        Primitive("0<"),
        Primitive("AND"),
        Primitive("OR"),
        Primitive("XOR"),
        Primitive("UM+"),
        Primitive("UM/MOD"),
        # Primitive("DEBUG"),
    )

def by_the_book_system_and_user_variables(start_of_user_area_address, number_of_vocabularies):
    """ Builds and returns a WordsSet that contains EForth words allowing to
    define system and user variables as well as the variables required by
    EForth to run as described in the book.
    """
    return WordsSet("system_and_user_variables",
        ColonWord("doVAR",
            [WR("R>"), (WR("EXIT"))],
            compile_only=True),

        ColonWord("UP",
            [WR("doVAR"), start_of_user_area_address]),
        ColonWord("+",
            WR("UM+", "DROP", "EXIT")),
        ColonWord("doUSER",
            WR("R>", "@", "UP", "@", "+", "EXIT"),
            compile_only=True),
        UserVariable("SP0"),
        UserVariable("RP0"),
        UserVariable("'?KEY"),
        UserVariable("'EMIT"),
        UserVariable("'EXPECT"),
        UserVariable("'TAP"),
        UserVariable("'ECHO"),
        UserVariable("'PROMPT"),
        UserVariable("BASE"),
        UserVariable("tmp", compile_only=True),
        UserVariable("SPAN"),
        UserVariable(">IN"),
        UserVariable("#TIB", cells=2),
        UserVariable("CSP"),
        UserVariable("'EVAL"),
        UserVariable("'NUMBER"),
        UserVariable("HLD"),
        UserVariable("HANDLER"),
        UserVariable("CONTEXT", cells=number_of_vocabularies),
        UserVariable("CURRENT", cells=2),
        UserVariable("CP"),
        UserVariable("NP"),
        UserVariable("LAST"),
        ColonWord("doVOC",
            WR("R>", "CONTEXT", "!", "EXIT"),
            compile_only=True),
        ColonWord("FORTH",
            [WR("doVOC"), 0, 0]
        ),
        requirements=["primitives"]
    )

def by_the_book_common_words():
    """
    """
    return WordsSet("common",
        ColonWord("?DUP",
            [WR("DUP"),
            WR("?branch"), LR("?DUP1"),
            WR("DUP"),
            L("?DUP1"), WR("EXIT")]
        ),
        ColonWord("ROT",
            code(">R SWAP R> SWAP EXIT")
        ),
        ColonWord("2DROP",
            code("DROP DROP EXIT")
        ),
        ColonWord("2DUP",
            code("OVER OVER EXIT")
        ),
        # + is defined in compile_system_and_user_variables() because doUser requires it
        ColonWord("NOT",
            [WR("doLIT"), -1, WR("XOR"), WR("EXIT")
        ]),
        ColonWord("NEGATE",
            [WR("NOT"), WR("doLIT"), 1, WR("+"), WR("EXIT")]
        ),
        ColonWord("DNEGATE",
            [WR("NOT"), WR(">R"), WR("NOT"), WR("doLIT"), 1, WR("UM+"), WR("R>"), WR("+"), WR("EXIT")]
        ),
        ColonWord("D+",
            code(">R SWAP >R UM+ R> R> + + EXIT")
        ),
        ColonWord("-",
            code("NEGATE + EXIT")
        ),
        ColonWord("ABS",
            [WR("DUP"), WR("0<"),
            WR("?branch"), LR("ABS1"),
            WR("NEGATE"), L("ABS1"), WR("EXIT")]
        ),
        requirements=["primitives"]
    )

def by_the_book_comparison_words():
    return WordsSet("comparison",
        ColonWord("=",
            [WR("XOR"),
            WR("?branch"), LR("=1"),
            WR("doLIT"), 0, WR("EXIT"),
        L("=1"), WR("doLIT"), -1, WR("EXIT")]
        ),
        ColonWord("U<",
            [WR("2DUP"), WR("XOR"), WR("0<"),
            WR("?branch"), LR("ULES1"),
            WR("SWAP"), WR("DROP"), WR("0<"), WR("EXIT"),
        L("ULES1"), WR("-"), WR("0<"), WR("EXIT")]
        ),
        ColonWord("<",
            [WR("2DUP"), WR("XOR"), WR("0<"),
            WR("?branch"), LR("<1"),
            WR("DROP"), WR("0<"), WR("EXIT"),
        L("<1"), WR("-"), WR("0<"), WR("EXIT")]
        ),
        ColonWord("MAX",
            [WR("2DUP"), WR("<"),
            WR("?branch"), LR("MAX1"),
            WR("SWAP"),
        L("MAX1"), WR("DROP"), WR("EXIT")]
        ),
        ColonWord("MIN",
            [WR("2DUP"), WR("SWAP"), WR("<"),
            WR("?branch"), LR("MIN1"),
            WR("SWAP"),
        L("MIN1"), WR("DROP"), WR("EXIT")]
        ),
        ColonWord("WITHIN",
            code("OVER - >R - R> U< EXIT")
        ),
        requirements=["primitives"]
    )

def by_the_book_divide_words():
    """
    """
    return WordsSet("divide",
        # TODO: I was not able to implement this word in Forth so I created a primitive for it.
        # TODO: Come back on it later...
        # ColonWord("UM/MOD",
        #     [WR("2DUP"), WR("U<"),
        #     WR("?branch"), LR("UMM4"),
        #     WR("NEGATE"), WR("doLIT"), 15, WR(">R"),
        # L("UMM1"), WR(">R"), WR("DUP"), WR("UM+"),
        #     WR(">R"), WR(">R"), WR("DUP"), WR("UM+"),
        #     WR("R>"), WR("+"), WR("DUP"),
        #     WR("R>"), WR("R@"), WR("SWAP"), WR(">R"),
        #     WR("UM+"), WR("R>"), WR("OR"),
        #     WR("?branch"), LR("UMM2"),
        #     WR(">R"), WR("DROP"), WR("doLIT"), 1, WR("+"), WR("R>"),
        #     WR("branch"), LR("UMM3"),
        # L("UMM2"), WR("DROP"),
        # L("UMM3"), WR("R>"),
        #     WR("next"), LR("UMM1"),
        #     WR("DROP"), WR("SWAP"), WR("EXIT"),
        # L("UMM4"), WR("DROP"), WR("2DROP"),
        #     WR("doLIT"), -1, WR("DUP"), WR("EXIT")
        #     ]
        # ),
        ColonWord("M/MOD",
            [WR("DUP"), WR("0<"), WR("DUP"), WR(">R"),
            WR("?branch"), LR("MMOD1"),
            WR("NEGATE"), WR(">R"), WR("DNEGATE"), WR("R>"),
        L("MMOD1"), WR(">R"), WR("DUP"), WR("0<"),
            WR("?branch"), LR("MMOD2"),
            WR("R@"), WR("+"),
        L("MMOD2"), WR("R>"), WR("UM/MOD"), WR("R>"),
            WR("?branch"), LR("MMOD3"),
            WR("SWAP"), WR("NEGATE"), WR("SWAP"),
        L("MMOD3"), WR("EXIT")]
        ),
        ColonWord("/MOD",
            [WR("OVER"), WR("0<"), WR("SWAP"), WR("M/MOD"), WR("EXIT")]
        ),
        ColonWord("MOD",
            [WR("/MOD"), WR("DROP"), WR("EXIT")]
        ),
        ColonWord("/",
            [WR("/MOD"), WR("SWAP"), WR("DROP"), WR("EXIT")]
        ),
        requirements=["primitives", "common", "comparison"]
    )

def by_the_book_multiply_words():
    """
    """
    return WordsSet("multiply",
        ColonWord("UM*",
            [WR("doLIT"), 0, WR("SWAP"), WR("doLIT"), 15, WR(">R"),
        L("UMST1"), WR("DUP"), WR("UM+"), WR(">R"), WR(">R"),
            WR("DUP"), WR("UM+"), WR("R>"), WR("+"), WR("R>"),
            WR("?branch"), LR("UMST2"),
            WR(">R"), WR("OVER"), WR("UM+"),WR("R>"), WR("+"),
        L("UMST2"), WR("next"), LR("UMST1"),
            WR("ROT"), WR("DROP"), WR("EXIT")]
        ),
        ColonWord("*",
            [WR("UM*"), WR("DROP"), WR("EXIT")]
        ),
        ColonWord("M*",
            [WR("2DUP"), WR("XOR"), WR("0<"), WR(">R"),
            WR("ABS"), WR("SWAP"), WR("ABS"), WR("UM*"),
            WR("R>"),
            WR("?branch"), LR("MSTA1"),
            WR("DNEGATE"),
        L("MSTA1"), WR("EXIT")]
        ),
        ColonWord("*/MOD",
            [WR(">R"), WR("M*"), WR("R>"), WR("M/MOD"), WR("EXIT")]
        ),
        ColonWord("*/",
            [WR("*/MOD"), WR("SWAP"), WR("DROP"), WR("EXIT")]
        ),
        requirements=["primitives", "common", "comparison"]
    )

def by_the_book_memory_alignment_words(cell_size):
    """
    """
    return WordsSet("memory_alignment",
        ColonWord("CELL+",
            [WR("doLIT"), cell_size, WR("+"), WR("EXIT")]
        ),
        ColonWord("CELL-",
            [WR("doLIT"), 0-cell_size, WR("+"), WR("EXIT")]
        ),
        ColonWord("CELLS",
            [WR("doLIT"), cell_size, WR("*"), WR("EXIT")]
        ),
        ColonWord("ALIGNED",
            [WR("DUP"), WR("doLIT"), 0, WR("doLIT"), cell_size,
            WR("UM/MOD"), WR("DROP"), WR("DUP"),
            WR("?branch"), LR("ALGN1"),
            WR("doLIT"), cell_size, WR("SWAP"), WR("-"),
        L("ALGN1"), WR("+"), WR("EXIT")]
        ),
        ColonWord("BL",
            [WR("doLIT"), ord(' '), WR("EXIT")]
        ),
        ColonWord(">CHAR",
            [WR("doLIT"), 0x07F, WR("AND"), WR("DUP"),
            WR("doLIT"), 127, WR("BL"), WR("WITHIN"),
            WR("?branch"), LR("TCHA1"),
            WR("DROP"), WR("doLIT"), ord('_'),
        L("TCHA1"), WR("EXIT")]
        ),
        ColonWord("DEPTH",
            [WR("SP@"), WR("SP0"), WR("@"), WR("SWAP"), WR("-"),
            WR("doLIT"), cell_size, WR("/"), WR("EXIT")]
        ),
        ColonWord("PICK",
            [WR("doLIT"), 1, WR("+"), WR("CELLS"),
            WR("SP@"), WR("+"), WR("@"), WR("EXIT")]
        )
    )

def by_the_book_memory_access_words(cell_size):
    """
    """
    return WordsSet("memory_access",
        ColonWord("+!",
            [WR("SWAP"), WR("OVER"), WR("@"), WR("+"),
            WR("SWAP"), WR("!"), WR("EXIT")]
        ),
        ColonWord("2!",
            [WR("SWAP"), WR("OVER"), WR("!"),
            WR("CELL+"), WR("!"), WR("EXIT")]
        ),
        ColonWord("2@",
            [WR("DUP"), WR("CELL+"), WR("@"),
            WR("SWAP"), WR("@"), WR("EXIT")]
        ),
        ColonWord("COUNT",
            [WR("DUP"), WR("doLIT"), 1, WR("+"),
            WR("SWAP"), WR("C@"), WR("EXIT")]
        ),
        ColonWord("HERE",
            [WR("CP"), WR("@"), WR("EXIT")]
        ),
        ColonWord("PAD",
            [WR("HERE"), WR("doLIT"), 80, WR("+"), WR("EXIT")]
        ),
        ColonWord("TIB",
            [WR("#TIB"), WR("CELL+"), WR("@"), WR("EXIT")]
        ),
        ColonWord("@EXECUTE",
            [WR("@"), WR("?DUP"),
            WR("?branch"), LR("EXE1"),
            WR("EXECUTE"),
        L("EXE1"), WR("EXIT")]
        ),
        ColonWord("CMOVE",
            [WR(">R"),
            WR("branch"), LR("CMOV2"),
        L("CMOV1"), WR(">R"), WR("DUP"), WR("C@"),
            WR("R@"), WR("C!"),
            WR("doLIT"), 1, WR("+"),
            WR("R>"), WR("doLIT"), 1, WR("+"),
        L("CMOV2"), WR("next"), LR("CMOV1"),
            WR("2DROP"), WR("EXIT")]
        ),
        ColonWord("FILL",
            [WR("SWAP"), WR(">R"), WR("SWAP"),
            WR("branch"), LR("FILL2"),
        L("FILL1"), WR("2DUP"), WR("C!"), WR("doLIT"), 1, WR("+"),
        L("FILL2"), WR("next"), LR("FILL1"),
            WR("2DROP"), WR("EXIT")]
        ),
        ColonWord("-TRAILING",
            [WR(">R"),
            WR("branch"), LR("DTRA2"),
        L("DTRA1"), WR("BL"), WR("OVER"), WR("R@"), WR("+"), WR("C@"), WR("<"),
            WR("?branch"), LR("DTRA2"),
            WR("R>"), WR("doLIT"), 1, WR("+"), WR("EXIT"),
        L("DTRA2"), WR("next"), LR("DTRA1"),
            WR("doLIT"), 0, WR("EXIT")]
        ),
        ColonWord("PACK$",
            [WR("ALIGNED"), WR("DUP"), WR(">R"),
            WR("OVER"), WR("DUP"), WR("doLIT"), 0,
            WR("doLIT"), cell_size, WR("UM/MOD"), WR("DROP"),
            WR("-"), WR("OVER"), WR("+"),
            WR("doLIT"), 0, WR("SWAP"), WR("!"),
            WR("2DUP"), WR("C!"), WR("doLIT"), 1, WR("+"),
            WR("SWAP"), WR("CMOVE"), WR("R>"), WR("EXIT")]
        )
    )

def by_the_book_numeric_output_single_precision_words():
    return WordsSet("numeric_output_single_precision",
        ColonWord("DIGIT",
            [WR("doLIT"), 9, WR("OVER"), WR("<"),
            WR("doLIT"), 7, WR("AND"), WR("+"),
            WR("doLIT"), ord('0'), WR("+"), WR("EXIT")]
        ),
        ColonWord("EXTRACT",
            [WR("doLIT"), 0, WR("SWAP"), WR("UM/MOD"),
            WR("SWAP"), WR("DIGIT"), WR("EXIT")]
        ),
        ColonWord("<#",
            code("PAD HLD ! EXIT")
        ),
        ColonWord("HOLD",
            [WR("HLD"), WR("@"), WR("doLIT"), 1, WR("-"),
            WR("DUP"), WR("HLD"), WR("!"), WR("C!"), WR("EXIT")]
        ),
        ColonWord("#",
            code("BASE @ EXTRACT HOLD EXIT")
        ),
        ColonWord("#S",
        [L("DIGS1"), WR("#"), WR("DUP"),
            WR("?branch"), LR("DIGS2"),
            WR("branch"), LR("DIGS1"),
        L("DIGS2"), WR("EXIT")]
        ),
        ColonWord("SIGN",
            [WR("0<"),
            WR("?branch"), LR("SIGN1"),
            WR("doLIT"), ord("-"), WR("HOLD"),
        L("SIGN1"), WR("EXIT")]
        ),
        ColonWord("#>",
            [WR("DROP"), WR("HLD"), WR("@"),
            WR("PAD"), WR("OVER"), WR("-"), WR("EXIT")]
        ),
        ColonWord("str",
            [WR("DUP"), WR(">R"), WR("ABS"),
            WR("<#"), WR("#S"), WR("R>"),
            WR("SIGN"), WR("#>"), WR("EXIT")]
        ),
        ColonWord("HEX",
            [WR("doLIT"), 16, WR("BASE"), WR("!"), WR("EXIT")]
        ),
        ColonWord("DECIMAL",
            [WR("doLIT"), 10, WR("BASE"), WR("!"), WR("EXIT")]
        )
    )

def by_the_book_numeric_input_single_precision_words():
    return WordsSet("numeric_input_single_precision",
        ColonWord("DIGIT?",
            [WR(">R"), WR("doLIT"), ord('0'), WR("-"),
            WR("doLIT"), 9, WR("OVER"), WR("<"),
            WR("?branch"), LR("DGTQ1"),
            WR("doLIT"), 7, WR("-"),
            WR("DUP"), WR("doLIT"), 10, WR("<"), WR("OR"),
        L("DGTQ1"), WR("DUP"), WR("R>"), WR("U<"), WR("EXIT")]
        ),
        ColonWord("NUMBER?",
            [WR("BASE"), WR("@"), WR(">R"), WR("doLIT"), 0, WR("OVER"), WR("COUNT"),
            WR("OVER"), WR("C@"), WR("doLIT"), ord('$'), WR("="),
            WR("?branch"), LR("NUMQ1"),
            WR("HEX"), WR("SWAP"), WR("doLIT"), 1, WR("+"),
            WR("SWAP"), WR("doLIT"), 1, WR("-"),
        L("NUMQ1"), WR("OVER"), WR("C@"), WR("doLIT"), ord('-'), WR("="), WR(">R"),
            WR("SWAP"), WR("R@"), WR("-"), WR("SWAP"), WR("R@"), WR("+"), WR("?DUP"),
            WR("?branch"), LR("NUMQ6"),
            WR("doLIT"), 1, WR("-"), WR(">R"),
        L("NUMQ2"), WR("DUP"), WR(">R"), WR("C@"), WR("BASE"), WR("@"), WR("DIGIT?"),
            WR("?branch"), LR("NUMQ4"),
            WR("SWAP"), WR("BASE"), WR("@"), WR("*"), WR("+"), WR("R>"),
            WR("doLIT"), 1, WR("+"),
            WR("next"), LR("NUMQ2"),
            WR("R@"), WR("SWAP"), WR("DROP"),
            WR("?branch"), LR("NUMQ3"),
            WR("NEGATE"),
        L("NUMQ3"), WR("SWAP"),
            WR("branch"), LR("NUMQ5"),
        L("NUMQ4"), WR("R>"), WR("R>"), WR("2DROP"), WR("2DROP"), WR("doLIT"), 0,
        L("NUMQ5"), WR("DUP"),
        L("NUMQ6"), WR("R>"), WR("2DROP"),
            WR("R>"), WR("BASE"), WR("!"), WR("EXIT")]
        )
    )

def by_the_book_basic_io_words():
    """
    """
    # TODO:probably needs host's line ending convention as input
    return WordsSet("basic_io",
        ColonWord("?KEY",
            [WR("'?KEY"), WR("@EXECUTE"), WR("EXIT")]
        ),
        ColonWord("KEY",
        [L("KEY1"), WR("?KEY"),
            WR("?branch"), LR("KEY1"),
            WR("EXIT")]
        ),
        ColonWord("EMIT",
            [WR("'EMIT"), WR("@EXECUTE"), WR("EXIT")]
        ),
        ColonWord("NUF?",
            [WR("?KEY"), WR("DUP"),
            WR("?branch"), LR("NUFQ1"),
            WR("2DROP"), WR("KEY"), WR("doLIT"), 10, WR("="),  # 13 = CR, 10 = LF # NOTE: I changed 13 to 10
        L("NUFQ1"), WR("EXIT")]
        ),
        ColonWord("PACE",
            [WR("doLIT"), 11, WR("EMIT"), WR("EXIT")]
        ),
        ColonWord("SPACE",
            [WR("BL"), WR("EMIT"), WR("EXIT")]
        ),
        ColonWord("SPACES",
            [WR("doLIT"), 0, WR("MAX"), WR(">R"),
            WR("branch"), LR("CHAR2"),
        L("CHAR1"), WR("SPACE"),
        L("CHAR2"), WR("next"), LR("CHAR1"),
            WR("EXIT")]
        ),
        ColonWord("TYPE",
            [WR(">R"),
            WR("branch"), LR("TYPE2"),
        L("TYPE1"), WR("DUP"), WR("C@"), WR("EMIT"),
            WR("doLIT"), 1, WR("+"),
        L("TYPE2"), WR("next"), LR("TYPE1"),
            WR("DROP"), WR("EXIT")]
        ),
        ColonWord("CR",
            [WR("doLIT"), 13, WR("EMIT"), # CR = 13
            WR("doLIT"), 10, WR("EMIT"), WR("EXIT")] #LF = 10
        ),
        ColonWord("do$",
            [WR("R>"), WR("R@"), WR("R>"), WR("COUNT"), WR("+"),
            WR("ALIGNED"), WR(">R"), WR("SWAP"), WR(">R"), WR("EXIT")],
            compile_only=True
        ),
        ColonWord('$"|',
            [WR("do$"), WR("EXIT")],
            compile_only=True
        ),
        ColonWord('."|',
            [WR("do$"), WR("COUNT"), WR("TYPE"), WR("EXIT")],
            compile_only=True
        ),
        ColonWord(".R",
            [WR(">R"), WR("str"), WR("R>"), WR("OVER"), WR("-"),
            WR("SPACES"), WR("TYPE"), WR("EXIT")]
        ),
        ColonWord("U.R",
            [WR(">R"), WR("<#"), WR("#S"), WR("#>"),
            WR("R>"), WR("OVER"), WR("-"),
            WR("SPACES"), WR("TYPE"), WR("EXIT")]
        ),
        ColonWord("U.",
            [WR("<#"), WR("#S"), WR("#>"),
            WR("SPACE"), WR("TYPE"), WR("EXIT")]
        ),
        ColonWord(".",
            [WR("BASE"), WR("@"), WR("doLIT"), 10, WR("XOR"),
            WR("?branch"), LR("DOT1"),
            WR("U."),WR("EXIT"),
        L("DOT1"), WR("str"), WR("SPACE"),WR("TYPE"), WR("EXIT")]
        ),
        ColonWord("?",
            [WR("@"), WR("."), WR("EXIT")]
        )
    )

def by_the_book_parsing_words():
    """
    """
    return WordsSet("parsing",
        ColonWord("parse",
            [WR("tmp"), WR("!"), WR("OVER"), WR(">R"), WR("DUP"),
            WR("?branch"), LR("PARS8"),
            WR("doLIT"), 1, WR("-"), WR("tmp"), WR("@"), WR("BL"), WR("="),
            WR("?branch"), LR("PARS3"),
            WR(">R"),
        L("PARS1"), WR("BL"), WR("OVER"), WR("C@"),
            WR("-"), WR("0<"), WR("NOT"),
            WR("?branch"), LR("PARS2"),
            WR("doLIT"), 1, WR("+"),
            WR("next"), LR("PARS1"),
            WR("R>"), WR("DROP"), WR("doLIT"), 0, WR("DUP"), WR("EXIT"),
        L("PARS2"), WR("R>"),
        L("PARS3"), WR("OVER"), WR("SWAP"),
            WR(">R"),
        L("PARS4"), WR("tmp"), WR("@"), WR("OVER"), WR("C@"), WR("-"),
            WR("tmp"), WR("@"), WR("BL"), WR("="),
            WR("?branch"), LR("PARS5"),
            WR("0<"),
        L("PARS5"), WR("?branch"), LR("PARS6"),
            WR("doLIT"), 1, WR("+"),
            WR("next"), LR("PARS4"),
            WR("DUP"), WR(">R"),
            WR("branch"), LR("PARS7"),
        L("PARS6"), WR("R>"), WR("DROP"), WR("DUP"),
            WR("doLIT"), 1, WR("+"), WR(">R"),
        L("PARS7"), WR("OVER"), WR("-"),
            WR("R>"), WR("R>"), WR("-"), WR("EXIT"),
        L("PARS8"), WR("OVER"), WR("R>"), WR("-"), WR("EXIT")]
        ),
        ColonWord("PARSE",
            [WR(">R"), WR("TIB"), WR(">IN"), WR("@"), WR("+"),
            WR("#TIB"), WR("@"), WR(">IN"), WR("@"), WR("-"),
            WR("R>"), WR("parse"), WR(">IN"), WR("+!"), WR("EXIT")]
        ),
        ColonWord(".(",
            [WR("doLIT"), ord('('), WR("PARSE"), WR("TYPE"), WR("EXIT")],
            immediate=True
        ),
        ColonWord("(",
            [WR("doLIT"), ord(')'), WR("PARSE"), WR("2DROP"), WR("EXIT")],
            immediate=True
        ),
        ColonWord("\\",
            [WR("#TIB"), WR("@"), WR(">IN"), WR("!"), WR("EXIT")],
            immediate=True
        ),
        ColonWord("CHAR",
            [WR("BL"), WR("PARSE"), WR("DROP"), WR("C@"), WR("EXIT")]
        ),
        ColonWord("TOKEN",
            [WR("BL"), WR("PARSE"), WR("doLIT"), 31, WR("MIN"),
            WR("NP"), WR("@"), WR("OVER"), WR("-"), WR("CELL-"),
            WR("PACK$"), WR("EXIT")]
        ),
        ColonWord("WORD",
            [WR("PARSE"), WR("HERE"), WR("PACK$"), WR("EXIT")]
        )
    )

def by_the_book_dictionary_search_words(lexicon_mask, cell_size):
    """
    """
    # NOTE: This words set highly relies on how words are encoded in memory
    return WordsSet("dictionary_search",
        # NOTE: this word is not in EForth but is useful to avoid hardcode lexicon bit mask
        ColonWord("LEXICON_MASK",
            [WR("doLIT"), lexicon_mask, WR("EXIT")]
        ),
        ColonWord("NAME>",
            [WR("CELL-"), WR("CELL-"), WR("@"), WR("EXIT")]
        ),
        ColonWord("SAME?",
            [WR(">R"),
            WR("branch"), LR("SAME2"),
        L("SAME1"), WR("OVER"), WR("R@"), WR("CELLS"), WR("+"), WR("@"),
            WR("OVER"), WR("R@"), WR("CELLS"), WR("+"), WR("@"),
            WR("-"), WR("?DUP"),
            WR("?branch"), LR("SAME2"),
            WR("R>"), WR("DROP"), WR("EXIT"),
        L("SAME2"), WR("next"), LR("SAME1"),
            WR("doLIT"), 0, WR("EXIT")]
        ),
        ColonWord("find",
            [WR("SWAP"), WR("DUP"), WR("C@"),
            WR("doLIT"), cell_size, WR("/"), WR("tmp"), WR("!"),
            # WR("doLIT"), 0x01F, WR("AND"), WR("tmp"), WR("!"), # TOREMOVE: tried to fix previous line with that... Was endianess problem, EForth expects little endian! This line should be removed
            WR("DUP"), WR("@"), WR(">R"),
            WR("CELL+"), WR("SWAP"),
        L("FIND1"), WR("@"), WR("DUP"),
            WR("?branch"), LR("FIND6"),
            WR("DUP"), WR("@"),
            WR("LEXICON_MASK"), WR("AND"), WR("R@"), WR("XOR"),
            WR("?branch"), LR("FIND2"),
            WR("CELL+"), WR("doLIT"), -1,
            WR("branch"), LR("FIND3"),
        L("FIND2"), WR("CELL+"), WR("tmp"), WR("@"), WR("SAME?"),
        L("FIND3"), WR("branch"), LR("FIND4"),
        L("FIND6"), WR("R>"), WR("DROP"),
            WR("SWAP"), WR("CELL-"), WR("SWAP"), WR("EXIT"),
        L("FIND4"), WR("?branch"), LR("FIND5"),
            WR("CELL-"), WR("CELL-"),
            WR("branch"), LR("FIND1"),
        L("FIND5"), WR("R>"), WR("DROP"), WR("SWAP"), WR("DROP"),
            WR("CELL-"),
            WR("DUP"), WR("NAME>"), WR("SWAP"), WR("EXIT")]
        ),
        ColonWord("NAME?",
            [WR("CONTEXT"), WR("DUP"), WR("2@"), WR("XOR"),
            WR("?branch"), LR("NAMQ1"),
            WR("CELL-"),
        L("NAMQ1"), WR(">R"),
        L("NAMQ2"), WR("R>"), WR("CELL+"), WR("DUP"), WR(">R"),
            WR("@"), WR("?DUP"),
            WR("?branch"), LR("NAMQ3"),
            WR("find"), WR("?DUP"),
            WR("?branch"), LR("NAMQ2"),
            WR("R>"), WR("DROP"), WR("EXIT"),
        L("NAMQ3"), WR("R>"), WR("DROP"),
            WR("doLIT"), 0, WR("EXIT")]
        )
    )

def by_the_book_terminal_response_words():
    """
    """
    # TODO:probably needs host's line ending convention as input
    return WordsSet('terminal_response',
        ColonWord("^H",
            [WR(">R"), WR("OVER"), WR("R>"), WR("SWAP"), WR("OVER"), WR("XOR"),
            WR("?branch"), LR("BACK1"),
            WR("doLIT"), 8, WR("'ECHO"), WR("@EXECUTE"), WR("doLIT"), 1, WR("-"), # 8 = backspace
            WR("BL"), WR("'ECHO"), WR("@EXECUTE"),
            WR("doLIT"), 8, WR("'ECHO"), WR("@EXECUTE"), # 8 = backspace
        L("BACK1"), WR("EXIT")]
        ),
        ColonWord("TAP",
            [WR("DUP"), WR("'ECHO"), WR("@EXECUTE"),
            WR("OVER"), WR("C!"), WR("doLIT"), 1, WR("+"), WR("EXIT")]
        ),
        ColonWord("kTAP",
            [WR("DUP"), WR("doLIT"), 10, WR("XOR"), # 13 = CR, 10 = LF # NOTE: I changed 13 to 10
            WR("?branch"), LR("KTAP2"),
            WR("doLIT"), 8, WR("XOR"), # 8 = backspace
            WR("?branch"), LR("KTAP1"),
            WR("BL"), WR("TAP"), WR("EXIT"),
        L("KTAP1"), WR("^H"), WR("EXIT"),
        L("KTAP2"), WR("DROP"), WR("SWAP"), WR("DROP"), WR("DUP"), WR("EXIT")]
        ),
        ColonWord("accept",
            [WR("OVER"), WR("+"), WR("OVER"),
        L("ACCP1"), WR("2DUP"), WR("XOR"),
            WR("?branch"), LR("ACCP4"),
            WR("KEY"), WR("DUP"),
            # WR("BL"), WR("-"), WR("doLIT"), 95, WR("U<"), # Also commented in assembly file.
            WR("BL"), WR("doLIT"), 127, WR("WITHIN"),
            WR("?branch"), LR("ACCP2"),
            WR("TAP"),
            WR("branch"), LR("ACCP3"),
        L("ACCP2"), WR("'TAP"), WR("@EXECUTE"),
        L("ACCP3"), WR("branch"), LR("ACCP1"),
        L("ACCP4"), WR("DROP"), WR("OVER"), WR("-"), WR("EXIT")]
        ),
        ColonWord("EXPECT",
            code("'EXPECT @EXECUTE SPAN ! DROP EXIT")
        ),
        ColonWord("QUERY",
            [WR("TIB"), WR("doLIT"), 80, WR("'EXPECT"), WR("@EXECUTE"), WR("#TIB"), WR("!"),
            WR("DROP"), WR("doLIT"), 0, WR(">IN"), WR("!"), WR("EXIT")]
        )
    )

def by_the_book_error_handling_words():
    return WordsSet("error_handling",
        ColonWord("CATCH",
            [WR("SP@"), WR(">R"), WR("HANDLER"), WR("@"), WR(">R"),
            WR("RP@"), WR("HANDLER"), WR("!"), WR("EXECUTE"),
            WR("R>"), WR("HANDLER"), WR("!"),
            WR("R>"), WR("DROP"), WR("doLIT"), 0, WR("EXIT")]
        ),
        ColonWord("THROW",
            [WR("HANDLER"), WR("@"), WR("RP!"),
            WR("R>"), WR("HANDLER"), WR("!"),
            WR("R>"), WR("SWAP"), WR(">R"), WR("SP!"),
            WR("DROP"), WR("R>"), WR("EXIT")]
        ),
        ColonWord("NULL$",
            [WR("doVAR"),
            0,
            Byte(99), Byte(111), Byte(121), Byte(111), Byte(116), Byte(101),
            Align()]
        ),
        ColonWord("ABORT",
            [WR("NULL$"), WR("THROW")]
        ),
        ColonWord('abort"',
            [WR("?branch"), LR("ABOR1"),
            WR("do$"), WR("THROW"),
        L("ABOR1"), WR("do$"), WR("DROP"), WR("EXIT")],
            compile_only=True
        )
    )

def by_the_book_text_interpreter_words(compile_only_bit):
    """
    """
    return WordsSet("text_interpreter",
        ColonWord("$INTERPRET",
            [WR("NAME?"), WR("?DUP"),
            WR("?branch"), LR("INTE1"),
            WR("@"), WR("doLIT"), compile_only_bit, WR("AND"),
            WR('abort"'), " compile only",
            WR("EXECUTE"), WR("EXIT"),
        L("INTE1"), WR("'NUMBER"), WR("@EXECUTE"),
            WR("?branch"), LR("INTE2"),
            WR("EXIT"),
        L("INTE2"), WR("THROW")]
        ),
        ColonWord("[",
            [WR("doLIT"), WR("$INTERPRET"), WR("'EVAL"), WR("!"), WR("EXIT")],
            immediate=True
        ),
        ColonWord(".OK",
            [WR("doLIT"), WR("$INTERPRET"), WR("'EVAL"), WR("@"), WR("="),
            WR("?branch"), LR("DOTO1"),
            WR('."|'), ' ok',
        L("DOTO1"), WR("CR"), WR("EXIT")]
        ),
        ColonWord("?STACK",
            [WR("DEPTH"), WR("0<"),
            WR('abort"'), ' underflow',
            WR("EXIT")]
        ),
        ColonWord("EVAL",
        [L("EVAL1"), WR("TOKEN"), WR("DUP"), WR("C@"),
            WR("?branch"), LR("EVAL2"),
            WR("'EVAL"), WR("@EXECUTE"), WR("?STACK"),
            WR("branch"), LR("EVAL1"),
        L("EVAL2"), WR("DROP"), WR("'PROMPT"), WR("@EXECUTE"), WR("EXIT")]
        )
    )

def by_the_book_shell_words(terminal_input_buffer_address):
    return WordsSet("shell_words",
        ColonWord("PRESET",
            [WR("SP0"), WR("@"), WR("SP!"),
            WR("doLIT"), terminal_input_buffer_address, WR("#TIB"), WR("CELL+"), WR("!"), WR("EXIT")]
        ),
        ColonWord("xio",
            [WR("doLIT"), WR("accept"), WR("'EXPECT"), WR("!"),
            WR("'TAP"), WR("!"), WR("'ECHO"), WR("!"), WR("'PROMPT"), WR("!"), WR("EXIT")],
            compile_only=True
        ),
        ColonWord("FILE",
            [WR("doLIT"), WR("PACE"), WR("doLIT"), WR("DROP"),
            WR("doLIT"), WR("kTAP"), WR("xio"), WR("EXIT")]
        ),
        ColonWord("HAND",
            [WR("doLIT"), WR(".OK"), WR("doLIT"), WR("EMIT"),
            WR("doLIT"), WR("kTAP"), WR("xio"), WR("EXIT")]
        ),
        ColonWord("I/O",
            [WR("doVAR"), WR("?RX"), WR("TX!")]
        ),
        ColonWord("CONSOLE",
            [WR("I/O"), WR("2@"), WR("'?KEY"), WR("2!"),
            WR("HAND"), WR("EXIT")]
        ),
        ColonWord("QUIT",
            [WR("RP0"), WR("@"), WR("RP!"),
        L("QUIT1"), WR("["),
        L("QUIT2"), WR("QUERY"),
            WR("doLIT"), WR("EVAL"), WR("CATCH"), WR("?DUP"),
            WR("?branch"), LR("QUIT2"),
            WR("'PROMPT"), WR("@"), WR("SWAP"),
            WR("CONSOLE"), WR("NULL$"), WR("OVER"), WR("XOR"),
            WR("?branch"), LR("QUIT3"),
            WR("SPACE"), WR("COUNT"), WR("TYPE"),
            WR('."|'), ' ? ',
        L("QUIT3"), WR("doLIT"), WR(".OK"), WR("XOR"),
            WR("?branch"), LR("QUIT4"),
            WR("doLIT"), 27, WR("EMIT"), # 27 = Error escape
        L("QUIT4"), WR("PRESET"),
            WR("branch"), LR("QUIT1") ]
        )
    )

def by_the_book_compiler_words():
    """
    """
    return WordsSet("compiler",
        ColonWord("'",
            [WR("TOKEN"), WR("NAME?"),
            WR("?branch"), LR("TICK1"),
            WR("EXIT"),
        L("TICK1"), WR("THROW")]
        ),
        ColonWord("ALLOT",
            [WR("CP"), WR("+!"), WR("EXIT")]
        ),
        ColonWord(",",
            [WR("HERE"), WR("DUP"), WR("CELL+"),
            WR("CP"), WR("!"), WR("!"), WR("EXIT")]
        ),
        ColonWord("[COMPILE]",
            [WR("'"), WR(","), WR("EXIT")],
            immediate=True
        ),
        ColonWord("COMPILE",
            [WR("R>"), WR("DUP"), WR("@"), WR(","),
            WR("CELL+"), WR(">R"), WR("EXIT")],
            compile_only=True
        ),
        ColonWord("LITERAL",
            [WR("COMPILE"), WR("doLIT"), WR(","), WR("EXIT")],
            immediate=True
        ),
        ColonWord('$,"',
            [WR("doLIT"), ord('"'), WR("WORD"),
            WR("COUNT"), WR("+"), WR("ALIGNED"),
            WR("CP"), WR("!"), WR("EXIT")]
        ),
        ColonWord("RECURSE",
            [WR("LAST"), WR("@"), WR("NAME>"), WR(","), WR("EXIT")],
            immediate=True
        )
    )

def by_the_book_structure_words():
    return WordsSet("structure",
        ColonWord("FOR",
            [WR("COMPILE"), WR(">R"), WR("HERE"), WR("EXIT")],
            immediate=True
        ),
        ColonWord("BEGIN",
            [WR("HERE"), WR("EXIT")],
            immediate=True
        ),
        ColonWord("NEXT",
            [WR("COMPILE"), WR("next"), WR(","), WR("EXIT")],
            immediate=True
        ),
        ColonWord("UNTIL",
            [WR("COMPILE"), WR("?branch"), WR(","), WR("EXIT")],
            immediate=True
        ),
        ColonWord("AGAIN",
            [WR("COMPILE"), WR("branch"), WR(","), WR("EXIT")],
            immediate=True
        ),
        ColonWord("IF",
            [WR("COMPILE"), WR("?branch"), WR("HERE"),
            WR("doLIT"), 0, WR(","), WR("EXIT")],
            immediate=True
        ),
        ColonWord("AHEAD",
            [WR("COMPILE"), WR("branch"), WR("HERE"), WR("doLIT"), 0, WR(","), WR("EXIT")],
            immediate=True
        ),
        ColonWord("REPEAT",
            [WR("AGAIN"), WR("HERE"), WR("SWAP"), WR("!"), WR("EXIT")],
            immediate=True
        ),
        ColonWord("THEN",
            [WR("HERE"), WR("SWAP"), WR("!"), WR("EXIT")],
            immediate=True
        ),
        ColonWord("AFT",
            [WR("DROP"), WR("AHEAD"), WR("BEGIN"), WR("SWAP"), WR("EXIT")],
            immediate=True
        ),
        ColonWord("ELSE",
            [WR("AHEAD"), WR("SWAP"), WR("THEN"), WR("EXIT")],
            immediate=True
        ),
        ColonWord("WHILE",
            [WR("IF"), WR("SWAP"), WR("EXIT")],
            immediate=True
        ),
        ColonWord('ABORT"',
            [WR("COMPILE"), WR('abort"'), WR('$,"'), WR("EXIT")],
            immediate=True
        ),
        ColonWord('$"',
            [WR("COMPILE"), WR('$"|'), WR('$,"'), WR("EXIT")],
            immediate=True
        ),
        ColonWord('."',
            [WR("COMPILE"), WR('."|'), WR('$,"'), WR("EXIT")],
            immediate=True
        )
    )

def by_the_book_name_compiler_words():
    return WordsSet("name_compiler",
        ColonWord("?UNIQUE",
            [WR("DUP"), WR("NAME?"),
            WR("?branch"), LR("UNIQ1"),
            WR('."|'), " reDef ",
            WR("OVER"), WR("COUNT"), WR("TYPE"),
        L("UNIQ1"), WR("DROP"), WR("EXIT")]
        ),
        ColonWord("$,n",
            [WR("DUP"), WR("C@"),
            WR("?branch"), LR("PNAM1"),
            WR("?UNIQUE"),
            WR("DUP"), WR("LAST"), WR("!"),
            WR("HERE"), WR("ALIGNED"), WR("SWAP"),
            WR("CELL-"),
            WR("CURRENT"), WR("@"), WR("@"), WR("OVER"), WR("!"),
            WR("CELL-"), WR("DUP"), WR("NP"), WR("!"),
            WR("!"), WR("EXIT"),
        L("PNAM1"), WR('$"|'), " name",
            WR("THROW")]
        )
    )

def by_the_book_forth_compiler_words(immediate_bit, doLISTCode):
    return WordsSet("forth_compiler",
        ColonWord("$COMPILE",
            [WR("NAME?"), WR("?DUP"),
            WR("?branch"), LR("SCOM2"),
            WR("@"), WR("doLIT"), immediate_bit, WR("AND"),
            WR("?branch"), LR("SCOM1"),
            WR("EXECUTE"), WR("EXIT"),
        L("SCOM1"), WR(","), WR("EXIT"),
        L("SCOM2"), WR("'NUMBER"), WR("@EXECUTE"),
            WR("?branch"), LR("SCOM3"),
            WR("LITERAL"), WR("EXIT"),
        L("SCOM3"), WR("THROW")]
        ),
        ColonWord("OVERT",
            [WR("LAST"), WR("@"), WR("CURRENT"), WR("@"), WR("!"), WR("EXIT")]
        ),
        ColonWord(";",
            [WR("COMPILE"), WR("EXIT"), WR("["), WR("OVERT"), WR("EXIT")],
            compile_only=True,
            immediate=True
        ),
        ColonWord("]",
            [WR("doLIT"), WR("$COMPILE"), WR("'EVAL"), WR("!"), WR("EXIT")]
        ),
        ColonWord("call,",
            []#TODO
        ),
        ColonWord(":", # Implementation different from EFORTH.ASM !
            [WR("TOKEN"), WR("$,n"),
            WR("doLIT"), doLISTCode, WR(","),
            WR("]"), WR("EXIT")]
        ),
        ColonWord("IMMEDIATE",
            [WR("doLIT"), immediate_bit, WR("LAST"), WR("@"), WR("@"), WR("OR"),
            WR("LAST"), WR("@"), WR("!"), WR("EXIT")]
        )
    )

def by_the_book_defining_words(doLISTCode):
    return WordsSet("defining",
        ColonWord("USER", # Implementation different from EFORTH.ASM !
            [WR("TOKEN"), WR("$,n"), WR("OVERT"),
            WR("doLIT"), doLISTCode, WR(","),
            WR("COMPILE"), WR("doUSER"), WR(","), WR("EXIT")]
        ),
        ColonWord("CREATE", # Implementation different from EFORTH.ASM !
            [WR("TOKEN"), WR("$,n"), WR("OVERT"),
            WR("doLIT"), doLISTCode, WR(","),
            WR("COMPILE"), WR("doVAR"), WR("EXIT")]
        ),
        ColonWord("VARIABLE",
            [WR("CREATE"), WR("doLIT"), 0, WR(","), WR("EXIT")]
        )
    )

def by_the_book_tools_words():
    """
    """
    return WordsSet("tools",
        ColonWord("_TYPE",
            [WR(">R"),
            WR("branch"), LR("UTYP2"),
        L("UTYP1"), WR("DUP"), WR("C@"), WR(">CHAR"), WR("EMIT"),
            WR("doLIT"), 1, WR("+"),
        L("UTYP2"), WR("next"), LR("UTYP1"),
            WR("DROP"), WR("EXIT")]
        ),
        ColonWord("dm+",
            [WR("OVER"), WR("doLIT"), 4, WR("U.R"),
            WR("SPACE"), WR(">R"),
            WR("branch"), LR("PDUM2"),
        L("PDUM1"), WR("DUP"), WR("C@"), WR("doLIT"), 3, WR("U.R"),
            WR("doLIT"), 1, WR("+"),
        L("PDUM2"), WR("next"), LR("PDUM1"),
            WR("EXIT")]
        ),
        ColonWord("DUMP",
            [WR("BASE"), WR("@"), WR(">R"), WR("HEX"),
            WR("doLIT"), 16, WR("/"),
            WR(">R"),
        L("DUMP1"), WR("CR"), WR("doLIT"), 16, WR("2DUP"), WR("dm+"),
            WR("ROT"), WR("ROT"),
            WR("SPACE"), WR("SPACE"), WR("_TYPE"),
            WR("NUF?"), WR("NOT"),
            WR("?branch"), LR("DUMP2"),
            WR("next"), LR("DUMP1"),
            WR("branch"), LR("DUMP3"),
        L("DUMP2"), WR("R>"), WR("DROP"),
        L("DUMP3"), WR("DROP"), WR("R>"), WR("BASE"), WR("!"),
            WR("EXIT")]
        ),
        # ColonWord(".S",
        #     [WR("CR"), WR("DEPTH"),
        #     WR(">R"),
        #     WR("branch"), LR("DOTS2"),
        # L("DOTS1"), WR("R@"), WR("PICK"), WR("."),
        # L("DOTS2"), WR("next"), LR("DOTS1"),
        #     WR('."|'), ' <sp',
        #     WR("EXIT")]
        # )
        # ColonWord("!CSP",
        #     []#TODO
        # )
        # ColonWord("?CSP",
        #     []#TODO
        # )
        # ColonWord(">NAME",
        #     []#TODO
        # )
        # ColonWord(".ID",
        #     []#TODO
        # )
        # ColonWord("SEE",
        #     []#TODO
        # )
        # ColonWord("WORDS",
        #     []#TODO
        # )
    )

def by_the_book_hardware_reset_words(version_number, init_values_size, cell_size, start_of_user_area_address, cold_boot_address):
    """
    """
    return WordsSet("hardware_reset",
        ColonWord("VER",
            [WR("doLIT"), version_number, WR("EXIT")]
        ),
        ColonWord("hi",
            [WR("!IO"), WR("CR"),
            WR('."|'), 'eForth v',
            WR("BASE"), WR("@"), WR("HEX"),
            WR("VER"), WR("<#"), WR("#"), WR("#"),
            WR("doLIT"), ord('.'), WR("HOLD"),
            WR("#S"), WR("#>"), WR("TYPE"),
            WR("BASE"), WR("!"), WR("CR"), WR("EXIT")]
        ),
        ColonWord("'BOOT",
            [WR("doVAR"),
            WR("hi")]
        ),
        ColonWord("COLD",
        [L("COLD1"), WR("doLIT"), cold_boot_address, WR("doLIT"), start_of_user_area_address,
            WR("doLIT"), init_values_size*cell_size, WR("CMOVE"),
            WR("PRESET"),
            WR("'BOOT"), WR("@EXECUTE"),
            WR("FORTH"), WR("CONTEXT"), WR("@"), WR("DUP"),
            WR("CURRENT"), WR("2!"), WR("OVERT"),
            WR("QUIT"),
            WR("branch"), LR("COLD1")]
        )
    )

def by_the_book_memory_initialization(start_of_data_stack_address,
                                      start_of_return_stack_address,
                                      terminal_input_buffer_address,
                                      number_of_vocabularies,
                                      cold_boot_address):
    """ Initialize memory with default user variable values.
    """
    def initializer(compiler):
        last_name_address = compiler.name_address + 2*compiler.cell_size
        top_of_name_dictionary = compiler.name_address
        top_of_code_dictionary = compiler.code_address
        init_values = ([ 0,0,0,0,
            start_of_data_stack_address, # SP0
            start_of_return_stack_address, # RP0
            compiler.lookup_word(WR("?RX")), # '?KEY
            compiler.lookup_word(WR("TX!")), # 'EMIT
            compiler.lookup_word(WR("accept")), # 'EXPECT
            compiler.lookup_word(WR("kTAP")), # 'TAP
            compiler.lookup_word(WR("TX!")), # 'ECHO
            compiler.lookup_word(WR(".OK")), # 'PROMPT
            10, # BASE
            0, # tmp
            0, # SPAN
            0, # >IN
            terminal_input_buffer_address, 0, # TIB
            0, # CSP
            compiler.lookup_word(WR("$INTERPRET")), # 'EVAL
            compiler.lookup_word(WR("NUMBER?")), # 'NUMBER
            0, # HLD
            0 # HANDLER
            ] +
            (number_of_vocabularies * [0]) + # CONTEXT
            [0, 0, # CURRENT
            top_of_code_dictionary, # CP
            top_of_name_dictionary, # NP
            last_name_address # LAST
        ])

        for address, value in zip(range(cold_boot_address, cold_boot_address+compiler.cell_size*len(init_values), compiler.cell_size), init_values):
            compiler.write_cell_at_address(address, value)

    return initializer

def by_the_book_eforth_image(start_of_data_stack_address,
                             start_of_return_stack_address,
                             start_of_user_area_address, # UPP
                             number_of_vocabularies, # VOCCS
                             cell_size,
                             lexicon_mask,
                             immediate_bit,
                             compile_only_bit,
                             doLISTCode,
                             version_number,
                             terminal_input_buffer_address,
                             cold_boot_address,
                             include_tools_wordset=False):
    image = Image(
        by_the_book_primitives(),
        by_the_book_system_and_user_variables(start_of_user_area_address, number_of_vocabularies),
        by_the_book_common_words(),
        by_the_book_comparison_words(),
        by_the_book_divide_words(),
        by_the_book_multiply_words(),
        by_the_book_memory_alignment_words(cell_size),
        by_the_book_memory_access_words(cell_size),
        by_the_book_numeric_output_single_precision_words(),
        by_the_book_numeric_input_single_precision_words(),
        by_the_book_basic_io_words(),
        by_the_book_parsing_words(),
        by_the_book_dictionary_search_words(lexicon_mask, cell_size),
        by_the_book_terminal_response_words(),
        by_the_book_error_handling_words(),
        by_the_book_text_interpreter_words(compile_only_bit),
        by_the_book_shell_words(terminal_input_buffer_address),
        by_the_book_compiler_words(),
        by_the_book_structure_words(),
        by_the_book_name_compiler_words(),
        by_the_book_forth_compiler_words(immediate_bit, doLISTCode),
        by_the_book_defining_words(doLISTCode),
        memory_initializer=by_the_book_memory_initialization(
            start_of_data_stack_address,
            start_of_return_stack_address,
            terminal_input_buffer_address,
            number_of_vocabularies,
            cold_boot_address)
    )

    if include_tools_wordset:
        image.add_words_set(by_the_book_tools_words())

    image.add_words_set(
        by_the_book_hardware_reset_words(
            version_number,
            sum(uv.cells for uv in image.user_variables)+4,
            cell_size,
            start_of_user_area_address,
            cold_boot_address
        )
    )

    return image
