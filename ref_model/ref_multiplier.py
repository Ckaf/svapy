def reference_multiplier(clk_seq, rst_n_seq, valid_in_seq, data_in_seq):
    """
    Reference model for the pipelined multiplier with saturation.
    
    Args:
        clk_seq (list): Sequence of clock values (0/1)
        rst_n_seq (list): Sequence of reset values (0/1)
        valid_in_seq (list): Sequence of valid input signals
        data_in_seq (list): Sequence of input data values (0-255)
        
    Returns:
        tuple: (valid_out_seq, data_out_seq)
    """
    # Initialize registers
    valid_reg = 0
    data_reg = 0
    # Store previous inputs for pipeline behavior
    prev_valid_in = 0
    prev_data_in = 0
    
    valid_out_seq = []
    data_out_seq = []
    prev_clk = 0  # Previous clock state for edge detection
    
    for i in range(len(clk_seq)):
        clk = clk_seq[i]
        rst_n = rst_n_seq[i]
        valid_in = valid_in_seq[i]
        data_in = data_in_seq[i]
        
        # Calculate next values based on previous inputs
        if prev_valid_in:
            if prev_data_in < 128:
                next_data_val = prev_data_in * 2
            else:
                next_data_val = 255  # Saturation
        else:
            next_data_val = 0
            
        next_valid_val = prev_valid_in
        
        # Reset handling (asynchronous)
        if not rst_n:
            valid_reg = 0
            data_reg = 0
        # Clock edge detection (posedge)
        elif prev_clk == 0 and clk == 1:
            valid_reg = next_valid_val
            data_reg = next_data_val
        
        # Store current register values
        valid_out_seq.append(valid_reg)
        data_out_seq.append(data_reg)
        
        # Update previous values for next cycle
        prev_valid_in = valid_in
        prev_data_in = data_in
        prev_clk = clk
    
    return valid_out_seq, data_out_seq
