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
    compiler.compile_primitive("RP!")
    compiler.compile_primitive("R>")
    compiler.compile_primitive("R@")
    compiler.compile_primitive(">R")
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
    )
    compiler.compile_colon("DEPTH",
        [WR("SP@"), WR("SP0"), WR("@"), WR("SWAP"), WR("-"),
        WR("doLIT"), compiler.cell_size, WR("/"), WR("EXIT")]
    )
    compiler.compile_colon("PICK",
        [WR("doLIT"), 1, WR("+"), WR("CELLS"),
        WR("SP@"), WR("+"), WR("@"), WR("EXIT")]
    )

    # # Memory Access
    # compiler.compile_colon("+!",
    #     []#TODO
    # )
    # compiler.compile_colon("2!",
    #     []#TODO
    # )
    # compiler.compile_colon("2@",
    #     []#TODO
    # )
    # compiler.compile_colon("COUNT",
    #     []#TODO
    # )
    # compiler.compile_colon("HERE",
    #     []#TODO
    # )
    # compiler.compile_colon("PAD",
    #     []#TODO
    # )
    # compiler.compile_colon("TIB",
    #     []#TODO
    # )
    # compiler.compile_colon("@EXECUTE",
    #     []#TODO
    # )
    # compiler.compile_colon("CMOVE",
    #     []#TODO
    # )
    # compiler.compile_colon("FILL",
    #     []#TODO
    # )
    # compiler.compile_colon("-TRAILING",
    #     []#TODO
    # )
    # compiler.compile_colon("PACK$",
    #     []#TODO
    # )

    # #
    # compiler.compile_colon("",
    #     []#TODO
    # )

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