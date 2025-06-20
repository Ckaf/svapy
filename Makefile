DESIGN = example/csr.v
TEST_DIR = gen/tests
TB_FILES := $(wildcard $(TEST_DIR)/*.sv)

BUILD_DIR = build
BIN_DIR = $(BUILD_DIR)/bin
ifeq ($(wildcard $(BUILD_DIR)),)
  $(shell mkdir -p $(BIN_DIR))
endif

.PHONY: all clean sim

all: sim

SIMS := $(patsubst $(TEST_DIR)/%.sv, $(BIN_DIR)/%, $(TB_FILES))

$(BIN_DIR)/%: $(DESIGN) $(TEST_DIR)/%.sv | $(BIN_DIR)
	@echo "Compiling and simulating $< + $@.sv ..."
	iverilog -g2012 -o $@.out $(DESIGN) $(TEST_DIR)/$*.sv && \
	vvp $@.out && \
	mv $@.out $@ && \
	echo "== Simulation of $* done. Binary: $@"

$(BIN_DIR):
	mkdir -p $(BIN_DIR)

sim: $(SIMS)

clean:
	rm -rf $(BUILD_DIR)
