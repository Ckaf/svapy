# Configuration
DESIGN = example/counter.v
MODULE_NAME = counter
TEST_DIR = gen/tests
TB_FILES := $(wildcard $(TEST_DIR)/*.sv)

BUILD_DIR = build
BIN_DIR = $(BUILD_DIR)/bin
ifeq ($(wildcard $(BUILD_DIR)),)
  $(shell mkdir -p $(BIN_DIR))
endif

.PHONY: all clean sim generate test python-test help test-unit test-integration test-lint test-all

# Default target
all: generate sim

# Help target
help:
	@echo "Available targets:"
	@echo "  generate       - Generate test files from Verilog module"
	@echo "  sim            - Compile and run SystemVerilog simulations"
	@echo "  python-test    - Run Python property-based tests"
	@echo "  test           - Run both Python tests and SystemVerilog simulations"
	@echo "  test-unit      - Run unit tests"
	@echo "  test-integration - Run integration tests"
	@echo "  test-lint      - Run linting and type checking"
	@echo "  test-all       - Run all tests and checks"
	@echo "  clean          - Clean build artifacts"
	@echo ""
	@echo "Usage examples:"
	@echo "  make generate DESIGN=example/counter.v MODULE_NAME=counter"
	@echo "  make test DESIGN=example/multiplier_pipe.v MODULE_NAME=multiplier_pipe"
	@echo "  make test-all"

# Generate test files
generate:
	@echo "Generating test files for $(MODULE_NAME) from $(DESIGN)..."
	poetry run python main.py $(MODULE_NAME) $(DESIGN)
	@echo "== Test generation complete"

# SystemVerilog simulations
SIMS := $(patsubst $(TEST_DIR)/%.sv, $(BIN_DIR)/%, $(TB_FILES))

$(BIN_DIR)/%: $(DESIGN) $(TEST_DIR)/%.sv | $(BIN_DIR)
	@echo "Compiling and simulating $< + $@.sv ..."
	iverilog -g2012 -o $@.out $(DESIGN) $(TEST_DIR)/$*.sv && \
	vvp $@.out && \
	mv $@.out $@ && \
	echo "== Simulation of $* done. Binary: $@"

$(BIN_DIR):
	mkdir -p $(BIN_DIR)

sim: generate $(SIMS)

# Python property-based tests
python-test: generate
	@echo "Running Python property-based tests for $(MODULE_NAME)..."
	poetry run python -m pytest gen/run_$(MODULE_NAME).py -v
	@echo "== Python tests complete"

# Run all tests
test: generate
	@echo "Running all tests for $(MODULE_NAME)..."
	@echo "1. Running Python property-based tests..."
	poetry run python -m pytest gen/run_$(MODULE_NAME).py -v
	@echo "2. Running SystemVerilog simulations..."
	$(MAKE) sim DESIGN=$(DESIGN) MODULE_NAME=$(MODULE_NAME)
	@echo "== All tests complete"

# Unit tests
test-unit:
	@echo "Running unit tests..."
	poetry run pytest tests/ -m "not integration" --cov=svapy --cov-report=term-missing

# Integration tests
test-integration:
	@echo "Running integration tests..."
	poetry run pytest tests/ -m "integration" --cov=svapy --cov-append --cov-report=term-missing

# Linting
test-lint:
	@echo "Running linting checks..."
	poetry run flake8 svapy/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
	poetry run flake8 svapy/ tests/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	@echo "Running type checking..."
	poetry run mypy svapy/ --show-error-codes --strict

# All tests
test-all: test-lint test-unit test-integration
	@echo "All tests completed!"

clean:
	rm -rf $(BUILD_DIR)
	rm -rf gen/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf *.egg-info/
