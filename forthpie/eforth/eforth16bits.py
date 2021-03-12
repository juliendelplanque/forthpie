import sys
import logging

from ..forth import Memory, ForthInterpreter, StatisticsInterpreter, OptimizedInterpreter
from ..compiler import ImageCompiler
from ..model import WR
from .images.by_the_book import by_the_book_eforth_image
from .primitives.by_the_book import primitives_store as by_the_book_primitives_store
from .compiler.by_the_book import Compiler

CELL_SIZE = 2
VOCSS = 8

EM = 0x4000
COLDD = 0x100
US = 64*CELL_SIZE # user area size in cells
RTS = 64*CELL_SIZE # return stack/TIB size
RPP = EM-8*CELL_SIZE # 0x3F7F # start of return stack (RP0)
TIBB = RPP-RTS # 0x3E80 # terminal input buffer (TIB)
SPP = TIBB-8*CELL_SIZE # 0x3E7F # start of data stack (SP0)
UPP = EM-256*CELL_SIZE # 0x3F80 # start of user area (UP0)
NAMEE = UPP-8*CELL_SIZE # 0x3BFF # name dictionary
CODEE = COLDD+US # 0x180 # code dictionary

primitives_store = by_the_book_primitives_store()

def bootstrap_16bits_eforth():
    compiler = Compiler(
        cell_size=CELL_SIZE,
        initial_code_address=CODEE,
        initial_name_address=NAMEE,
        initial_user_address=4*CELL_SIZE,
        # memory=Memory(EM),
        memory=Memory(0x8000), #More memory for the heap!
        primitives_provider=primitives_store)

    image = by_the_book_eforth_image(
        start_of_data_stack_address=SPP,
        start_of_return_stack_address=RPP,
        start_of_user_area_address=UPP,
        number_of_vocabularies=VOCSS,
        cell_size=CELL_SIZE,
        lexicon_mask=compiler.LEXICON_MASK,
        immediate_bit=compiler.IMMEDIATE,
        compile_only_bit=compiler.COMPILE_ONLY,
        doLISTCode=5, #TODO: do not hardcode
        version_number=0,
        terminal_input_buffer_address=TIBB,
        cold_boot_address=COLDD,
        include_tools_wordset=True
    )

    ImageCompiler(compiler).visit_Image(image)

    return compiler

def run():
    # print(f"CELL_SIZE = {hex(CELL_SIZE)}")
    # print(f"VOCSS = {hex(VOCSS)}")
    # print(f"EM = {hex(EM)}")
    # print(f"COLDD = {hex(COLDD)}")
    # print(f"US = {hex(US)}")
    # print(f"RTS = {hex(RTS)}")
    # print(f"RPP = {hex(RPP)}")
    # print(f"TIBB = {hex(TIBB)}")
    # print(f"SPP = {hex(SPP)}")
    # print(f"UPP = {hex(UPP)}")
    # print(f"NAMEE = {hex(NAMEE)}")
    # print(f"CODEE = {hex(CODEE)}")
    logging.basicConfig()
    logging.root.setLevel(logging.WARNING)

    compiler = bootstrap_16bits_eforth()
    # interpreter_class = ForthInterpreter
    # interpreter_class = StatisticsInterpreter
    interpreter_class = OptimizedInterpreter
    interpreter = interpreter_class(
                    cell_size=compiler.cell_size,
                    primitives=primitives_store,
                    data_stack_pointer=SPP,
                    return_stack_pointer=RPP,
                    input_stream=sys.stdin,
                    output_stream=sys.stdout,
                    logger=logging,
                    compiler_metadata=compiler.compiler_metadata
                )
    interpreter.interpreter_pointer = compiler.code_address
    compiler.compile_word_body([WR("COLD")])
    interpreter.memory = compiler.memory
    try:
        interpreter.start()
        print(interpreter.execution_statistics.word_names_to_count(compiler.compiler_metadata))
    finally:
        interpreter.print_data_stack()

        interpreter.print_return_stack()

        print("User variables:")
        for address in range(UPP, UPP+compiler.user_address, compiler.cell_size):
            print(f"\t{hex(address)}: ", hex(interpreter.read_cell_at_address(address)))

        print("TIB[0:10]:")
        for address in range(TIBB, TIBB+10):
            print(f"\t{hex(interpreter.memory[address])} ({chr(interpreter.memory[address])})")

if __name__ == "__main__":
    run()