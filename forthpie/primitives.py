class primitive(object):
    def __init__(self, code, name):
        self.code = code
        self.name = name
        self.function = None

    def __call__(self, function):
        self.function = function
        return self

    def execute(self, vm):
        return self.function(vm)

class debug(primitive):
    def __init__(self, primitive):
        self.primitive = primitive

    @property
    def code(self):
        return self.primitive.code

    @property
    def name(self):
        return self.primitive.name

    @property
    def function(self):
        return self.primitive.function

    def execute(self, vm):
        print(f"DEBUG: {self.primitive.name}")
        return self.primitive.execute(vm)

class NoPrimitiveFound(Exception):
    def __init__(self, primitive_code_or_name):
        self.primitive_code_or_name = primitive_code_or_name

    def __str__(self):
        return "Primitive not found: %d" % self.primitive_code_or_name

class NullPrimitive(primitive):
    def __init__(self, code):
        super().__init__(code, "Null")
    def execute(self, vm):
        raise NoPrimitiveFound(self.code)

class PrimitiveStore(object):
    def __init__(self, *args):
        self.primitives = args
        self.primitive_index = self.create_primitive_index()

    def create_primitive_index(self):
        primitives_index = [None] * (max(prim.code for prim in self.primitives)+1)
        for i in range(len(primitives_index)):
            primitives_index[i] = NullPrimitive(i)
        for primitive in self.primitives:
            primitives_index[primitive.code] = primitive
        return tuple(primitives_index)

    def get_primitive_by_address(self, address):
        return self.primitive_index[address]

    def get_primitive_by_name(self, name):
        try:
            return next(prim for prim in self.primitives if prim.name == name)
        except StopIteration:
            raise NoPrimitiveFound(name)

# From here, we define EForth primitives

## System interface
@primitive(0, "BYE")
def bye(vm):
    """( -- , exit Forth )
    """
    vm.log_info("Exiting the VM.")
    # Does nothing and, most importantly, do not call next() thus stopping the vm.

@primitive(1, "?RX")
def imrx(vm):
    """Return input character and true, or a false if no input.

    ( -- c T | F )
    """
    c = vm.input_stream.read(1)
    if c != "":
        vm.push_on_data_stack(ord(c))
        vm.push_on_data_stack(vm.cell_all_bit_at_one())
    else:
        vm.push_on_data_stack(0)
    vm.next()

@primitive(2, "TX!")
def txem(vm):
    """Send character c to output device.

    ( c -- )
    """
    c = vm.pop_from_data_stack()
    vm.output_stream.write(chr(c))
    vm.output_stream.flush()
    vm.next()

@primitive(3, "!IO")
def emio(vm):
    """Initialize the serial I/O devices.

    ( -- )
    """
    vm.next() # Nothing to do here.

## Inner vm
@primitive(4, "doLIT")
def doLIT(vm):
    """Push inline literal on data stack.

    ( -- w )
    """
    literal_value = vm.read_cell_at_address(vm.interpreter_pointer)
    vm.interpreter_pointer += vm.cell_size
    vm.push_on_data_stack(literal_value)
    vm.next()

@primitive(5, "doLIST")
def doLIST(vm):
    """Run address list in a colon word.

    ( a -- )
    """
    # Push intepreter pointer on return stack
    vm.push_on_return_stack(vm.interpreter_pointer)
    # Update IP to address of cell after W
    vm.interpreter_pointer = vm.word_pointer + vm.cell_size
    vm.next()

@primitive(6, "EXECUTE")
def EXECUTE(vm):
    """Execute the word at ca.

    ( ca -- )
    """
    ca = vm.pop_from_data_stack()
    vm.word_pointer = ca
    vm.step(vm.read_cell_at_address(ca))

@primitive(7, "EXIT")
def EXIT(vm):
    """Terminate a colon definition.
    """
    vm.interpreter_pointer = vm.pop_from_return_stack()
    vm.next()

@primitive(8, "next")
def next_primitive(vm):
    """Run time code for the single index loop.

    ( -- )

    High level version:
    : next
        r> r> dup if 1 - >r @ >r exit then drop cell+ >r ;
    """
    index = vm.pop_from_return_stack()
    index -= 1
    if index < 0:
        vm.interpreter_pointer += vm.cell_size
    else:
        vm.push_on_return_stack(index)
        vm.interpreter_pointer = vm.read_cell_at_address(vm.interpreter_pointer)
    vm.next()

@primitive(9, "?branch")
def imbranch(vm):
    """Branch if flag is zero.

    ( f -- )
    """
    flag = vm.pop_from_data_stack()
    if flag == 0:
        vm.interpreter_pointer = vm.read_cell_at_address(vm.interpreter_pointer)
    else:
        vm.interpreter_pointer += vm.cell_size
    vm.next()

@primitive(10, "branch")
def branch(vm):
    """Branch to an inline address.

    ( -- )
    """
    vm.interpreter_pointer = vm.read_cell_at_address(vm.interpreter_pointer)
    vm.next()

## Memory access
@primitive(11, "!")
def em(vm):
    """Pop the data stack to memory.

    ( w a -- )
    """
    a = vm.pop_from_data_stack()
    w = vm.pop_from_data_stack()
    vm.write_cell_at_address(a, w)
    vm.next()

@primitive(12, "@")
def at(vm):
    """Push memory location to data stack.

    ( a -- w )
    """
    a = vm.pop_from_data_stack()
    w = vm.read_cell_at_address(a)
    vm.push_on_data_stack(w)
    vm.next()

@primitive(13, "C!")
def Cem(vm):
    """Pop data stack to byte memory.

    ( c b -- )
    """
    b = vm.pop_from_data_stack()
    c = vm.pop_from_data_stack()
    vm.memory[b] = c
    vm.next()

@primitive(14, "C@")
def Cat(vm):
    """Push byte memory content on data stack.

    ( b -- c )
    """
    b = vm.pop_from_data_stack()
    vm.push_on_data_stack(vm.memory[b])
    vm.next()

## Return stack

@primitive(15, "RP@")
def RPat(vm):
    """Push current RP to data stack.

    ( -- a )
    """
    vm.push_on_data_stack(vm.return_stack_pointer)
    vm.next()

@primitive(16, "RP!")
def RPem(vm):
    """Set the return stack pointer.

    ( a -- )
    """
    vm.return_stack_pointer = vm.pop_from_data_stack()
    vm.next()

@primitive(17, "R>")
def Rgt(vm):
    """Pop return stack to data stack.

    ( -- w )
    """
    w = vm.pop_from_return_stack()
    vm.push_on_data_stack(w)
    vm.next()

@primitive(18, "R@")
def Rat(vm):
    """Copy top of return stack to data stack.

    ( -- w )
    """
    w = vm.top_of_return_stack()
    vm.push_on_data_stack(w)
    vm.next()

@primitive(19, ">R")
def gtR(vm):
    """Pop from data stack and push on return stack.

    ( w -- )
    """
    w = vm.pop_from_data_stack()
    vm.push_on_return_stack(w)
    vm.next()

## Data stack
@primitive(20, "DROP")
def DROP(vm):
    """Discard top stack item.

    ( w -- )
    """
    vm.deallocate_data_stack()
    vm.next()

@primitive(21, "DUP")
def DUP(vm):
    """Duplicate the top stack item.

    ( w -- w w )
    """
    vm.push_on_data_stack(vm.top_of_data_stack())
    vm.next()

@primitive(22, "SWAP")
def SWAP(vm):
    """Exchange top two stack items.

    ( w1 w2 -- w2 w1 )
    """
    w2 = vm.pop_from_data_stack()
    w1 = vm.pop_from_data_stack()
    vm.push_on_data_stack(w2)
    vm.push_on_data_stack(w1)
    vm.next()

@primitive(23, "OVER")
def OVER(vm):
    """Copy second stack item to top.

    ( w1 w2 -- w1 w2 w1 )
    """
    w1 = vm.tops_of_data_stack(2)[0]
    vm.push_on_data_stack(w1)
    vm.next()

@primitive(24, "SP@")
def SPat(vm):
    """Push the current data stack pointer.

    ( -- a )
    """
    vm.push_on_data_stack(vm.data_stack_pointer)
    vm.next()

@primitive(25, "SP!")
def SPem(vm):
    """Set the data stack pointer.

    ( a -- )
    """
    vm.data_stack_pointer = vm.pop_from_data_stack()
    vm.next()

## Logic
@primitive(26, "0<")
def zeroSt(vm):
    """Return true if n is negative.

    ( n -- f )
    """
    n = vm.pop_from_data_stack()
    if (n >> ((vm.cell_size-1)*8)) == 0:
        vm.push_on_data_stack(0)
    else:
        vm.push_on_data_stack(vm.cell_all_bit_at_one())
    vm.next()

@primitive(27, "AND")
def AND(vm):
    """Bitwise AND.

    ( w w -- w )
    """
    vm.push_on_data_stack(
        vm.pop_from_data_stack() & vm.pop_from_data_stack()
    )
    vm.next()

@primitive(28, "OR")
def OR(vm):
    """Bitwise inclusive OR.

    ( w w -- w )
    """
    vm.push_on_data_stack(
        vm.pop_from_data_stack() | vm.pop_from_data_stack()
    )
    vm.next()

@primitive(29, "XOR")
def XOR(vm):
    """Bitwise exclusive OR.

    ( w w -- w )
    """
    vm.push_on_data_stack(
        vm.pop_from_data_stack() ^ vm.pop_from_data_stack()
    )
    vm.next()

## Arithmetic
@primitive(30, "UM+")
def UMplus(vm):
    """Add two numbers, return the sum and carry flag.

    ( w1 w2 -- w cy )
    """
    w1 = vm.pop_from_data_stack()
    w2 = vm.pop_from_data_stack()
    w = w1 + w2
    vm.push_on_data_stack(w)
    if (w >> (vm.cell_size * 8)) > 0:
        vm.push_on_data_stack(vm.cell_all_bit_at_one())
    else:
        vm.push_on_data_stack(0)
    vm.next()

@primitive(31, "UM/MOD")
def UMMOD(vm):
    u = vm.pop_from_data_stack()
    d = vm.pop_from_data_stack() << vm.cell_size
    d |= vm.pop_from_data_stack()

    vm.push_on_data_stack(d % u)
    vm.push_on_data_stack(d // u)
    vm.next()

@primitive(32, "DEBUG")
def DEBUG(vm):
    breakpoint()
    vm.next()

by_the_book_primitives_store = PrimitiveStore(
    bye,
    imrx,
    txem,
    emio,
    doLIT,
    doLIST,
    EXECUTE,
    EXIT,
    next_primitive,
    imbranch,
    branch,
    em,
    at,
    Cem,
    Cat,
    RPat,
    RPem,
    Rgt,
    Rat,
    gtR,
    DROP,
    DUP,
    SWAP,
    OVER,
    SPat,
    SPem,
    zeroSt,
    AND,
    OR,
    XOR,
    UMplus,
    UMMOD,
    DEBUG
)
