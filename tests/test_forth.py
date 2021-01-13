import pytest
import io

from forthpie.forth import *

@pytest.fixture
def interpreter():
    yield ForthInterpreter(4, 100)

def test_registers_are_set_to_0(interpreter):

    assert interpreter.interpreter_pointer == 0
    assert interpreter.data_stack_pointer == 0
    assert interpreter.return_stack_pointer == 0
    assert interpreter.word_pointer == 0

def test_read_cell_at_address(interpreter):

    interpreter.memory[50] = 1
    interpreter.memory[51] = 2
    interpreter.memory[52] = 3
    interpreter.memory[53] = 4

    assert interpreter.read_cell_at_address(50) == (1 << 24) | (2 << 16) | (3 << 8) | 4

def test_write_cell_at_address(interpreter):

    interpreter.write_cell_at_address(50, 0x01020304)

    assert interpreter.memory[50] == 1
    assert interpreter.memory[51] == 2
    assert interpreter.memory[52] == 3
    assert interpreter.memory[53] == 4

def test_lookup_primitive(interpreter):

    bye = interpreter.lookup_primitive(0)

    assert bye.function.__name__ == "bye"

def test_cell_all_bit_at_one(interpreter):

    assert interpreter.cell_all_bit_at_one() == 0xFFFFFFFF

def test_imrx_no_input(interpreter):
    interpreter.data_stack_pointer = 50

    # Initialize interpreter
    interpreter.interpreter_pointer = 70

    # Address of a code word located at address 90 in memory
    interpreter.memory[70] = 0
    interpreter.memory[71] = 0
    interpreter.memory[72] = 0
    interpreter.memory[73] = 90
    # Address of a code word located at address 94 in memory
    interpreter.memory[74] = 0
    interpreter.memory[75] = 0
    interpreter.memory[76] = 0
    interpreter.memory[77] = 94

    # txem primitive code
    interpreter.memory[90] = 0
    interpreter.memory[91] = 0
    interpreter.memory[92] = 0
    interpreter.memory[93] = 1
    # bye primitive code
    interpreter.memory[94] = 0
    interpreter.memory[95] = 0
    interpreter.memory[96] = 0
    interpreter.memory[97] = 0

    interpreter.next()

    assert interpreter.memory[50:54] == [0,0,0,0]
    assert interpreter.word_pointer == 94
    assert interpreter.interpreter_pointer == 78
    assert interpreter.data_stack_pointer == 54

def test_imrx_input(interpreter):
    interpreter.data_stack_pointer = 50
    interpreter.input_stream = io.StringIO("a")

    # Initialize interpreter
    interpreter.interpreter_pointer = 70

    # Address of a code word located at address 90 in memory
    interpreter.memory[70] = 0
    interpreter.memory[71] = 0
    interpreter.memory[72] = 0
    interpreter.memory[73] = 90
    # Address of a code word located at address 94 in memory
    interpreter.memory[74] = 0
    interpreter.memory[75] = 0
    interpreter.memory[76] = 0
    interpreter.memory[77] = 94

    # txem primitive code
    interpreter.memory[90] = 0
    interpreter.memory[91] = 0
    interpreter.memory[92] = 0
    interpreter.memory[93] = 1
    # bye primitive code
    interpreter.memory[94] = 0
    interpreter.memory[95] = 0
    interpreter.memory[96] = 0
    interpreter.memory[97] = 0

    interpreter.next()
    
    assert interpreter.memory[50:54] == [0,0,0,97]
    assert interpreter.memory[54:58] == [0xFF,0xFF,0xFF,0xFF]
    assert interpreter.word_pointer == 94
    assert interpreter.interpreter_pointer == 78
    assert interpreter.data_stack_pointer == 58

def test_txem(interpreter):
    # Initialize data stack
    interpreter.data_stack_pointer = 54

    interpreter.memory[50] = 0
    interpreter.memory[51] = 0
    interpreter.memory[52] = 0
    interpreter.memory[53] = 97

    # Initialize interpreter
    interpreter.interpreter_pointer = 70

    # Address of a code word located at address 90 in memory
    interpreter.memory[70] = 0
    interpreter.memory[71] = 0
    interpreter.memory[72] = 0
    interpreter.memory[73] = 90
    # Address of a code word located at address 94 in memory
    interpreter.memory[74] = 0
    interpreter.memory[75] = 0
    interpreter.memory[76] = 0
    interpreter.memory[77] = 94

    # txem primitive code
    interpreter.memory[90] = 0
    interpreter.memory[91] = 0
    interpreter.memory[92] = 0
    interpreter.memory[93] = 2
    # bye primitive code
    interpreter.memory[94] = 0
    interpreter.memory[95] = 0
    interpreter.memory[96] = 0
    interpreter.memory[97] = 0

    interpreter.next()

    assert interpreter.data_stack_pointer == 50
    interpreter.output_stream.seek(0)
    assert interpreter.output_stream.read(1) == "a"

def test_next(interpreter):
    interpreter.interpreter_pointer = 50

    # Address of a code word located at address 90 in memory
    interpreter.memory[50] = 0
    interpreter.memory[51] = 0
    interpreter.memory[52] = 0
    interpreter.memory[53] = 90

    # bye primitive code
    interpreter.memory[90] = 0
    interpreter.memory[91] = 0
    interpreter.memory[92] = 0
    interpreter.memory[93] = 0

    interpreter.next()

    assert interpreter.word_pointer == 90
    assert interpreter.interpreter_pointer == 54

def test_doLIT(interpreter):
    interpreter.interpreter_pointer = 50
    interpreter.data_stack_pointer = 70

    # Address of a code word located at address 90 in memory
    interpreter.memory[50] = 0
    interpreter.memory[51] = 0
    interpreter.memory[52] = 0
    interpreter.memory[53] = 90
    # Literal to push on stack
    interpreter.memory[54] = 1
    interpreter.memory[55] = 2
    interpreter.memory[56] = 3
    interpreter.memory[57] = 4
    # Address of a code word located at address 90 in memory
    interpreter.memory[58] = 0
    interpreter.memory[59] = 0
    interpreter.memory[60] = 0
    interpreter.memory[61] = 94

    # doLIT primitive code
    interpreter.memory[90] = 0
    interpreter.memory[91] = 0
    interpreter.memory[92] = 0
    interpreter.memory[93] = 4
    # bye primitive code
    interpreter.memory[94] = 0
    interpreter.memory[95] = 0
    interpreter.memory[96] = 0
    interpreter.memory[97] = 0
    
    interpreter.next()

    assert interpreter.word_pointer == 94
    assert interpreter.interpreter_pointer == 62
    assert interpreter.data_stack_pointer == 74
    assert interpreter.read_cell_at_address(70) == 0x01020304
