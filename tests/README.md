# Tests

This directory contains comprehensive tests for the Svapy framework.

## Test Structure

- **`test_parser.py`** - Unit tests for Verilog parsing functionality
- **`test_core.py`** - Unit tests for code generation functionality  
- **`test_integration.py`** - Integration tests for complete workflows

## Running Tests

### All Tests
```bash
make test-all
```

### Unit Tests Only
```bash
make test-unit
```

### Integration Tests Only
```bash
make test-integration
```

### Linting
```bash
make test-lint
```

### Individual Test Files
```bash
poetry run pytest tests/test_parser.py -v
poetry run pytest tests/test_core.py -v
poetry run pytest tests/test_integration.py -v
```

## Test Coverage

Tests provide 97% code coverage:
- `svapy/core.py`: 100% coverage
- `svapy/parser.py`: 92% coverage (missing parameter width resolution)
- `svapy/templates/`: 100% coverage

## Test Categories

### Unit Tests
- **Parser Tests**: Verilog module parsing, port extraction, error handling
- **Core Tests**: Template rendering, code generation, edge cases

### Integration Tests
- **Workflow Tests**: Complete end-to-end testing with real Verilog modules
- **Makefile Tests**: Build system integration
- **Error Handling**: Invalid input handling
- **Consistency Tests**: Template rendering consistency

## Test Markers

- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.xfail` - Expected failures (e.g., unimplemented features)

## Adding New Tests

1. **Unit Tests**: Add to appropriate test file in `tests/`
2. **Integration Tests**: Add to `test_integration.py` with `@pytest.mark.integration`
3. **Test Data**: Use temporary files for test data
4. **Cleanup**: Ensure proper cleanup in `teardown_method`

## CI/CD Integration

Tests are automatically run in GitHub Actions:
- Unit tests on Python 3.12 and 3.13
- Integration tests with coverage reporting
- Linting with flake8
- Code generation validation
