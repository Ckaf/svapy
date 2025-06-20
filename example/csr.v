module csr (
    input clk,
    input reset_n,
    
    // CSR interface
    input [7:0] addr,
    input [31:0] wdata,
    input wr_en,
    input rd_en,
    output reg [31:0] rdata,
    output reg ready
);
    // Define CSR addresses
    localparam CTRL_ADDR    = 8'h00;
    localparam STATUS_ADDR  = 8'h04;
    localparam CONFIG_ADDR  = 8'h08;
    localparam DATA_IN_ADDR = 8'h0C;
    localparam DATA_OUT_ADDR= 8'h10;
    localparam VERSION_ADDR = 8'hFC;

    // CSR registers
    reg [31:0] ctrl_reg;     // Control register
    reg [31:0] status_reg;   // Status register
    reg [31:0] config_reg;   // Configuration register
    reg [31:0] data_out_reg; // Data output register
    
    // Internal signals
    reg [31:0] data_buffer;
    reg [3:0] state;
    reg processing;
    reg [7:0] counter;
    
    // Version register (constant)
    wire [31:0] version_reg = 32'h0001_0002; // Major=1, Minor=2
    
    // Control register bits
    localparam START_BIT = 0;
    localparam RESET_BIT = 1;
    localparam IE_BIT    = 2;  // Interrupt enable
    
    // Status register bits
    localparam DONE_BIT  = 0;
    localparam BUSY_BIT  = 1;
    localparam ERR_BIT   = 2;
    
    // State machine states
    localparam IDLE      = 4'b0001;
    localparam PROCESS   = 4'b0010;
    localparam COMPLETE  = 4'b0100;
    localparam ERROR     = 4'b1000;
    
    // Read logic
    always @(*) begin
        rdata = 32'h0000_0000;
        ready = 1'b1;
        
        if (rd_en) begin
            case (addr)
                CTRL_ADDR:     rdata = ctrl_reg;
                STATUS_ADDR:   rdata = status_reg;
                CONFIG_ADDR:   rdata = config_reg;
                DATA_OUT_ADDR: rdata = data_out_reg;
                VERSION_ADDR:  rdata = version_reg;
                default:       rdata = 32'hDEAD_BEEF; // Invalid address
            endcase
        end
    end
    
    // Write logic
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            // Reset all writable registers
            ctrl_reg   <= 32'h0000_0000;
            config_reg <= 32'h0000_0000;
            status_reg <= 32'h0000_0000;
            data_buffer <= 32'h0000_0000;
            data_out_reg <= 32'h0000_0000;
            
            // Reset state machine
            state <= IDLE;
            processing <= 1'b0;
            counter <= 8'h00;
        end else begin
            // Handle CSR writes
            if (wr_en) begin
                case (addr)
                    CTRL_ADDR: begin
                        ctrl_reg[31:3] <= wdata[31:3];
                        ctrl_reg[IE_BIT] <= wdata[IE_BIT];
                        ctrl_reg[RESET_BIT] <= wdata[RESET_BIT];
                        ctrl_reg[START_BIT] <= wdata[START_BIT];
                    end
                    
                    CONFIG_ADDR: begin
                        config_reg <= wdata;
                    end
                    
                    DATA_IN_ADDR: begin
                        data_buffer <= wdata;
                    end
                    
                    STATUS_ADDR: begin
                        // Only error bit is writable
                        status_reg[ERR_BIT] <= wdata[ERR_BIT];
                    end
                endcase
            end
            
            // Clear start bit after one cycle
            if (ctrl_reg[START_BIT]) begin
                ctrl_reg[START_BIT] <= 1'b0;
            end
            
            // State machine
            case (state)
                IDLE: begin
                    status_reg[BUSY_BIT] <= 1'b0;
                    status_reg[DONE_BIT] <= 1'b0;
                    counter <= 8'h00;
                    
                    if (ctrl_reg[START_BIT]) begin
                        state <= PROCESS;
                        status_reg[BUSY_BIT] <= 1'b1;
                        status_reg[DONE_BIT] <= 1'b0;
                    end
                end
                
                PROCESS: begin
                    counter <= counter + 1;
                    
                    // Simple processing example
                    data_out_reg <= data_buffer + counter;
                    
                    if (counter == config_reg[7:0]) begin
                        state <= COMPLETE;
                        status_reg[DONE_BIT] <= 1'b1;
                    end else if (counter == 8'hFF) begin
                        state <= ERROR;
                        status_reg[ERR_BIT] <= 1'b1;
                    end
                end
                
                COMPLETE: begin
                    if (!ctrl_reg[START_BIT]) begin
                        state <= IDLE;
                        status_reg[BUSY_BIT] <= 1'b0;
                    end
                end
                
                ERROR: begin
                    if (ctrl_reg[RESET_BIT]) begin
                        state <= IDLE;
                        status_reg <= 32'h0000_0000;
                        ctrl_reg[RESET_BIT] <= 1'b0;
                    end
                end
            endcase
        end
    end
    
    // Generate interrupt signal (example)
    wire interrupt = status_reg[DONE_BIT] && ctrl_reg[IE_BIT];
    
endmodule
