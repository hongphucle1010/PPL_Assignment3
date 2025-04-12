import unittest
from TestUtils import TestChecker
from AST import *


class CheckSuite(unittest.TestCase):
    # ! ===================== REDECLARATION ===================== ! #
    def test_400(self):
        """
        Test normal case
        var x int;
        """
        input = Program(
            [
                VarDecl("x", IntType(), None),
            ]
        )
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 400))

    def test_401(self):
        """
        Redeclaration of variable
        var x int;
        var x int;
        """
        input = Program(
            [
                VarDecl("x", IntType(), None),
                VarDecl("x", IntType(), None),
            ]
        )
        expect = "Redeclared Variable: x\n"
        self.assertTrue(TestChecker.test(input, expect, 401))

    def test_402(self):
        """
        Variable declared at init, redeclared in loop body
        func main () {
            for var x = 0; x < 10; x += 1 {
                var x = 2;
            }
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            ForStep(
                                VarDecl("x", None, IntLiteral(0)),
                                BinaryOp("<", Id("x"), IntLiteral(10)),
                                Assign(Id("x"), BinaryOp("+", Id("x"), IntLiteral(1))),
                                Block(
                                    [VarDecl("x", None, IntLiteral(2))]  # ❌ Redeclared
                                ),
                            )
                        ]
                    ),
                )
            ]
        )
        expect = "Redeclared Variable: x\n"
        self.assertTrue(TestChecker.test(input, expect, 402))

    def test_403(self):
        """
        Variable implicitly declared by := in init, redeclared in loop body
        func main () {
            for x := 0; x < 3; x := x + 1 {
                var x = 2;   // ❌ Redeclared Variable: x
            }
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            ForStep(
                                # init  ──> implicit declaration of x via :=
                                Assign(Id("x"), IntLiteral(0)),
                                # cond  ──> boolean expression (x < 3)
                                BinaryOp("<", Id("x"), IntLiteral(3)),
                                # upda  ──> another := update
                                Assign(Id("x"), BinaryOp("+", Id("x"), IntLiteral(1))),
                                # loop body ──> explicit redeclaration
                                Block([VarDecl("x", None, IntLiteral(2))]),
                            )
                        ]
                    ),
                )
            ]
        )
        expect = "Redeclared Variable: x\n"
        self.assertTrue(TestChecker.test(input, expect, 403))

    def test_404(self):
        """
        Redeclared constant with same name as existing variable
        var a = 1;
        const a = 2;
        """
        input = Program(
            [
                VarDecl("a", None, IntLiteral(1)),
                ConstDecl("a", None, IntLiteral(2)),  # ❌ Redeclared Constant: a
            ]
        )
        expect = "Redeclared Constant: a\n"
        self.assertTrue(TestChecker.test(input, expect, 404))

    def test_405(self):
        """
        Constant declared inside for loop body with same name as loop variable
        for var i = 0; i < 3; i += 1 {
            const i = 2;
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            ForStep(
                                VarDecl("i", None, IntLiteral(0)),
                                BinaryOp("<", Id("i"), IntLiteral(3)),
                                Assign(Id("i"), BinaryOp("+", Id("i"), IntLiteral(1))),
                                Block(
                                    [
                                        ConstDecl(
                                            "i", None, IntLiteral(2)
                                        )  # ❌ Redeclared Constant: i
                                    ]
                                ),
                            )
                        ]
                    ),
                )
            ]
        )
        expect = "Redeclared Constant: i\n"
        self.assertTrue(TestChecker.test(input, expect, 405))

    def test_406(self):
        """
        func foo(a int, a int) {}
        """
        input = Program(
            [
                FuncDecl(
                    "foo",
                    [ParamDecl("a", IntType()), ParamDecl("a", IntType())],
                    VoidType(),
                    Block([Return(None)]),
                )
            ]
        )
        expect = "Redeclared Parameter: a\n"
        self.assertTrue(TestChecker.test(input, expect, 406))

    def test_407(self):
        """
        type T struct {}
        func (x T) foo(a int, a int) {}
        """
        input = Program(
            [
                StructType("T", [], []),
                MethodDecl(
                    "x",
                    Id("T"),
                    FuncDecl(
                        "foo",
                        [ParamDecl("a", IntType()), ParamDecl("a", IntType())],
                        VoidType(),
                        Block([Return(None)]),
                    ),
                ),
            ]
        )
        expect = "Redeclared Parameter: a\n"
        self.assertTrue(TestChecker.test(input, expect, 407))

    def test_408(self):
        """
        var a = 1;
        func foo(a int) {
            return;
        }
        """
        input = Program(
            [
                VarDecl("a", None, IntLiteral(1)),
                FuncDecl(
                    "foo",
                    [ParamDecl("a", IntType())],
                    VoidType(),
                    Block([Return(None)]),
                ),
            ]
        )
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 408))

    def test_409(self):
        """
        func foo(a int) {
            var a = 2;
            return;
        }
        """
        input = Program(
            [
                FuncDecl(
                    "foo",
                    [ParamDecl("a", IntType())],
                    VoidType(),
                    Block([VarDecl("a", None, IntLiteral(2)), Return(None)]),
                )
            ]
        )
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 409))

    def test_410(self):
        """
        type A struct {}
        type A struct {}
        """
        input = Program([StructType("A", [], []), StructType("A", [], [])])
        expect = "Redeclared Type: A\n"
        self.assertTrue(TestChecker.test(input, expect, 410))

    def test_411(self):
        """
        type I interface {}
        type I interface {}
        """
        input = Program([InterfaceType("I", []), InterfaceType("I", [])])
        expect = "Redeclared Type: I\n"
        self.assertTrue(TestChecker.test(input, expect, 411))

    def test_412(self):
        """
        type M struct {}
        type M interface {}
        """
        input = Program([StructType("M", [], []), InterfaceType("M", [])])
        expect = "Redeclared Type: M\n"
        self.assertTrue(TestChecker.test(input, expect, 412))

    def test_413(self):
        """
        var T = 1;
        type T struct {}
        """
        input = Program([VarDecl("T", None, IntLiteral(1)), StructType("T", [], [])])
        expect = "Redeclared Type: T\n"
        self.assertTrue(TestChecker.test(input, expect, 413))

    def test_414(self):
        """
        const T = 1;
        type T interface {}
        """
        input = Program([ConstDecl("T", None, IntLiteral(1)), InterfaceType("T", [])])
        expect = "Redeclared Type: T\n"
        self.assertTrue(TestChecker.test(input, expect, 414))

    def test_415(self):
        """
        func foo() {}
        func foo() {}
        """
        input = Program(
            [
                FuncDecl("foo", [], VoidType(), Block([Return(None)])),
                FuncDecl("foo", [], VoidType(), Block([Return(None)])),
            ]
        )
        expect = "Redeclared Function: foo\n"
        self.assertTrue(TestChecker.test(input, expect, 415))

    def test_416(self):
        """
        var foo = 1;
        func foo() {}
        """
        input = Program(
            [
                VarDecl("foo", None, IntLiteral(1)),
                FuncDecl("foo", [], VoidType(), Block([Return(None)])),
            ]
        )
        expect = "Redeclared Function: foo\n"
        self.assertTrue(TestChecker.test(input, expect, 416))

    def test_417(self):
        """
        const foo = 1;
        func foo() {}
        """
        input = Program(
            [
                ConstDecl("foo", None, IntLiteral(1)),
                FuncDecl("foo", [], VoidType(), Block([Return(None)])),
            ]
        )
        expect = "Redeclared Function: foo\n"
        self.assertTrue(TestChecker.test(input, expect, 417))

    def test_418(self):
        """
        type foo struct {}
        func foo() {}
        """
        input = Program(
            [
                StructType("foo", [], []),
                FuncDecl("foo", [], VoidType(), Block([Return(None)])),
            ]
        )
        expect = "Redeclared Function: foo\n"
        self.assertTrue(TestChecker.test(input, expect, 418))

    def test_419(self):
        """
        type T struct {}
        func (a T) foo() {}
        func (b T) foo() {}
        """
        input = Program(
            [
                MethodDecl(
                    "a", Id("T"), FuncDecl("foo", [], VoidType(), Block([Return(None)]))
                ),
                MethodDecl(
                    "b", Id("T"), FuncDecl("foo", [], VoidType(), Block([Return(None)]))
                ),
                StructType("T", [], []),
            ]
        )
        expect = "Redeclared Method: foo\n"
        self.assertTrue(TestChecker.test(input, expect, 419))

    def test_420(self):
        """
        type A struct {}
        type B struct {}
        func (x A) foo() {}
        func (y B) foo() {}
        """
        input = Program(
            [
                MethodDecl(
                    "x", Id("A"), FuncDecl("foo", [], VoidType(), Block([Return(None)]))
                ),
                MethodDecl(
                    "y", Id("B"), FuncDecl("foo", [], VoidType(), Block([Return(None)]))
                ),
                StructType("A", [], []),
                StructType("B", [], []),
            ]
        )
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 420))

    def test_421(self):
        """
        type I interface {
            foo();
            foo();
        }
        """
        input = Program(
            [
                InterfaceType(
                    "I",
                    [
                        Prototype("foo", [], VoidType()),
                        Prototype("foo", [], VoidType()),  # ❌ Redeclared
                    ],
                )
            ]
        )
        expect = "Redeclared Prototype: foo\n"
        self.assertTrue(TestChecker.test(input, expect, 421))

    def test_422(self):
        """
        type A struct {
            x int;
            x float;
        }
        """
        input = Program(
            [
                StructType(
                    "A",
                    [("x", IntType()), ("x", FloatType())],  # ❌ Redeclared Field: x
                    [],
                )
            ]
        )
        expect = "Redeclared Field: x\n"
        self.assertTrue(TestChecker.test(input, expect, 422))

    def test_423(self):
        """
        func main() {
            a := 1;       // implicitly declared
            var a = 2;    // ❌ Redeclared
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            Assign(Id("a"), IntLiteral(1)),
                            VarDecl("a", None, IntLiteral(2)),
                        ]
                    ),
                )
            ]
        )
        expect = "Redeclared Variable: a\n"
        self.assertTrue(TestChecker.test(input, expect, 423))

    def test_424(self):
        """
        func main() {
            for b := 0; b < 5; b := b + 1 {
                const b = 2;   // ❌ Redeclared
            }
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            ForStep(
                                Assign(Id("b"), IntLiteral(0)),  # implicit declaration
                                BinaryOp("<", Id("b"), IntLiteral(5)),
                                Assign(Id("b"), BinaryOp("+", Id("b"), IntLiteral(1))),
                                Block(
                                    [ConstDecl("b", None, IntLiteral(2))]  # Redeclared
                                ),
                            )
                        ]
                    ),
                )
            ]
        )
        expect = "Redeclared Constant: b\n"
        self.assertTrue(TestChecker.test(input, expect, 424))

    def test_425(self):
        """
        type A struct {
            foo int;
            func (a A) foo() {}
        }
        """
        input = Program([
            MethodDecl(
                "a", Id("A"),
                FuncDecl("foo", [], VoidType(), Block([Return(None)]))
            ),
            StructType("A", [("foo", IntType())], [])  # Field 'foo'
        ])
        expect = "Redeclared Method: foo\n"
        self.assertTrue(TestChecker.test(input, expect, 425))

    # ! ===================== UNDECLARATION ===================== ! #
    def test_426(self):
        """
        func main() {
            x := y;  // ❌ 'y' is undeclared
        }
        """
        input = Program(
            [FuncDecl("main", [], VoidType(), Block([Assign(Id("x"), Id("y"))]))]
        )
        expect = "Undeclared Identifier: y\n"
        self.assertTrue(TestChecker.test(input, expect, 426))

    def test_427(self):
        """
        func main() {
            x := x + 1;  // ❌ RHS uses 'x' before declared
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block([Assign(Id("x"), BinaryOp("+", Id("x"), IntLiteral(1)))]),
                )
            ]
        )
        expect = "Undeclared Identifier: x\n"
        self.assertTrue(TestChecker.test(input, expect, 427))

    def test_428(self):
        """
        func main() {
            x := 10;  // ✅ correct scalar assignment (declares x)
            y := x;   // ✅ 'x' is declared now
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block([Assign(Id("x"), IntLiteral(10)), Assign(Id("y"), Id("x"))]),
                )
            ]
        )
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 428))

    def test_429(self):
        """
        func main() {
            foo();  // ❌ function 'foo' is not declared
        }
        """
        input = Program(
            [FuncDecl("main", [], VoidType(), Block([FuncCall("foo", [])]))]
        )
        expect = "Undeclared Function: foo\n"
        self.assertTrue(TestChecker.test(input, expect, 429))

    def test_430(self):
        """
        var foo = 1;
        func main() {
            foo();  // ❌ 'foo' is not a function
        }
        """
        input = Program(
            [
                VarDecl("foo", None, IntLiteral(1)),
                FuncDecl("main", [], VoidType(), Block([FuncCall("foo", [])])),
            ]
        )
        expect = "Undeclared Function: foo\n"
        self.assertTrue(TestChecker.test(input, expect, 430))

    def test_431(self):
        """
        type A struct {
            x int;
        }

        func (a A) foo() {}

        func main() {
            var obj A;
            obj.foo();     // ✅ declared
            obj.bar();     // ❌ bar not declared in A
        }
        """
        input = Program(
            [
                StructType("A", [("x", IntType())], []),
                MethodDecl(
                    "a", Id("A"), FuncDecl("foo", [], VoidType(), Block([Return(None)]))
                ),
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl("obj", Id("A"), None),
                            MethCall(Id("obj"), "foo", []),
                            MethCall(Id("obj"), "bar", []),  # ❌
                        ]
                    ),
                ),
            ]
        )
        expect = "Undeclared Method: bar\n"
        self.assertTrue(TestChecker.test(input, expect, 431))

    def test_432(self):
        """
        type A struct {
            x int;
            y float;
        }

        func main() {
            var obj A;
            var a = obj.x;   // ✅ valid
            var b = obj.z;   // ❌ undeclared field 'z'
        }
        """
        input = Program(
            [
                StructType("A", [("x", IntType()), ("y", FloatType())], []),
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl("obj", Id("A"), None),
                            VarDecl("a", None, FieldAccess(Id("obj"), "x")),
                            VarDecl("b", None, FieldAccess(Id("obj"), "z")),  # ❌
                        ]
                    ),
                ),
            ]
        )
        expect = "Undeclared Field: z\n"
        self.assertTrue(TestChecker.test(input, expect, 432))

    # ! ===================== TYPE MISMATCH ===================== ! #

    def test_433(self):
        """
        func main() {
            var x void;
            x := 1;
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [VarDecl("x", VoidType(), None), Assign(Id("x"), IntLiteral(1))]
                    ),
                )
            ]
        )
        expect = "Type Mismatch: VarDecl(x,VoidType)\n"
        self.assertTrue(TestChecker.test(input, expect, 433))

    def test_434(self):
        """
        func main() {
            var s string;
            s := 1;
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl("s", StringType(), None),
                            Assign(Id("s"), IntLiteral(1)),
                        ]
                    ),
                )
            ]
        )
        expect = "Type Mismatch: Assign(Id(s),IntLiteral(1))\n"
        self.assertTrue(TestChecker.test(input, expect, 434))

    def test_435(self):
        """
        func main() {
            var f float;
            f := 10;  // ✅ int to float coercion
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl("f", FloatType(), None),
                            Assign(Id("f"), IntLiteral(10)),
                        ]
                    ),
                )
            ]
        )
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 435))

    def test_436(self):
        """
        func main() {
            var a [2]int;
            a := [3]int{1, 2, 3};  // ❌ mismatched dimension
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl("a", ArrayType([IntLiteral(2)], IntType()), None),
                            Assign(
                                Id("a"),
                                ArrayLiteral(
                                    [IntLiteral(3)],
                                    IntType(),
                                    [IntLiteral(1), IntLiteral(2), IntLiteral(3)],
                                ),
                            ),
                        ]
                    ),
                )
            ]
        )
        expect = "Type Mismatch: Assign(Id(a),ArrayLiteral([IntLiteral(3)],IntType,[IntLiteral(1),IntLiteral(2),IntLiteral(3)]))\n"
        self.assertTrue(TestChecker.test(input, expect, 436))

    def test_437(self):
        """
        func main() {
            var a [3]int;
            a := [3]int{1, 2, 3};  // ✅ correct type and size
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl("a", ArrayType([IntLiteral(3)], IntType()), None),
                            Assign(
                                Id("a"),
                                ArrayLiteral(
                                    [IntLiteral(3)],
                                    IntType(),
                                    [IntLiteral(1), IntLiteral(2), IntLiteral(3)],
                                ),
                            ),
                        ]
                    ),
                )
            ]
        )
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 437))

    def test_438(self):
        """
        type I interface {
            foo();
        }

        type A struct {}
        func (x A) foo() {}

        func main() {
            var x I;
            var y A;
            x := y;  // ✅ A implements I
        }
        """
        input = Program(
            [
                InterfaceType("I", [Prototype("foo", [], VoidType())]),
                StructType("A", [], []),
                MethodDecl(
                    "x", Id("A"), FuncDecl("foo", [], VoidType(), Block([Return(None)]))
                ),
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl("x", Id("I"), None),
                            VarDecl("y", Id("A"), None),
                            Assign(Id("x"), Id("y")),
                        ]
                    ),
                ),
            ]
        )
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 438))

    def test_439(self):
        """
        func main() {
            var s string = 1;  // ❌ string := int
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block([VarDecl("s", StringType(), IntLiteral(1))]),
                )
            ]
        )
        expect = "Type Mismatch: VarDecl(s,StringType,IntLiteral(1))\n"
        self.assertTrue(TestChecker.test(input, expect, 439))

    def test_440(self):
        """
        func main() {
            var f float = 3;  // ✅ int → float coercion
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block([VarDecl("f", FloatType(), IntLiteral(3))]),
                )
            ]
        )
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 440))

    def test_441(self):
        """
        func main() {
            var x = "hello";  // ✅ inferred type is string
            var y = 3.14;     // ✅ inferred type is float
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl("x", None, StringLiteral("hello")),
                            VarDecl("y", None, FloatLiteral(3.14)),
                        ]
                    ),
                )
            ]
        )
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 441))

    def test_442(self):
        """
        func main() {
            var ok boolean = 1;  // ❌ int ≠ boolean
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block([VarDecl("ok", BoolType(), IntLiteral(1))]),
                )
            ]
        )
        expect = "Type Mismatch: VarDecl(ok,BoolType,IntLiteral(1))\n"
        self.assertTrue(TestChecker.test(input, expect, 442))

    def test_443(self):
        """
        func main() {
            var i int = 3.14;  // ❌ float ≠ int
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block([VarDecl("i", IntType(), FloatLiteral(3.14))]),
                )
            ]
        )
        expect = "Type Mismatch: VarDecl(i,IntType,FloatLiteral(3.14))\n"
        self.assertTrue(TestChecker.test(input, expect, 443))

    def test_444(self):
        """
        func main() {
            var s string = true;  // ❌ boolean ≠ string
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block([VarDecl("s", StringType(), BooleanLiteral(True))]),
                )
            ]
        )
        expect = "Type Mismatch: VarDecl(s,StringType,BooleanLiteral(true))\n"
        self.assertTrue(TestChecker.test(input, expect, 444))

    def test_445(self):
        """
        type A struct {}
        type B struct {}

        func main() {
            var x A = B{};  // ❌ struct B ≠ struct A
        }
        """
        input = Program(
            [
                StructType("A", [], []),
                StructType("B", [], []),
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block([VarDecl("x", Id("A"), StructLiteral("B", []))]),
                ),
            ]
        )
        expect = "Type Mismatch: VarDecl(x,Id(A),StructLiteral(B,[]))\n"
        self.assertTrue(TestChecker.test(input, expect, 445))

    def test_446(self):
        """
        type A struct {}

        func main() {
            var x A = 10;  // ❌ int ≠ struct A
        }
        """
        input = Program(
            [
                StructType("A", [], []),
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block([VarDecl("x", Id("A"), IntLiteral(10))]),
                ),
            ]
        )
        expect = "Type Mismatch: VarDecl(x,Id(A),IntLiteral(10))\n"
        self.assertTrue(TestChecker.test(input, expect, 446))

    def test_447(self):
        """
        func main() {
            if 1 {
                return;
            }
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block([If(IntLiteral(1), Block([Return(None)]), None)]),
                )
            ]
        )
        expect = "Type Mismatch: If(IntLiteral(1),Block([Return()]))\n"
        self.assertTrue(TestChecker.test(input, expect, 447))

    def test_448(self):
        """
        func main() {
            for 3.14 {
                return;
            }
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block([ForBasic(FloatLiteral(3.14), Block([Return(None)]))]),
                )
            ]
        )
        expect = "Type Mismatch: For(FloatLiteral(3.14),Block([Return()]))\n"
        self.assertTrue(TestChecker.test(input, expect, 448))

    def test_449(self):
        """
        func main() {
            for var x void = 1; x < 10; x += 1 {
                return;
            }
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            ForStep(
                                VarDecl(
                                    "x", VoidType(), IntLiteral(1)
                                ),  # ❌ invalid init
                                BinaryOp("<", Id("x"), IntLiteral(10)),
                                Assign(Id("x"), BinaryOp("+", Id("x"), IntLiteral(1))),
                                Block([Return(None)]),
                            )
                        ]
                    ),
                )
            ]
        )
        expect = "Type Mismatch: VarDecl(x,VoidType,IntLiteral(1))\n"
        self.assertTrue(TestChecker.test(input, expect, 449))

    def test_450(self):
        """
        func main() {
            for var i = 0; "abc"; i += 1 {
                return;
            }
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            ForStep(
                                VarDecl("i", None, IntLiteral(0)),
                                StringLiteral("abc"),  # ❌ invalid condition
                                Assign(Id("i"), BinaryOp("+", Id("i"), IntLiteral(1))),
                                Block([Return(None)]),
                            )
                        ]
                    ),
                )
            ]
        )
        expect = "Type Mismatch: For(VarDecl(i,IntLiteral(0)),StringLiteral(abc),Assign(Id(i),BinaryOp(Id(i),+,IntLiteral(1))),Block([Return()]))\n"
        self.assertTrue(TestChecker.test(input, expect, 450))

    def test_451(self):
        """
        func main() {
            for var i = 0; i < 10; x += 1 {
                return;
            }
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            ForStep(
                                VarDecl("i", None, IntLiteral(0)),
                                BinaryOp("<", Id("i"), IntLiteral(10)),
                                Assign(
                                    Id("x"), BinaryOp("+", Id("x"), IntLiteral(1))
                                ),  # ❌ 'x' undeclared
                                Block([Return(None)]),
                            )
                        ]
                    ),
                )
            ]
        )
        expect = "Undeclared Identifier: x\n"
        self.assertTrue(TestChecker.test(input, expect, 451))

    def test_452(self):
        """
        func main() {
            for i, v := range [3]int{1, 2, 3} {
                return;
            }
        }
        // 'i' and 'v' are not declared before → ❌ Undeclared Identifier
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            ForEach(
                                Id("i"),
                                Id("v"),
                                ArrayLiteral(
                                    [IntLiteral(3)],
                                    IntType(),
                                    [IntLiteral(1), IntLiteral(2), IntLiteral(3)],
                                ),
                                Block([Return(None)]),
                            )
                        ]
                    ),
                )
            ]
        )
        expect = "Undeclared Identifier: i\n"
        self.assertTrue(TestChecker.test(input, expect, 452))

    def test_453(self):
        """
        func main() {
            var i int;
            for i, v := range [2]int{1, 2} {
                return;
            }
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl("i", IntType(), None),
                            ForEach(
                                Id("i"),
                                Id("v"),
                                ArrayLiteral(
                                    [IntLiteral(2)],
                                    IntType(),
                                    [IntLiteral(1), IntLiteral(2)],
                                ),
                                Block([Return(None)]),
                            ),
                        ]
                    ),
                )
            ]
        )
        expect = "Undeclared Identifier: v\n"
        self.assertTrue(TestChecker.test(input, expect, 453))

    def test_454(self):
        """
        func main() {
            var v int;
            for i, v := range [2]int{1, 2} {
                return;
            }
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl("v", IntType(), None),
                            ForEach(
                                Id("i"),
                                Id("v"),
                                ArrayLiteral(
                                    [IntLiteral(2)],
                                    IntType(),
                                    [IntLiteral(1), IntLiteral(2)],
                                ),
                                Block([Return(None)]),
                            ),
                        ]
                    ),
                )
            ]
        )
        expect = "Undeclared Identifier: i\n"
        self.assertTrue(TestChecker.test(input, expect, 454))

    def test_455(self):
        """
        func main() {
            var i int;
            var v int;
            for i, v := range 123 {
                return;
            }
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl("i", IntType(), None),
                            VarDecl("v", IntType(), None),
                            ForEach(
                                Id("i"),
                                Id("v"),
                                IntLiteral(123),  # ❌ not an array
                                Block([Return(None)]),
                            ),
                        ]
                    ),
                )
            ]
        )
        expect = (
            "Type Mismatch: ForEach(Id(i),Id(v),IntLiteral(123),Block([Return()]))\n"
        )
        self.assertTrue(TestChecker.test(input, expect, 455))

    def test_456(self):
        """
        func foo(a int) {}

        func main() {
            foo(1, 2);  // ❌ too many arguments
        }
        """
        input = Program(
            [
                FuncDecl(
                    "foo",
                    [ParamDecl("a", IntType())],
                    VoidType(),
                    Block([Return(None)]),
                ),
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block([FuncCall("foo", [IntLiteral(1), IntLiteral(2)])]),
                ),
            ]
        )
        expect = "Type Mismatch: FuncCall(foo,[IntLiteral(1),IntLiteral(2)])\n"
        self.assertTrue(TestChecker.test(input, expect, 456))

    def test_457(self):
        """
        func foo(a int, b string) {}

        func main() {
            foo(1);  // ❌ missing string argument
        }
        """
        input = Program(
            [
                FuncDecl(
                    "foo",
                    [ParamDecl("a", IntType()), ParamDecl("b", StringType())],
                    VoidType(),
                    Block([Return(None)]),
                ),
                FuncDecl(
                    "main", [], VoidType(), Block([FuncCall("foo", [IntLiteral(1)])])
                ),
            ]
        )
        expect = "Type Mismatch: FuncCall(foo,[IntLiteral(1)])\n"
        self.assertTrue(TestChecker.test(input, expect, 457))

    def test_458(self):
        """
        type A struct {}
        func (x A) foo(a int) {}

        func main() {
            var a A;
            a.foo("hello");  // ❌ string passed instead of int
        }
        """
        input = Program(
            [
                StructType("A", [], []),
                MethodDecl(
                    "x",
                    Id("A"),
                    FuncDecl(
                        "foo",
                        [ParamDecl("a", IntType())],
                        VoidType(),
                        Block([Return(None)]),
                    ),
                ),
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl("a", Id("A"), None),
                            MethCall(Id("a"), "foo", [StringLiteral("hello")]),
                        ]
                    ),
                ),
            ]
        )
        expect = "Type Mismatch: MethodCall(Id(a),foo,[StringLiteral(hello)])\n"
        self.assertTrue(TestChecker.test(input, expect, 458))

    def test_459(self):
        """
        func main() {
            var x int;
            x.foo();  // ❌ int does not have methods
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [VarDecl("x", IntType(), None), MethCall(Id("x"), "foo", [])]
                    ),
                )
            ]
        )
        expect = "Type Mismatch: MethodCall(Id(x),foo,[])\n"
        self.assertTrue(TestChecker.test(input, expect, 459))

    def test_460(self):
        """
        type I interface {
            foo();
        }

        type A struct {}
        func (x A) foo() {}

        func main() {
            var i I;
            var a A;
            i := a;     // A implements I
            i.foo();    // ✅ valid method call
        }
        """
        input = Program(
            [
                InterfaceType("I", [Prototype("foo", [], VoidType())]),
                StructType("A", [], []),
                MethodDecl(
                    "x", Id("A"), FuncDecl("foo", [], VoidType(), Block([Return(None)]))
                ),
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl("i", Id("I"), None),
                            VarDecl("a", Id("A"), None),
                            Assign(Id("i"), Id("a")),
                            MethCall(Id("i"), "foo", []),
                        ]
                    ),
                ),
            ]
        )
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 460))

    def test_461(self):
        """
        func main() {
            return 1;  // ❌ main is void
        }
        """
        input = Program(
            [FuncDecl("main", [], VoidType(), Block([Return(IntLiteral(1))]))]
        )
        expect = "Type Mismatch: Return(IntLiteral(1))\n"
        self.assertTrue(TestChecker.test(input, expect, 461))

    def test_462(self):
        """
        func foo() int {
            return;  // ❌ expected int return
        }
        """
        input = Program([FuncDecl("foo", [], IntType(), Block([Return(None)]))])
        expect = "Type Mismatch: Return()\n"
        self.assertTrue(TestChecker.test(input, expect, 462))

    def test_463(self):
        """
        type A struct {}
        func (x A) foo() int {
            return 42;  // ✅ correct return
        }
        """
        input = Program(
            [
                StructType("A", [], []),
                MethodDecl(
                    "x",
                    Id("A"),
                    FuncDecl("foo", [], IntType(), Block([Return(IntLiteral(42))])),
                ),
            ]
        )
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 463))

    def test_464(self):
        """
        type A struct {}
        func (x A) foo() int {
            return;  // ❌ expected int
        }
        """
        input = Program(
            [
                StructType("A", [], []),
                MethodDecl(
                    "x", Id("A"), FuncDecl("foo", [], IntType(), Block([Return(None)]))
                ),
            ]
        )
        expect = "Type Mismatch: Return()\n"
        self.assertTrue(TestChecker.test(input, expect, 464))

    def test_465(self):
        """
        func myFloat() float {
            return 1;  // ❌ expected float, got int
        }
        """
        input = Program(
            [
                FuncDecl(
                    "myFloat",
                    [],
                    FloatType(),
                    Block([Return(IntLiteral(1))]),  # ❌ mismatch
                )
            ]
        )
        expect = "Type Mismatch: Return(IntLiteral(1))\n"
        self.assertTrue(TestChecker.test(input, expect, 465))

    def test_466(self):
        """
        func main() {
            var a int;
            var x = a[0];  // ❌ a is not an array
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl("a", IntType(), None),
                            VarDecl("x", None, ArrayCell(Id("a"), [IntLiteral(0)])),
                        ]
                    ),
                )
            ]
        )
        expect = "Type Mismatch: ArrayCell(Id(a),[IntLiteral(0)])\n"
        self.assertTrue(TestChecker.test(input, expect, 466))

    def test_467(self):
        """
        func main() {
            var arr [3]int;
            var x = arr["0"];  // ❌ index must be int
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl("arr", ArrayType([IntLiteral(3)], IntType()), None),
                            VarDecl(
                                "x", None, ArrayCell(Id("arr"), [StringLiteral("0")])
                            ),
                        ]
                    ),
                )
            ]
        )
        expect = "Type Mismatch: ArrayCell(Id(arr),[StringLiteral(0)])\n"
        self.assertTrue(TestChecker.test(input, expect, 467))

    def test_468(self):
        """
        func main() {
            var x int;
            var y = x.f;  // ❌ int has no fields
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl("x", IntType(), None),
                            VarDecl("y", None, FieldAccess(Id("x"), "f")),
                        ]
                    ),
                )
            ]
        )
        expect = "Type Mismatch: FieldAccess(Id(x),f)\n"
        self.assertTrue(TestChecker.test(input, expect, 468))

    def test_469(self):
        """
        func main() {
            var x = 1 + 2.5;
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl(
                                "x",
                                None,
                                BinaryOp("+", IntLiteral(1), FloatLiteral(2.5)),
                            )
                        ]
                    ),
                )
            ]
        )
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 469))

    def test_470(self):
        """
        func main() {
            var x = 1 + "hello";  // ❌ incompatible + operands
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl(
                                "x",
                                None,
                                BinaryOp("+", IntLiteral(1), StringLiteral("hello")),
                            )
                        ]
                    ),
                )
            ]
        )
        expect = "Type Mismatch: BinaryOp(IntLiteral(1),+,StringLiteral(hello))\n"
        self.assertTrue(TestChecker.test(input, expect, 470))

    def test_471(self):
        """
        func main() {
            var s = "a" + "b";  // ✅ valid string concat
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl(
                                "s",
                                None,
                                BinaryOp("+", StringLiteral("a"), StringLiteral("b")),
                            )
                        ]
                    ),
                )
            ]
        )
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 471))

    def test_472(self):
        """
        func main() {
            var x = 3.5 % 2;  // ❌ % only allowed for int
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl(
                                "x",
                                None,
                                BinaryOp("%", FloatLiteral(3.5), IntLiteral(2)),
                            )
                        ]
                    ),
                )
            ]
        )
        expect = "Type Mismatch: BinaryOp(FloatLiteral(3.5),%,IntLiteral(2))\n"
        self.assertTrue(TestChecker.test(input, expect, 472))

    def test_473(self):
        """
        func main() {
            var x = 5 % 2;  // ✅ valid int modulo
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl(
                                "x", None, BinaryOp("%", IntLiteral(5), IntLiteral(2))
                            )
                        ]
                    ),
                )
            ]
        )
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 473))

    def test_474(self):
        """
        func main() {
            var x = 5 == 10;  // ✅ valid int comparison
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl(
                                "x", None, BinaryOp("==", IntLiteral(5), IntLiteral(10))
                            )
                        ]
                    ),
                )
            ]
        )
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 474))

    def test_475(self):
        """
        func main() {
            var x = "a" >= "b";  // ✅ valid string lex compare
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl(
                                "x",
                                None,
                                BinaryOp(">=", StringLiteral("a"), StringLiteral("b")),
                            )
                        ]
                    ),
                )
            ]
        )
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 475))

    def test_476(self):
        """
        func main() {
            var x = 5 < "abc";  // ❌ different types
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl(
                                "x",
                                None,
                                BinaryOp("<", IntLiteral(5), StringLiteral("abc")),
                            )
                        ]
                    ),
                )
            ]
        )
        expect = "Type Mismatch: BinaryOp(IntLiteral(5),<,StringLiteral(abc))\n"
        self.assertTrue(TestChecker.test(input, expect, 476))

    def test_477(self):
        """
        func main() {
            var x = 3.14 == "pi";  // ❌ different types
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl(
                                "x",
                                None,
                                BinaryOp("==", FloatLiteral(3.14), StringLiteral("pi")),
                            )
                        ]
                    ),
                )
            ]
        )
        expect = "Type Mismatch: BinaryOp(FloatLiteral(3.14),==,StringLiteral(pi))\n"
        self.assertTrue(TestChecker.test(input, expect, 477))

    def test_478(self):
        """
        func main() {
            var x = 1.5 < 2.5;  // ✅ valid float comparison
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl(
                                "x",
                                None,
                                BinaryOp("<", FloatLiteral(1.5), FloatLiteral(2.5)),
                            )
                        ]
                    ),
                )
            ]
        )
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 478))

    def test_479(self):
        """
        func main() {
            var x = true && false;  // ✅ valid boolean AND
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl(
                                "x",
                                None,
                                BinaryOp(
                                    "&&", BooleanLiteral(True), BooleanLiteral(False)
                                ),
                            )
                        ]
                    ),
                )
            ]
        )
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 479))

    def test_480(self):
        """
        func main() {
            var x = 1 && true;  // ❌ int not allowed in boolean AND
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl(
                                "x",
                                None,
                                BinaryOp("&&", IntLiteral(1), BooleanLiteral(True)),
                            )
                        ]
                    ),
                )
            ]
        )
        expect = "Type Mismatch: BinaryOp(IntLiteral(1),&&,BooleanLiteral(true))\n"
        self.assertTrue(TestChecker.test(input, expect, 480))

    def test_481(self):
        """
        func main() {
            var x = "abc" || false;  // ❌ string not allowed in boolean OR
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl(
                                "x",
                                None,
                                BinaryOp(
                                    "||", StringLiteral("abc"), BooleanLiteral(False)
                                ),
                            )
                        ]
                    ),
                )
            ]
        )
        expect = (
            "Type Mismatch: BinaryOp(StringLiteral(abc),||,BooleanLiteral(false))\n"
        )
        self.assertTrue(TestChecker.test(input, expect, 481))

    def test_482(self):
        """
        func main() {
            var x = !true;  // ✅ boolean negation
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block([VarDecl("x", None, UnaryOp("!", BooleanLiteral(True)))]),
                )
            ]
        )
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 482))

    def test_483(self):
        """
        func main() {
            var x = !"abc";  // ❌ logical NOT on string
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block([VarDecl("x", None, UnaryOp("!", StringLiteral("abc")))]),
                )
            ]
        )
        expect = "Type Mismatch: UnaryOp(!,StringLiteral(abc))\n"
        self.assertTrue(TestChecker.test(input, expect, 483))

    def test_484(self):
        """
        func main() {
            var a [3]int;
            var x = a[1];  // ✅ valid array access
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl("a", ArrayType([IntLiteral(3)], IntType()), None),
                            VarDecl("x", None, ArrayCell(Id("a"), [IntLiteral(1)])),
                        ]
                    ),
                )
            ]
        )
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 484))

    def test_485(self):
        """
        func main() {
            var a [2][3]int;
            var x = a[1][2];  // ✅ valid 2D array access
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl(
                                "a",
                                ArrayType([IntLiteral(2), IntLiteral(3)], IntType()),
                                None,
                            ),
                            VarDecl(
                                "x",
                                None,
                                ArrayCell(Id("a"), [IntLiteral(1), IntLiteral(2)]),
                            ),
                        ]
                    ),
                )
            ]
        )
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 485))

    def test_486(self):
        """
        func main() {
            var a [3]int;
            var x = a["0"];  // ❌ string used as index
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl("a", ArrayType([IntLiteral(3)], IntType()), None),
                            VarDecl(
                                "x", None, ArrayCell(Id("a"), [StringLiteral("0")])
                            ),
                        ]
                    ),
                )
            ]
        )
        expect = "Type Mismatch: ArrayCell(Id(a),[StringLiteral(0)])\n"
        self.assertTrue(TestChecker.test(input, expect, 486))

    def test_487(self):
        """
        func main() {
            var b int;
            var x = b[1];  // ❌ b is not an array
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl("b", IntType(), None),
                            VarDecl("x", None, ArrayCell(Id("b"), [IntLiteral(1)])),
                        ]
                    ),
                )
            ]
        )
        expect = "Type Mismatch: ArrayCell(Id(b),[IntLiteral(1)])\n"
        self.assertTrue(TestChecker.test(input, expect, 487))

    def test_488(self):
        """
        func main() {
            var x int;
            {
                var x string;  // ✅ valid: inner scope shadows outer
            }
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl("x", IntType(), None),
                            Block([VarDecl("x", StringType(), None)]),
                        ]
                    ),
                )
            ]
        )
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 488))

    def test_489(self):
        """
        func main() {
            {
                var x int;
            }
            {
                var x float;  // ✅ valid: different blocks
            }
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            Block([VarDecl("x", IntType(), None)]),
                            Block([VarDecl("x", FloatType(), None)]),
                        ]
                    ),
                )
            ]
        )
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 489))

    def test_490(self):
        """
        type I interface {
            greet();
        }

        type A struct {}
        func (a A) greet() {}

        func main() {
            var i I;
            var a A;
            i := a;     // ✅ A implements I
            i.greet();  // ✅ valid
        }
        """
        input = Program(
            [
                InterfaceType("I", [Prototype("greet", [], VoidType())]),
                StructType("A", [], []),
                MethodDecl(
                    "a",
                    Id("A"),
                    FuncDecl("greet", [], VoidType(), Block([Return(None)])),
                ),
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl("i", Id("I"), None),
                            VarDecl("a", Id("A"), None),
                            Assign(Id("i"), Id("a")),
                            MethCall(Id("i"), "greet", []),
                        ]
                    ),
                ),
            ]
        )
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 490))

    def test_491(self):
        """
        type I interface {
            greet();
        }

        func main() {
            var i I;
            i := nil;  // ✅ nil can be assigned to interface
        }
        """
        input = Program(
            [
                InterfaceType("I", [Prototype("greet", [], VoidType())]),
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block([VarDecl("i", Id("I"), None), Assign(Id("i"), NilLiteral())]),
                ),
            ]
        )
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 491))

    def test_492(self):
        """
        type A struct {}
        func (a A) hello() {}

        func main() {
            var x A;
            {
                x.hello();  // ✅ method call in nested block
            }
        }
        """
        input = Program(
            [
                StructType("A", [], []),
                MethodDecl(
                    "a",
                    Id("A"),
                    FuncDecl("hello", [], VoidType(), Block([Return(None)])),
                ),
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl("x", Id("A"), None),
                            Block([MethCall(Id("x"), "hello", [])]),
                        ]
                    ),
                ),
            ]
        )
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 492))

    def test_493(self):
        """
        func main() {
            var x int;
            for x := 0; x < 10; x := x + 1 {
                if x % 2 == 0 {
                    var x string;  // ✅ shadowing
                }
            }
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl("x", IntType(), None),
                            ForStep(
                                Assign(Id("x"), IntLiteral(0)),
                                BinaryOp("<", Id("x"), IntLiteral(10)),
                                Assign(Id("x"), BinaryOp("+", Id("x"), IntLiteral(1))),
                                Block(
                                    [
                                        If(
                                            BinaryOp(
                                                "==",
                                                BinaryOp("%", Id("x"), IntLiteral(2)),
                                                IntLiteral(0),
                                            ),
                                            Block([VarDecl("x", StringType(), None)]),
                                            None,
                                        )
                                    ]
                                ),
                            ),
                        ]
                    ),
                )
            ]
        )
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 493))

    def test_494(self):
        """
        type I interface {
            ping();
        }

        type S struct {}
        func (s S) ping() {}

        func main() {
            var i I;
            var s S;
            i := s;
            i.ping();  // ✅ interface method call
        }
        """
        input = Program(
            [
                InterfaceType("I", [Prototype("ping", [], VoidType())]),
                StructType("S", [], []),
                MethodDecl(
                    "s",
                    Id("S"),
                    FuncDecl("ping", [], VoidType(), Block([Return(None)])),
                ),
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl("i", Id("I"), None),
                            VarDecl("s", Id("S"), None),
                            Assign(Id("i"), Id("s")),
                            MethCall(Id("i"), "ping", []),
                        ]
                    ),
                ),
            ]
        )
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 494))

    def test_496(self):
        """
        func add(a int, b int) int {
            return a + b;
        }

        func main() {
            var result = add(3, 4);
        }
        """
        input = Program(
            [
                FuncDecl(
                    "add",
                    [ParamDecl("a", IntType()), ParamDecl("b", IntType())],
                    IntType(),
                    Block([Return(BinaryOp("+", Id("a"), Id("b")))]),
                ),
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl(
                                "result",
                                None,
                                FuncCall("add", [IntLiteral(3), IntLiteral(4)]),
                            )
                        ]
                    ),
                ),
            ]
        )
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 496))

    def test_497(self):
        """
        func main() {
            var a, b boolean;
            var result = a && b;
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl("a", BoolType(), None),
                            VarDecl("b", BoolType(), None),
                            VarDecl("result", None, BinaryOp("&&", Id("a"), Id("b"))),
                        ]
                    ),
                )
            ]
        )
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 497))

    def test_498(self):
        """
        func main() {
            var a = "apple";
            var b = "banana";
            var result = a < b;
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl("a", None, StringLiteral("apple")),
                            VarDecl("b", None, StringLiteral("banana")),
                            VarDecl("result", None, BinaryOp("<", Id("a"), Id("b"))),
                        ]
                    ),
                )
            ]
        )
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 498))

    def test_499(self):
        """
        func sum(arr [3]int) {}

        func main() {
            sum([3]int{1, 2, 3});
        }
        """
        input = Program(
            [
                FuncDecl(
                    "sum",
                    [ParamDecl("arr", ArrayType([IntLiteral(3)], IntType()))],
                    VoidType(),
                    Block([Return(None)]),
                ),
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            FuncCall(
                                "sum",
                                [
                                    ArrayLiteral(
                                        [IntLiteral(3)],
                                        IntType(),
                                        [IntLiteral(1), IntLiteral(2), IntLiteral(3)],
                                    )
                                ],
                            )
                        ]
                    ),
                ),
            ]
        )
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 499))

    def test_500(self):
        """
        func main() {
            var a, b boolean;
            if a || b {
                return;
            }
        }
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl("a", BoolType(), None),
                            VarDecl("b", BoolType(), None),
                            If(
                                BinaryOp("||", Id("a"), Id("b")),
                                Block([Return(None)]),
                                None,
                            ),
                        ]
                    ),
                )
            ]
        )
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 500))

    # ! ==== ADVANCED TEST CASES ==== !

    def test_501(self):
        """
        var a int = a;
        """
        input = Program([VarDecl("a", IntType(), Id("a"))])
        expect = "Undeclared Identifier: a\n"
        self.assertTrue(TestChecker.test(input, expect, 501))

    def test_502(self):
        """
        Same name with built-in function
        var getInt int;
        """
        input = Program([VarDecl("getInt", IntType(), None)])
        expect = "Redeclared Variable: getInt\n"
        self.assertTrue(TestChecker.test(input, expect, 502))

    def test_503(self):
        input = """func main() { 
            var data [10]string; for _, item := range data {
              const MSG = "hello"; const MSG = "world"; }; }
              """
        expect = "Undeclared Identifier: item\n"
        self.assertTrue(TestChecker.test(input, expect, 503))

    def test_504(self):
        """
        func main() {
            var i int;
            var s string;
            for i, s := range [2]int{1, 2} {
                return;
            }
        }
        // ❌ s is string, but array elements are int
        """
        input = Program(
            [
                FuncDecl(
                    "main",
                    [],
                    VoidType(),
                    Block(
                        [
                            VarDecl("i", IntType(), None),
                            VarDecl("s", StringType(), None),
                            ForEach(
                                Id("i"),
                                Id("s"),
                                ArrayLiteral(
                                    [IntLiteral(2)],
                                    IntType(),
                                    [IntLiteral(1), IntLiteral(2)],
                                ),
                                Block([Return(None)]),
                            ),
                        ]
                    ),
                )
            ]
        )
        expect = "Type Mismatch: ForEach(Id(i),Id(s),ArrayLiteral([IntLiteral(2)],IntType,[IntLiteral(1),IntLiteral(2)]),Block([Return()]))\n"
        self.assertTrue(TestChecker.test(input, expect, 504))

    def test_505(self):
        """
        const a = 4;
        var b = [a] int {3}
        Normal case
        """
        input = Program(
            [
                ConstDecl("a", IntType(), IntLiteral(4)),
                VarDecl("b", None, ArrayLiteral([IntLiteral(3)], IntType(), [])),
            ]
        )
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 505))

    # ! ===================== Declaration Aspect ===================== !
    # * ============== Variable Declaration ============== *
    
    def test_506(self):
        """
        var x int;

        func main() {
            var x string;  // ✅ shadows global
        }
        """
        input = Program([
            VarDecl("x", IntType(), None),
            FuncDecl("main", [], VoidType(),
                Block([
                    VarDecl("x", StringType(), None)
                ])
            )
        ])
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 506))


    def test_507(self):
        """
        func main(x int) {
            var x float;  // ✅ shadows parameter
        }
        """
        input = Program([
            FuncDecl("main",
                [ParamDecl("x", IntType())],
                VoidType(),
                Block([
                    VarDecl("x", FloatType(), None)
                ])
            )
        ])
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 507))

    def test_508(self):
        """
        func main() {
            var a int = 10;
        }
        """
        input = Program([
            FuncDecl("main", [], VoidType(),
                Block([
                    VarDecl("a", IntType(), IntLiteral(10))
                ])
            )
        ])
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 508))

    def test_509(self):
        """
        func main() {
            var s = "MiniGo";  // ✅ type inferred as string
        }
        """
        input = Program([
            FuncDecl("main", [], VoidType(),
                Block([
                    VarDecl("s", None, StringLiteral("MiniGo"))
                ])
            )
        ])
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 509))

    def test_510(self):
        """
        func main() {
            var flag bool;
        }
        """
        input = Program([
            FuncDecl("main", [], VoidType(),
                Block([
                    VarDecl("flag", BoolType(), None)
                ])
            )
        ])
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 510))

    # * ============== Constant Declaration ============== *
    # NOTE: No tests because the above tests already cover the constant declaration aspect
    
    # * ============== Function Declaration ============== *
    def test_511(self):
        """
        func getInt() int {
            return 1;
        }
        // ❌ getInt is built-in
        """
        input = Program([
            FuncDecl("getInt", [], IntType(),
                Block([Return(IntLiteral(1))])
            )
        ])
        expect = "Redeclared Function: getInt\n"
        self.assertTrue(TestChecker.test(input, expect, 511))

    def test_512(self):
        """
        func add(a int, b int) int {
            return a + b;
        }
        """
        input = Program([
            FuncDecl("add", [
                ParamDecl("a", IntType()),
                ParamDecl("b", IntType())
            ], IntType(),
                Block([
                    Return(BinaryOp("+", Id("a"), Id("b")))
                ])
            )
        ])
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 512))

    def test_513(self):
        """
        func greet() {
            return;
        }
        """
        input = Program([
            FuncDecl("greet", [], VoidType(),
                Block([Return(None)])
            )
        ])
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 513))

    def test_514(self):
        """
        func foo(a int, a float) {}  // ❌ duplicate parameter name
        """
        input = Program([
            FuncDecl("foo", [
                ParamDecl("a", IntType()),
                ParamDecl("a", FloatType())
            ], VoidType(),
                Block([Return(None)])
            )
        ])
        expect = "Redeclared Parameter: a\n"
        self.assertTrue(TestChecker.test(input, expect, 514))

    def test_515(self):
        """
        func foo(a int) {
            var a float;  // ✅ shadowing is OK
        }
        """
        input = Program([
            FuncDecl("foo", [ParamDecl("a", IntType())], VoidType(),
                Block([
                    VarDecl("a", FloatType(), None)
                ])
            )
        ])
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 515))

    def test_516(self):
        """
        type A struct {}
        func (a A) hello() {}
        func (b A) hello() {}  // ❌ redeclared method
        """
        input = Program([
            StructType("A", [], []),
            MethodDecl("a", Id("A"),
                FuncDecl("hello", [], VoidType(), Block([Return(None)]))
            ),
            MethodDecl("b", Id("A"),
                FuncDecl("hello", [], VoidType(), Block([Return(None)]))
            )
        ])
        expect = "Redeclared Method: hello\n"
        self.assertTrue(TestChecker.test(input, expect, 516))

    def test_517(self):
        """
        type A struct {}
        func (a A) compute(x int) int {
            var x = 10;  // ✅ shadowing parameter is OK
            return x;
        }
        """
        input = Program([
            StructType("A", [], []),
            MethodDecl("a", Id("A"),
                FuncDecl("compute", [ParamDecl("x", IntType())], IntType(),
                    Block([
                        VarDecl("x", IntType(), IntLiteral(10)),
                        Return(Id("x"))
                    ])
                )
            )
        ])
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 517))

    # * ============== Function Call ============== *

    def test_518(self):
        """
        func foo() {}

        func main() {
            foo();  // ✅ valid function call as a statement
        }
        """
        input = Program([
            FuncDecl("foo", [], VoidType(), Block([Return(None)])),
            FuncDecl("main", [], VoidType(),
                Block([FuncCall("foo", [])])
            )
        ])
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 518))

    def test_519(self):
        """
        func main() {
            getInt();  // ✅ calling built-in function
        }
        """
        input = Program([
            FuncDecl("main", [], VoidType(),
                Block([FuncCall("getInt", [])])
            )
        ])
        expect = "Type Mismatch: FuncCall(getInt,[])\n"
        self.assertTrue(TestChecker.test(input, expect, 519))

    def test_520(self):
        """
        func add(a int, b int) int {
            return a + b;
        }

        func main() {
            var result = add(3, 4);  // ✅ function call as an expression
        }
        """
        input = Program([
            FuncDecl("add", [
                ParamDecl("a", IntType()),
                ParamDecl("b", IntType())
            ], IntType(),
                Block([
                    Return(BinaryOp("+", Id("a"), Id("b")))
                ])
            ),
            FuncDecl("main", [], VoidType(),
                Block([VarDecl("result", None, FuncCall("add", [IntLiteral(3), IntLiteral(4)]))])
            )
        ])
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 520))

    def test_521(self):
        """
        func add(a int, b int) int {
            return a + b;
        }

        func main() {
            var result = add(3, "hello");  // ❌ mismatch, second param should be int
        }
        """
        input = Program([
            FuncDecl("add", [ParamDecl("a", IntType()), ParamDecl("b", IntType())], IntType(),
                Block([Return(BinaryOp("+", Id("a"), Id("b")))])
            ),
            FuncDecl("main", [], VoidType(),
                Block([VarDecl("result", None, FuncCall("add", [IntLiteral(3), StringLiteral("hello")]))])
            )
        ])
        expect = "Type Mismatch: FuncCall(add,[IntLiteral(3),StringLiteral(hello)])\n"
        self.assertTrue(TestChecker.test(input, expect, 521))

    def test_522(self):
        """
        func foo() {}

        func main() {
            var x = foo();  // ❌ function call should be a statement, not an expression here
        }
        """
        input = Program([
            FuncDecl("foo", [], VoidType(), Block([Return(None)])),
            FuncDecl("main", [], VoidType(),
                Block([VarDecl("x", None, FuncCall("foo", []))])
            )
        ])
        expect = "Type Mismatch: FuncCall(foo,[])\n"
        self.assertTrue(TestChecker.test(input, expect, 522))

    def test_523(self):
        """
        func foo() {}

        func main() {
            const x = foo();  // ❌ function call should be treated as statement in const declaration
        }
        """
        input = Program([
            FuncDecl("foo", [], VoidType(), Block([Return(None)])),
            FuncDecl("main", [], VoidType(),
                Block([ConstDecl("x", None, FuncCall("foo", []))])
            )
        ])
        expect = "Type Mismatch: FuncCall(foo,[])\n"
        self.assertTrue(TestChecker.test(input, expect, 523))

    def test_524(self):
        """
        func foo(a int) {}

        func main() {
            foo(foo(3));  // ❌ function call in function parameter should not be allowed
        }
        """
        input = Program([
            FuncDecl("foo", [ParamDecl("a", IntType())], VoidType(), Block([Return(None)])),
            FuncDecl("main", [], VoidType(),
                Block([FuncCall("foo", [FuncCall("foo", [IntLiteral(3)])])])
            )
        ])
        expect = "Type Mismatch: FuncCall(foo,[IntLiteral(3)])\n"
        self.assertTrue(TestChecker.test(input, expect, 524))

    def test_525(self):
        """
        func foo() {}

        func main() {
            if foo() {  // ❌ function call in conditional expression not allowed
                return;
            }
        }
        """
        input = Program([
            FuncDecl("foo", [], VoidType(), Block([Return(None)])),
            FuncDecl("main", [], VoidType(),
                Block([If(FuncCall("foo", []), Block([Return(None)]), None)])
            )
        ])
        expect = "Type Mismatch: FuncCall(foo,[])\n"
        self.assertTrue(TestChecker.test(input, expect, 525))

    def test_526(self):
        """
        func foo() {}

        func main() {
            var result = foo() + 1;  // ❌ function call in binary operation not allowed
        }
        """
        input = Program([
            FuncDecl("foo", [], VoidType(), Block([Return(None)])),
            FuncDecl("main", [], VoidType(),
                Block([VarDecl("result", None, BinaryOp("+", FuncCall("foo", []), IntLiteral(1)))]),
            )
        ])
        expect = "Type Mismatch: FuncCall(foo,[])\n"
        self.assertTrue(TestChecker.test(input, expect, 526))

    def test_527(self):
        """
        func add(a int, b int) int {
            return a + b;
        }

        func main() {
            var result = add(3, 4);  // ✅ valid function call as an expression
        }
        """
        input = Program([
            FuncDecl("add", [ParamDecl("a", IntType()), ParamDecl("b", IntType())], IntType(),
                Block([Return(BinaryOp("+", Id("a"), Id("b")))])
            ),
            FuncDecl("main", [], VoidType(),
                Block([VarDecl("result", None, FuncCall("add", [IntLiteral(3), IntLiteral(4)]))])
            )
        ])
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 527))


    # ! ===================== Advance 2 ===================== !
    def test_528(self):
        """
        var a [5]int = [4]int{1, 2, 3, 4};  // ❌ array size mismatch
        """
        input = Program([
            VarDecl("a", ArrayType([IntLiteral(5)], IntType()),
                ArrayLiteral([IntLiteral(4)], IntType(), [IntLiteral(1), IntLiteral(2), IntLiteral(3), IntLiteral(4)]))
        ])
        expect = "Type Mismatch: VarDecl(a,ArrayType(IntType,[IntLiteral(5)]),ArrayLiteral([IntLiteral(4)],IntType,[IntLiteral(1),IntLiteral(2),IntLiteral(3),IntLiteral(4)]))\n"
        self.assertTrue(TestChecker.test(input, expect, 528))

    def test_529(self):
        """
        var a[5] float = [5]float{1.0, 2.0, 3.0};  // ✅ valid array initialization
        """
        input = Program([
            VarDecl("a", ArrayType([IntLiteral(5)], FloatType()),
                ArrayLiteral([IntLiteral(5)], FloatType(), [FloatLiteral(1.0), FloatLiteral(2.0), FloatLiteral(3.0)]))
        ])
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 529))