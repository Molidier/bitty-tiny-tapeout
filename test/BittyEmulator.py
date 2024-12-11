# BittyEmulator.py
from shared_memory import generate_shared_memory  # Import shared memory generator

class BittyEmulator:
    def __init__(self):
        self.d_out = 0
        self.registers = [0] * 8
        self.instruction_array = []
        self.memory_array = generate_shared_memory()  # Shared memory instance
        for index, el in enumerate(self.memory_array):
            print(f"Emulator Memory {index}: {el:04X}")

    
        # Load instructions from file
        try:
            with open("instructions_for_em.txt", "r") as infile:
                for line in infile:
                    instr = int(line.strip(), 16)
                    print(f"Instruction read and stored: {instr:04x}")
                    self.instruction_array.append(instr)

        except FileNotFoundError:
            print("Error opening file")

    def evaluate(self, address):
        instruction = self.instruction_array[address]
        format_code = instruction & 0x0003
        rx = (instruction & 0xE000) >> 13
        ry, in_b = None, None

        if format_code == 0:  # Normal format
            ry = (instruction & 0x1C00) >> 10
            in_b = self.registers[ry]
            print("Normal")
        elif format_code == 1:  # Immediate format
            print("Immediate")
            in_b = (instruction & 0x1FE0) >> 5
        elif format_code == 2:  # Branch format
            branch_cond = (instruction & 0x000C) >> 2
            branch_immediate = (instruction & 0x0FF0) >> 4
            print("Branch")
            prev_instruction = self.instruction_array[address - 1]
            prev_val_reg = (prev_instruction & 0xE000) >> 13
            #compare_value = self.registers[prev_val_reg]
            compare_value = self.d_out
        
            # Branch based on conditions
            if branch_cond == 0 and compare_value == 0:
                return branch_immediate
            elif branch_cond == 1 and compare_value == 1:
                return branch_immediate
            elif branch_cond == 2 and compare_value == 2:
                return branch_immediate
            else:
                return address + 1
        elif format_code == 3:  # Load/Store format
            ry = (instruction & 0x1C00) >> 10
            mem_address = self.registers[ry] & 0x00FF  # Limit address to within 256 memory entries
            data_to_ld = self.memory_array[mem_address]
            data_to_st = self.registers[rx]
            ls_code = instruction & 0x0004
            if ls_code == 0:  # Load operation
                self.set_register_value(rx, data_to_ld)
                print(f"Loaded {data_to_ld:04X} into register {rx}")
            else:  # Store operation
                self.memory_array[mem_address] = data_to_st
                print(f"Stored {data_to_st:04X} into memory at address {mem_address}")
        else:
            print("Invalid format code")

        # ALU Operations
        alu_sel = (instruction & 0x001C) >> 2
        if format_code == 0 or format_code == 1:
            result = 0
            if alu_sel == 0x0:  # Addition
                result = (self.registers[rx] + in_b) & 0xFFFF
            elif alu_sel == 0x1:  # Subtraction
                result = (self.registers[rx] - in_b) & 0xFFFF
            elif alu_sel == 0x2:  # Bitwise AND
                result = self.registers[rx] & in_b
            elif alu_sel == 0x3:  # Bitwise OR
                result = self.registers[rx] | in_b
            elif alu_sel == 0x4:  # Bitwise XOR
                result = self.registers[rx] ^ in_b
            elif alu_sel == 0x5:  # Shift left
                result = (self.registers[rx] << (in_b%16)) & 0xFFFF
                print(f"Shift left: {self.registers[rx]} << {in_b} = {result}")
            elif alu_sel == 0x6:  # Shift right
                result = (self.registers[rx] >> (in_b%16)) & 0xFFFF
            elif alu_sel == 0x7:  # Compare
                if self.registers[rx] == in_b:
                    result = 0
                elif self.registers[rx] > in_b:
                    result = 1
                else:
                    result = 2
            print("Emulator result:", result)
            self.registers[rx] = result
            self.set_register_value(rx, result)
            self.d_out = result

        return address + 1

    def get_register_value(self, reg_num):
        return self.registers[reg_num]

    def get_instruction_value(self, address):
        return self.instruction_array[address]

    def set_register_value(self, reg_num, value):
        self.registers[reg_num] = value & 0xFFFF  # Ensure value is treated as 16-bit unsigned
