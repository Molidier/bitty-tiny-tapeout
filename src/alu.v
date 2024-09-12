/****** alu.sv ******/


module alu(
    input [2:0] select,
    input [15:0] in_a,
    input [15:0] in_b,
    output reg [15:0] alu_out
);
    reg [15:0] res; 

    parameter ADD = 3'b000; 
    parameter SUB = 3'b001;
    parameter AND = 3'b010;
    parameter OR =  3'b011;
    parameter XOR = 3'b100;
    parameter SHL = 3'b101;
    parameter SHR = 3'b110;
    parameter CMP = 3'b111;

    always @(*) begin
        case (select)
            ADD: res = in_a + in_b;
            SUB: res = in_a - in_b;
            AND: res = in_a & in_b;
            OR:  res = in_a | in_b;
            XOR: res = in_a ^ in_b;
            SHL: res = in_a << (in_b % 32); 
            SHR: res = in_a >> (in_b % 32); 
            CMP: begin
                if(in_a == in_b) begin
                    res = 0;
                end
                else if(in_a > in_b) begin
                    res = 1;
                end
                else begin
                    res = 2;
                end
            end
            default: res = 16'h0000; // Default value as 16-bit zero
        endcase
    end

    assign alu_out = res;

endmodule
