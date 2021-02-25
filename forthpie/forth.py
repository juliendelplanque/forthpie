# -*- coding: utf-8 -*-

import io

class NotAByte(Exception):
    def __init__(self, value):
        self.value = value

class Memory(object):
    def __init__(self, size):
        self.bytes_array = [0]*size

    def __len__(self):
        return len(self.bytes_array)

    def __getitem__(self, index):
        return self.bytes_array[index]

    def __setitem__(self, index, value):
        if value < 0 or value > 255:
            raise NotAByte(value)
        self.bytes_array[index] = value

class MemoryManipulator(object):
    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.memory = None

    def read_cell_at_address(self, address):
        value = 0
        # NOTE: I changed this because it should be encoded in little endian! Eforth makes assumption about that!
        # for i in range(self.cell_size):
        #     value = (value << 8) | self.memory[address+i]

        addr = address + (self.cell_size - 1)
        for i in range(self.cell_size):
            value = (value << 8) | self.memory[addr-i]

        return value

    def write_cell_at_address(self, address, cell_value):
        to_write = cell_value
        # NOTE: I changed this because it should be encoded in little endian! Eforth makes assumption about that!
        # for addr in range(address + self.cell_size - 1, address-1, -1):
        #     self.memory[addr] = to_write & 0xFF
        #     to_write = to_write >> 8

        for addr in range(address, address + self.cell_size, 1):
            self.memory[addr] = to_write & 0xFF
            to_write = to_write >> 8

class ForthInterpreter(MemoryManipulator):
    def __init__(
        self,
        cell_size,
        primitives,
        memory_size=0,
        input_stream=None,
        output_stream=None,
        logger=None,
        compiler_metadata=None
    ):
        self.cell_size = cell_size
        self.interpreter_pointer = 0
        self.data_stack_pointer = 0
        self.return_stack_pointer = 0
        self.word_pointer = 0
        self.memory = Memory(memory_size)
        self.primitives = primitives
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
        self.compiler_metadata = compiler_metadata

    def log_info(self, *args, **kwargs):
        if not self.logger:
            return
        self.logger.info(*args, **kwargs)

    def log_debug(self, *args, **kwargs):
        if not self.logger:
            return
        self.logger.debug(*args, **kwargs)

    def step(self, address):
        primitive = self.get_primitive_by_address(address)
        self.log_debug(
            f"primitive[{primitive.code}][{primitive.name}] - fct={primitive.function.__name__}"
        )
        primitive.execute(self)

    def next(self):
        """
        """
        self.keep_going = True

    def _log_ip(self, wordname_filter=lambda wordname: True):
        if not self.compiler_metadata:
            return
        log_str = f"IP: {self.interpreter_pointer} "

        word_name = None
        try:
            word_name = self.compiler_metadata.word_address_belongs_to(self.interpreter_pointer).name
            log_str += f"({word_name})"
        except StopIteration:
            log_str += "(?)"
        try:
            address_of_word_called = self.read_cell_at_address(self.interpreter_pointer)
            word_called_name = self.compiler_metadata.word_address_belongs_to(address_of_word_called).name
            log_str += f"-> {word_called_name}()"
        except StopIteration:
            log_str += f"-> ?{hex(address_of_word_called)}?()"
        if wordname_filter(word_name):
            self.log_info(log_str)

    def _next(self):
        # self._log_ip(lambda wn: wn in ["QUIT", ".OK"])
        self._log_ip()
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

    def get_primitive_by_address(self, *args, **kwargs):
        return self.primitives.get_primitive_by_address(*args, **kwargs)

    def get_primitive_by_name(self, *args, **kwargs):
        return self.primitives.get_primitive_by_name(*args, **kwargs)

    def allocate_data_stack(self):
        """Allocate a cell on the data stack.

        Data stack grows upward.
        """
        self.data_stack_pointer -= self.cell_size

    def deallocate_data_stack(self):
        """Deallocate a cell on the data stack.

        Data stack grows upward.
        """
        self.data_stack_pointer += self.cell_size

    def tops_of_data_stack(self, count=1):
        current_stack_pointer = self.data_stack_pointer
        cells = []
        for i in range(count):
            cells.insert(0, self.read_cell_at_address(current_stack_pointer))
            current_stack_pointer += self.cell_size
        return cells

    def top_of_data_stack(self):
        return self.tops_of_data_stack(1)[0]

    def push_on_data_stack(self, cell_value):
        self.log_debug(f"push_on_data_stack({cell_value})")
        self.allocate_data_stack()
        self.write_cell_at_address(self.data_stack_pointer, cell_value)

    def pop_from_data_stack(self):
        self.log_debug(f"pop_from_data_stack() -> {self.top_of_data_stack()}")
        cell = self.read_cell_at_address(self.data_stack_pointer)
        self.deallocate_data_stack()
        return cell

    def allocate_return_stack(self):
        """Allocate a cell on the return stack.

        Return stack grows downward.
        """
        self.return_stack_pointer -= self.cell_size

    def deallocate_return_stack(self):
        """Deallocate a cell on the return stack.

        Return stack grows downward.
        """
        self.return_stack_pointer += self.cell_size

    def pop_from_return_stack(self):
        self.log_debug(f"pop_from_return_stack() -> {self.top_of_return_stack()}")
        cell = self.read_cell_at_address(self.return_stack_pointer)
        self.deallocate_return_stack()
        return cell

    def push_on_return_stack(self, cell_value):
        self.log_debug(f"push_on_return_stack({cell_value})")
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

class ExecutionStatistics(object):
    def __init__(self):
        self.words_calls = dict()

    def increment_calls_count(self, word_address):
        if word_address not in self.words_calls.keys():
            self.words_calls[word_address] = 0

        self.words_calls[word_address] = self.words_calls[word_address] + 1

    def word_names_to_count(self, compiler_metadata):
        names_to_count = dict()
        for word_address, calls_count in self.words_calls.items():
            name = None
            try:
                name = compiler_metadata.word_address_belongs_to(word_address).name
            except:
                name = '?'
            names_to_count[name] = calls_count
        return names_to_count

class StatisticsInterpreter(ForthInterpreter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.execution_statistics = ExecutionStatistics()

    def _next(self):
        self.execution_statistics.increment_calls_count(
            self.read_cell_at_address(self.interpreter_pointer)
        )
        return super()._next()
