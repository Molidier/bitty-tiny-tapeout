# Makefile
# See https://docs.cocotb.org/en/stable/quickstart.html for more info

# defaults
SIM ?= verilator
TOPLEVEL_LANG ?= verilog
SRC_DIR = $(PWD)/../src
PROJECT_SOURCES = \
  project_final.v \
  fui_control_2.v \
  alu.v \
  bitty.v \
  branch_logic.v \
  cpu.v \
  dff_lol.v \
  fetch_instruction.v \
  lsu.v \
  mux.v \
  mux2to1_1.v \
  mux2to1_8.v \
  mux2to1.v \
  pc.v \
  uart_module.v \
  uart_tx.v \
  uart_rx.v

ifneq ($(GATES),yes)

# RTL simulation:
SIM_BUILD				= sim_build/rtl
VERILOG_SOURCES += $(addprefix $(SRC_DIR)/,$(PROJECT_SOURCES))
COMPILE_ARGS 		+= -I$(SRC_DIR)

else

# Gate level simulation:
SIM_BUILD				= sim_build/gl
COMPILE_ARGS    += -DGL_TEST
COMPILE_ARGS    += -DFUNCTIONAL
COMPILE_ARGS    += -DUSE_POWER_PINS
COMPILE_ARGS    += -DSIM
COMPILE_ARGS    += -DUNIT_DELAY=\#1
VERILOG_SOURCES += $(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/verilog/primitives.v
VERILOG_SOURCES += $(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/verilog/sky130_fd_sc_hd.v

# this gets copied in by the GDS action workflow
VERILOG_SOURCES += $(PWD)/gate_level_netlist.v

endif

# Include the testbench sources:
VERILOG_SOURCES += $(PWD)/tb.v
TOPLEVEL = tb

# MODULE is the basename of the Python test file
MODULE = new_tb

# Verilator-specific flags
VERILATOR_FLAGS += --trace --Wno-IMPLICIT --Wno-WIDTHEXPAND --Wno-LATCH
# Optional: Enable waveform generation (VCD format)
WAVEFORM = 1
VERILATOR_ARGS += --trace
EXTRA_ARGS += --trace --trace-structs
# Specify Verilog source files
# Export environment variables for cocotb
export COCOTB_RESOLVE_MODULE=$(MODULE)

# Include Cocotb's Makefile
include $(shell cocotb-config --makefiles)/Makefile.sim
