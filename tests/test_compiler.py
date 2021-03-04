import pytest

from forthpie.forth import Memory
from forthpie.model import WordReference
from forthpie.eforth.primitives.by_the_book import primitives_store
from forthpie.eforth.compiler.by_the_book import Compiler

@pytest.fixture
def compiler():
    """Yields a compiler for EForth with 2 bytes cells and a
        memory layout similar to the one described in the book.
    """
    yield Compiler(
        cell_size=2,
        primitives_provider=primitives_store,
        initial_code_address=0x180,
        initial_name_address=0x3BFF,
        initial_user_address=0x3F80,
        memory=Memory(0x3FFF+1))

def test_compile_name_header(compiler):
    expected_new_name_address = compiler.name_address - (compiler.cell_size*(2+1)+len("testWord"))
    compiler.compile_name_header(0b01000000, "testWord")

    assert compiler.name_address == expected_new_name_address
    assert compiler.read_cell_at_address(compiler.name_address) == 0x180
    assert compiler.read_cell_at_address(compiler.name_address+compiler.cell_size) == 0x3BFF
    assert compiler.memory[(compiler.name_address+2*compiler.cell_size)] == (len("testWord")|0b01000000)
    assert compiler.memory[(compiler.name_address+2*compiler.cell_size)+1:(compiler.name_address+2*compiler.cell_size)+1+len("testWord")] == [ord(c) for c in "testWord"]
    assert (compiler.name_address+2*compiler.cell_size)+1+len("testWord")+1 == 0x3BFF
    assert compiler.memory[0x3BFF] == 0 # padding byte

def test_compile_colon_header(compiler):
    expected_new_code_address = compiler.code_address + compiler.cell_size
    expected_new_name_address = compiler.name_address - (compiler.cell_size*2 +1+len("testWord")+1)
    compiler.compile_colon_header(0b01000000, "testWord")

    assert compiler.name_address == expected_new_name_address
    assert compiler.read_cell_at_address(compiler.name_address) == 0x180
    assert compiler.read_cell_at_address(compiler.name_address+compiler.cell_size) == 0x3BFF
    assert compiler.memory[(compiler.name_address+2*compiler.cell_size)] == (len("testWord")|0b01000000)
    assert compiler.memory[(compiler.name_address+2*compiler.cell_size)+1:(compiler.name_address+2*compiler.cell_size)+1+len("testWord")] == [ord(c) for c in "testWord"]
    assert (compiler.name_address+2*compiler.cell_size)+1+len("testWord")+1 == 0x3BFF
    assert compiler.memory[0x3BFF] == 0 # padding byte

    assert compiler.code_address == expected_new_code_address
    assert compiler.read_cell_at_address(compiler.code_address - compiler.cell_size) == compiler.get_primitive_by_name("doLIST").code

def test_compile_user_header(compiler):
    compiler.compile_colon_header(0b000, "doUSER")
    doUser_name_address = compiler.name_address
    expected_new_code_address = compiler.code_address + 3*compiler.cell_size
    expected_new_name_address = compiler.name_address - (compiler.cell_size*2 +1+len("testUser")+1)
    expected_new_user_address = compiler.user_address + compiler.cell_size

    compiler.compile_user_header(0b01000000, "testUser")

    assert compiler.name_address == expected_new_name_address
    assert compiler.read_cell_at_address(compiler.name_address) == 0x182
    assert compiler.read_cell_at_address(compiler.name_address+compiler.cell_size) == doUser_name_address
    assert compiler.memory[(compiler.name_address+2*compiler.cell_size)] == (len("testUser")|0b01000000)
    assert compiler.memory[(compiler.name_address+2*compiler.cell_size)+1:(compiler.name_address+2*compiler.cell_size)+1+len("testUser")] == [ord(c) for c in "testUser"]
    assert (compiler.name_address+2*compiler.cell_size)+1+len("testUser")+1 == doUser_name_address
    assert compiler.memory[0x3BFF] == 0 # padding byte

    assert compiler.code_address == expected_new_code_address
    assert compiler.read_cell_at_address(0x180) == compiler.get_primitive_by_name("doLIST").code
    assert compiler.read_cell_at_address(0x182) == compiler.get_primitive_by_name("doLIST").code
    assert compiler.read_cell_at_address(0x184) == compiler.lookup_word(WordReference("doUSER"))
    assert compiler.read_cell_at_address(0x186) == 0x3F80

    assert compiler.user_address == expected_new_user_address