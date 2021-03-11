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
    def __init__(self, input_count=0, output_count=0):
        self.input_count = input_count
        self.output_count = output_count
        self.primitive = None

    def __call__(self, primitive):
        self.primitive = primitive
        return self

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
        print(f"DEBUG PRIMITIVE: {self.primitive.name}")
        print(f"Input=(top){vm.tops_of_data_stack(self.input_count)}(bottom)")
        result = self.primitive.execute(vm)
        print(f"Output=(top){vm.tops_of_data_stack(self.output_count)}(bottom)")
        return result

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
