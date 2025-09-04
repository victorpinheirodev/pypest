from pypest import describe, it, expect, run_tests

describe("Simple Test", lambda: (
    it("should pass", lambda: expect(1 + 1).to_equal(2)),
    it("should also pass", lambda: expect("hello".upper()).to_equal("HELLO"))
))

if __name__ == "__main__":
    run_tests()