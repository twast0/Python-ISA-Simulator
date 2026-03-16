import sys
import re

print("\nWelcome to the ISA simulator! - Designed by me")

if len(sys.argv) < 4:
    print('Too few arguments.')
    sys.exit(2)
elif (len(sys.argv) > 4):
    print('Too many arguments.')
    sys.exit(2)

'''
This class models the register file of the processor. It contains 16 8-bit unsigned
registers named from R0 to R15 (the names are strings). R0 is read only and
reads always 0 (zero). When an object of the class RegisterFile is instantiated,
the registers are generated and initialized to 0.
'''
class RegisterFile:
    def __init__(self):
        self.registers = {}
        for i in range(0, 16):
            self.registers['R'+str(i)] = 0

    '''
    This method writes the content of the specified register.
    '''

    # sys.exit(-1) removed in favor of raising errors where applicable
    def write_register(self, register, register_value):
        if register not in self.registers:
            raise ValueError('Register ' + str(register) + ' does not exist. Terminating execution.')
        if register == 'R0':
            raise ValueError('WARNING: Cannot write R0. Register R0 is read only.')
        
        # Biggest change to this function is how out of bounds values are checked
        # for the sake of getting used to using binary/hexadecimal operations
        # we decided to implement binary operators instead of modulo (%)
        self.registers[register] = int(register_value) & 0xFF 

    '''
    This method reads the content of the specified register.
    '''
    def read_register(self, register):
        # Kept the same but removed sys.exit, 
        if register not in self.registers:
            raise ValueError('Register ' + str(register) + ' does not exist. Terminating execution.')
        return self.registers[register]

    '''
    This method prints the content of the specified register.
    '''
    def print_register(self, register):
        if register in self.registers:
            print(register + ' = ' + str(self.registers[register]))
        else:
            raise ValueError('Register ' + str(register) + ' does not exist. Terminating execution.')
            

    '''
    This method prints the content of the entire register file.
    '''
    def print_all(self):
        print('Register file content:')
        for i in range(0, 16):
            self.print_register('R' + str(i))


'''
This class models the data memory of the processor. When an object of the
class DataMemory is instantiated, the data memory model is generated and au-
tomatically initialized with the memory content specified in the file passed as
second argument of the simulator. The memory has 256 location addressed form
0 to 255. Each memory location contains an unsigned 8-bit value. Uninitialized
data memory locations contain the value zero.
'''
class DataMemory:
    def __init__(self):
        self.data_memory = {}
        print('\nInitializing data memory content from file.')
        try:
            with open(sys.argv[3], 'r') as fd:
                file_content = fd.readlines()
        except:
             raise MemoryError('Failed to open data memory file. Terminating execution.')
        file_content = ''.join(file_content)
        file_content = re.sub(r'#.*?\n', ' ', file_content)
        file_content = re.sub(r'#.*? ', ' ', file_content)
        file_content = file_content.replace('\n', '')
        file_content = file_content.replace('\t', '')
        file_content = file_content.replace(' ', '')
        file_content_list = file_content.split(';')
        file_content = None
        while '' in file_content_list:
            file_content_list.remove('')
        try:
            for entry in file_content_list:
                address, data = entry.split(':')
                self.write_data(int(address), int(data))
        except:
            raise MemoryError('Malformed data memory file. Terminating execution.')
        print('Data memory initialized.')

    '''
    This method writes the content of the memory location at the specified address.
    '''
    def write_data(self, address, data):
        if address < 0 or address > 255:
            raise ValueError("Out of range data memory write access. Terminating execution.")
        self.data_memory[address] = data % 256

    '''
    This method writes the content of the memory location at the specified address.
    '''
    def read_data(self, address):
        if address < 0 or address > 255:
            raise ValueError("Out of range data memory read access. Terminating execution.")
        if address in self.data_memory:
            return self.data_memory[address]
        else:
            self.data_memory[address] = 0
            return 0

    '''
    This method prints the content of the memory location at the specified address.
    '''
    def print_data(self, address):
        if address < 0 or address > 255:
            raise ValueError('Address ' + str(address) + ' does not exist. Terminating execution.')
        if address in self.data_memory:
            print('Address ' + str(address) + ' = ' + str(self.data_memory[address]))
        else:
            print('Address ' + str(address) + ' = 0')

    '''
    This method prints the content of the entire data memory.
    '''
    def print_all(self):
        print('Data memory content:')
        for address in range(0, 256):
            self.print_data(address)

    '''
    This method prints the content only of the data memory that have been used
    (initialized, read or written at least once).
    '''
    def print_used(self):
        print('Data memory content (used locations only):')
        for address in range(0, 256):
            if address in self.data_memory:
                print('Address ' + str(address) + ' = ' + str(self.data_memory[address]))


'''
This class models the data memory of the processor. When an object of the class
InstructionMemory is instantiated, the instruction memory model is generated
and automatically initialized with the program specified in the file passed as first
argument of the simulator. The memory has 256 location addressed form 0 to
255. Each memory location contains one instruction. Uninitialized instruction
memory locations contain the instruction NOP.
'''
class InstructionMemory:
    def __init__(self):
        self.instruction_memory = {}
        print('\nInitializing instruction memory content from file.')
        try:
            with open(sys.argv[2], 'r') as fd:
                file_content = fd.readlines()
        except:
             raise LookupError('Failed to open program file. Terminating execution.')
        file_content = ''.join(file_content)
        file_content = re.sub(r'#.*?\n', '', file_content)
        file_content = re.sub(r'#.*? ', '', file_content)
        file_content = re.sub(r'\s*[\n\t]+\s*', '', file_content)
        file_content = re.sub(r'\s\s+', ' ', file_content)
        file_content = file_content.replace(': ', ':')
        file_content = file_content.replace(' :', ':')
        file_content = file_content.replace(', ', ',')
        file_content = file_content.replace(' ,', ',')
        file_content = file_content.replace('; ', ';')
        file_content = file_content.replace(' ;', ';')
        file_content = file_content.strip()
        file_content = file_content.replace(' ', ',')
        file_content_list = file_content.split(';')
        file_content = None
        while '' in file_content_list:
            file_content_list.remove('')
        try:
            for entry in file_content_list:
                address, instruction_string = entry.split(':')
                instruction = instruction_string.split(',')
                if len(instruction)<1 or len(instruction)>4:
                    raise Exception('Malformed program.')
                self.instruction_memory[int(address)] = {'opcode': str(instruction[0]), 'op_1':'-','op_2':'-','op_3':'-' }
                if len(instruction)>1:
                    self.instruction_memory[int(address)]['op_1'] = str(instruction[1])
                if len(instruction)>2:
                    self.instruction_memory[int(address)]['op_2'] = str(instruction[2])
                if len(instruction)>3:
                    self.instruction_memory[int(address)]['op_3'] = str(instruction[3])
        except:
            raise MemoryError('Malformed program memory file. Terminating execution.')
        print('Instruction memory initialized.')

    '''
    This method returns the OPCODE of the instruction located in the instruction
    memory location in the specified address. For example, if the instruction is ADD
    R1, R2, R3;, this method returns ADD.
    '''
    def read_opcode(self, address):
        if address < 0 or address > 255:
            raise ValueError("Out of range instruction memory access. Terminating execution.")
        if address in self.instruction_memory:
            return self.instruction_memory[address]['opcode']
        else:
            return 'NOP'

    '''
    This method returns the first operand of the instruction located in the instruc-
    tion memory location in the specified address. For example, if the instruction
    is ADD R1, R2, R3;, this method returns R1.
    '''
    def read_operand_1(self, address):
        if address < 0 or address > 255:
            raise ValueError("Out of range instruction memory access. Terminating execution.")
        if address in self.instruction_memory:
            return self.instruction_memory[address]['op_1']
        else:
            return '-'

    '''
    This method returns the second operand of the instruction located in the instruc-
    tion memory location in the specified address. For example, if the instruction
    is ADD R1, R2, R3;, this method returns R2.
    '''
    def read_operand_2(self, address):
        if address < 0 or address > 255:
            raise ValueError("Out of range instruction memory access. Terminating execution.")
        if address in self.instruction_memory:
            return self.instruction_memory[address]['op_2']
        else:
            return '-'

    '''
    This method returns the third operand of the instruction located in the instruc-
    tion memory location in the specified address. For example, if the instruction
    is ADD R1, R2, R3;, this method returns R3.
    '''
    def read_operand_3(self, address):
        if address < 0 or address > 255:
            raise ValueError("Out of range instruction memory access. Terminating execution.")
        if address in self.instruction_memory:
            return self.instruction_memory[address]['op_3']
        else:
            return '-'

    '''
    This method prints the instruction located at the specified address.
    '''
    def print_instruction(self, address):
        if address < 0 or address > 255:
            raise ValueError("Out of range instruction memory access. Terminating execution.")
        if address in self.instruction_memory:
            print(self.read_opcode(address), end='')
            if self.read_operand_1(address)!='-':
                print(' ' + self.read_operand_1(address), end='')
            if self.read_operand_2(address)!='-':
                print(', ' + self.read_operand_2(address), end='')
            if self.read_operand_3(address)!='-':
                print(', ' + self.read_operand_3(address), end='')
            print(';')
        else:
            print('NOP;')

    '''
    This method prints the content of the entire instruction memory (i.e., the pro-
    gram).
    '''
    def print_program(self):
        print('Instruction memory content (program only, the rest are NOP):')
        for address in range(0, 256):
            if address in self.instruction_memory:
                print('Address ' + str(address) + ' = ', end='')
                self.print_instruction(address)


class ISA:
    """
    Simulator for an 8-bit instruction set architecture (ISA).

    This class manages the complete processor state:
    - 16 × 8-bit registers (RegisterFile)
    - 256-byte instruction memory (InstructionMemory)
    - 256-byte data memory (DataMemory)
    - Program counter (PC) and cycle counter

    It fetches, decodes, and executes instructions in a loop
    until either the cycle limit is reached or an END instruction is executed.

    The simulation can be started via the class method ISA.main().
    """

    OPCODES = {'LI', 'LD', 'ADD', 'SUB', 'OR', 'AND',
               'NOT', 'NOP', 'JR', 'SD', 'JEQ', 'JLT', 'END'}
    """Set of all supported instructions.
    
    Each opcode in this set has a corresponding method in this class.
    """

    def __init__(self):
        """
        Initialize a new ISA simulator instance.

        Creates fresh instances of:
        - RegisterFile (all registers initialized to 0)
        - InstructionMemory (loaded from program file)
        - DataMemory (loaded from data file)
        Sets program counter and cycle counter to 0.
        """
        self.registerFile = RegisterFile()
        self.dataMemory = DataMemory()
        self.instructionMemory = InstructionMemory()
        self.current_cycle = 0
        self.program_counter = 0

    def execute_operation(self, opcode: str, operands: list) -> None:
        """
        Execute a single instruction by dispatching to the appropriate handler.

        Looks up the handler method for the given opcode and calls it with
        the provided operands.

        Args:
            opcode: The instruction (must be in OPCODES)
            operands: List of string operands from instruction memory

        Raises:
            ValueError: If opcode is not supported
            RuntimeError: If a supported opcode has no matching method
            (and any exceptions raised by the specific handler)
        """
        if opcode not in self.OPCODES:
            raise ValueError(f"Unsupported opcode: {opcode!r}")
        try:
            handler = getattr(self, opcode)
        except AttributeError:
            raise RuntimeError(f"Opcode '{opcode}' is declared but not implemented")
        handler(operands)

    def read_opcode(self) -> str:
        """
        Fetch the opcode of the instruction at the current program counter.

        Returns:
            The opcode string (or 'NOP' if location is empty)
        """
        pc = self.program_counter
        return self.instructionMemory.read_opcode(pc)

    def read_operands(self) -> list[str]:
        """
        Fetch and clean the operands of the current instruction.

        Filters out placeholder '-' values that indicate missing operands.

        Returns:
            List of operand strings (only actual operands)
        """
        pc = self.program_counter
        op1 = self.instructionMemory.read_operand_1(pc)
        op2 = self.instructionMemory.read_operand_2(pc)
        op3 = self.instructionMemory.read_operand_3(pc)
        return [op for op in (op1, op2, op3) if op != '-']

    def increment_pc(self) -> None:
        """Increment the program counter by one."""
        self.program_counter += 1

    def wr(self, register: str, value: int) -> None:
        """Write an 8-bit value to the specified register."""
        self.registerFile.write_register(register, value)

    def rr(self, register: str) -> int:
        """Read the current 8-bit value from the specified register."""
        return self.registerFile.read_register(register)

    # ───────────────────────────────────────────────────────────────
    # Instruction handlers: 8-bit unsigned operations
    # ───────────────────────────────────────────────────────────────

    def ADD(self, operands: list) -> None:
        """ADD Rd, Rs, Rt   ->   Rd <- Rs + Rt   (8-bit unsigned)"""
        if len(operands) != 3:
            raise ValueError("ADD requires exactly 3 operands: Rd, Rs, Rt")
        result = self.rr(operands[1]) + self.rr(operands[2])
        self.wr(operands[0], result)
        self.increment_pc()

    def SUB(self, operands: list) -> None:
        """SUB Rd, Rs, Rt   ->   Rd <- Rs - Rt   (8-bit unsigned)"""
        if len(operands) != 3:
            raise ValueError("SUB requires exactly 3 operands: Rd, Rs, Rt")
        result = self.rr(operands[1]) - self.rr(operands[2])
        self.wr(operands[0], result)
        self.increment_pc()

    def LI(self, operands: list) -> None:
        """LI Rd, imm   ->   Rd <- imm   (load immediate 8-bit value)"""
        if len(operands) != 2:
            raise ValueError("LI requires exactly 2 operands: Rd, imm")
        self.wr(operands[0], operands[1])
        self.increment_pc()

    def LD(self, operands: list) -> None:
        """LD Rd, Ra   ->   Rd <- Mem[Ra]   (load byte from data memory)"""
        if len(operands) != 2:
            raise ValueError("LD requires exactly 2 operands: Rd, Ra")
        self.wr(operands[0], self.dataMemory.read_data(self.rr(operands[1])))
        self.increment_pc()

    def OR(self, operands: list) -> None:
        """OR Rd, Rs, Rt   ->   Rd <- Rs | Rt   (bitwise OR)"""
        if len(operands) != 3:
            raise ValueError("OR requires exactly 3 operands: Rd, Rs, Rt")
        self.wr(operands[0], self.rr(operands[1]) | self.rr(operands[2]))
        self.increment_pc()

    def AND(self, operands: list) -> None:
        """AND Rd, Rs, Rt   ->   Rd <- Rs & Rt   (bitwise AND)"""
        if len(operands) != 3:
            raise ValueError("AND requires exactly 3 operands: Rd, Rs, Rt")
        self.wr(operands[0], self.rr(operands[1]) & self.rr(operands[2]))
        self.increment_pc()

    def NOT(self, operands: list) -> None:
        """NOT Rd, Rs   ->   Rd <- ~Rs   (bitwise NOT, 8-bit)"""
        if len(operands) != 2:
            raise ValueError("NOT requires exactly 2 operands: Rd, Rs")
        self.wr(operands[0], ~self.rr(operands[1]))
        self.increment_pc()

    def NOP(self, operands: list) -> None:
        """NOP   ->   no operation (just advance PC)"""
        if operands:
            raise ValueError("NOP does not accept operands")
        self.increment_pc()

    def JR(self, operands: list) -> None:
        """JR Rt   ->   PC <- Rt   (jump to address in register, 8-bit)"""
        if len(operands) != 1:
            raise ValueError("JR requires exactly 1 operand: Rt")
        self.program_counter = self.rr(operands[0]) & 0xFF

    def SD(self, operands: list) -> None:
        """SD Rs, Ra   ->  Mem[Ra] <- Rs   (store byte to data memory)"""
        if len(operands) != 2:
            raise ValueError("SD requires exactly 2 operands: Rs, Ra")
        self.dataMemory.write_data(self.rr(operands[1]), self.rr(operands[0]))
        self.increment_pc()

    def JEQ(self, operands: list) -> None:
        """JEQ Rtarget, Rs, Rt   ->   if Rs == Rt then PC <- Rtarget"""
        if len(operands) != 3:
            raise ValueError("JEQ requires exactly 3 operands: Rtarget, Rs, Rt")
        if self.rr(operands[1]) == self.rr(operands[2]):
            self.program_counter = self.rr(operands[0]) & 0xFF
        else:
            self.increment_pc()

    def JLT(self, operands: list) -> None:
        """
        JLT Rtarget, Rs, Rt   ->   if Rs <- Rt (unsigned) then PC <- Rtarget

        Uses borrow detection: (Rs - Rt) & 0x100 indicates Rs <- Rt unsigned.
        """
        if len(operands) != 3:
            raise ValueError("JLT requires exactly 3 operands: Rtarget, Rs, Rt")
        if (self.rr(operands[1]) - self.rr(operands[2])) & 0x100:
            self.program_counter = self.rr(operands[0]) & 0xFF
        else:
            self.increment_pc()

    def END(self, operands: list) -> None:
        """END   ->   terminate simulation and print final machine state"""
        if operands:
            raise ValueError("END does not accept operands")
        self.final_print()
        print("\n---End of Simulation---\n")
        import sys
        sys.exit(0)

    def final_print(self) -> None:
        """
        Print final simulation state:
        - All 16 registers
        - Used data memory locations
        - Total number of cycles executed
        """
        self.registerFile.print_all()
        self.dataMemory.print_used()
        print(f"Executed in {self.current_cycle} cycles.")

    @staticmethod
    def max_cycles() -> int:
        """
        Parse the maximum cycle count from command-line argument (sys.argv[1]).

        Returns:
            Integer value of max_cycles

        Raises:
            SystemExit: If argument is missing or cannot be converted to int
        """
        try:
            return int(sys.argv[1])
        except (IndexError, ValueError) as e:
            print("First argument must be a valid integer (max cycles)", file=sys.stderr)
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(2)

    def run(self) -> None:
        """
        Run the main simulation loop.

        Executes instructions cycle-by-cycle until:
        - max_cycles is reached, or
        - an END instruction is executed, or
        - a runtime exception occurs

        On error, prints current machine state before exiting.
        """
        cycle_max = self.max_cycles()
        print('\n---Start of simulation---')
        while self.current_cycle < cycle_max:
            print(f"Current Cycle: {self.current_cycle}")
            print(f"Program Counter: {self.program_counter}\n")
            opcode = self.read_opcode()
            operands = self.read_operands()
            try:
                self.execute_operation(opcode, operands)
                print(f"{self.registerFile.print_all()}\n")
                print(f"{self.dataMemory.print_used()}")
                print('-'*50)
            except Exception as e:
                print("\nCurrent state is:")
                self.final_print()
                print(f"\nSimulation terminated at cycle {self.current_cycle} due to: {e}")
                sys.exit(1)
            self.current_cycle += 1
        print("Too few cycles to achieve any output!")
        print('\n---End of simulation---\n')

    @classmethod
    def main(cls) -> None:
        """
        Entry point: create an ISA instance and start the simulation.
        """
        sim = cls()
        sim.run()


if __name__ == "__main__":
    ISA.main()














