from pypest import describe, it, expect, before_each, after_each, before_all, after_all, run_tests

# Example test suite demonstrating basic functionality
describe("Math operations", lambda: [
  it("should add numbers correctly", lambda: (
    expect(2 + 3).to_equal(5)
  )),

  it("should multiply numbers correctly", lambda: (
    expect(4 * 5).to_equal(20)
  )),

  it("should handle division", lambda: (
    expect(10 / 2).to_equal(5)
  )),
])

# Example with hooks and state
counter = 0

describe("Counter tests with hooks", lambda: [
  before_all(lambda: print("Starting counter tests")),

  after_all(lambda: print("Finished counter tests")),

  before_each(lambda: globals().update(counter=0)),

  after_each(lambda: print(f"Counter after test: {counter}")),

  it("should start at zero", lambda: (
    expect(counter).to_equal(0)
  )),

  it("should increment", lambda: (
    globals().update(counter=counter + 1),
    expect(counter).to_equal(1)
  )),
])

# Example testing various matchers
describe("Expectation matchers", lambda: [
  it("should test equality", lambda: (
    expect("hello").to_equal("hello")
  )),

  it("should test truthiness", lambda: (
    expect(True).to_be_truthy()
  )),

  it("should test falsiness", lambda: (
    expect(False).to_be_falsy()
  )),

  it("should test none", lambda: (
    expect(None).to_be_none()
  )),

  it("should test greater than", lambda: (
    expect(5).to_be_greater_than(3)
  )),

  it("should test less than", lambda: (
    expect(2).to_be_less_than(5)
  )),

  it("should test contains", lambda: (
    expect([1, 2, 3]).to_contain(2)
  )),

  it("should test length", lambda: (
    expect("hello").to_have_length(5)
  )),

  it("should test instance type", lambda: (
    expect("hello").to_be_instance_of(str)
  )),

  it("should test exceptions", lambda: (
    expect(lambda: 1/0).to_throw(ZeroDivisionError)
  )),
])

# Example with nested test suites
describe("Nested test suites", lambda: [
  it("should run outer test", lambda: (
    expect(1).to_equal(2)
  )),

  describe("Inner suite", lambda: [
    it("should run inner test", lambda: (
      expect(2).to_equal(2)
    )),

    describe("Deeply nested suite", lambda: [
      it("should run deeply nested test", lambda: (
        expect(3).to_equal(3)
      )),
    ]),
  ]),

  it("should run another outer test", lambda: (
    expect(4).to_equal(4)
  )),
])

# Run all tests
if __name__ == "__main__":
    run_tests()
