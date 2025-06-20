module counter (
    input wire clk,
    input wire rst_n,
    output reg [7:0] count
);
    initial begin
        count = 0;
    end
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) count <= 0;
        else count <= count + 1;
    end
endmodule
