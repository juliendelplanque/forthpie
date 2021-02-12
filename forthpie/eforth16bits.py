from .forth import Memory
from .compiler import Compiler, WordReference, Label, LabelReference, Byte, Align

CELL_SIZE = 2
VOCSS = 8

EM = 0x4000
COLDD = 0x100
US = 64*CELL_SIZE # user area size in cells
RTS = 64*CELL_SIZE # return stack/TIB size
RPP = 0x3F7F #EM-8*CELL_SIZE # start of return stack (RP0)
TIBB = 0x3E80 #RPP-RTS # terminal input buffer (TIB)
SPP = 0x3E7F #TIBB-8*CELL_SIZE # start of data stack (SP0)
UPP = 0x3F80 #EM-256*CELL_SIZE # start of user area (UP0)
NAMEE = 0x3BFF #UPP-8*CELL_SIZE # name dictionary
CODEE = 0x180 #COLDD+US #code dictionary

def code(string):
    return [WordReference(s) for s in string.split()] 

def WR(*args):
    if len(args) == 1:
        return WordReference(args[0])
    elif len(args) > 1:
        return [WordReference(s) for s in args]
    else:
        Exception("Can not build WR")

L = Label
LR = LabelReference

def compile_kernel_words(compiler):
    compiler.compile_primitive("BYE")
    compiler.compile_primitive("?RX")
    compiler.compile_primitive("TX!")
    compiler.compile_primitive("!IO")
    compiler.compile_primitive("doLIT", compiler.COMPILE_ONLY)
    compiler.compile_primitive("doLIST", compiler.COMPILE_ONLY)
    compiler.compile_primitive("EXIT")
    compiler.compile_primitive("EXECUTE")
    compiler.compile_primitive("next", compiler.COMPILE_ONLY)
    compiler.compile_primitive("?branch", compiler.COMPILE_ONLY)
    compiler.compile_primitive("branch", compiler.COMPILE_ONLY)
    compiler.compile_primitive("!")
    compiler.compile_primitive("@")
    compiler.compile_primitive("C!")
    compiler.compile_primitive("C@")
    compiler.compile_primitive("RP@")
    compiler.compile_primitive("RP!", compiler.COMPILE_ONLY)
    compiler.compile_primitive("R>")
    compiler.compile_primitive("R@")
    compiler.compile_primitive(">R", compiler.COMPILE_ONLY)
    compiler.compile_primitive("SP@")
    compiler.compile_primitive("SP!")
    compiler.compile_primitive("DROP")
    compiler.compile_primitive("DUP")
    compiler.compile_primitive("SWAP")
    compiler.compile_primitive("OVER")
    compiler.compile_primitive("0<")
    compiler.compile_primitive("AND")
    compiler.compile_primitive("OR")
    compiler.compile_primitive("XOR")
    compiler.compile_primitive("UM+")
    compiler.compile_primitive("UM/MOD")
    compiler.compile_primitive("DEBUG")
    return compiler

def compile_system_and_user_variables(compiler):
    compiler.compile_colon("doVAR",
        [WR("R>"), (WR("EXIT"))],
        compiler.COMPILE_ONLY)

    compiler.compile_colon("UP",
        [WR("doVAR"), UPP])
    compiler.compile_colon("+",
        WR("UM+", "DROP", "EXIT"))
    compiler.compile_colon("doUSER",
        WR("R>", "@", "UP", "@", "+", "EXIT"),
        compiler.COMPILE_ONLY)
    compiler.compile_user("SP0")
    compiler.compile_user("RP0")
    compiler.compile_user("'?KEY")
    compiler.compile_user("'EMIT")
    compiler.compile_user("'EXPECT")
    compiler.compile_user("'TAP")
    compiler.compile_user("'ECHO")
    compiler.compile_user("'PROMPT")
    compiler.compile_user("BASE")
    compiler.compile_user("tmp", compiler.COMPILE_ONLY)
    compiler.compile_user("SPAN")
    compiler.compile_user(">IN")
    compiler.compile_user("#TIB", cells=2)
    compiler.compile_user("CSP")
    compiler.compile_user("'EVAL")
    compiler.compile_user("'NUMBER")
    compiler.compile_user("HLD")
    compiler.compile_user("HANDLER")
    compiler.compile_user("CONTEXT", cells=VOCSS)
    compiler.compile_user("CURRENT", cells=2)
    compiler.compile_user("CP")
    compiler.compile_user("NP")
    compiler.compile_user("LAST")
    compiler.compile_colon("doVOC",
        WR("R>", "CONTEXT", "!", "EXIT"),
        compiler.COMPILE_ONLY)
    compiler.compile_colon("FORTH",
        [WR("doVOC"), 0, 0]
    )
    return compiler

def compile_common_words(compiler):
    compiler.compile_colon("?DUP",
        [WR("DUP"),
        WR("?branch"), LR("?DUP1"),
        WR("DUP"),
        L("?DUP1"), WR("EXIT")]
    )
    compiler.compile_colon("ROT",
        code(">R SWAP R> SWAP EXIT")
    )
    compiler.compile_colon("2DROP",
        code("DROP DROP EXIT")
    )
    compiler.compile_colon("2DUP",
        code("OVER OVER EXIT")
    )
    # + is defined in compile_system_and_user_variables() because doUser requires it
    compiler.compile_colon("NOT",
        [WR("doLIT"), -1, WR("XOR"), WR("EXIT")
    ])
    compiler.compile_colon("NEGATE",
        [WR("NOT"), WR("doLIT"), 1, WR("+"), WR("EXIT")]
    )
    compiler.compile_colon("DNEGATE",
        [WR("NOT"), WR(">R"), WR("NOT"), WR("doLIT"), 1, WR("UM+"), WR("R>"), WR("+"), WR("EXIT")]
    )
    compiler.compile_colon("D+",
        code(">R SWAP >R UM+ R> R> + + EXIT")
    )
    compiler.compile_colon("-",
        code("NEGATE + EXIT")
    )
    compiler.compile_colon("ABS",
        [WR("DUP"), WR("0<"),
        WR("?branch"), LR("ABS1"),
        WR("NEGATE"), L("ABS1"), WR("EXIT")]
    )
    return compiler

def compile_comparison_words(compiler):
    compiler.compile_colon("=",
        [WR("XOR"),
        WR("?branch"), LR("=1"),
        WR("doLIT"), 0, WR("EXIT"),
        L("=1"), WR("doLIT"), -1, WR("EXIT")]
    )
    compiler.compile_colon("U<",
        [WR("2DUP"), WR("XOR"), WR("0<"),
        WR("?branch"), LR("ULES1"),
        WR("SWAP"), WR("DROP"), WR("0<"), WR("EXIT"),
    L("ULES1"), WR("-"), WR("0<"), WR("EXIT")]
    )
    compiler.compile_colon("<",
        [WR("2DUP"), WR("XOR"), WR("0<"),
        WR("?branch"), LR("<1"),
        WR("DROP"), WR("0<"), WR("EXIT"),
        L("<1"), WR("-"), WR("0<"), WR("EXIT")]
    )
    compiler.compile_colon("MAX",
        [WR("2DUP"), WR("<"),
        WR("?branch"), LR("MAX1"),
        WR("SWAP"),
        L("MAX1"), WR("DROP"), WR("EXIT")]
    )
    compiler.compile_colon("MIN",
        [WR("2DUP"), WR("SWAP"), WR("<"),
        WR("?branch"), LR("MIN1"),
        WR("SWAP"),
        L("MIN1"), WR("DROP"), WR("EXIT")]
    )
    compiler.compile_colon("WITHIN",
        code("OVER - >R - R> U< EXIT")
    )
    return compiler

def compile_divide_words(compiler):
    # Divide
    # TODO: I was not able to implement this word in Forth so I created a primitive for it.
    # TODO: Come back on it later...
    # compiler.compile_colon("UM/MOD",
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
    # )
    compiler.compile_colon("M/MOD",
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
    )
    compiler.compile_colon("/MOD",
        [WR("OVER"), WR("0<"), WR("SWAP"), WR("M/MOD"), WR("EXIT")]
    )
    compiler.compile_colon("MOD",
        [WR("/MOD"), WR("DROP"), WR("EXIT")]
    )
    compiler.compile_colon("/",
        [WR("/MOD"), WR("SWAP"), WR("DROP"), WR("EXIT")]
    )
    return compiler

def compile_multiply_words(compiler):
    compiler.compile_colon("UM*",
        [WR("doLIT"), 0, WR("SWAP"), WR("doLIT"), 15, WR(">R"),
    L("UMST1"), WR("DUP"), WR("UM+"), WR(">R"), WR(">R"),
        WR("DUP"), WR("UM+"), WR("R>"), WR("+"), WR("R>"),
        WR("?branch"), LR("UMST2"),
        WR(">R"), WR("OVER"), WR("UM+"),WR("R>"), WR("+"),
    L("UMST2"), WR("next"), LR("UMST1"),
        WR("ROT"), WR("DROP"), WR("EXIT")]
    )
    compiler.compile_colon("*",
        [WR("UM*"), WR("DROP"), WR("EXIT")]
    )
    compiler.compile_colon("M*",
        [WR("2DUP"), WR("XOR"), WR("0<"), WR(">R"),
        WR("ABS"), WR("SWAP"), WR("ABS"), WR("UM*"),
        WR("R>"),
        WR("?branch"), LR("MSTA1"),
        WR("DNEGATE"),
    L("MSTA1"), WR("EXIT")]
    )
    compiler.compile_colon("*/MOD",
        [WR(">R"), WR("M*"), WR("R>"), WR("M/MOD"), WR("EXIT")]
    )
    compiler.compile_colon("*/",
        [WR("*/MOD"), WR("SWAP"), WR("DROP"), WR("EXIT")]
    )
    return compiler

def compile_memory_alignment_words(compiler):
    compiler.compile_colon("CELL+",
        [WR("doLIT"), compiler.cell_size, WR("+"), WR("EXIT")]
    )
    compiler.compile_colon("CELL-",
        [WR("doLIT"), 0-compiler.cell_size, WR("+"), WR("EXIT")]
    )
    compiler.compile_colon("CELLS",
        [WR("doLIT"), compiler.cell_size, WR("*"), WR("EXIT")]
    )
    compiler.compile_colon("ALIGNED",
        [WR("DUP"), WR("doLIT"), 0, WR("doLIT"), compiler.cell_size,
        WR("UM/MOD"), WR("DROP"), WR("DUP"),
        WR("?branch"), LR("ALGN1"),
        WR("doLIT"), compiler.cell_size, WR("SWAP"), WR("-"),
    L("ALGN1"), WR("+"), WR("EXIT")]
    )
    compiler.compile_colon("BL",
        [WR("doLIT"), 32, WR("EXIT")]
    )
    compiler.compile_colon(">CHAR",
        [WR("doLIT"), 0x07F, WR("AND"), WR("DUP"),
        WR("doLIT"), 127, WR("BL"), WR("WITHIN"),
        WR("?branch"), LR("TCHA1"),
        WR("DROP"), WR("doLIT"), ord('_'),
    L("TCHA1"), WR("EXIT")]
    )#TODO:from here, test words...
    compiler.compile_colon("DEPTH",
        [WR("SP@"), WR("SP0"), WR("@"), WR("SWAP"), WR("-"),
        WR("doLIT"), compiler.cell_size, WR("/"), WR("EXIT")]
    )
    compiler.compile_colon("PICK",
        [WR("doLIT"), 1, WR("+"), WR("CELLS"),
        WR("SP@"), WR("+"), WR("@"), WR("EXIT")]
    )
    return compiler

def compile_memory_access_words(compiler):
    compiler.compile_colon("+!",
        [WR("SWAP"), WR("OVER"), WR("@"), WR("+"),
        WR("SWAP"), WR("!"), WR("EXIT")]
    )
    compiler.compile_colon("2!",
        [WR("SWAP"), WR("OVER"), WR("!"),
        WR("CELL+"), WR("!"), WR("EXIT")]
    )
    compiler.compile_colon("2@",
        [WR("DUP"), WR("CELL+"), WR("@"),
        WR("SWAP"), WR("@"), WR("EXIT")]
    )
    compiler.compile_colon("COUNT",
        [WR("DUP"), WR("doLIT"), 1, WR("+"),
        WR("SWAP"), WR("C@"), WR("EXIT")]
    )
    compiler.compile_colon("HERE",
        [WR("CP"), WR("@"), WR("EXIT")]
    )
    compiler.compile_colon("PAD",
        [WR("HERE"), WR("doLIT"), 80, WR("+"), WR("EXIT")]
    )
    compiler.compile_colon("TIB",
        [WR("#TIB"), WR("CELL+"), WR("@"), WR("EXIT")]
    )
    compiler.compile_colon("@EXECUTE",
        [WR("@"), WR("?DUP"),
        WR("?branch"), LR("EXE1"),
        WR("EXECUTE"),
    L("EXE1"), WR("EXIT")]
    )
    compiler.compile_colon("CMOVE",
        [WR(">R"),
        WR("branch"), LR("CMOV2"),
    L("CMOV1"), WR(">R"), WR("DUP"), WR("C@"),
        WR("R@"), WR("C!"),
        WR("doLIT"), 1, WR("+"),
        WR("R>"), WR("doLIT"), 1, WR("+"),
    L("CMOV2"), WR("next"), LR("CMOV1"),
        WR("2DROP"), WR("EXIT")]
    )
    compiler.compile_colon("FILL",
        [WR("SWAP"), WR(">R"), WR("SWAP"),
        WR("branch"), LR("FILL2"),
    L("FILL1"), WR("2DUP"), WR("C!"), WR("doLIT"), 1, WR("+"),
    L("FILL2"), WR("next"), LR("FILL1"),
        WR("2DROP"), WR("EXIT")]
    )
    compiler.compile_colon("-TRAILING",
        [WR(">R"),
        WR("branch"), LR("DTRA2"),
    L("DTRA1"), WR("BL"), WR("OVER"), WR("R@"), WR("+"), WR("C@"), WR("<"),
        WR("?branch"), LR("DTRA2"),
        WR("R>"), WR("doLIT"), 1, WR("+"), WR("EXIT"),
    L("DTRA2"), WR("next"), LR("DTRA1"),
        WR("doLIT"), 0, WR("EXIT")]
    )
    compiler.compile_colon("PACK$",
        [WR("ALIGNED"), WR("DUP"), WR(">R"),
        WR("OVER"), WR("DUP"), WR("doLIT"), 0,
        WR("doLIT"), compiler.cell_size, WR("UM/MOD"), WR("DROP"),
        WR("-"), WR("OVER"), WR("+"),
        WR("doLIT"), 0, WR("SWAP"), WR("!"),
        WR("2DUP"), WR("C!"), WR("doLIT"), 1, WR("+"),
        WR("SWAP"), WR("CMOVE"), WR("R>"), WR("EXIT")]
    )
    return compiler

def compile_numeric_output_single_precision_words(compiler):
    compiler.compile_colon("DIGIT",
        [WR("doLIT"), 9, WR("OVER"), WR("<"),
        WR("doLIT"), 7, WR("AND"), WR("+"),
        WR("doLIT"), ord('0'), WR("+"), WR("EXIT")]
    )
    compiler.compile_colon("EXTRACT",
        [WR("doLIT"), 0, WR("SWAP"), WR("UM/MOD"),
        WR("SWAP"), WR("DIGIT"), WR("EXIT")]
    )
    compiler.compile_colon("<#",
        code("PAD HLD ! EXIT")
    )
    compiler.compile_colon("HOLD",
        [WR("HLD"), WR("@"), WR("doLIT"), 1, WR("-"),
        WR("DUP"), WR("HLD"), WR("!"), WR("C!"), WR("EXIT")]
    )
    compiler.compile_colon("#",
        code("BASE @ EXTRACT HOLD EXIT")
    )
    compiler.compile_colon("#S",
    [L("DIGS1"), WR("#"), WR("DUP"),
        WR("?branch"), LR("DIGS2"),
        WR("branch"), LR("DIGS1"),
    L("DIGS2"), WR("EXIT")]
    )
    compiler.compile_colon("SIGN",
        [WR("0<"),
        WR("?branch"), LR("SIGN1"),
        WR("doLIT"), ord("-"), WR("HOLD"),
    L("SIGN1"), WR("EXIT")]
    )
    compiler.compile_colon("#>",
        [WR("DROP"), WR("HLD"), WR("@"),
        WR("PAD"), WR("OVER"), WR("-"), WR("EXIT")]
    )
    compiler.compile_colon("str",
        [WR("DUP"), WR(">R"), WR("ABS"),
        WR("<#"), WR("#S"), WR("R>"),
        WR("SIGN"), WR("#>"), WR("EXIT")]
    )
    compiler.compile_colon("HEX",
        [WR("doLIT"), 16, WR("BASE"), WR("!"), WR("EXIT")]
    )
    compiler.compile_colon("DECIMAL",
        [WR("doLIT"), 10, WR("BASE"), WR("!"), WR("EXIT")]
    )
    return compiler

def compile_numeric_input_single_precision_words(compiler):
    compiler.compile_colon("DIGIT?",
        [WR(">R"), WR("doLIT"), ord('0'), WR("-"),
        WR("doLIT"), 9, WR("OVER"), WR("<"),
        WR("?branch"), LR("DGTQ1"),
        WR("doLIT"), 7, WR("-"),
        WR("DUP"), WR("doLIT"), 10, WR("<"), WR("OR"),
    L("DGTQ1"), WR("DUP"), WR("R>"), WR("U<"), WR("EXIT")]
    )
    compiler.compile_colon("NUMBER?",
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
    return compiler

def compile_basic_io_words(compiler):
    compiler.compile_colon("?KEY",
        [WR("'?KEY"), WR("@EXECUTE"), WR("EXIT")]
    )
    compiler.compile_colon("KEY",
    [L("KEY1"), WR("?KEY"),
        WR("?branch"), LR("KEY1"),
        WR("EXIT")]
    )
    compiler.compile_colon("EMIT",
        [WR("'EMIT"), WR("@EXECUTE"), WR("EXIT")]
    )
    compiler.compile_colon("NUF?",
        [WR("?KEY"), WR("DUP"),
        WR("?branch"), LR("NUFQ1"),
        WR("2DROP"), WR("KEY"), WR("doLIT"), 10, WR("="),  # 13 = CR, 10 = LF # NOTE: I changed 13 to 10
    L("NUFQ1"), WR("EXIT")]
    )
    compiler.compile_colon("PACE",
        [WR("doLIT"), 11, WR("EMIT"), WR("EXIT")]
    )
    compiler.compile_colon("SPACE",
        [WR("BL"), WR("EMIT"), WR("EXIT")]
    )
    compiler.compile_colon("SPACES",
        [WR("doLIT"), 0, WR("MAX"), WR(">R"),
        WR("branch"), LR("CHAR2"),
    L("CHAR1"), WR("SPACE"),
    L("CHAR2"), WR("next"), LR("CHAR1"),
        WR("EXIT")]
    )
    compiler.compile_colon("TYPE",
        [WR(">R"),
        WR("branch"), LR("TYPE2"),
    L("TYPE1"), WR("DUP"), WR("C@"), WR("EMIT"),
        WR("doLIT"), 1, WR("+"),
    L("TYPE2"), WR("next"), LR("TYPE1"),
        WR("DROP"), WR("EXIT")]
    )
    compiler.compile_colon("CR",
        [WR("doLIT"), 13, WR("EMIT"), # CR = 13
        WR("doLIT"), 10, WR("EMIT"), WR("EXIT")] #LF = 10
    )
    compiler.compile_colon("do$",
        [WR("R>"), WR("R@"), WR("R>"), WR("COUNT"), WR("+"),
        WR("ALIGNED"), WR(">R"), WR("SWAP"), WR(">R"), WR("EXIT")],
        compiler.COMPILE_ONLY
    )
    compiler.compile_colon('$"|',
        [WR("do$"), WR("EXIT")],
        compiler.COMPILE_ONLY
    )
    compiler.compile_colon('."|',
        [WR("do$"), WR("COUNT"), WR("TYPE"), WR("EXIT")],
        compiler.COMPILE_ONLY
    )
    compiler.compile_colon(".R",
        [WR(">R"), WR("str"), WR("R>"), WR("OVER"), WR("-"),
        WR("SPACES"), WR("TYPE"), WR("EXIT")]
    )
    compiler.compile_colon("U.R",
        [WR(">R"), WR("<#"), WR("#S"), WR("#>"),
        WR("R>"), WR("OVER"), WR("-"),
        WR("SPACES"), WR("TYPE"), WR("EXIT")]
    )
    compiler.compile_colon("U.",
        [WR("<#"), WR("#S"), WR("#>"),
        WR("SPACE"), WR("TYPE"), WR("EXIT")]
    )
    compiler.compile_colon(".",
        [WR("BASE"), WR("@"), WR("doLIT"), 10, WR("XOR"),
        WR("?branch"), LR("DOT1"),
        WR("U."),WR("EXIT"),
    L("DOT1"), WR("str"), WR("SPACE"),WR("TYPE"), WR("EXIT")]
    )
    compiler.compile_colon("?",
        [WR("@"), WR("."), WR("EXIT")]
    )
    return compiler

def compile_parsing_words(compiler):
    compiler.compile_colon("parse",
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
    )
    compiler.compile_colon("PARSE",
        [WR(">R"), WR("TIB"), WR(">IN"), WR("@"), WR("+"),
        WR("#TIB"), WR("@"), WR(">IN"), WR("@"), WR("-"),
        WR("R>"), WR("parse"), WR(">IN"), WR("+!"), WR("EXIT")]
    )
    compiler.compile_colon(".(",
        [WR("doLIT"), ord('('), WR("PARSE"), WR("TYPE"), WR("EXIT")],
        compiler.IMMEDIATE
    )
    compiler.compile_colon("(",
        [WR("doLIT"), ord(')'), WR("PARSE"), WR("2DROP"), WR("EXIT")],
        compiler.IMMEDIATE
    )
    compiler.compile_colon("\\",
        [WR("#TIB"), WR("@"), WR(">IN"), WR("!"), WR("EXIT")],
        compiler.IMMEDIATE
    )
    compiler.compile_colon("CHAR",
        [WR("BL"), WR("PARSE"), WR("DROP"), WR("C@"), WR("EXIT")]
    )
    compiler.compile_colon("TOKEN",
        [WR("BL"), WR("PARSE"), WR("doLIT"), 31, WR("MIN"),
        WR("NP"), WR("@"), WR("OVER"), WR("-"), WR("CELL-"),
        WR("PACK$"), WR("EXIT")]
    )
    compiler.compile_colon("WORD",
        [WR("PARSE"), WR("HERE"), WR("PACK$"), WR("EXIT")]
    )
    return compiler

def compile_dictionary_search_words(compiler):
    compiler.compile_colon("NAME>",
        [WR("CELL-"), WR("CELL-"), WR("@"), WR("EXIT")]
    )
    compiler.compile_colon("SAME?",
        [WR(">R"),
        WR("branch"), LR("SAME2"),
    L("SAME1"), WR("OVER"), WR("R@"), WR("CELLS"), WR("+"), WR("@"),
        WR("OVER"), WR("R@"), WR("CELLS"), WR("+"), WR("@"),
        WR("-"), WR("?DUP"),
        WR("?branch"), LR("SAME2"), 
        WR("R>"), WR("DROP"), WR("EXIT"),
    L("SAME2"), WR("next"), LR("SAME1"),
        WR("doLIT"), 0, WR("EXIT")]
    )
    compiler.compile_colon("find",
        [WR("SWAP"), WR("DUP"), WR("C@"),
        WR("doLIT"), compiler.cell_size, WR("/"), WR("tmp"), WR("!"),
        # WR("doLIT"), 0x01F, WR("AND"), WR("tmp"), WR("!"), # TOREMOVE: tried to fix previous line with that... Was endianess problem, EForth expects little endian! This line should be removed
        WR("DUP"), WR("@"), WR(">R"),
        WR("CELL+"), WR("SWAP"),
    L("FIND1"), WR("@"), WR("DUP"),
        WR("?branch"), LR("FIND6"),
        WR("DUP"), WR("@"),
        WR("doLIT"), compiler.LEXICON_MASK, WR("AND"), WR("R@"), WR("XOR"),
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
    )
    compiler.compile_colon("NAME?",
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
    return compiler

def compile_terminal_response_words(compiler):
    # Terminal response
    compiler.compile_colon("^H",
        [WR(">R"), WR("OVER"), WR("R>"), WR("SWAP"), WR("OVER"), WR("XOR"),
        WR("?branch"), LR("BACK1"),
        WR("doLIT"), 8, WR("'ECHO"), WR("@EXECUTE"), WR("doLIT"), 1, WR("-"), # 8 = backspace
        WR("BL"), WR("'ECHO"), WR("@EXECUTE"),
        WR("doLIT"), 8, WR("'ECHO"), WR("@EXECUTE"), # 8 = backspace
    L("BACK1"), WR("EXIT")]
    )
    compiler.compile_colon("TAP",
        [WR("DUP"), WR("'ECHO"), WR("@EXECUTE"),
        WR("OVER"), WR("C!"), WR("doLIT"), 1, WR("+"), WR("EXIT")]
    )
    compiler.compile_colon("kTAP",
        [WR("DUP"), WR("doLIT"), 10, WR("XOR"), # 13 = CR, 10 = LF # NOTE: I changed 13 to 10
        WR("?branch"), LR("KTAP2"),
        WR("doLIT"), 8, WR("XOR"), # 8 = backspace
        WR("?branch"), LR("KTAP1"),
        WR("BL"), WR("TAP"), WR("EXIT"),
    L("KTAP1"), WR("^H"), WR("EXIT"),
    L("KTAP2"), WR("DROP"), WR("SWAP"), WR("DROP"), WR("DUP"), WR("EXIT")]
    )
    compiler.compile_colon("accept",
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
    )
    compiler.compile_colon("EXPECT",
        code("'EXPECT @EXECUTE SPAN ! DROP EXIT")
    )
    compiler.compile_colon("QUERY",
        [WR("TIB"), WR("doLIT"), 80, WR("'EXPECT"), WR("@EXECUTE"), WR("#TIB"), WR("!"),
        WR("DROP"), WR("doLIT"), 0, WR(">IN"), WR("!"), WR("EXIT")]
    )
    return compiler

def compile_error_handling_words(compiler):
    compiler.compile_colon("CATCH",
        [WR("SP@"), WR(">R"), WR("HANDLER"), WR("@"), WR(">R"),
        WR("RP@"), WR("HANDLER"), WR("!"), WR("EXECUTE"),
        WR("R>"), WR("HANDLER"), WR("!"),
        WR("R>"), WR("DROP"), WR("doLIT"), 0, WR("EXIT")]
    )
    compiler.compile_colon("THROW",
        [WR("HANDLER"), WR("@"), WR("RP!"),
        WR("R>"), WR("HANDLER"), WR("!"),
        WR("R>"), WR("SWAP"), WR(">R"), WR("SP!"),
        WR("DROP"), WR("R>"), WR("EXIT")]
    )
    compiler.compile_colon("NULL$",
        [WR("doVAR"),
        0,
        Byte(99), Byte(111), Byte(121), Byte(111), Byte(116), Byte(101),
        Align()]
    )
    compiler.compile_colon("ABORT",
        [WR("NULL$"), WR("THROW")]
    )
    compiler.compile_colon('abort"',
        [WR("?branch"), LR("ABOR1"),
        WR("do$"), WR("THROW"),
    L("ABOR1"), WR("do$"), WR("DROP"), WR("EXIT")],
        compiler.COMPILE_ONLY
    )
    return compiler

def compile_text_interpreter_words(compiler):
    compiler.compile_colon("$INTERPRET",
        [WR("NAME?"), WR("?DUP"),
        WR("?branch"), LR("INTE1"),
        WR("@"), WR("doLIT"), compiler.COMPILE_ONLY, WR("AND"),
        WR('abort"'), " compile only",
        WR("EXECUTE"), WR("EXIT"),
    L("INTE1"), WR("'NUMBER"), WR("@EXECUTE"),
        WR("?branch"), LR("INTE2"),
        WR("EXIT"),
    L("INTE2"), WR("THROW")]
    )
    compiler.compile_colon("[",
        [WR("doLIT"), WR("$INTERPRET"), WR("'EVAL"), WR("!"), WR("EXIT")],
        compiler.IMMEDIATE
    )
    compiler.compile_colon(".OK",
        [WR("doLIT"), WR("$INTERPRET"), WR("'EVAL"), WR("@"), WR("="),
        WR("?branch"), LR("DOTO1"),
        WR('."|'), ' ok',
    L("DOTO1"), WR("CR"), WR("EXIT")]
    )
    compiler.compile_colon("?STACK",
        [WR("DEPTH"), WR("0<"),
        WR('abort"'), ' underflow',
        WR("EXIT")]
    )
    compiler.compile_colon("EVAL",
    [L("EVAL1"), WR("TOKEN"), WR("DUP"), WR("C@"),
        WR("?branch"), LR("EVAL2"),
        WR("'EVAL"), WR("@EXECUTE"), WR("?STACK"),
        WR("branch"), LR("EVAL1"),
    L("EVAL2"), WR("DROP"), WR("'PROMPT"), WR("@EXECUTE"), WR("EXIT")]
    )
    return compiler

def compile_shell_words(compiler):
    compiler.compile_colon("PRESET",
        [WR("SP0"), WR("@"), WR("SP!"),
        WR("doLIT"), TIBB, WR("#TIB"), WR("CELL+"), WR("!"), WR("EXIT")]
    )
    compiler.compile_colon("xio",
        [WR("doLIT"), WR("accept"), WR("'EXPECT"), WR("2!"),
        WR("'ECHO"), WR("2!"), WR("EXIT")],
        compiler.COMPILE_ONLY
    )
    compiler.compile_colon("FILE",
        [WR("doLIT"), WR("PACE"), WR("doLIT"), WR("DROP"),
        WR("doLIT"), WR("kTAP"), WR("xio"), WR("EXIT")]
    )
    compiler.compile_colon("HAND",
        [WR("doLIT"), WR(".OK"), WR("doLIT"), WR("EMIT"),
        WR("doLIT"), WR("kTAP"), WR("xio"), WR("EXIT")]
    )
    compiler.compile_colon("I/O",
        [WR("doVAR"), WR("'?KEY"), WR("TX!")]
    )
    compiler.compile_colon("CONSOLE",
        [WR("I/O"), WR("2@"), WR("'?KEY"), WR("2!"),
        WR("HAND"), WR("EXIT")]
    )
    compiler.compile_colon("QUIT",
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
    L("QUIT3"), WR(".OK"), WR("XOR"),
        WR("?branch"), LR("QUIT4"),
        WR("doLIT"), 27, WR("EMIT"), # 27 = Error escape
    L("QUIT4"), WR("PRESET"),
        WR("branch"), LR("QUIT1") ] 
    )
    return compiler

def compile_compiler_words(compiler):
    compiler.compile_colon("'",
        [WR("TOKEN"), WR("NAME?"),
        WR("?branch"), LR("TICK1"),
        WR("EXIT"),
    L("TICK1"), WR("THROW")]
    )
    compiler.compile_colon("ALLOT",
        [WR("CP"), WR("+!"), WR("EXIT")]
    )
    compiler.compile_colon(",",
        [WR("HERE"), WR("DUP"), WR("CELL+"),
        WR("CP"), WR("!"), WR("!"), WR("EXIT")]
    )
    compiler.compile_colon("[COMPILE]",
        [WR("'"), WR(","), WR("EXIT")],
        compiler.IMMEDIATE
    )
    compiler.compile_colon("COMPILE",
        [WR("R>"), WR("DUP"), WR("@"), WR(","),
        WR("CELL+"), WR(">R"), WR("EXIT")],
        compiler.COMPILE_ONLY
    )
    compiler.compile_colon("LITERAL",
        [WR("COMPILE"), WR("doLIT"), WR(","), WR("EXIT")],
        compiler.IMMEDIATE
    )
    compiler.compile_colon('$,"',
        [WR("doLIT"), ord('"'), WR("WORD"),
        WR("COUNT"), WR("+"), WR("ALIGNED"),
        WR("CP"), WR("!"), WR("EXIT")]
    )
    compiler.compile_colon("RECURSE",
        [WR("LAST"), WR("@"), WR("NAME>"), WR(","), WR("EXIT")],
        compiler.IMMEDIATE
    )
    return compiler

def compile_structure_words(compiler):
    # Structures
    compiler.compile_colon("FOR",
        [WR("COMPILE"), WR(">R"), WR("HERE"), WR("EXIT")],
        compiler.IMMEDIATE
    )
    compiler.compile_colon("BEGIN",
        [WR("HERE"), WR("EXIT")],
        compiler.IMMEDIATE
    )
    compiler.compile_colon("NEXT",
        [WR("COMPILE"), WR("next"), WR(","), WR("EXIT")],
        compiler.IMMEDIATE
    )
    compiler.compile_colon("UNTIL",
        [WR("COMPILE"), WR("?branch"), WR(","), WR("EXIT")],
        compiler.IMMEDIATE
    )
    compiler.compile_colon("AGAIN",
        [WR("COMPILE"), WR("branch"), WR(","), WR("EXIT")],
        compiler.IMMEDIATE
    )
    compiler.compile_colon("IF",
        [WR("COMPILE"), WR("?branch"), WR("HERE"),
        WR("doLIT"), 0, WR(","), WR("EXIT")],
        compiler.IMMEDIATE
    )
    compiler.compile_colon("AHEAD",
        [WR("COMPILE"), WR("branch"), WR("HERE"), WR("doLIT"), 0, WR(","), WR("EXIT")],
        compiler.IMMEDIATE
    )
    compiler.compile_colon("REPEAT",
        [WR("AGAIN"), WR("HERE"), WR("SWAP"), WR("!"), WR("EXIT")],
        compiler.IMMEDIATE
    )
    compiler.compile_colon("THEN",
        [WR("HERE"), WR("SWAP"), WR("!"), WR("EXIT")],
        compiler.IMMEDIATE
    )
    compiler.compile_colon("AFT",
        [WR("DROP"), WR("AHEAD"), WR("BEGIN"), WR("SWAP"), WR("EXIT")],
        compiler.IMMEDIATE
    )
    compiler.compile_colon("ELSE",
        [WR("AHEAD"), WR("SWAP"), WR("THEN"), WR("EXIT")],
        compiler.IMMEDIATE
    )
    compiler.compile_colon("WHILE",
        [WR("IF"), WR("SWAP"), WR("EXIT")],
        compiler.IMMEDIATE
    )
    compiler.compile_colon('ABORT"',
        [WR("COMPILE"), WR('abort"'), WR('$,"'), WR("EXIT")],
        compiler.IMMEDIATE
    )
    compiler.compile_colon('$"',
        [WR("COMPILE"), WR('$"|'), WR('$,"'), WR("EXIT")],
        compiler.IMMEDIATE
    )
    compiler.compile_colon('."',
        [WR("COMPILE"), WR('."|'), WR('$,"'), WR("EXIT")],
        compiler.IMMEDIATE
    )
    return compiler

def compile_name_compiler_words(compiler):
    compiler.compile_colon("?UNIQUE",
        [WR("DUP"), WR("NAME?"),
        WR("?branch"), LR("UNIQ1"),
        WR('."|'), " reDef ",
        WR("OVER"), WR("COUNT"), WR("TYPE"),
    L("UNIQ1"), WR("DROP"), WR("EXIT")]
    )
    compiler.compile_colon("$,n",
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
    return compiler

def compile_forth_compiler_words(compiler):
    compiler.compile_colon("$COMPILE",
        [WR("NAME?"), WR("?DUP"),
        WR("?branch"), LR("SCOM2"),
        WR("@"), WR("doLIT"), compiler.IMMEDIATE, WR("AND"),
        WR("?branch"), LR("SCOM1"),
        WR("EXECUTE"), WR("EXIT"),
    L("SCOM1"), WR(","), WR("EXIT"),
    L("SCOM2"), WR("'NUMBER"), WR("@EXECUTE"),
        WR("?branch"), LR("SCOM3"),
        WR("LITERAL"), WR("EXIT"),
    L("SCOM3"), WR("THROW")]
    )
    compiler.compile_colon("OVERT",
        [WR("LAST"), WR("@"), WR("CURRENT"), WR("@"), WR("!"), WR("EXIT")]
    )
    compiler.compile_colon(";",
        [WR("COMPILE"), WR("EXIT"), WR("["), WR("OVERT"), WR("EXIT")],
        compiler.IMMEDIATE+compiler.COMPILE_ONLY
    )
    compiler.compile_colon("]",
        [WR("doLIT"), WR("$COMPILE"), WR("'EVAL"), WR("!"), WR("EXIT")]
    )
    compiler.compile_colon("call,",
        []#TODO
    )
    compiler.compile_colon(":", # Implementation different from EFORTH.ASM !
        [WR("TOKEN"), WR("$,n"),
        WR("doLIT"), compiler.get_primitive_by_name("doLIST").code, WR(","),
        WR("]"), WR("EXIT")]
    )
    compiler.compile_colon("IMMEDIATE",
        [WR("doLIT"), compiler.IMMEDIATE, WR("LAST"), WR("@"), WR("@"), WR("OR"),
        WR("LAST"), WR("@"), WR("!"), WR("EXIT")]
    )
    return compiler

def compile_defining_words(compiler):
    compiler.compile_colon("USER", # Implementation different from EFORTH.ASM !
        [WR("TOKEN"), WR("$,n"), WR("OVERT"),
        WR("doLIT"), compiler.get_primitive_by_name("doLIST").code, WR(","),
        WR("COMPILE"), WR("doUSER"), WR(","), WR("EXIT")]
    )
    compiler.compile_colon("CREATE", # Implementation different from EFORTH.ASM !
        [WR("TOKEN"), WR("$,n"), WR("OVERT"),
        WR("doLIT"), compiler.get_primitive_by_name("doLIST").code, WR(","),
        WR("COMPILE"), WR("doVAR"), WR("EXIT")]
    )
    compiler.compile_colon("VARIABLE",
        [WR("CREATE"), WR("doLIT"), 0, WR(","), WR("EXIT")]
    )
    return compiler

def compile_tools_words(compiler):
    compiler.compile_colon("_TYPE",
        [WR(">R"),
        WR("branch"), LR("UTYP2"),
    L("UTYP1"), WR("DUP"), WR("C@"), WR(">CHAR"), WR("EMIT"),
        WR("doLIT"), 1, WR("+"),
    L("UTYP2"), WR("next"), LR("UTYP1"),
        WR("DROP"), WR("EXIT")]
    )
    compiler.compile_colon("dm+",
        [WR("OVER"), WR("doLIT"), 4, WR("U.R"),
        WR("SPACE"), WR(">R"),
        WR("branch"), LR("PDUM2"),
    L("PDUM1"), WR("DUP"), WR("C@"), WR("doLIT"), 3, WR("U.R"),
        WR("doLIT"), 1, WR("+"),
    L("PDUM2"), WR("next"), LR("PDUM1"),
        WR("EXIT")]
    )
    compiler.compile_colon("DUMP",
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
    )
    compiler.compile_colon(".S",
        [WR("CR"), WR("DEPTH"),
        WR(">R"),
        WR("branch"), LR("DOTS2"),
    L("DOTS1"), WR("R@"), WR("PICK"), WR("."),
    L("DOTS2"), WR("next"), LR("DOTS1"),
        WR('."|'), ' <sp',
        WR("EXIT")]
    )
    # compiler.compile_colon("!CSP",
    #     []#TODO
    # )
    # compiler.compile_colon("?CSP",
    #     []#TODO
    # )
    # compiler.compile_colon(">NAME",
    #     []#TODO
    # )
    # compiler.compile_colon(".ID",
    #     []#TODO
    # )
    # compiler.compile_colon("SEE",
    #     []#TODO
    # )
    # compiler.compile_colon("WORDS",
    #     []#TODO
    # )
    return compiler

def compile_hardware_reset_words(compiler):
    compiler.compile_colon("VER", #TODO: proper version number
        [WR("doLIT"), 0, WR("EXIT")]
    )
    compiler.compile_colon("hi",
        [WR("!IO"), WR("CR"),
        WR('."|'), 'eForth v',
        WR("BASE"), WR("@"), WR("HEX"),
        WR("VER"), WR("<#"), WR("#"), WR("#"),
        WR("doLIT"), ord('.'), WR("HOLD"),
        WR("#S"), WR("#>"), WR("TYPE"),
        WR("BASE"), WR("!"), WR("CR"), WR("EXIT")]
    )
    compiler.compile_colon("'BOOT",
        [WR("doVAR"),
        WR("hi")]
    )
    compiler.compile_colon("COLD",
    [L("COLD1"), WR("doLIT"), COLDD, WR("doLIT"), UPP,
        WR("doLIT"), 37*compiler.cell_size, WR("CMOVE"), #TODO: do not hardcode init_values list size
        WR("PRESET"),
        WR("'BOOT"), WR("@EXECUTE"),
        WR("FORTH"), WR("CONTEXT"), WR("@"), WR("DUP"),
        WR("CURRENT"), WR("2!"), WR("OVERT"), 
        WR("QUIT"),
        WR("branch"), LR("COLD1")]
    )
    return compiler

def initialize_cold_boot_memory(compiler):
    # Initialize memory with default user variable values
    LASTN = compiler.name_address + 8
    print(f"Last name address (LASTN) = {hex(LASTN)}")
    NTOP = compiler.name_address + 4
    print(f"Name dict (NTOP)={hex(NTOP)}")
    CTOP = compiler.code_address
    print(f"Code dict (CTOP)={hex(CTOP)}")
    init_values = ([ 0,0,0,0,
        SPP,
        RPP,
        compiler.lookup_word(WR("?RX")),
        compiler.lookup_word(WR("TX!")),
        compiler.lookup_word(WR("accept")),
        compiler.lookup_word(WR("kTAP")),
        compiler.lookup_word(WR("TX!")), # 'ECHO
        compiler.lookup_word(WR(".OK")),
        10, # Default radix
        0, # tmp
        0, # SPAN
        0, # >IN
        0, # #TIB
        TIBB,
        0,
        compiler.lookup_word(WR("$INTERPRET")),
        compiler.lookup_word(WR("NUMBER?")),
        0,
        0,
        0] +
        (VOCSS * [0]) +
        [0,
        0,
        CTOP,
        NTOP,
        LASTN
    ])

    for address, value in zip(range(COLDD, COLDD+compiler.cell_size*len(init_values), compiler.cell_size), init_values):
        compiler.write_cell_at_address(address, value)
    return compiler

def bootstrap_16bits_eforth():
    compiler = Compiler(
        cell_size=CELL_SIZE,
        initial_code_address=CODEE,
        initial_name_address=NAMEE,
        initial_user_address=4*CELL_SIZE,
        memory=Memory(EM))
    
    compile_kernel_words(compiler)
    compile_system_and_user_variables(compiler)
    compile_common_words(compiler)
    compile_comparison_words(compiler)
    compile_divide_words(compiler)
    compile_multiply_words(compiler)
    compile_memory_alignment_words(compiler)
    compile_memory_access_words(compiler)
    compile_numeric_output_single_precision_words(compiler)
    compile_numeric_input_single_precision_words(compiler)    
    compile_basic_io_words(compiler)
    compile_parsing_words(compiler)
    compile_dictionary_search_words(compiler)
    compile_terminal_response_words(compiler)
    compile_error_handling_words(compiler)
    compile_text_interpreter_words(compiler)
    compile_shell_words(compiler)
    compile_compiler_words(compiler)
    compile_structure_words(compiler)
    compile_name_compiler_words(compiler)
    compile_forth_compiler_words(compiler)
    compile_defining_words(compiler)
    compile_tools_words(compiler)
    compile_hardware_reset_words(compiler)

    initialize_cold_boot_memory(compiler)

    return compiler

def run():
    import sys
    from .forth import ForthInterpreter
    import logging
    print(f"CELL_SIZE = {hex(CELL_SIZE)}")
    print(f"VOCSS = {hex(VOCSS)}")
    print(f"EM = {hex(EM)}")
    print(f"COLDD = {hex(COLDD)}")
    print(f"US = {hex(US)}")
    print(f"RTS = {hex(RTS)}")
    print(f"RPP = {hex(RPP)}")
    print(f"TIBB = {hex(TIBB)}")
    print(f"SPP = {hex(SPP)}")
    print(f"UPP = {hex(UPP)}")
    print(f"NAMEE = {hex(NAMEE)}")
    print(f"CODEE = {hex(CODEE)}")
    logging.basicConfig()
    logging.root.setLevel(logging.INFO)

    compiler = bootstrap_16bits_eforth()
    interpreter = ForthInterpreter(
                    compiler.cell_size,
                    input_stream=sys.stdin,
                    output_stream=sys.stdout,
                    # logger=logging,
                    compiler_metadata=compiler.compiler_metadata
                )
    interpreter.data_stack_pointer = SPP
    interpreter.return_stack_pointer = RPP
    interpreter.interpreter_pointer = compiler.code_address
    compiler.compile_word_body([WR("COLD")])
    interpreter.memory = compiler.memory
    try:
        interpreter.start()
    finally:
        print("Data stack:")
        for address in range(SPP, interpreter.data_stack_pointer, -compiler.cell_size):
            print("\t", interpreter.read_cell_at_address(address))
        print("\t^ TOP")

        print("Return stack:")
        for address in range(RPP, interpreter.return_stack_pointer-compiler.cell_size, -compiler.cell_size):
            address_on_stack = interpreter.read_cell_at_address(address)
            try:
                word_name = interpreter.compiler_metadata.word_address_belongs_to(address_on_stack).name
            except StopIteration:
                word_name = "(?)"
            print(f"\t{address_on_stack} ({word_name})")
        print("\t^ TOP")

        print("User variables:")
        for address in range(UPP, UPP+compiler.user_address, compiler.cell_size):
            print("\t", hex(interpreter.read_cell_at_address(address)))
        
        print("TIB[0:10]:")
        for address in range(TIBB, TIBB+10*compiler.cell_size, compiler.cell_size):
            print(f"\t{hex(interpreter.memory[address])} ({chr(interpreter.memory[address])})")

if __name__ == "__main__":
    run()
    # from more_itertools import grouper, peekable
    # c = bootstrap_16bits_eforth()
    # name_tokens_iterator = peekable(c.name_tokens_iterator())
    # try:
    #     while True:
    #         name_token = next(name_tokens_iterator)
    #         next_name_token = name_tokens_iterator.peek()
    #         first_xt_address = c.read_execution_token_address(name_token)
    #         cells_to_show = 20
    #         # last_xt_address = c.read_execution_token_address(next_name_token)
    #         print(c.read_word_name(name_token), " xt: ", hex(first_xt_address))
    #         print([hex(x) for x in range(first_xt_address,first_xt_address+cells_to_show*c.cell_size,c.cell_size)])
    #         print([hex((b1<<8)|b2) for b1,b2 in grouper(c.memory[first_xt_address:first_xt_address+cells_to_show*c.cell_size], c.cell_size)])
    #         # print("---")
    #         # print([hex(x) for x in range(last_xt_address,first_xt_address+c.cell_size,c.cell_size)])
    #         # print([hex((b1<<8)|b2) for b1,b2 in grouper(c.memory[last_xt_address:first_xt_address+c.cell_size], c.cell_size)])
    #         print("####")
    # except StopIteration:
    #     print("Finished listing words")
    
    # xt = c.read_execution_token_address(c.lookup_word(WordReference("?DUP")))
    # print(c.memory[xt:xt+6])
    # print([hex(x) for x in range(0x348,0x348+18,2)])
    # print([hex((b1<<8)|b2) for b1,b2 in grouper(c.memory[0x348:0x348+18], 2)])