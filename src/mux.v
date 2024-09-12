module mux(

    input [15:0] reg0,
    input [15:0] reg1,
    input [15:0] reg2,
    input [15:0] reg3,
    input [15:0] reg4,
    input [15:0] reg5,
    input [15:0] reg6,
    input [15:0] reg7,
    input [15:0] im_d,
    input [15:0] def_val,

    input [3:0] mux_sel,
    output reg [15:0] mux_out
);

    always @(*) begin
        case(mux_sel)
            4'b0000: mux_out= reg0;
            4'b0001: mux_out= reg1;
            4'b0010: mux_out= reg2;
            4'b0011: mux_out= reg3;
            4'b0100: mux_out= reg4;
            4'b0101: mux_out= reg5;
            4'b0110: mux_out= reg6;
            4'b0111: mux_out= reg7;
            4'b1000: mux_out= im_d;
            4'b1001: mux_out= def_val;

            default: mux_out= 16'b0;
        endcase

    end

endmodule