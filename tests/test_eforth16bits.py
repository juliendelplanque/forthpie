import pytest
import logging

from forthpie.forth import ForthInterpreter
from forthpie.eforth.primitives.by_the_book import primitives_store
from forthpie.compiler import WordReference
WR = WordReference
import forthpie.eforth16bits as eforth16bits

@pytest.mark.parametrize("to_compile, expected_data_stack",
    [
        pytest.param(
            [WordReference("doLIT"),1,WordReference("doLIT"),2,WordReference("doLIT"),3,WordReference("BYE")],
            [1,2,3],
            id="doLIT"
        ),
        pytest.param(
            [WordReference("doLIT"), 1, WordReference("doLIT"), WordReference("DUP"), WordReference("EXECUTE")],
            [1, 1],
            id="1 ' DUP EXECUTE"
        ),
        pytest.param(
            [WordReference("doLIT"), 1, WordReference("doLIT"), WordReference("DUP"), WordReference("EXECUTE"), WordReference("DROP")],
            [1],
            id="1 ' DUP EXECUTE DROP"
        ),
        pytest.param(
            [WordReference("doLIT"), 1, WordReference("doLIT"), WordReference("DUP"), WordReference("EXECUTE"), WordReference("DROP"), WordReference("DROP")],
            [],
            id="1 ' DUP EXECUTE DROP DROP"
        ),
        pytest.param(
            [WordReference("doLIT"), 1, WordReference("doLIT"), 2, WordReference("doLIT"), WordReference("SWAP"), WordReference("EXECUTE")],
            [2, 1],
            id="1 2 ' SWAP EXECUTE"
        ),
        pytest.param(
            [WordReference("doLIT"),0b010101,WordReference("doLIT"),0b010001,WordReference("XOR"),WordReference("BYE")],
            [0b000100],
            id="XOR"
        ),
        pytest.param(
            [WordReference("doLIT"),0b010101,WordReference("doLIT"),0b010001,WordReference("OR"),WordReference("BYE")],
            [0b010101],
            id="OR"
        ),
        pytest.param(
            [WordReference("doLIT"),1,WordReference("doLIT"),1,WordReference("UM+"),WordReference("BYE")],
            [2,0],
            id="UMPlus"
        ),
        pytest.param(
            [WordReference("doLIT"),-1,WordReference("doLIT"),-1,WordReference("UM+"),WordReference("BYE")],
            [0xFFFE,0xFFFF],
            id="UMPlus-carry"
        ),
        pytest.param(
            [WordReference("doLIT"), -2, WordReference("doLIT"), 1, WordReference("UM+"),WordReference("BYE")],
            [0b1111111111111111, 0],
            id="UMPlus -2 + 1"
        ),
        pytest.param(
            [WordReference("doLIT"),42,WordReference("doLIT"),43,WordReference("SWAP"),WordReference("BYE")],
            [43,42],
            id="SWAP"
        ),
        pytest.param(
            [WordReference("doLIT"),42,WordReference("doLIT"),43,WordReference("OVER"),WordReference("BYE")],
            [42,43,42],
            id="OVER"
        ),
        pytest.param(
            [WordReference("doLIT"),43,WordReference("0<"),WordReference("BYE")],
            [0],
            id="0<"
        ),
        pytest.param(
            [WordReference("doLIT"),0b100000000000001,WordReference("0<"),WordReference("BYE")],
            [0xFFFF],
            id="0< -1"
        ),
        pytest.param(
            [WordReference("doLIT"),2, WordReference("NEGATE"), WordReference("0<"),WordReference("BYE")],
            [0xFFFF],
            id="0< 2 NEGATE"
        ),
        pytest.param(
            [WordReference("doLIT"), 42,WordReference("doLIT"), 43,WordReference("2DUP"),WordReference("BYE")],
            [42,43,42,43],
            id="2DUP"
        ),
        pytest.param(
            [WordReference("doLIT"), 1,WordReference("doLIT"), 2,WordReference("<"),WordReference("BYE")],
            [0xFFFF],
            id="1<2"
        ),
        pytest.param(
            [WordReference("doLIT"), 2,WordReference("doLIT"), 1,WordReference("<"),WordReference("BYE")],
            [0x0000],
            id="2<1"
        ),
        pytest.param(
            [WordReference("doLIT"), 1,WordReference("doLIT"), 2,WordReference("U<"),WordReference("BYE")],
            [0xFFFF],
            id="1 U< 2"
        ),
        pytest.param(
            [WordReference("doLIT"), 2,WordReference("doLIT"), 1,WordReference("U<"),WordReference("BYE")],
            [0x0000],
            id="2 U< 1"
        ),
        pytest.param(
            [WordReference("doLIT"), 2,WordReference("doLIT"), -1,WordReference("U<"),WordReference("BYE")],
            [0xFFFF],
            id="2 U< -1"
        ),
        pytest.param(
            [WordReference("doLIT"), 1,WordReference("doLIT"), 2,WordReference("MIN"),WordReference("BYE")],
            [1],
            id="MIN"
        ),
        pytest.param(
            [WordReference("doLIT"), 1,WordReference("doLIT"), 2,WordReference("MAX"),WordReference("BYE")],
            [2],
            id="MAX"
        ),
        pytest.param(
            [WordReference("doLIT"), 0b010101010101010,WordReference("NOT"),WordReference("BYE")],
            [0b1101010101010101],
            id="NOT"
        ),
        pytest.param(
            [WordReference("doLIT"), 0b1,WordReference("NOT"),WordReference("BYE")],
            [0b1111111111111110],
            id="NOT 1"
        ),
        pytest.param(
            [WordReference("doLIT"), 1,WordReference("NEGATE"),WordReference("BYE")],
            [0xFFFF],
            id="1 NEGATE"
        ),
        pytest.param(
            [WordReference("doLIT"), 3,WordReference("NEGATE"),WordReference("BYE")],
            [0b1111111111111101],
            id="3 NEGATE"
        ),
        pytest.param(
            [WordReference("doLIT"), -1,WordReference("NEGATE"),WordReference("BYE")],
            [1],
            id="-1 NEGATE"
        ),
        pytest.param(
            [WordReference("doLIT"), -32768,WordReference("NEGATE"),WordReference("BYE")],
            [32768],
            id="-32768 NEGATE"
        ),
        pytest.param(
            [WordReference("doLIT"), -2, WordReference("doLIT"), 1, WordReference("+"),WordReference("BYE")],
            [0xFFFF],
            id="+"
        ),
        pytest.param(
            [WordReference("SP0"), WordReference("@")],
            [0],
            id="SP0 @"
        ),
        pytest.param(
            [WordReference("doLIT"), 42, WordReference("SP0"), WordReference("!"), WordReference("SP0"), WordReference("@")],
            [42],
            id="SP0 42 ! SP0 @"
        ),
        pytest.param(
            [WordReference("doLIT"), 1, WordReference("doLIT"), 1, WordReference("-"),WordReference("BYE")],
            [0],
            id="1-1"
        ),
        pytest.param(
            [WordReference("doLIT"), 0, WordReference("doLIT"), 1, WordReference("-"),WordReference("BYE")],
            [0b1111111111111111],
            id="0-1"
        ),
        pytest.param(
            [WordReference("doLIT"), 42, WordReference("doLIT"), 3, WordReference("-"),WordReference("BYE")],
            [39],
            id="42-3"
        ),
        pytest.param(
            [WordReference("doLIT"), 7, WordReference("doLIT"), 5, WordReference("doLIT"), 10,  WordReference("WITHIN"),WordReference("BYE")],
            [0xFFFF],
            id="7 5 10 WITHIN"
        ),
        pytest.param(
            [WordReference("doLIT"), 15, WordReference("doLIT"), 5, WordReference("doLIT"), 10, WordReference("WITHIN"),WordReference("BYE")],
            [0],
            id="15 5 10 WITHIN"
        ),
        pytest.param(
            [WordReference("doLIT"), 97, WordReference("doLIT"), 32, WordReference("doLIT"), 127, WordReference("WITHIN"),WordReference("BYE")],
            [0xFFFF],
            id="97 32 127 WITHIN"
        ),
        pytest.param(
            [WordReference("doLIT"), 1, WordReference("doLIT"), 2, WordReference("doLIT"), 3, WordReference("ROT"),WordReference("BYE")],
            [2, 3, 1],
            id="ROT"
        ),
        pytest.param(
            [WordReference("doLIT"), 0, WordReference("doLIT"), 0, WordReference("doLIT"), 1, WordReference("UM/MOD"),WordReference("BYE")],
            [0, 0],
            id="0 0 1 UM/MOD"
        ),
        pytest.param(
            [WordReference("doLIT"), 1, WordReference("doLIT"), 0, WordReference("doLIT"), 1, WordReference("UM/MOD"),WordReference("BYE")],
            [0, 1],
            id="1 0 1 UM/MOD"
        ),
        pytest.param(
            [WordReference("doLIT"), 1, WordReference("doLIT"), 0, WordReference("doLIT"), 2, WordReference("UM/MOD"),WordReference("BYE")],
            [1, 0],
            id="1 0 2 UM/MOD"
        ),
        pytest.param(
            [WordReference("doLIT"), 3, WordReference("doLIT"), 0, WordReference("doLIT"), 2, WordReference("UM/MOD"),WordReference("BYE")],
            [1, 1],
            id="3 0 2 UM/MOD"
        ),
        pytest.param(
            [WordReference("doLIT"), 2, WordReference("doLIT"), 2, WordReference("/MOD"),WordReference("BYE")],
            [0, 1],
            id="2 2 /MOD"
        ),
        pytest.param(
            [WordReference("doLIT"), 3, WordReference("doLIT"), 2, WordReference("/MOD"),WordReference("BYE")],
            [1, 1],
            id="3 2 /MOD"
        ),
        pytest.param(
            [WordReference("doLIT"), 3, WordReference("doLIT"), 2, WordReference("MOD"),WordReference("BYE")],
            [3%2],
            id="3 2 MOD"
        ),
        pytest.param(
            [WordReference("doLIT"), 42, WordReference("doLIT"), 5, WordReference("MOD"),WordReference("BYE")],
            [42%5],
            id="42 5 MOD"
        ),
        pytest.param(
            [WordReference("doLIT"), 3, WordReference("doLIT"), 2, WordReference("/"),WordReference("BYE")],
            [3//2],
            id="3 2 /"
        ),
        pytest.param(
            [WordReference("doLIT"), 42, WordReference("doLIT"), 5, WordReference("/"),WordReference("BYE")],
            [42//5],
            id="42 5 /"
        ),
        pytest.param(
            [WordReference("doLIT"), 3, WordReference("doLIT"), 2, WordReference("*"),WordReference("BYE")],
            [3*2],
            id="3 2 *"
        ),
        pytest.param(
            [WordReference("doLIT"), 42, WordReference("doLIT"), 5, WordReference("*"),WordReference("BYE")],
            [42*5],
            id="42 5 *"
        ),
        pytest.param(
            [WordReference("doLIT"), 42, WordReference("CELL+"),WordReference("BYE")],
            [44],
            id="42 CELL+"
        ),
        pytest.param(
            [WordReference("doLIT"), 42, WordReference("CELL-"),WordReference("BYE")],
            [40],
            id="42 CELL-"
        ),
        pytest.param(
            [WordReference("doLIT"), 42, WordReference("CELLS"),WordReference("BYE")],
            [42*2],
            id="42 CELLS"
        ),
        pytest.param(
            [WordReference("doLIT"), 42, WordReference("ALIGNED"),WordReference("BYE")],
            [42],
            id="42 ALIGNED"
        ),
        pytest.param(
            [WordReference("doLIT"), 41, WordReference("ALIGNED"),WordReference("BYE")],
            [42],
            id="41 ALIGNED"
        ),
        pytest.param(
            [WordReference("doLIT"), 40, WordReference("ALIGNED"),WordReference("BYE")],
            [40],
            id="40 ALIGNED"
        ),
        pytest.param(
            [WordReference("BL"),WordReference("BYE")],
            [ord(" ")],
            id="BL"
        ),
        pytest.param(
            [WordReference("doLIT"), ord("a"), WordReference(">CHAR"),WordReference("BYE")],
            [ord("a")],
            id="a >CHAR"
        ),
        pytest.param(
            [WordReference("doLIT"), 0, WordReference(">CHAR"),WordReference("BYE")],
            [ord("_")],
            id="0 >CHAR"
        ),
        # pytest.param(
        #     [WordReference("doLIT"), 40, WordReference("SP0"), WordReference("!"), WordReference("SP0"), WordReference("@"), WordReference("BYE")],
        #     [40],
        #     id="40 SP0 ! SP0 @" #TODO: can not work because SP0 & co are compile only, they call doVAR!
        # ),
        # pytest.param(
        #     [WordReference("doLIT"), 40, WordReference("SP0"), WordReference("!"), WordReference("doLIT"), 42, WordReference("SP!"), WordReference("DEPTH"), WordReference("BYE")],
        #     [1],
        #     id="40 SP0 ! 42 SP! DEPTH" #TODO: can not work because SP0 & co are compile only, they call doVAR!
        # ),
        pytest.param(
            [WordReference("doLIT"), 10, WordReference("doLIT"), 42, WordReference("!"), WordReference("doLIT"), 1, WordReference("doLIT"), 42, WordReference("+!"), WordReference("doLIT"), 42, WordReference("@"), WordReference("BYE")],
            [11],
            id="10 42 ! 1 42 +! 42 @"
        ),
        pytest.param(
            [WordReference("doLIT"), 0, WordReference("DIGIT"),WordReference("BYE")],
            [ord("0")],
            id="0 DIGIT"
        ),
        pytest.param(
            [WordReference("doLIT"), 1, WordReference("DIGIT"),WordReference("BYE")],
            [ord("1")],
            id="1 DIGIT"
        ),
        pytest.param(
            [WordReference("doLIT"), 2, WordReference("DIGIT"),WordReference("BYE")],
            [ord("2")],
            id="2 DIGIT"
        ),
        pytest.param(
            [WordReference("doLIT"), 3, WordReference("DIGIT"),WordReference("BYE")],
            [ord("3")],
            id="3 DIGIT"
        ),
        pytest.param(
            [WordReference("doLIT"), 4, WordReference("DIGIT"),WordReference("BYE")],
            [ord("4")],
            id="4 DIGIT"
        ),
        pytest.param(
            [WordReference("doLIT"), 5, WordReference("DIGIT"),WordReference("BYE")],
            [ord("5")],
            id="5 DIGIT"
        ),
        pytest.param(
            [WordReference("doLIT"), 6, WordReference("DIGIT"),WordReference("BYE")],
            [ord("6")],
            id="6 DIGIT"
        ),
        pytest.param(
            [WordReference("doLIT"), 7, WordReference("DIGIT"),WordReference("BYE")],
            [ord("7")],
            id="7 DIGIT"
        ),
        pytest.param(
            [WordReference("doLIT"), 8, WordReference("DIGIT"),WordReference("BYE")],
            [ord("8")],
            id="8 DIGIT"
        ),
        pytest.param(
            [WordReference("doLIT"), 9, WordReference("DIGIT"),WordReference("BYE")],
            [ord("9")],
            id="9 DIGIT"
        ),
    ]
)
def test_WORD(to_compile, expected_data_stack):
    compiler = eforth16bits.bootstrap_16bits_eforth()
    interpreter = ForthInterpreter(compiler.cell_size, primitives_store, logger=logging)
    interpreter.data_stack_pointer = eforth16bits.SPP
    interpreter.return_stack_pointer = eforth16bits.RPP

    interpreter.interpreter_pointer = compiler.code_address

    compiler.compile_word_body(to_compile)

    initial_data_stack_pointer = interpreter.data_stack_pointer
    initial_return_stack_pointer = interpreter.return_stack_pointer
    interpreter.memory = compiler.memory
    interpreter.start()
    assert interpreter.data_stack_pointer == initial_data_stack_pointer - len(expected_data_stack)*interpreter.cell_size
    assert interpreter.return_stack_pointer == initial_return_stack_pointer

    # for i, stack_data in enumerate(expected_data_stack):
    #     assert interpreter.read_cell_at_address(interpreter.data_stack_pointer-len(expected_data_stack)*interpreter.cell_size+i*interpreter.cell_size) == stack_data

    assert expected_data_stack == interpreter.tops_of_data_stack(len(expected_data_stack))