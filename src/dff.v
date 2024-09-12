import "DPI-C" function void notify_counter_nine_here();

module dff(
    input clk,
    input en,
    input wire [15:0] d_in,
    input [15:0] starting,
    input reset,

    output reg [15:0] mux_out

);
    always @(posedge clk) begin
        if (reset) begin
            /* verilator lint_off BLKSEQ */
            mux_out = starting;
        end
        else if(en) begin
            //notify_counter_nine_here();
            /* verilator lint_off BLKSEQ */
            mux_out = d_in;
        end
    end
endmodule