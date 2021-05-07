import sys
import logging

from ..forth import Memory
from .. import forth as interpreters
from ..compiler import ImageCompiler
from ..model import WR
# from .images.by_the_book import by_the_book_eforth_image as image_builder
from .images.forthpie import forthpie_eforth_image as image_builder
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

    image = image_builder(
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

def run(interpreter_class, memory, cell_size, compiler_metadata=None, log_level=logging.WARNING):
    logging.root.setLevel(log_level)
    interpreter = interpreter_class(
                    cell_size=cell_size,
                    primitives=primitives_store,
                    data_stack_pointer=SPP,
                    return_stack_pointer=RPP,
                    input_stream=sys.stdin,
                    output_stream=sys.stdout,
                    logger=logging,
                    compiler_metadata=compiler_metadata
                )
    interpreter.memory = memory
    interpreter.interpreter_pointer = interpreter.read_cell_at_address(COLDD)
    # print(interpreter.read_cell_at_address(COLDD))
    if interpreter.read_cell_at_address(COLDD+2*cell_size) != 0:
        interpreter.data_stack_pointer = interpreter.read_cell_at_address(COLDD+2*cell_size)
    # print(interpreter.data_stack_pointer)
    if interpreter.read_cell_at_address(COLDD+3*cell_size) != 0:
        interpreter.return_stack_pointer = interpreter.read_cell_at_address(COLDD+3*cell_size)
    # print(interpreter.return_stack_pointer)

    try:
        interpreter.start()
        # print(interpreter.execution_statistics.word_names_to_count(compiler.compiler_metadata))
    finally:
        pass
        # interpreter.print_data_stack()

        # interpreter.print_return_stack()

        # print("User variables:")
        # for address in range(UPP, UPP+compiler.user_address, compiler.cell_size):
        #     print(f"\t{hex(address)}: ", hex(interpreter.read_cell_at_address(address)))

        # print("TIB[0:10]:")
        # for address in range(TIBB, TIBB+10):
        #     print(f"\t{hex(interpreter.memory[address])} ({chr(interpreter.memory[address])})")

def boostrap_run(interpreter_class, log_level=logging.WARNING):
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

    compiler = bootstrap_16bits_eforth()
    run(
        interpreter_class,
        compiler.memory,
        cell_size=compiler.cell_size,
        compiler_metadata=compiler.compiler_metadata,
        log_level=log_level
    )

if __name__ == "__main__":
    from docopt import docopt
    arguments = docopt(
"""EForth with 16bits cell-size.

Usage:
  eforth16bits.py run [--log=<level>] [--interpreter=<name>] <file_path>
  eforth16bits.py bootstrap-run [--log=<level>] [--interpreter=<name>]
  eforth16bits.py bootstrap <file_path>

Options:
  --log=<level>         Log level for the VM [default: WARNING].
  --interpreter=<name>  Specify which interpreter to use [default: OptimizedInterpreter].

""")
    logging.basicConfig()
    if arguments["run"]:
        memory = Memory.from_file(arguments["<file_path>"])
        run(
            getattr(interpreters, arguments["--interpreter"]),
            memory,
            cell_size=2,
            log_level=getattr(logging, arguments["--log"].upper())
        )
    elif arguments["bootstrap-run"]:
        boostrap_run(
            getattr(interpreters, arguments["--interpreter"]),
            log_level=getattr(logging, arguments["--log"].upper())
        )
    elif arguments["bootstrap"]:
        compiler = bootstrap_16bits_eforth()
        compiler.memory.save(arguments["<file_path>"])
