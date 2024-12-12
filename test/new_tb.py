import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, RisingEdge, FallingEdge, First
from cocotb.queue import Queue
from shared_memory import generate_shared_memory
from BittyEmulator import BittyEmulator

# Shared memory and instruction set
verilog_memory = generate_shared_memory(size=256)
emulator_memory = verilog_memory.copy()

# Load instructions from files
def load_instructions(em_file="instructions_for_em.txt"):
    with open(em_file, "r") as f:
        instructions_set = [int(line.strip(), 16) for line in f]
    return instructions_set

class TB:
    def __init__(self, dut, baud_rate=115200, clk_freq=50_000_000):
        self.dut = dut
        self.baud_rate = baud_rate
        self.clk_freq = clk_freq
        self.clks_per_bit = int(clk_freq / baud_rate)
        self.bit_time_ns = int(1e9 / baud_rate)  # Bit time in nanoseconds

        # Map I/O signals
        self.reset = dut.rst_n
        self.rx_data_bit = dut.uio_in_0
        self.tx_data_bit = dut.uo_out_0


        # Safely resolve MSB and LSB values
        self.clks_per_bit_msb = self.resolve_binary_value(dut.uio_in_7to3, 0, 4)  # Extract bits 7:3
        self.clks_per_bit_lsb = self.resolve_binary_value(dut.ui_in, 0, 7)   # Extract bits 7:0
        self.clks_per_bits = (self.clks_per_bit_msb << 8) | self.clks_per_bit_lsb
        # Reconstruct the full 13-bit value from MSB and LSB
        #self.clks_per_bit = (self.clks_per_bit_msb << 8) | self.clks_per_bit_lsb
        self.clock = dut.clk

        # Start the clock
        cocotb.start_soon(Clock(self.clock, 1e9 / clk_freq, units="ns").start())
    def resolve_binary_value(self, signal, start_bit, end_bit):
        """Resolve a portion of a signal's binary value safely."""
        value = signal.value
        if 'x' in str(value) or 'z' in str(value):
            self.dut._log.warning(f"Signal {signal._name} contains unresolved bits: {value}")
            return 0  # Default to 0 for unresolved bits
        return (int(value) >> start_bit) & ((1 << (end_bit - start_bit + 1)) - 1)




    async def reset_dut(self):
        """Apply and release active-low reset."""
        self.reset.value = 0
        self.rx_data_bit.value = 1

        # Assign the decremented value to self.dut.clks_per_bit.value
        # Assign the decremented value back to the DUT inputs
        self.dut.ui_in.value = (int(self.clks_per_bit) -1) & 0xFF  # Set LSB (bits 7:0)
        self.dut.uio_in_7to3.value = ((int(self.clks_per_bit) -1)  >> 8) & 0x1F  # Set MSB (bits 12:8)


        print("Resetting DUT")
        await Timer(100, units="us")  # Hold reset for 100 microseconds
        self.reset.value = 1
        print("DUT reset complete")

    async def send_uart_data(self, data):
        """Simulate sending a byte over UART."""
        self.rx_data_bit.value = 0  # Start bit
        print("TX -> RX Start bit: 0")
        await Timer(self.bit_time_ns, units="ns")

        for i in range(8):  # Data bits (LSB first)
            bit = (data >> i) & 1
            self.rx_data_bit.value = bit
            print(f"TX -> RX Bit {i}: {bit}")
            await Timer(self.bit_time_ns, units="ns")

        self.rx_data_bit.value = 1  # Stop bit
        print("TX -> RX Stop bit: 1")

    async def transmit_from_tx(self):
        """Capture the UART transmission."""
        print("before tx star bit")
        await FallingEdge(self.tx_data_bit)  # Wait for start bit
        print("RX <- TX Start bit: 0")
        received_bits = []

        for i in range(8):  # Capture 8 data bits
            await Timer(self.bit_time_ns, units="ns")
            bit = int(self.tx_data_bit.value)
            received_bits.append(bit)
            print(f"RX <- TX Bit {i}: {bit}")

        print("RX <- TX Stop bit: 1")
        return sum((bit << i) for i, bit in enumerate(received_bits))

    async def wait_for_rx_done(self, timeout_us=100):
        """Wait for the RX `done` signal to go high or timeout."""
        try:
            print("Waiting for RX done signal...")
            await First(RisingEdge(self.dut.user_project.top_inst.uart_inst.rx_done), Timer(timeout_us, units="us"))
            print("RX done signal received.")
        except TimeoutError:
            print("Timeout waiting for RX done signal.")
            self.dut._log.warning("Timeout waiting for RX done signal.")

@cocotb.test()
async def uart_module_test(dut):
    """Integrated UART and instruction processing test."""
    tb = TB(dut)
    log_file = "uart_emulator_log.txt"

    # Emulator and instructions
    emulator = BittyEmulator()
    instruction_set = load_instructions()

    await tb.reset_dut()

    flag_queue = Queue()  # Queue for UART communication

    # UART receiver task (runs in parallel)
    async def uart_receiver():
        while True:
            flag_byte = await tb.transmit_from_tx()
            print(f"Received Flag Byte: 0x{flag_byte:02X}")
            await flag_queue.put(flag_byte)
            print("Flag byte added to queue.")

    uart_task = cocotb.start_soon(uart_receiver())

    async def process_flag(flag_byte):
        """Process UART flag."""
        print(f"Processing Flag Byte: 0x{flag_byte:02X}")
        if flag_byte == 0x03:  # Instruction
            print("Instruction flag received.")
            address = await flag_queue.get()
            print(f"Address received: {address}")
            if address < len(instruction_set):
                instruction = instruction_set[address]
                print(f"Instruction: 0x{instruction:04X}")
                await tb.send_uart_data(instruction >> 8)  # High byte
                await tb.wait_for_rx_done()
                await tb.send_uart_data(instruction & 0xFF)  # Low byte
        elif flag_byte == 0x01:  # Load
            print("Load flag received.")
            address = await flag_queue.get()
            print(f"Address received: {address}")
            if address < len(emulator_memory):
                data = emulator_memory[address]
                print(f"Loaded Data: 0x{data:04X} from address 0x{address:02X}")
                await tb.send_uart_data(data >> 8)
                await tb.wait_for_rx_done()
                await tb.send_uart_data(data & 0xFF)
        elif flag_byte == 0x02:  # Store
            print("Store flag received.")
            address = await flag_queue.get()
            print(f"Address received: {address}")
            high_byte = await flag_queue.get()
            print(f"High byte received: 0x{high_byte:02X}")
            low_byte = await flag_queue.get()
            print(f"Low byte received: 0x{low_byte:02X}")
            emulator_memory[address] = (high_byte << 8) | low_byte
            print(f"Stored 0x{emulator_memory[address]:04X} at address 0x{address:02X}")

    try:
        pc = 0
        i = 0
        with open(log_file, "w") as log:
            while pc < len(instruction_set):
                print("start")
                flag_byte = await flag_queue.get()
                print("took flag")
                await process_flag(flag_byte)

                instruction = instruction_set[pc]
                format_code = instruction & 0x0003

                if format_code == 3:
                    flag_byte = await flag_queue.get()
                    dut._log.info(f"Received flag byte: {flag_byte:X}")
                    await process_flag(flag_byte)

                await FallingEdge(dut.user_project.top_inst.bitty_inst.done)

                i = emulator.evaluate(i)
                pc = int(dut.user_project.top_inst.pc_inst.d_out.value)

                rx_register = (instruction & 0xE000) >> 13

                try:
                    dut_rx_value = int(dut.user_project.top_inst.bitty_inst.out[rx_register].value)
                except Exception as e:
                    dut_rx_value = 0
                    dut._log.warning(f"Error reading DUT RX register {rx_register}: {e}")
                
                if format_code != 2:
                    emulator_rx_value = emulator.get_register_value(rx_register)
                    if dut_rx_value == emulator_rx_value:
                        log.write(f"Instruction: {instruction:04X}, Register: {rx_register:04X}\n")
                        log.write(f"PC {pc:04X} VS em_i {i:04X}\n")
                        log.write(f"OK -> RX matches ({dut_rx_value:04X})\n\n")
                    else:
                        log.write(f"Instruction: {instruction:04X}, Register: {rx_register:04X}\n")
                        log.write(f"PC {pc:04X} VS em_i {i:04X}\n")
                        log.write(f"ERROR -> RX mismatch (DUT: {dut_rx_value:04X}, Emulator: {emulator_rx_value:04X})\n")
                        break

    except Exception as e:
        dut._log.error(f"Test error: {e}")

    finally:
        uart_task.kill()
