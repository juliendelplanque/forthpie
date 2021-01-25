# -*- coding: utf-8 -*-

import io

class Memory(object):
    def __init__(self, size):
        self.bytes_array = [0]*size

    def __len__(self):
        return len(self.bytes_array)
    
    def __getitem__(self, index):
        return self.bytes_array[index]
    
    def __setitem__(self, index, value):
        self.bytes_array[index] = value

class primitive(object):
    def __init__(self, code, name):
        self.code = code
        self.name = name
        self.function = None
    
    def __call__(self, function):
        self.function = function
        return self
    
    def execute(self, interpreter):
        return self.function(interpreter)

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

    def execute(self, interpreter):
        print(f"DEBUG: {self.primitive.name}")
        return self.primitive.execute(interpreter)

class NoPrimitiveFound(Exception):
    def __init__(self, primitive_code):
        self.primitive_code = primitive_code
    
class MemoryManipulator(object):
    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.memory = None
    
    def read_cell_at_address(self, address):
        value = 0
        for i in range(self.cell_size):
            value = (value << 8) | self.memory[address+i]
        return value
    
    def write_cell_at_address(self, address, cell_value):
        to_write = cell_value
        for addr in range(address + self.cell_size - 1, address-1, -1):
            self.memory[addr] = to_write & 0xFF
            to_write = to_write >> 8

class ForthInterpreter(MemoryManipulator):
    def __init__(
        self,
        cell_size,
        memory_size=0,
        input_stream=None,
        output_stream=None,
        logger=None
    ):
        self.cell_size = cell_size
        self.interpreter_pointer = 0
        self.data_stack_pointer = 0
        self.return_stack_pointer = 0
        self.word_pointer = 0
        self.memory = Memory(memory_size)
        if input_stream:
            self.input_stream = input_stream
        else:
            self.input_stream = io.StringIO("")
        if output_stream:
            self.output_stream = output_stream
        else:
            self.output_stream = io.StringIO("")
        self.logger = logger
        self.keep_going = False
    
    def log_info(self, *args, **kwargs):
        if not self.logger:
            return
        self.logger.info(*args, **kwargs)
    
    def step(self, address):
        try:
            primitive = self.lookup_primitive(address)
            self.log_info(
                f"primitive[{primitive.code}][{primitive.name}] - fct={primitive.function.__name__}"
            )
            primitive.execute(self)
        except NoPrimitiveFound:
            print("Primitive not found: %d" % address)
    
    def next(self):
        """
        """
        self.keep_going = True
    
    def _next(self):
        self.log_info(f"IP: {self.interpreter_pointer}")
        self.word_pointer = self.read_cell_at_address(self.interpreter_pointer)
        self.interpreter_pointer += self.cell_size
        self.step(self.read_cell_at_address(self.word_pointer))
        
    def start(self):
        """Start interpreting Forth image.
        """
        self.keep_going = True
        while self.keep_going:
            self.keep_going = False
            self._next()
    
    @classmethod
    def get_primitive_by_address(cls, address):
        for prim_name in dir(cls):
            attribute =  getattr(cls, prim_name)
            if isinstance(attribute, primitive) and attribute.code == address:
                return attribute
        raise NoPrimitiveFound(address)
    
    @classmethod
    def get_primitive_by_name(cls, name):
        for prim_name in dir(cls):
            attribute =  getattr(cls, prim_name)
            if isinstance(attribute, primitive) and attribute.name == name:
                return attribute
        raise NoPrimitiveFound(name)
    
    def lookup_primitive(self, address):
        return self.__class__.get_primitive_by_address(address)

    def allocate_data_stack(self):
        """Allocate a cell on the data stack.

        Data stack grows upward.
        """
        self.data_stack_pointer += self.cell_size
    
    def deallocate_data_stack(self):
        """Deallocate a cell on the data stack.

        Data stack grows upward.
        """
        self.data_stack_pointer -= self.cell_size

    def tops_of_data_stack(self, count=1):
        current_stack_pointer = self.data_stack_pointer
        cells = []
        for i in range(count):
            current_stack_pointer -= self.cell_size
            cells.insert(0, self.read_cell_at_address(current_stack_pointer))
        return cells
    
    def top_of_data_stack(self):
        return self.tops_of_data_stack(1)[0]
    
    def push_on_data_stack(self, cell_value):
        # import inspect
        # print(f"push_on_data_stack({cell_value}) from {inspect.stack()[1][3]}")
        self.log_info(f"push_on_data_stack({cell_value})")
        self.write_cell_at_address(self.data_stack_pointer, cell_value)
        self.allocate_data_stack()
    
    def pop_from_data_stack(self):
        # import inspect
        # print(f"pop_from_data_stack() -> {self.top_of_data_stack()} from {inspect.stack()[1][3]}")
        self.log_info(f"pop_from_data_stack() -> {self.top_of_data_stack()}")
        self.deallocate_data_stack()
        return self.read_cell_at_address(self.data_stack_pointer)
    
    def allocate_return_stack(self):
        """Allocate a cell on the return stack.

        Return stack grows downward.
        """
        # import inspect
        # print(f"allocate_return_stack() from {inspect.stack()[1][3]}")
        self.return_stack_pointer -= self.cell_size
    
    def deallocate_return_stack(self):
        """Deallocate a cell on the return stack.

        Return stack grows downward.
        """
        # import inspect
        # print(f"deallocate_return_stack() from {inspect.stack()[1][3]}")
        self.return_stack_pointer += self.cell_size

    def pop_from_return_stack(self):
        # import inspect
        # print(f"pop_from_return_stack() -> {self.top_of_return_stack()} from {inspect.stack()[1][3]}")
        self.log_info(f"pop_from_return_stack() -> {self.top_of_return_stack()}")
        cell = self.read_cell_at_address(self.return_stack_pointer)
        self.deallocate_return_stack()
        return cell
    
    def push_on_return_stack(self, cell_value):
        # import inspect
        # print(f"push_on_return_stack({cell_value}) from {inspect.stack()[1][3]}")
        self.log_info(f"push_on_return_stack({cell_value})")
        self.allocate_return_stack()
        self.write_cell_at_address(self.return_stack_pointer, cell_value)
    
    def tops_of_return_stack(self, count=1):
        current_stack_pointer = self.return_stack_pointer
        cells = []
        for i in range(count):
            cells.insert(0, self.read_cell_at_address(current_stack_pointer))
            current_stack_pointer += self.cell_size
        return cells

    def top_of_return_stack(self):
        return self.read_cell_at_address(self.return_stack_pointer)
    
    def cell_all_bit_at_one(self):
        """Generates the value for a cell with all bits at 1.
        """
        cell = 0
        for i in range(self.cell_size):
            cell = (cell << 8) | 0xFF
        return cell
    
    # From here, we define EForth primitives

    ## System interface
    @primitive(0, "BYE")
    def bye(self):
        """( -- , exit Forth )
        """
        return # Does nothing and, most importantly, do not call next() thus stopping the interpreter.
    
    @primitive(1, "?RX")
    def imrx(self):
        """Return input character and true, or a false if no input.
        
        ( -- c T | F )
        """
        c = self.input_stream.read(1)
        if c != "":
            self.push_on_data_stack(ord(c))
            self.push_on_data_stack(self.cell_all_bit_at_one())
        else:
            self.push_on_data_stack(0)
        self.next()
    
    @primitive(2, "TX!")
    def txem(self):
        """Send character c to output device.

        ( c -- )
        """
        c = self.pop_from_data_stack()
        self.output_stream.write(chr(c))
        self.next()

    @primitive(3, "!IO")
    def emio(self):
        """Initialize the serial I/O devices.

        ( -- )
        """
        self.next() # Nothing to do here.
    
    ## Inner interpreter
    @primitive(4, "doLIT")
    def doLIT(self):
        """Push inline literal on data stack.

        ( -- w )
        """
        literal_value = self.read_cell_at_address(self.interpreter_pointer)
        self.interpreter_pointer += self.cell_size
        self.push_on_data_stack(literal_value)
        self.next()
    
    @primitive(5, "doLIST")
    def doLIST(self):
        """Run address list in a colon word.

        ( a -- )
        """
        # Push intepreter pointer on return stack
        self.allocate_return_stack()
        self.write_cell_at_address(self.return_stack_pointer, self.interpreter_pointer) # Save IP on stack
        # Update IP to address of cell after W
        self.interpreter_pointer = self.word_pointer + self.cell_size
        self.next()
    
    @primitive(6, "EXECUTE")
    def EXECUTE(self):
        """Execute the word at ca.

        ( ca -- )
        """
        self.step(self.pop_from_data_stack())
    
    @primitive(7, "EXIT")
    def EXIT(self):
        """Terminate a colon definition.
        """
        self.interpreter_pointer = self.read_cell_at_address(self.return_stack_pointer)
        self.return_stack_pointer += self.cell_size # deallocate space for cell on datastack
        self.next()
    
    @primitive(8, "next")
    def next_primitive(self):
        """Run time code for the single index loop.

        ( -- )

        High level version:
        : next
            r> r> dup if 1 - >r @ >r exit then drop cell+ >r ;
        """
        index = self.pop_from_return_stack()
        index -= 1
        if index < 0:
            self.interpreter_pointer += self.cell_size
        else:
            self.push_on_return_stack(index)
            self.interpreter_pointer = self.read_cell_at_address(self.interpreter_pointer)
        self.next()
    
    @primitive(9, "?branch")
    def imbranch(self):
        """Branch if flag is zero.

        ( f -- )
        """
        flag = self.pop_from_data_stack()
        if flag == 0:
            self.interpreter_pointer = self.read_cell_at_address(self.interpreter_pointer)
        else:
            self.interpreter_pointer += self.cell_size
        self.next()

    @primitive(10, "branch")
    def branch(self):
        """Branch to an inline address.

        ( -- )
        """
        self.interpreter_pointer = self.read_cell_at_address(self.interpreter_pointer)
        self.next()
    
    ## Memory access
    @primitive(11, "!")
    def em(self):
        """Pop the data stack to memory.

        ( w a -- )
        """
        a = self.pop_from_data_stack()
        w = self.pop_from_data_stack()
        self.write_cell_at_address(a, w)
        self.next()
    
    @primitive(12, "@")
    def at(self):
        """Push memory location to data stack.

        ( a -- w )
        """
        a = self.pop_from_data_stack()
        w = self.read_cell_at_address(a)
        self.push_on_data_stack(w)
        self.next()
    
    @primitive(13, "C!")
    def Cem(self):
        """Pop data stack to byte memory.

        ( c b -- )
        """
        b = self.pop_from_data_stack() ## TODO: check that b <= 255 ?
        c = self.pop_from_data_stack()
        self.memory[b] = c
        self.next()
    
    @primitive(14, "C@")
    def Cat(self):
        """Push byte memory content on data stack.

        ( b -- c )
        """
        b = self.pop_from_data_stack() ## TODO: check that b <= 255 ?
        self.push_on_data_stack(self.memory[b])
        self.next()
    
    ## Return stack

    @primitive(15, "RP@")
    def RPat(self):
        """Push current RP to data stack.

        ( -- a )
        """
        self.push_on_data_stack(self.return_stack_pointer)
        self.next()

    @primitive(16, "RP!")
    def RPem(self):
        """Set the return stack pointer.

        ( a -- )
        """
        self.return_stack_pointer = self.pop_from_data_stack()
        self.next()

    @primitive(17, "R>")
    def Rgt(self):
        """Pop return stack to data stack.

        ( -- w )
        """
        w = self.pop_from_return_stack()
        self.push_on_data_stack(w)
        self.next()

    @primitive(18, "R@")
    def Rat(self):
        """Copy top of return stack to data stack.

        ( -- w )
        """
        w = self.top_of_return_stack()
        self.push_on_data_stack(w)
        self.next()

    @primitive(19, ">R")
    def gtR(self):
        """Pop from data stack and push on return stack.

        ( w -- )
        """
        w = self.pop_from_data_stack()
        self.push_on_return_stack(w)
        self.next()

    ## Data stack
    @primitive(20, "DROP")
    def DROP(self):
        """Discard top stack item.

        ( w -- )
        """
        self.deallocate_data_stack()
        self.next()
    
    @primitive(21, "DUP")
    def DUP(self):
        """Duplicate the top stack item.

        ( w -- w w )
        """
        self.push_on_data_stack(self.top_of_data_stack())
        self.next()
    
    @primitive(22, "SWAP")
    def SWAP(self):
        """Exchange top two stack items.

        ( w1 w2 -- w2 w1 )
        """
        w2 = self.pop_from_data_stack()
        w1 = self.pop_from_data_stack()
        self.push_on_data_stack(w2)
        self.push_on_data_stack(w1)
        self.next()
    
    @primitive(23, "OVER")
    def OVER(self):
        """Copy second stack item to top.

        ( w1 w2 -- w1 w2 w1 )
        """
        w1 = self.read_cell_at_address(self.data_stack_pointer-2*self.cell_size)
        self.push_on_data_stack(w1)
        self.next()
    
    @primitive(24, "SP@")
    def SPat(self):
        """Push the current data stack pointer.

        ( -- a )
        """
        a = self.push_on_data_stack(self.data_stack_pointer)
        self.next()
    
    @primitive(25, "SP!")
    def SPem(self):
        """Set the data stack pointer.

        ( a -- )
        """
        self.data_stack_pointer = self.pop_from_data_stack()
        self.next()

    ## Logic
    @primitive(26, "0<")
    def zeroSt(self):
        """Return true if n is negative.

        ( n -- f )
        """
        n = self.pop_from_data_stack()
        if (n >> ((self.cell_size-1)*8)) == 0:
            self.push_on_data_stack(0)
        else:
            self.push_on_data_stack(self.cell_all_bit_at_one())
        self.next()
    
    @primitive(27, "AND")
    def AND(self):
        """Bitwise AND.

        ( w w -- w )
        """
        self.push_on_data_stack(
            self.pop_from_data_stack() & self.pop_from_data_stack()
        )
        self.next()
    
    @primitive(28, "OR")
    def OR(self):
        """Bitwise inclusive OR.
        
        ( w w -- w )
        """
        self.push_on_data_stack(
            self.pop_from_data_stack() | self.pop_from_data_stack()
        )
        self.next()
    

    @primitive(29, "XOR")
    def XOR(self):
        """Bitwise exclusive OR.

        ( w w -- w )
        """
        self.push_on_data_stack(
            self.pop_from_data_stack() ^ self.pop_from_data_stack()
        )
        self.next()

    ## Arithmetic
    @primitive(30, "UM+")
    def UMplus(self):
        """Add two numbers, return the sum and carry flag.

        ( w1 w2 -- w cy )
        """
        w1 = self.pop_from_data_stack()
        w2 = self.pop_from_data_stack()
        w = w1 + w2
        self.push_on_data_stack(w)
        if (w >> (self.cell_size * 8)) > 0:
            self.push_on_data_stack(self.cell_all_bit_at_one())
        else:
            self.push_on_data_stack(0)
        self.next()

    @primitive(31, "UM/MOD")
    def UMMOD(self):
        u = self.pop_from_data_stack()
        d = self.pop_from_data_stack()<<self.cell_size
        d |= self.pop_from_data_stack()

        self.push_on_data_stack(d % u)
        self.push_on_data_stack(d // u)
        self.next()