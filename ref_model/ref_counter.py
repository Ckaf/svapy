def reference_counter(clk_seq, rst_n_seq):
    """
    Reference model of the Verilog counter module.

    Args:
        clk_seq (list of int): Sequence of clock signal values (0 or 1).
        rst_n_seq (list of int): Sequence of reset signal values (0 or 1).

    Returns:
        list of int: Sequence of counter values.
    """

    # Initialize the counter and the output sequence
    prev_count = 0
    current_count = 0
    count_seq = []

    for clk, rst_n in zip(clk_seq, rst_n_seq):
        prev_count = current_count
        if not rst_n:  # Active low reset
            current_count = 0
        elif clk:  # Positive clock edge
            current_count += 1
        count_seq.append(prev_count)
        

    return count_seq
