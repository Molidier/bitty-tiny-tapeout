/* verilator lint_off MODDUP */
module bitty(
    input run,
    input clk,
    input reset,
    input [15:0] d_instr,

    output [15:0] d_out,
    output done
);
    genvar k;
    wire [3:0] mux_sel;
    wire [7:0] en;
    logic [15:0] out [7:0];

    wire [15:0] out_mux;

    // ALU components
    wire [15:0] alu_out;

    // CPU components
    wire en_s, en_c, en_inst;
    wire [2:0] alu_sel;
    wire [15:0] instruction;
    wire [15:0] im_d;

    // Additional components
    wire [15:0] regs;
    wire [15:0] regc;

    // CPU connection
    cpu cpu_inst(
        .clk(clk),
        .run(run),
        .reset(reset),
        .d_inst(instruction),
        .mux_sel(mux_sel),
        .done(done),
        .sel(alu_sel),
        .en_s(en_s),
        .en_c(en_c),
        .en(en),
        .en_inst(en_inst),
        .im_d(im_d)
    );



    // ALU Connection
    alu alu_inst(
        .in_a(regs),
        .in_b(out_mux),
        .select(alu_sel),
        .alu_out(alu_out) // Changed to alu_out
    );

    // MUX connection
    generate
        for (k = 0; k < 8; k++) begin
            /* verilator lint_off PINMISSING */
            dff reg_out (
                .clk(clk),
                .en(en[k]),
                .d_in(regc),
                .reset(reset),
                .starting(16'h0000), // Corrected input signal name
                .mux_out(out[k])      // Corrected output signal name
            );
        end
    endgenerate

    mux mux_inst(
        .reg0(out[0]),
        .reg1(out[1]),
        .reg2(out[2]),
        .reg3(out[3]),
        .reg4(out[4]),
        .reg5(out[5]),
        .reg6(out[6]),
        .reg7(out[7]),
        .im_d(im_d),
        .def_val(0),
        .mux_sel(mux_sel),
        .mux_out(out_mux)
    );

    dff reg_inst(clk, en_inst, d_instr, 16'h0000, reset, instruction);
    dff reg_s(clk, en_s, out_mux, 16'h0000, reset, regs);
    dff reg_c(clk, en_c, alu_out, 16'h0000, reset, regc);

    // Assigning out array elements to module outputs
    assign d_out = regc;
    

    /*assign rega = regs;
    assign regb = out_mux;

    assign regcc = regc;
    assign regss = regs;
    assign reg0 = out[0];
    assign reg1 = out[1];
    assign reg2 = out[2];
    assign reg3 = out[3];
    assign reg4 = out[4];
    assign reg5 = out[5];
    assign reg6 = out[6];
    assign reg7 = out[7];
    assign reginst = instruction;*/

endmodule
