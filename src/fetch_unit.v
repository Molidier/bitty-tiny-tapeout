/******* fetch_unit.sv ****/
/* verilator lint_off DECLFILENAME */
/* verilator lint_off MODDUP */
module memory(
    input clk,
    input [7:0] addr,
    output reg [15:0] out
);
    reg [15:0] memory_array [0:255]; // 256 instructions each with 16 bits
    initial begin
        $readmemh("instructions.txt", memory_array);
    end

    always @(posedge clk) begin
        out <= memory_array[addr];
    end
endmodule

module pc(
    input clk,
    input en_pc,
    input reset,
    input [7:0] d_in,
    output reg [7:0] d_out
);

    always @(posedge clk) begin
        if (reset) begin
            d_out <= 8'b0;
        end else if (en_pc) begin
            d_out <= d_in;
        end
    end

endmodule

/* verilator lint_off MODDUP */
module branch_logic (
    input [7:0] address,
    /* verilator lint_off UNUSED */
    input [15:0] instruction,
    input [15:0] last_alu_result,
    output reg [7:0] new_pc
);
   /* typedef enum  logic [1:0] { 
        S0 = 2'b00,
        S1 = 2'b01,
        S2 = 2'b10,
        S3 = 2'b11
    } states;*/

    //states cur_state, next_state;

    reg [1:0] branch_cond;
    reg [7:0] immediate;
    reg [1:0] format;
    assign branch_cond = instruction[3:2];
    assign immediate = instruction[11:4];
    assign format = instruction[1:0];

    always @(*) begin
        if(format == 2'b10) begin
            case(branch_cond)
            2'b00: begin
                if (last_alu_result == 0) begin
                    new_pc = immediate;
                    $display("branching to: ", immediate);
                end else begin
                    new_pc = address + 1;
                end
            end
            2'b01: begin
                if (last_alu_result == 1) begin
                    new_pc = immediate;
                    $display("branching to: ", immediate);
                end else begin
                    new_pc = address + 1;
                end  
            end
            2'b10: begin
                if (last_alu_result == 2) begin
                    new_pc = immediate;
                    $display("branching to: ", immediate);
                end else begin
                    new_pc = address + 1;
                end  
            end
            default: begin
                new_pc = address + 1;
            end
            endcase
        end
        else begin
            new_pc = address + 1;
        end
    end

endmodule
