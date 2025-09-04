from typing import List, Callable, Optional

class TestResult:
  def __init__(self):
    self.passed = 0
    self.failed = 0
    self.errors: List[str] = []

class TestSuite:
  def __init__(self, name: str):
    self.name = name
    self.tests: List['Test'] = []
    self.before_each_hooks: List[Callable] = []
    self.before_all_hooks: List[Callable] = []
    self.after_each_hooks: List[Callable] = []
    self.after_all_hooks: List[Callable] = []
    self.nested_suites: List['TestSuite'] = []

class Test:
  def __init__(self, name: str, test_func: Callable):
    self.name = name
    self.test_func = test_func

class TestRunner:
  def __init__(self):
    self.current_suite: Optional[TestSuite] = None
    self.suite_stack: List[TestSuite] = []
    self.root_suites: List[TestSuite] = []
    self.result = TestResult()

  def describe(self, name: str, suite_func: Callable):
    parent_suite = self.current_suite
    new_suite = TestSuite(name)

    if parent_suite:
      parent_suite.nested_suites.append(new_suite)
    else:
      self.root_suites.append(new_suite)

    self.suite_stack.append(new_suite)
    self.current_suite = new_suite

    suite_func()

    self.suite_stack.pop()
    self.current_suite = parent_suite

  def it(self, name: str, test_func: Callable):
    if not self.current_suite:
      raise RuntimeError("it() must be called inside a describe() block")

    test = Test(name, test_func)
    self.current_suite.tests.append(test)

  def before_each(self, hook_func: Callable):
    if not self.current_suite:
      raise RuntimeError("beforeEach() must be called inside a describe() block")
    self.current_suite.before_each_hooks.append(hook_func)

  def before_all(self, hook_func: Callable):
    if not self.current_suite:
      raise RuntimeError("beforeAll() must be called inside a describe() block")
    self.current_suite.before_all_hooks.append(hook_func)

  def after_each(self, hook_func: Callable):
    if not self.current_suite:
      raise RuntimeError("afterEach() must be called inside a describe() block")
    self.current_suite.after_each_hooks.append(hook_func)

  def after_all(self, hook_func: Callable):
    if not self.current_suite:
      raise RuntimeError("afterAll() must be called inside a describe() block")
    self.current_suite.after_all_hooks.append(hook_func)

  def run_suite(self, suite: TestSuite, indent: int = 0):
    print("  " * indent + suite.name)

    for hook in suite.before_all_hooks:
      try:
        hook()
      except Exception as e:
        error_msg = f"beforeAll hook failed in '{suite.name}': {str(e)}"
        self.result.errors.append(error_msg)
        print("  " * (indent + 1) + f" {error_msg}")

    for test in suite.tests:
      # Run beforeEach hooks
      for hook in suite.before_each_hooks:
        try:
          hook()
        except Exception as e:
          error_msg = f"beforeEach hook failed for '{test.name}': {str(e)}"
          self.result.errors.append(error_msg)
          print("  " * (indent + 1) + f" {error_msg}")

      try:
        test.test_func()
        self.result.passed += 1
        print("  " * (indent + 1) + f" {test.name}")
      except Exception as e:
        self.result.failed += 1
        error_msg = f"{test.name}: {str(e)}"
        self.result.errors.append(error_msg)
        print("  " * (indent + 1) + f" {error_msg}")

      for hook in suite.after_each_hooks:
        try:
            hook()
        except Exception as e:
            error_msg = f"afterEach hook failed for '{test.name}': {str(e)}"
            self.result.errors.append(error_msg)
            print("  " * (indent + 1) + f" {error_msg}")

    for nested_suite in suite.nested_suites:
      self.run_suite(nested_suite, indent + 1)

    for hook in suite.after_all_hooks:
      try:
        hook()
      except Exception as e:
        error_msg = f"afterAll hook failed in '{suite.name}': {str(e)}"
        self.result.errors.append(error_msg)
        print("  " * (indent + 1) + f" {error_msg}")

  def run(self):
    print("Running tests...\n")

    for suite in self.root_suites:
      self.run_suite(suite)

    print(f"\nTest Results:")
    print(f"Passed: {self.result.passed}")
    print(f"Failed: {self.result.failed}")
    print(f"Total: {self.result.passed + self.result.failed}")

    if self.result.failed > 0:
      print(f"\nFailures:")
      for error in self.result.errors:
        print(f"  - {error}")

    return self.result.failed == 0

class Expectation:
  def __init__(self, actual):
    self.actual = actual

  def to_be(self, expected):
    if self.actual != expected:
      raise AssertionError(f"Expected {self.actual} to be {expected}")
    return self

  def to_equal(self, expected):
    if self.actual != expected:
      raise AssertionError(f"Expected {self.actual} to equal {expected}")
    return self

  def to_be_truthy(self):
    if not self.actual:
      raise AssertionError(f"Expected {self.actual} to be truthy")
    return self

  def to_be_falsy(self):
    if self.actual:
      raise AssertionError(f"Expected {self.actual} to be falsy")
    return self

  def to_be_none(self):
    if self.actual is not None:
      raise AssertionError(f"Expected {self.actual} to be None")
    return self

  def to_be_greater_than(self, expected):
    if not (self.actual > expected):
      raise AssertionError(f"Expected {self.actual} to be greater than {expected}")
    return self

  def to_be_less_than(self, expected):
    if not (self.actual < expected):
      raise AssertionError(f"Expected {self.actual} to be less than {expected}")
    return self

  def to_be_greater_than_or_equal(self, expected):
    if not (self.actual >= expected):
      raise AssertionError(f"Expected {self.actual} to be greater than or equal to {expected}")
    return self

  def to_be_less_than_or_equal(self, expected):
    if not (self.actual <= expected):
      raise AssertionError(f"Expected {self.actual} to be less than or equal to {expected}")
    return self

  def to_contain(self, expected):
    if expected not in self.actual:
      raise AssertionError(f"Expected {self.actual} to contain {expected}")
    return self

  def to_have_length(self, expected):
    actual_length = len(self.actual)
    if actual_length != expected:
      raise AssertionError(f"Expected {self.actual} to have length {expected}, but got {actual_length}")
    return self

  def to_be_instance_of(self, expected_type):
    if not isinstance(self.actual, expected_type):
      raise AssertionError(f"Expected {self.actual} to be instance of {expected_type}, but got {type(self.actual)}")
    return self

  def to_throw(self, expected_exception=None):
    if not callable(self.actual):
      raise AssertionError("Expected a callable function to test for exceptions")

    try:
      self.actual()
      raise AssertionError("Expected function to throw an exception, but it didn't")
    except Exception as e:
      if expected_exception and not isinstance(e, expected_exception):
        raise AssertionError(f"Expected function to throw {expected_exception}, but got {type(e)}")
    return self

def expect(actual):
  return Expectation(actual)

_test_runner = TestRunner()

describe = _test_runner.describe
it = _test_runner.it
before_each = _test_runner.before_each
before_all = _test_runner.before_all
after_each = _test_runner.after_each
after_all = _test_runner.after_all
run_tests = _test_runner.run
