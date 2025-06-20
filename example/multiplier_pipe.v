module multiplier_pipe (
    input clk,
    input rst_n,
    input valid_in,
    input [7:0] data_in,
    output reg valid_out,
    output reg [7:0] data_out
);

reg next_valid;
reg [7:0] next_data;

initial begin
    valid_out = 0;
    data_out = 0;
    next_data = 0;
end

always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        valid_out <= 1'b0;
        data_out <= 8'b0;
    end else begin
        valid_out <= next_valid;
        data_out <= next_data;
    end
end

always @(*) begin
    next_valid = valid_in;
    if (valid_in) begin
        next_data = (data_in < 128) ? data_in * 2 : 255;
    end else begin
        next_data = 0;
    end
end

endmodule
