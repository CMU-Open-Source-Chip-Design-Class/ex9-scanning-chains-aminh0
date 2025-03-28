import copy
import cocotb
from cocotb.triggers import Timer


# Make sure to set FILE_NAME
# to the filepath of the .log
# file you are working with
CHAIN_LENGTH = -1
FILE_NAME    = "adder/adder.log"



# Holds information about a register
# in your design.

################
# DO NOT EDIT!!!
################
class Register:

    def __init__(self, name) -> None:
        self.name = name            # Name of register, as in .log file
        self.size = -1              # Number of bits in register

        self.bit_list = list()      # Set this to the register's contents, if you want to
        self.index_list = list()    # List of bit mappings into chain. See handout

        self.first = -1             # LSB mapping into scan chain
        self.last  = -1             # MSB mapping into scan chain


# Holds information about the scan chain
# in your design.
        
################
# DO NOT EDIT!!!
################
class ScanChain:

    def __init__(self) -> None:
        self.registers = dict()     # Dictionary of Register objects, indexed by 
                                    # register name
        
        self.chain_length = 0       # Number of FFs in chain


# Sets up a new ScanChain object
# and returns it

################     
# DO NOT EDIT!!!
################
def setup_chain(filename):

    scan_chain = ScanChain()

    f = open(filename, "r")
    for line in f:
        linelist = line.split()
        index, name, bit = linelist[0], linelist[1], linelist[2]

        if name not in scan_chain.registers:
            reg = Register(name)
            reg.index_list.append((int(bit), int(index)))
            scan_chain.registers[name] = reg

        else:
            scan_chain.registers[name].index_list.append((int(bit), int(index)))
        
    f.close()

    for name in scan_chain.registers:
        cur_reg = scan_chain.registers[name]
        cur_reg.index_list.sort()
        new_list = list()
        for tuple in cur_reg.index_list:
            new_list.append(tuple[1])
        
        cur_reg.index_list = new_list
        cur_reg.bit_list   = [0] * len(new_list)
        cur_reg.size = len(new_list)
        cur_reg.first = new_list[0]
        cur_reg.last  = new_list[-1]
        scan_chain.chain_length += len(cur_reg.index_list)

    return scan_chain


# Prints info of given Register object

################
# DO NOT EDIT!!!
################
def print_register(reg):
    print("------------------")
    print(f"NAME:    {reg.name}")
    print(f"BITS:    {reg.bit_list}")
    print(f"INDICES: {reg.index_list}")
    print("------------------")


# Prints info of given ScanChain object

################   
# DO NOT EDIT!!!
################
def print_chain(chain):
    print("---CHAIN DISPLAY---\n")
    print(f"CHAIN SIZE: {chain.chain_length}\n")
    print("REGISTERS: \n")
    for name in chain.registers:
        cur_reg = chain.registers[name]
        print_register(cur_reg)



#-------------------------------------------------------------------

# This function steps the clock once.
    
# Hint: Use the Timer() builtin function
async def step_clock(dut):

    ######################
    dut.clk.value = 1
    
    await Timer(10, units="ns")
    
    dut.clk.value = 0
    
    await Timer(10, units="ns")
    ######################

    pass
    

#-------------------------------------------------------------------

# This function places a bit value inside FF of specified index.
        
# Hint: How many clocks would it take for value to reach
#       the specified FF?
        
async def input_chain_single(dut, bit, ff_index):

    ######################
    dut.scan_en.value = 1
    
    dut.scan_in.value = bit
    
    for _ in range(ff_index + 1):
        await step_clock(dut)
        
    dut.scan_en.value = 0
    ######################

    pass
    
#-------------------------------------------------------------------

# This function places multiple bit values inside FFs of specified indexes.
# This is an upgrade of input_chain_single() and should be accomplished
#   for Part H of Task 1
        
# Hint: How many clocks would it take for value to reach
#       the specified FF?
        
async def input_chain(dut, bit_list, ff_index):

    dut.scan_en.value = 1

    # print("Inputting bits:", bit_list)
    
    for bit in reversed(bit_list):
        dut.scan_in.value = bit
        await step_clock(dut)

    for _ in range(ff_index):
        dut.scan_in.value = 0
        await step_clock(dut)
        
    dut.scan_en.value = 0
    pass

#-----------------------------------------------

# This function retrieves a single bit value from the
# chain at specified index 
        
async def output_chain_single(dut, ff_index):

    dut.scan_en.value = 1
    
    cycles_needed = CHAIN_LENGTH - ff_index -1
    
    print(f"Reading from index {ff_index}, cycles needed: {cycles_needed}")
    
    for i in range(cycles_needed):
        await step_clock(dut)
        print(f"Shift cycle {i+1}/{cycles_needed}, scan_out: {int(dut.scan_out.value)}")
    
    bit_value = int(dut.scan_out.value)
    print(f"Final read from index {ff_index}: {bit_value}")
    
    dut.scan_en.value = 0
    
    return bit_value
    
    pass       

#-----------------------------------------------

# This function retrieves a single bit value from the
# chain at specified index 
# This is an upgrade of input_chain_single() and should be accomplished
#   for Part H of Task 1
        
async def output_chain(dut, ff_index, output_length):

    result = []
    
    dut.scan_en.value = 1
    
    cycles_needed = CHAIN_LENGTH - ff_index - output_length
    
    for _ in range(cycles_needed):
        await step_clock(dut)
        
    for _ in range(output_length):
        bit_value = int(dut.scan_out.value)
        result.append(bit_value)
        await step_clock(dut)
        
    dut.scan_en.value = 0
    
    return result

    pass       

#-----------------------------------------------

# Your main testbench function

@cocotb.test()
async def test(dut):

    global CHAIN_LENGTH
    global FILE_NAME        # Make sure to edit this guy
                            # at the top of the file

    # Setup the scan chain object
    chain = setup_chain(FILE_NAME)

    
    print_chain(chain)

    CHAIN_LENGTH = chain.chain_length
    
    dut.scan_en.value = 0
    dut.scan_in.value = 0
    dut.clk.value = 0
    
    test_cases = [
        {"a":2, "b":5, "expected": 7},
        {"a": 7, "b": 9, "expected": 16},
        {"a": 15, "b": 15, "expected": 30},
        {"a": 0, "b": 10, "expected": 10}
    ]
    
    for i, test_case in enumerate(test_cases):
        a_val = test_case["a"]
        b_val = test_case["b"]
        expected = test_case["expected"]
        
        print(f"\ntest case {i+1}: a_reg = {a_val}, b_reg = {b_val}")
        
        a_reg = chain.registers["a_reg"]
        b_reg = chain.registers["b_reg"]
        x_out = chain.registers["x_out"]
        
        a_bin = format(a_val, f'0{a_reg.size}b')
        b_bin = format(b_val, f'0{b_reg.size}b')
        
        bit_list = [0] * CHAIN_LENGTH
        
        for i, idx in enumerate(x_out.index_list):
            bit_list[idx] = 0
        
        for i, idx in enumerate(a_reg.index_list):
            bit_list[idx] = int(a_bin[a_reg.size - 1 - i])
        
        for i, idx in enumerate(b_reg.index_list):
            bit_list[idx] = int(b_bin[b_reg.size - 1 - i])
        
        await input_chain(dut, bit_list, 0)
        
        dut.scan_en.value = 0
        await step_clock(dut)
        
        result_bits = await output_chain(dut, x_out.first, x_out.size)
        
        result_val = 0
        for i, bit in enumerate(reversed(result_bits)):
            result_val += bit * (2 ** (i))
        
        print(f"Expected: {expected}")
        print(f"Result_val: {result_val}")
        
        if result_val == expected:
            print("test success!")
        else:
            print("test fail!")
