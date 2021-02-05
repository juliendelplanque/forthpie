from .forth import Memory
from .compiler import Compiler, WordReference, Label, LabelReference

CELL_SIZE = 2

EM = 0x4000
COLDD = 0x100
US = 64*CELL_SIZE # user area size in cells
RTS = 64*CELL_SIZE # return stack/TIB size
RPP = EM-8*CELL_SIZE # start of return stack (RP0)
TIBB = RPP-RTS # terminal input buffer (TIB)
SPP = TIBB-8*CELL_SIZE # start of data stack (SP0)
UPP = EM-256*CELL_SIZE # start of user area (UP0)
NAMEE = UPP-8*CELL_SIZE # name dictionary
CODEE = COLDD+US #code dictionary

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

def bootstrap_16bits_eforth():
    COMPILE_ONLY = Compiler.COMPILE_ONLY
    IMMEDIATE = Compiler.IMMEDIATE
    compiler = Compiler(
        cell_size=CELL_SIZE,
        initial_code_address=0x180,
        initial_name_address=0x3BFF,
        initial_user_address=0x3F80,
        memory=Memory(0x3FFF+1))
    
    # Kernel
    compiler.compile_primitive("BYE")
    compiler.compile_primitive("?RX")
    compiler.compile_primitive("TX!")
    compiler.compile_primitive("!IO")
    compiler.compile_primitive("doLIT", COMPILE_ONLY)
    compiler.compile_primitive("doLIST", COMPILE_ONLY)
    compiler.compile_primitive("EXIT")
    compiler.compile_primitive("EXECUTE")
    compiler.compile_primitive("next", COMPILE_ONLY)
    compiler.compile_primitive("?branch", COMPILE_ONLY)
    compiler.compile_primitive("branch", COMPILE_ONLY)
    compiler.compile_primitive("!")
    compiler.compile_primitive("@")
    compiler.compile_primitive("C!")
    compiler.compile_primitive("C@")
    compiler.compile_primitive("RP@")
    compiler.compile_primitive("RP!", COMPILE_ONLY)
    compiler.compile_primitive("R>")
    compiler.compile_primitive("R@")
    compiler.compile_primitive(">R", COMPILE_ONLY)
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

    # System and user variables
    compiler.compile_colon("doVAR",
        [WR("R>"), (WR("EXIT"))],
        COMPILE_ONLY)

    compiler.compile_colon("UP",
        [WR("doVAR"), UPP])
    compiler.compile_colon("+",
        WR("UM+", "DROP", "EXIT"))
    compiler.compile_colon("doUSER",
        WR("R>", "@", "UP", "@", "+", "EXIT"),
        COMPILE_ONLY)
    compiler.compile_user("SP0")
    compiler.compile_user("RP0")
    compiler.compile_user("'?KEY")
    compiler.compile_user("'EMIT")
    compiler.compile_user("'EXPECT")
    compiler.compile_user("'TAP")
    compiler.compile_user("'ECHO")
    compiler.compile_user("'PROMPT")
    compiler.compile_user("BASE")
    compiler.compile_user("tmp", COMPILE_ONLY)
    compiler.compile_user("SPAN")
    compiler.compile_user(">IN")
    compiler.compile_user("#TIB", cells=2)
    compiler.compile_user("CSP")
    compiler.compile_user("'EVAL")
    compiler.compile_user("'NUMBER")
    compiler.compile_user("HLD")
    compiler.compile_user("HANDLER")
    compiler.compile_user("CONTEXT")
    compiler.compile_user("CURRENT", cells=2)
    compiler.compile_user("CP")
    compiler.compile_user("NP")
    compiler.compile_user("LAST")
    compiler.compile_colon("doVOC",
        WR("R>", "CONTEXT", "!", "EXIT"),
        COMPILE_ONLY)
    compiler.compile_colon("FORTH",
        [WR("doVOC"), 0, 0]
    )
    
    # Common functions
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
    # + is defined above because doUser requires it
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
    
    # Comparison
    compiler.compile_colon("=",
        [WR("XOR"),
        WR("?branch"), LR("=1"),
        WR("doLIT"), 0, WR("EXIT"),
        L("=1"), WR("doLIT"), -1, WR("EXIT")]
    )
    compiler.compile_colon("U<",
        [WR("2DUP"), WR("XOR"), WR("0<"),
        WR("?branch"), LR("U<1"),
        WR("SWAP"), WR("DROP"), WR("0<"), WR("EXIT"),
        L("U<1"), WR("-"), WR("0<"), WR("EXIT")]
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
    # Multiply
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

    # Memory Alignment
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

    # Memory Access
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

    # Numeric output, single precision
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

    # Numeric input, single precision
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

    # Basic I/O
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
        WR("2DROP"), WR("KEY"), WR("doLIT"), 13, WR("="), # 13 = CR
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
        COMPILE_ONLY
    )
    compiler.compile_colon('$"|',
        [WR("do$"), WR("EXIT")],
        COMPILE_ONLY
    )
    compiler.compile_colon('."|',
        [WR("do$"), WR("COUNT"), WR("TYPE"), WR("EXIT")],
        COMPILE_ONLY
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

    # Parsing
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
        IMMEDIATE
    )
    compiler.compile_colon("(",
        [WR("doLIT"), ord(')'), WR("PARSE"), WR("2DROP"), WR("EXIT")],
        IMMEDIATE
    )
    compiler.compile_colon("\\",
        [WR("#TIB"), WR("@"), WR(">IN"), WR("!"), WR("EXIT")],
        IMMEDIATE
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

    # Dictionary search
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
    L("SAME2"), WR("next"), WR("SAME1"),
        WR("doLIT"), 0, WR("EXIT")]
    )
    compiler.compile_colon("find",
        [WR("SWAP"), WR("DUP"), WR("C@"),
        WR("doLIT"), compiler.cell_size, WR("/"), WR("tmp"), WR("!")]
    )
    compiler.compile_colon("NAME?",
        [WR("CONTEXT"), WR("DUP"), WR("2@"), WR("XOR"),
        WR("?branch"), LR("NAMQ1"),
        WR("CELL-"),
    L("NAMQ1"), WR(">R"),
    L("NAMQ2"), WR("R>"), WR("CELL+"), WR("DUP"), WR(">R"),
        WR("@"), WR("?DUP"),
        WR("?branch"), LR("NAMQ3")
        WR("find"), WR("?DUP"),
        WR("?branch"), LR("NAMQ2"),
        WR("R>"), WR("DROP"), WR("EXIT"),
    L("NAMQ3"), WR("R>"), WR("DROP"),
        WR("doLIT"), 0, WR("EXIT")]
    )

    # Terminal response
    compiler.compile_colon("^H",
        []#TODO
    )
    compiler.compile_colon("TAP",
        []#TODO
    )
    compiler.compile_colon("kTAP",
        []#TODO
    )
    compiler.compile_colon("accept",
        []#TODO
    )
    compiler.compile_colon("EXPECT",
        []#TODO
    )
    compiler.compile_colon("QUERY",
        []#TODO
    )

    # Error handling
    compiler.compile_colon("CATCH",
        []#TODO
    )
    compiler.compile_colon("THROW",
        []#TODO
    )
    compiler.compile_colon("NULL$",
        []#TODO
    )
    compiler.compile_colon("ABORT",
        []#TODO
    )
    compiler.compile_colon('abort"',
        [],#TODO
        COMPILE_ONLY
    )

    # The text interpreter
    compiler.compile_colon("$INTERPRET",
        []#TODO
    )
    compiler.compile_colon("[",
        [],#TODO
        IMMEDIATE
    )
    compiler.compile_colon(".OK",
        []#TODO
    )
    compiler.compile_colon("?STACK",
        []#TODO
    )
    compiler.compile_colon("EVAL",
        []#TODO
    )

    # Shell
    compiler.compile_colon("PRESET",
        []#TODO
    )
    compiler.compile_colon("xio",
        [],#TODO
        COMPILE_ONLY
    )
    compiler.compile_colon("FILE",
        []#TODO
    )
    compiler.compile_colon("HAND",
        []#TODO
    )
    compiler.compile_colon("I/O",
        []#TODO
    )
    compiler.compile_colon("CONSOLE",
        []#TODO
    )
    compiler.compile_colon("QUIT",
        []#TODO
    )

    # The compiler
    compiler.compile_colon("'",
        []#TODO
    )
    compiler.compile_colon("ALLOT",
        []#TODO
    )
    compiler.compile_colon(",",
        []#TODO
    )
    compiler.compile_colon("[COMPILE]",
        [],#TODO
        IMMEDIATE
    )
    compiler.compile_colon("COMPILE",
        [],#TODO
        COMPILE_ONLY
    )
    compiler.compile_colon("LITERAL",
        [],#TODO
        IMMEDIATE
    )
    compiler.compile_colon("$,",
        []#TODO
    )
    compiler.compile_colon("RECURSE",
        [],#TODO
        IMMEDIATE
    )
    
    # Structures
    compiler.compile_colon("FOR",
        [],#TODO
        IMMEDIATE
    )
    compiler.compile_colon("BEGIN",
        [],#TODO
        IMMEDIATE
    )
    compiler.compile_colon("NEXT",
        [],#TODO
        IMMEDIATE
    )
    compiler.compile_colon("UNTIL",
        [],#TODO
        IMMEDIATE
    )
    compiler.compile_colon("AGAIN",
        [],#TODO
        IMMEDIATE
    )
    compiler.compile_colon("IF",
        [],#TODO
        IMMEDIATE
    )
    compiler.compile_colon("AHEAD",
        [],#TODO
        IMMEDIATE
    )
    compiler.compile_colon("REPEAT",
        [],#TODO
        IMMEDIATE
    )
    compiler.compile_colon("THEN",
        [],#TODO
        IMMEDIATE
    )
    compiler.compile_colon("AFT",
        [],#TODO
        IMMEDIATE
    )
    compiler.compile_colon("ELSE",
        [],#TODO
        IMMEDIATE
    )
    compiler.compile_colon("WHILE",
        [],#TODO
        IMMEDIATE
    )
    compiler.compile_colon('ABORT"',
        [],#TODO
        IMMEDIATE
    )
    compiler.compile_colon('$"',
        [],#TODO
        IMMEDIATE
    )
    compiler.compile_colon('."',
        [],#TODO
        IMMEDIATE
    )

    # Name compiler
    compiler.compile_colon("?UNIQUE",
        []#TODO
    )
    compiler.compile_colon("$,n",
        []#TODO
    )

    # Forth compiler
    compiler.compile_colon("$COMPILE",
        []#TODO
    )
    compiler.compile_colon("OVERT",
        []#TODO
    )
    compiler.compile_colon(";",
        [],#TODO
        IMMEDIATE+COMPILE_ONLY
    )
    compiler.compile_colon("]",
        []#TODO
    )
    compiler.compile_colon("call,",
        []#TODO
    )
    compiler.compile_colon(":",
        []#TODO
    )
    compiler.compile_colon("IMMEDIATE",
        []#TODO
    )

    # Defining words
    compiler.compile_colon("USER",
        []#TODO
    )
    compiler.compile_colon("CREATE",
        []#TODO
    )
    compiler.compile_colon("VARIABLE",
        []#TODO
    )

    # Tools
    compiler.compile_colon("_TYPE",
        []#TODO
    )
    compiler.compile_colon("dm+",
        []#TODO
    )
    compiler.compile_colon("DUMP",
        []#TODO
    )
    compiler.compile_colon(".S",
        []#TODO
    )
    compiler.compile_colon("!CSP",
        []#TODO
    )
    compiler.compile_colon("?CSP",
        []#TODO
    )
    compiler.compile_colon(">NAME",
        []#TODO
    )
    compiler.compile_colon(".ID",
        []#TODO
    )
    compiler.compile_colon("SEE",
        []#TODO
    )
    compiler.compile_colon("WORDS",
        []#TODO
    )

    # Hardware reset
    compiler.compile_colon("VER",
        []#TODO
    )
    compiler.compile_colon("hi",
        []#TODO
    )
    compiler.compile_colon("'BOOT",
        []#TODO
    )
    compiler.compile_colon("COLD",
        []#TODO
    )

    # compiler.compile_colon("",
    #     []#TODO
    # )

    # Initialize memory with default user variable values
    # TODO
    # init_values = [
    #     SPP,
    #     RPP,
        
    # ]
    # for address, value in zip(range(COLDD, compiler.cell_size*len(init_values), compiler.cell_size), init_values):
    #     compiler.write_cell_at_address(address, value)

    return compiler

if __name__ == "__main__":
    from more_itertools import grouper, peekable
    c = bootstrap_16bits_eforth()
    name_tokens_iterator = peekable(c.name_tokens_iterator())
    try:
        while True:
            name_token = next(name_tokens_iterator)
            next_name_token = name_tokens_iterator.peek()
            first_xt_address = c.read_execution_token_address(name_token)
            cells_to_show = 20
            # last_xt_address = c.read_execution_token_address(next_name_token)
            print(c.read_word_name(name_token), " xt: ", hex(first_xt_address))
            print([hex(x) for x in range(first_xt_address,first_xt_address+cells_to_show*c.cell_size,c.cell_size)])
            print([hex((b1<<8)|b2) for b1,b2 in grouper(c.memory[first_xt_address:first_xt_address+cells_to_show*c.cell_size], c.cell_size)])
            # print("---")
            # print([hex(x) for x in range(last_xt_address,first_xt_address+c.cell_size,c.cell_size)])
            # print([hex((b1<<8)|b2) for b1,b2 in grouper(c.memory[last_xt_address:first_xt_address+c.cell_size], c.cell_size)])
            print("####")
    except StopIteration:
        print("Finished listing words")
    
    # xt = c.read_execution_token_address(c.lookup_word(WordReference("?DUP")))
    # print(c.memory[xt:xt+6])
    # print([hex(x) for x in range(0x348,0x348+18,2)])
    # print([hex((b1<<8)|b2) for b1,b2 in grouper(c.memory[0x348:0x348+18], 2)])