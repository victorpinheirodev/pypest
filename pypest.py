#!/usr/bin/env python3
from typing import List, Callable, Optional
import os
import sys
import glob
import argparse
import time

class Colors:
  GREEN = '\033[92m'
  RED = '\033[91m'
  YELLOW = '\033[93m'
  BLUE = '\033[94m'
  MAGENTA = '\033[95m'
  CYAN = '\033[96m'
  BOLD = '\033[1m'
  RESET = '\033[0m'
  DIM = '\033[2m'

class TestResult:
  def __init__(self):
    self.passed = 0
    self.failed = 0
    self.errors: List[str] = []
    self.start_time: Optional[float] = None
    self.end_time: Optional[float] = None

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
    print("  " * indent + f"{Colors.BOLD}{Colors.BLUE}{suite.name}{Colors.RESET}")

    for hook in suite.before_all_hooks:
      try:
        hook()
      except Exception as e:
        error_msg = f"beforeAll hook failed in '{suite.name}': {str(e)}"
        self.result.errors.append(error_msg)
        print("  " * (indent + 1) + f"{Colors.RED}✗ {error_msg}{Colors.RESET}")

    for test in suite.tests:
      # Run beforeEach hooks
      for hook in suite.before_each_hooks:
        try:
          hook()
        except Exception as e:
          error_msg = f"beforeEach hook failed for '{test.name}': {str(e)}"
          self.result.errors.append(error_msg)
          print("  " * (indent + 1) + f"{Colors.RED}✗ {error_msg}{Colors.RESET}")

      test_start_time = time.time()
      try:
        test.test_func()
        test_duration = time.time() - test_start_time
        self.result.passed += 1
        print("  " * (indent + 1) + f"{Colors.GREEN}✓ {test.name}{Colors.RESET} {Colors.DIM}({test_duration*1000:.1f}ms){Colors.RESET}")
      except Exception as e:
        self.result.failed += 1
        test_duration = time.time() - test_start_time
        error_msg = f"{test.name}: {str(e)}"
        self.result.errors.append(error_msg)
        print("  " * (indent + 1) + f"{Colors.RED}✗ {error_msg}{Colors.RESET} {Colors.DIM}({test_duration*1000:.1f}ms){Colors.RESET}")

      for hook in suite.after_each_hooks:
        try:
            hook()
        except Exception as e:
            error_msg = f"afterEach hook failed for '{test.name}': {str(e)}"
            self.result.errors.append(error_msg)
            print("  " * (indent + 1) + f"{Colors.RED}✗ {error_msg}{Colors.RESET}")

    for nested_suite in suite.nested_suites:
      self.run_suite(nested_suite, indent + 1)

    for hook in suite.after_all_hooks:
      try:
        hook()
      except Exception as e:
        error_msg = f"afterAll hook failed in '{suite.name}': {str(e)}"
        self.result.errors.append(error_msg)
        print("  " * (indent + 1) + f"{Colors.RED}✗ {error_msg}{Colors.RESET}")

  def run(self):
    print(f"{Colors.BOLD}Running tests...{Colors.RESET}\n")

    self.result.start_time = time.time()
    for suite in self.root_suites:
      self.run_suite(suite)
    self.result.end_time = time.time()

    total_time = self.result.end_time - self.result.start_time
    total_tests = self.result.passed + self.result.failed

    print(f"\n{Colors.BOLD}Test Results:{Colors.RESET}")
    if self.result.passed > 0:
      print(f"{Colors.GREEN}Passed: {self.result.passed}{Colors.RESET}")
    if self.result.failed > 0:
      print(f"{Colors.RED}Failed: {self.result.failed}{Colors.RESET}")
    print(f"Total: {total_tests}")
    print(f"{Colors.DIM}Time: {total_time*1000:.1f}ms{Colors.RESET}")

    if self.result.failed > 0:
      print(f"\n{Colors.RED}Failures:{Colors.RESET}")
      for error in self.result.errors:
        print(f"  {Colors.RED}✗{Colors.RESET} {error}")

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

def find_test_files(directory: str = ".") -> List[str]:
  test_files = []
  patterns = ["test_*.py", "*_test.py", "tests.py"]

  for root, dirs, files in os.walk(directory):
    for pattern in patterns:
      test_files.extend(glob.glob(os.path.join(root, pattern)))

  return test_files

def run_test_file(file_path: str, cwd: str = None) -> tuple[bool, int, int]:
  """Run a test file as a separate Python process and parse results."""
  import subprocess
  import re

  try:
    env = os.environ.copy()
    if cwd:
      current_path = env.get('PYTHONPATH', '')
      if current_path:
        env['PYTHONPATH'] = f"{cwd}{os.pathsep}{current_path}"
      else:
        env['PYTHONPATH'] = cwd

    result = subprocess.run([sys.executable, file_path],
                          capture_output=True, text=True, cwd=cwd, env=env)

    output = result.stdout
    print(output, end="")

    if result.stderr:
      print("STDERR:", result.stderr, end="")

    passed_match = re.search(r'Passed: (\d+)', output)
    failed_match = re.search(r'Failed: (\d+)', output)

    passed = int(passed_match.group(1)) if passed_match else 0
    failed = int(failed_match.group(1)) if failed_match else 0

    success = result.returncode == 0 and failed == 0
    return success, passed, failed

  except Exception as e:
    print(f"Error running test file {file_path}: {e}")
    return False, 0, 0

def main():
  parser = argparse.ArgumentParser(description="pypest - Python testing framework")
  parser.add_argument("path", nargs="?", default=".", help="Directory to search for test files or specific test file to run (default: current directory)")
  parser.add_argument("--pattern", help="Custom pattern for test files (e.g., 'spec_*.py')")

  args = parser.parse_args()
  original_cwd = os.getcwd()

  if os.path.isfile(args.path):
    test_files = [os.path.abspath(args.path)]
  elif os.path.isdir(args.path):
    if args.pattern:
      test_files = glob.glob(os.path.join(args.path, "**", args.pattern), recursive=True)
    else:
      test_files = find_test_files(args.path)

    test_files = [os.path.abspath(f) for f in test_files]

    if not test_files:
      print(f"No test files found in {args.path}")
      return 1
  else:
    print(f"Path not found: {args.path}")
    return 1

  print(f"Found {len(test_files)} test file(s):")
  for file_path in test_files:
    print(f"  - {file_path}")
  print()

  all_passed = True
  total_passed = 0
  total_failed = 0

  for file_path in test_files:
    print(f"Running tests from {file_path}:")
    print("=" * 50)

    success, passed, failed = run_test_file(file_path, original_cwd)
    total_passed += passed
    total_failed += failed

    if not success:
      all_passed = False

    print("=" * 50)
    print()

  print(f"{Colors.BOLD}Overall Results:{Colors.RESET}")
  if total_passed > 0:
    print(f"{Colors.GREEN}Total Passed: {total_passed}{Colors.RESET}")
  if total_failed > 0:
    print(f"{Colors.RED}Total Failed: {total_failed}{Colors.RESET}")
  print(f"Total Tests: {total_passed + total_failed}")

  return 0 if all_passed else 1

if __name__ == "__main__":
  sys.exit(main())
