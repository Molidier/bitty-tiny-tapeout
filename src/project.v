/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_bitty (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

    /* verilator lint_off UNUSEDSIGNAL */
    wire _unused = &{ena, rst_n, 1'b0, ui_in[7:2], uio_in};

    wire reset, run, done;
    reg [15:0] d_out;

    assign reset= ui_in[0];
    assign run = ui_in[1];

    
    assign uo_out = 8'b0;
    assign uio_out = 8'b0;
    assign uio_oe = 8'b0;



  // All output pins must be assigned. If not used, assign to 0.
    parameter S0 = 2'b00;
    parameter S1 = 2'b01;
    parameter S2 = 2'b10;
    parameter S3 = 2'b11;

    reg [1:0] cur_state, next_state;

    reg run_bitty;
    reg [15:0] mem_out;
    reg [7:0] addr;
    reg [7:0] new_pc;

    branch_logic instance_bl(
        .address(addr),
        .instruction(mem_out),
        .last_alu_result(d_out),
        .new_pc(new_pc)
    );

    pc instance_pc(
        .clk(clk),
        .en_pc(done),
        .reset(reset),
        .d_in(new_pc),
        .d_out(addr)
    );

    memory instance_memory(
        .clk(clk),
        .addr(addr),
        .out(mem_out)
    );


    always @(*) begin
        case (cur_state)
            S0: begin
                run_bitty = 0;
            end 
            S3:  run_bitty = 1;
            default: run_bitty = 0;
        endcase
    end
    

    always @(posedge clk) begin
        if(run) begin
            cur_state <= next_state;
        end
        if(reset || done) begin
            cur_state<= S0;
        end
    end

    always @(*) begin
        case(cur_state)
            S0: next_state = S1;
            S1: next_state = S2;
            S2: next_state = S3;
            S3: next_state = S0;
            default: next_state = S0;
        endcase
    end




    bitty instance_bitty(
        .clk(clk),
        .reset(reset),
        .run(run_bitty),
        .d_instr(mem_out),
        .done(done),
        .d_out(d_out)
    );

   assign uo_out[0] =  done;

endmodule
