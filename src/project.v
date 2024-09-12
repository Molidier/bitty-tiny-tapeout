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

  // All output pins must be assigned. If not used, assign to 0.
    typedef enum  logic [1:0] { 
        S0 = 2'b00,
        S1 = 2'b01,
        S2 = 2'b10,
        S3 = 2'b11
    } states;

    states cur_state, next_state;

    logic run_bitty;
    logic [15:0] mem_out;
    logic [7:0] addr;
    logic [7:0] new_pc;
    logic [7:0] d_in;

    branch_logic instance4(
        .address(addr),
        .instruction(mem_out),
        .last_alu_result(d_out),
        .done(done),
        .new_pc(new_pc)
    );

    pc instance1(
        .clk(clk),
        .en_pc(done),
        .reset(rst_n),
        .d_in(new_pc),
        .d_out(addr)
    );

    memory instance2(
        .clk(clk),
        .addr(addr),
        .out(mem_out)
    );



    logic instr_valid;

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
            cur_state <= next_state;
          //  $display("cur_state: ", cur_state);
            //$display("instr: ", instr);
        if(rst_n || done) begin
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


    bitty instance3(
        .clk(clk),
        .reset(rst_n),
        .run(run_bitty),
        .d_instr(mem_out),
        .done(done),
        .d_out(d_out)
    );

 

    assign instr = mem_out;

endmodule
