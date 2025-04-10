  
import unittest
from TestUtils import TestChecker
from AST import *

class CheckSuite(unittest.TestCase):
    def test_401(self):
        input = Program([VarDecl("a",IntType(),Id("b"))])
        expect = "Undeclared Identifier: b\n"
        self.assertTrue(TestChecker.test(input, expect, 401))

    def test_402(self):
        input = Program([VarDecl("a",IntType(),Id("a"))])
        expect = "Undeclared Identifier: a\n"
        self.assertTrue(TestChecker.test(input, expect, 402))

    def test_403(self):
        input = Program([VarDecl("a",IntType(),None),VarDecl("a",IntType(),None)])
        expect = "Redeclared Variable: a\n"
        self.assertTrue(TestChecker.test(input, expect, 403))

    def test_404(self):
        input = "var a boolean = true;"
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 404))

    def test_405(self):
        input = """var a int = 3.14;"""
        expect = "Type Mismatch: VarDecl(a,IntType,FloatLiteral(3.14))\n"
        self.assertTrue(TestChecker.test(input, expect, 405))

    def test_406(self):
        input = """var a int = 3.14 + 1.23;"""
        expect = "Type Mismatch: VarDecl(a,IntType,BinaryOp(FloatLiteral(3.14),+,FloatLiteral(1.23)))\n"
        self.assertTrue(TestChecker.test(input, expect, 406))

    def test_407(self):
        input = """var a int = 1 + 2;"""
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 407))

    def test_408(self):
        input = """var a float = 1 + 2.0;"""
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 408))

    def test_409(self):
        input = """var a float = 1.0 + 2;"""
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 409))

    def test_410(self):
        input = """var a string = "abc" + "def";"""
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 410))

    def test_411(self):
        input = """var a string = "abc" + 1;"""
        expect = """Type Mismatch: BinaryOp(StringLiteral("abc"),+,IntLiteral(1))\n"""
        self.assertTrue(TestChecker.test(input, expect, 411))

    def test_412(self):
        input = """var a int = 1 + 2.0;"""
        expect = """Type Mismatch: VarDecl(a,IntType,BinaryOp(IntLiteral(1),+,FloatLiteral(2.0)))\n"""
        self.assertTrue(TestChecker.test(input, expect, 412))
    
    def test_413(self):
        input = """var a int = (1>3) == (2<4);"""
        expect = """Type Mismatch: BinaryOp(BinaryOp(IntLiteral(1),>,IntLiteral(3)),==,BinaryOp(IntLiteral(2),<,IntLiteral(4)))\n"""
        self.assertTrue(TestChecker.test(input, expect, 413))
    
    def test_414(self):
        input = """const a = 1 + 2 * 3;"""
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 414))

    def test_415(self):
        input = """const a = 1 + 2 * 3.2;"""
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 415))

    def test_416(self):
        input = """func a(b int, c int) int { return b + c; };"""
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 416))

    def test_417(self):
        input = """func a(b int, c float) int { return b + c; };"""
        expect = """Type Mismatch: Return(BinaryOp(Id(b),+,Id(c)))\n"""
        self.assertTrue(TestChecker.test(input, expect, 417))

    def test_418(self):
        input = """var arr [3]int = [3]int { 10, 20, 30 };"""
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 418))

    """Program([VarDecl(arr,ArrayType(IntType,[IntLiteral(3)]),ArrayLiteral([IntLiteral(3)],IntType,[IntLiteral(10),IntLiteral(20),IntLiteral(30)]))])
Program([VarDecl(arr,ArrayType(FloatType,[IntLiteral(3)]),ArrayLiteral([IntLiteral(3)],IntType,[IntLiteral(10),IntLiteral(20),IntLiteral(30)]))])"""

    def test_419(self):
        input = """var arr [3]string = [3]int { 10, 20, 30 };"""
        expect = """Type Mismatch: VarDecl(arr,ArrayType(StringType,[IntLiteral(3)]),ArrayLiteral([IntLiteral(3)],IntType,[IntLiteral(10),IntLiteral(20),IntLiteral(30)]))\n"""
        self.assertTrue(TestChecker.test(input, expect, 419))

    def test_420(self):
        input = """var arr [3]int = [4]int { 10, 20, 30 };"""
        expect = """Type Mismatch: VarDecl(arr,ArrayType(IntType,[IntLiteral(3)]),ArrayLiteral([IntLiteral(4)],IntType,[IntLiteral(10),IntLiteral(20),IntLiteral(30)]))\n"""
        self.assertTrue(TestChecker.test(input, expect, 420))

    def test_421(self):
        input = """const dim = 3;
var arr [dim]int = [dim]int { 10, 20, 30 };"""
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 421))

    def test_421(self):
        input = """const dim = 3 + 1;
var arr [dim]int = [4]int { 10, 20, 30, 40 };"""
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 421))

    def test_422(self):
        input = """var dim = 3 + 1;
var arr [dim]int = [4]int { 10, 20, 30, 40 };"""
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 422))

#     def test_423(self):
#         input = """var dim = 3 + 1.0;
# var arr [dim]int = [4]int { 10, 20, 30, 40 };"""
#         expect = """Type Mismatch: VarDecl(arr,ArrayType(IntType,[Id(dim)]),ArrayLiteral([IntLiteral(4)],IntType,[IntLiteral(10),IntLiteral(20),IntLiteral(30),IntLiteral(40)]))\n"""
#         self.assertTrue(TestChecker.test(input, expect, 423))

    def test_424(self):
        input = """func main() {
    return;
};"""
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 424))

    def test_424(self):
        input = """func main() {
    a := 1;
    return;
};"""
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 424))

    def test_425(self):
        input = """
    var a [3][4] int;
    var b [4] int = a[0];
"""
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 425))

    def test_426(self):
        input = """
    var a [3][4] int;
    var b [4] int = a;
"""
        expect = """Type Mismatch: VarDecl(b,ArrayType(IntType,[IntLiteral(4)]),Id(a))\n"""
        self.assertTrue(TestChecker.test(input, expect, 426))

    def test_427(self):
        input = """func main() {
    a += 1;
    return;
};"""
        expect = """Undeclared Identifier: a\n"""
        self.assertTrue(TestChecker.test(input, expect, 427))

    def test_428(self):
        input = """func main() {
    a := 1.0;
    a := 1;
    return;
};"""
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 428))

    def test_429(self):
        input = """func main() {
    a := 1;
    a := 1.0;
    return;
};"""
        expect = """Type Mismatch: Assign(Id(a),FloatLiteral(1.0))\n"""
        self.assertTrue(TestChecker.test(input, expect, 429))

    def test_430(self):
        input = """func main() {
    x := 0;
    for x < 10 {
        x += 1;
    }
    return;
};"""
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 430))

    def test_431(self):
        input = """func main() {
    for x < 10 {
        x += 1;
    }
    return;
};"""
        expect = """Undeclared Identifier: x\n"""
        self.assertTrue(TestChecker.test(input, expect, 431))

    def test_432(self):
        input = """func main() {
    for i := 0; i < 10; i += 1 {
        i := 1;
    }
    return;
};"""
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 432))

    def test_433(self):
        input = """func main() {
    for i := 0; i < 10; i += 1 {
        i := 1;
    }
    i += 1;
    return;
};"""
        expect = """Undeclared Identifier: i\n"""
        self.assertTrue(TestChecker.test(input, expect, 433))

    def test_434(self):
        input = """func main() {
    for i := 0; i < 10; i += 1 {
        i += true;
    }
    return;
};"""
        expect = """Type Mismatch: BinaryOp(Id(i),+,BooleanLiteral(true))\n"""
        self.assertTrue(TestChecker.test(input, expect, 434))

    def test_435(self):
        input = """func main() {
    for i := 0; i + 10; i += 1 {
        i += 10;
    }
    return;
};"""
        expect = """Type Mismatch: For(Assign(Id(i),IntLiteral(0)),BinaryOp(Id(i),+,IntLiteral(10)),Assign(Id(i),BinaryOp(Id(i),+,IntLiteral(1))),Block([Assign(Id(i),BinaryOp(Id(i),+,IntLiteral(10)))]))\n"""
        self.assertTrue(TestChecker.test(input, expect, 435))

    def test_436(self): 
        input = """func main() {
    for i, v := range arr {
        i += 10;
    }
    return;
};"""
        expect = """Undeclared Identifier: i\n"""
        self.assertTrue(TestChecker.test(input, expect, 436))

    def test_437(self):
        input = """func main() {
    for i, v := range [3]int { 10, 20, 30 } {
        i += 10;
    }
    return;
};"""
        expect = """Undeclared Identifier: i\n"""
        self.assertTrue(TestChecker.test(input, expect, 437))

    def test_438(self):
        input = """func main() {
    var arr [3]int = [3]int { 10, 20, 30 };
    for i, v := range arr {
        i += 10;
        v += 10;
    }
    return;
};"""
        expect = """Undeclared Identifier: i\n"""
        self.assertTrue(TestChecker.test(input, expect, 438))

    def test_439(self):
        input = """func main() {
    var arr [3]int = [3]int { 10, 20, 30 };
    for i, v := range arr {
        i += 10;
        v += "10";
    }
    return;
};"""
        expect = """Undeclared Identifier: i\n"""
        self.assertTrue(TestChecker.test(input, expect, 439))

    def test_440(self):
        input = """func main() {
    var arr [2][3]int = [2][3]int { {10, 20, 30}, {40, 50, 60} };
    for i, v := range arr {
        i += 10;
        v += 10;
    }
    return;
};"""
        expect = """Undeclared Identifier: i\n"""
        self.assertTrue(TestChecker.test(input, expect, 440))

    def test_441(self):
        input = """func main() {
    var x int;
    for x + 10 {
        x += 1;
    }
    return;
};"""
        expect = """Type Mismatch: For(BinaryOp(Id(x),+,IntLiteral(10)),Block([Assign(Id(x),BinaryOp(Id(x),+,IntLiteral(1)))]))\n"""
        self.assertTrue(TestChecker.test(input, expect, 441))

    def test_442(self):
        input = """func main() {
    for i := 0; i < 10; i += 1 {
        var i int = 100;
    }
    return;
};"""
        expect = """Redeclared Variable: i\n"""
        self.assertTrue(TestChecker.test(input, expect, 442))

    def test_443(self):
        input = """func main() {
    for var i = 0; i < 10; i += 1 {
        var i int = 100;
    }
    return;
};"""
        expect = """Redeclared Variable: i\n"""
        self.assertTrue(TestChecker.test(input, expect, 443))

    def test_444(self):
        input = """func main() {
    var arr [2][3]int = [2][3]int { {10, 20, 30}, {40, 50, 60} };
    for i, v := range arr {
        i += 10;
        v[10] += 10;
    }
    return;
};"""
        expect = """Undeclared Identifier: i\n"""
        self.assertTrue(TestChecker.test(input, expect, 444))

    def test_445(self):
        input = """func a() int {
    return 1;
};
func main() {
    var x int = a();
};"""
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 445))

    def test_446(self):
        input = """ func main() {
    a := [1][1][1] int { {{1}}}
    for i,v := range a {
        var i = i;
        for i:=1.2; i < 10; i+=1 {
            var i int = 3;
            var v = v;
            return
        }
    }
    return;
};"""
        expect = """Undeclared Identifier: i\n"""
        self.assertTrue(TestChecker.test(input, expect, 446))

    def test_447(self):
        input = """func a() int {
    return 1;
};
func main() {
    var x int = 10;
    a();
};"""
        expect = """Type Mismatch: FuncCall(a,[])\n"""
        self.assertTrue(TestChecker.test(input, expect, 447))

    def test_448(self):
        input = """func a(x int) int {
    return 1;
};
func main() {
    var x int = 10;
    var y int = a(x);
};"""
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 448))

    def test_449(self):
        input = """func a(x string) float {
    return 1.0;
};
func main() {
    var x int = 10;
    var y float = a(x);
};"""
        expect = """Type Mismatch: FuncCall(a,[Id(x)])\n"""
        self.assertTrue(TestChecker.test(input, expect, 449))

    def test_450(self):
        input = """func main() {
    var arr [2][3]int = [2]int { 1, 2 };
    return;
};"""
        expect = """Type Mismatch: VarDecl(arr,ArrayType(IntType,[IntLiteral(2),IntLiteral(3)]),ArrayLiteral([IntLiteral(2)],IntType,[IntLiteral(1),IntLiteral(2)]))\n"""
        self.assertTrue(TestChecker.test(input, expect, 450))

    def test_451(self):
        input = """func main() [2]int {
    var arr [2]int = [2]int { 1, 2 };
    return arr;
};"""
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 451))

    def test_452(self):
        input = """func main() int {
    var arr [2]int = [2]int { 1, 2 };
    return arr;
};"""
        expect = """Type Mismatch: Return(Id(arr))\n"""
        self.assertTrue(TestChecker.test(input, expect, 452))

    def test_453(self):
        input = """func main() [2]int {
    var arr int = 1;
    return arr;
};"""
        expect = """Type Mismatch: Return(Id(arr))\n"""
        self.assertTrue(TestChecker.test(input, expect, 453))

    def test_454(self):
        input = """var dim = 3 + 1.0;
var arr [4]int = [dim]int { 10, 20, 30, 40 };"""
        expect = """Type Mismatch: ArrayLiteral([Id(dim)],IntType,[IntLiteral(10),IntLiteral(20),IntLiteral(30),IntLiteral(40)])\n"""
        self.assertTrue(TestChecker.test(input, expect, 454))

    def test_455(self):
        input = """var a int = 1;
var b float = a;"""
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 455))

    def test_456(self):
        input = """func main (a int) { 
            var a int = 3;
            if (3+2) {
                return ;
            }
        
        };"""
        expect = "Type Mismatch: If(BinaryOp(IntLiteral(3),+,IntLiteral(2)),Block([Return()]))\n"
        self.assertTrue(TestChecker.test(input, expect, 456))

    def test_457(self):
        input = """type A struct {
    a int
};
func (a A) get() int {
    return a.a
};
func main () {
    var a = A { a: 12 };
    var b = a.get();
};
"""
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 457))

    def test_458(self):
        input = """func main () {
    for 1 + 2 {
        return;
    }
};"""
        expect = """Type Mismatch: For(BinaryOp(IntLiteral(1),+,IntLiteral(2)),Block([Return()]))\n"""
        self.assertTrue(TestChecker.test(input, expect, 458))

    def test_459(self):
        input = """
                type C struct {
                    aa int
                    name string
                }
                func Test(a int, b int) int {
                    var a int = 3;
                    var c C = C { aa: a };
                    return c.aa;
                }
                """
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 459))

    def test_460_int_to_float(self):
        input = """
                var c =  6/2 + 3 - 1*2;
                var a [4] float = [c] int {1,c,3}
                """
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 460))

    def test_461_int_to_float(self):
        input = """var a [5][5] float = [5][5] int { {1,2,3} };"""
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 461))

    def test_462_int_to_float(self):
        input = """
type A struct {
    a float
}
func main () {
    var a A = A { a: 12 };
};
"""
        expect = """Type Mismatch: StructLiteral(A,[(a,IntLiteral(12))])\n"""
        self.assertTrue(TestChecker.test(input, expect, 462))

    def test_463_int_to_float(self):
        input = """var a [4] float;
func main() {
        a := [4] int {1,2,3,4};
};"""
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 463))

    def test_464_int_to_float(self):
        input = """var a [4][4] float;
func main() {
    a := [4][4] int { {1,2,3,4} };
};"""
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 464))

    def test_465_int_to_float(self):
        input = """type A struct {
    a float
}
func main () {
    var a A;
    a := A { a: 12 };
};"""
        expect = """Type Mismatch: StructLiteral(A,[(a,IntLiteral(12))])\n"""
        self.assertTrue(TestChecker.test(input, expect, 465))

    def test_466(self):
        input = """type A struct {
            a float
        }
        type B struct {
            b float
            a A
        }
        func main () {
            var b B = B { b: 12, a: A { a: 12 } };
        };"""
        expect = """Type Mismatch: StructLiteral(B,[(b,IntLiteral(12)),(a,StructLiteral(A,[(a,IntLiteral(12))]))])\n"""
        self.assertTrue(TestChecker.test(input, expect, 466))

    def test_467(self):
        input = """
            func a (b [3] int) int {
                return 123
            }
            func main () {
                var b = a([3] int {1,2,3});
            } 
            """
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 467))

    def test_468(self):
        input = """
type A interface {
    Get() int
}
type B struct {
    a int
}
func (b B) Get() int {
    return b.a
}
func main () {
    var b = B { a: 123 }
    var a = b.Get()
}
"""
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 468))

    def test_469(self):
        input = """
type A interface {
    Get() int
}
type B struct {
    a int
}
func main () {
    var b = B { a: 123 }
    var a A = b
    var c = a.Get()
}
"""
        expect = """Type Mismatch: VarDecl(a,Id(A),Id(b))\n"""
        self.assertTrue(TestChecker.test(input, expect, 469))

    def test_470(self):
        input = """
type A interface {
    Get() int
}
type B struct {
    a int
}
type C struct {
    b int
}
func (hcmut B) Get () int {
    return hcmut.a
}
func (hcmut C) Get () int {
    return hcmut.b
}
func main () {
    var b = B { a: 123 }
    var c = C { b: 123 }
    var a0 A = b
    var a1 A = c
    var x = a0.Get()
    var y = a1.Get()
}
"""
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 470))

    def test_471(self):
        input = """var a float = 1;
var b int = a;
"""
        expect = """Type Mismatch: VarDecl(b,IntType,Id(a))\n"""
        self.assertTrue(TestChecker.test(input, expect, 471))

    def test_472(self):
        input = """
type A interface {
    Get(x int) int
}
type B struct {
    a int
}
func main () {
    var b = B { a: 123 }
    var a A = b
    var c = a.Get(12)
}
"""
        expect = """Type Mismatch: VarDecl(a,Id(A),Id(b))\n"""
        self.assertTrue(TestChecker.test(input, expect, 472))

    def test_473(self):
        input = """
type A interface {
    Get(x int) int
}
type B struct {
    a int
}
func (b B) Get(y int) int {
    return b.a
}
func main () {
    var b B = B { a: 123 }
    var x = b.Get(1)
    var a A = b
    var c = a.Get(12)
}
"""
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 473))

#     def test_474(self):
#         input = """var dim = 3 + 1.0;
# var arr [dim]int;"""
#         expect = """Type Mismatch: VarDecl(arr,ArrayType(IntType,[Id(dim)]))\n"""
#         self.assertTrue(TestChecker.test(input, expect, 474))

#     def test_475(self): # Note: structdecl khong phai stmt, expr
#         input = """
# const dim = 3 + 1.0;
# type A struct {
#     a [dim] int
# }
# func (a A) get() [dim] int {
#     return a.a
# }
# func main () {
#     var a = A { a: 12 };
#     var b = a.get();
# }
#         """
#         expect = """Type Mismatch: StructType(A,[(a,ArrayType(IntType,[Id(dim)]))],[])\n"""
#         self.assertTrue(TestChecker.test(input, expect, 475))

#     def test_476(self): # Note: funcdecl khong phai stmt, expr
#         input = """
#             const dim = 3 + 1.0;
#             type A struct {
#                 a [4] int
#             }
#             func (a A) get() [dim] int {
#                 return a.a
#             }
#             func main () {
#                 var a = A { a: 12 };
#                 var b = a.get();
#             }
#         """
#         expect = """Type Mismatch: FuncDecl(get,[],ArrayType(IntType,[Id(dim)]),Block([Return(FieldAccess(Id(a),a))]))\n"""
#         self.assertTrue(TestChecker.test(input, expect, 476))

    def test_477(self):
        input = """
type A struct {
    a [4] int
}
func (a A) get() [4] int {
    return a.a
}
func main () {
    var a = A { a: 12 };
    var b = a.get();
}
        """
        expect = """Type Mismatch: StructLiteral(A,[(a,IntLiteral(12))])\n"""
        self.assertTrue(TestChecker.test(input, expect, 477))

    def test_478(self):
        input = """
            type A struct {
                a [4] int
            }
            func (a A) get() [4] int {
                return a.a
            }
            func main () {
                var a = A { a: [4] int {1,2,3,4} };
                var b = a.get();
            }
        """
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 478))

    def test_479(self):
        input = """
type A struct {
    a int
}
func main () {
    var a = A { a: 12 };
    var b = a.get();
}
"""
        expect = """Undeclared Method: get\n"""
        self.assertTrue(TestChecker.test(input, expect, 479))

    def test_480(self):
        input = """func main () {
    var a = add(1,2);
};"""
        expect = """Undeclared Function: add\n"""
        self.assertTrue(TestChecker.test(input, expect, 480))

    def test_481(self):
        input = """type A struct {
    a int
}
func main () {
    var a = A { a: 12 };
    var b = a.b;
};"""
        expect = """Undeclared Field: b\n"""
        self.assertTrue(TestChecker.test(input, expect, 481))

    def test_482(self):
        input = """var a int = 1;
var a float = 1;"""
        expect = """Redeclared Variable: a\n"""
        self.assertTrue(TestChecker.test(input, expect, 482))

    def test_483(self):
        input = """var a float = 1;
func main () {
    var a int = 1;
    var b int = 1;
    var b float = 1;
};"""
        expect = """Redeclared Variable: b\n"""
        self.assertTrue(TestChecker.test(input, expect, 483))

    def test_484(self):
        input = """const a = 1;
func main () {
    var a int = 1;
    var b int = 1;
    const b = 1;
};"""
        expect = """Redeclared Constant: b\n"""
        self.assertTrue(TestChecker.test(input, expect, 484))

    def test_485(self):
        input = """const a = 1;
const a = 1.1234;
func main () {
    var b int = 1;
    const b = 1;
};"""
        expect = """Redeclared Constant: a\n""" 
        self.assertTrue(TestChecker.test(input, expect, 485))

    def test_486(self):
        input = """
func a(a, a int) int {
    return 1;
}
"""
        expect = """Redeclared Parameter: a\n"""
        self.assertTrue(TestChecker.test(input, expect, 486))

    def test_487(self):
        input = """
func a(a, b int, c, d, a float) int {
    return 1;
}
"""
        expect = """Redeclared Parameter: a\n"""
        self.assertTrue(TestChecker.test(input, expect, 487))

    def test_488(self):
        input = """
func a(a, b int, c, d, e float) int {
    var a int = 1;
    return a;
}
"""
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 488))

    def test_489(self):
        input = """
type A struct {
    a int
}
type B struct {
    a int
}
type A struct {
    a int
}
"""
        expect = """Redeclared Type: A\n"""
        self.assertTrue(TestChecker.test(input, expect, 489))

    def test_490(self):
        input = """
type A struct {
    a int
}
type A interface {
    get() int
}
"""
        expect = """Redeclared Type: A\n"""
        self.assertTrue(TestChecker.test(input, expect, 490))

    def test_491(self):
        input = """
func a(a int) int {
    return 1;
}
func a() {
    return 1;
}
"""
        expect = """Redeclared Function: a\n"""
        self.assertTrue(TestChecker.test(input, expect, 491))

    def test_492(self):
        input = """
type A struct {
    a int
}
func (a A) a() int {
    return 1;
}
func (a A) a(x int) int {
    return 1;
}

"""
        expect = """Redeclared Method: a\n"""
        self.assertTrue(TestChecker.test(input, expect, 492))

    def test_493(self):
        input = """
type A interface {
    a() int
    a(x int) int
}
"""
        expect = """Redeclared Prototype: a\n"""
        self.assertTrue(TestChecker.test(input, expect, 493))

    def test_494(self):
        input = """
type A struct {
    a int
    a string
}
"""
        expect = """Redeclared Field: a\n"""
        self.assertTrue(TestChecker.test(input, expect, 494))

    def test_495(self):
        input = """
type A struct {
    a int
}
func (a A) a() int {
    return 1;
}
func main() {
    var a = A { a:1 }
    var x = a.a();
    var y = a.a;
}
"""
        expect = """Redeclared Method: a\n"""
        self.assertTrue(TestChecker.test(input, expect, 495))

    def test_496(self):
        input = """     
var a = putInt(1);
                """
        expect = """Type Mismatch: FuncCall(putInt,[IntLiteral(1)])\n"""
        self.assertTrue(TestChecker.test(input, expect, 496))

    def test_497(self):

        #  Symbol("getInt", FuncType([], IntType()), None),
        #     Symbol("putInt", FuncType([IntType()], VoidType()), None),
        #     Symbol("putIntLn", FuncType([IntType()], VoidType()), None),
        #     Symbol("getFloat", FuncType([], FloatType()), None),
        #     Symbol("putFloat", FuncType([FloatType()], VoidType()), None),
        #     Symbol("putFloatLn", FuncType([FloatType()], VoidType()), None),
        #     Symbol("getBool", FuncType([], BoolType()), None),
        #     Symbol("putBool", FuncType([BoolType()], VoidType()), None),
        #     Symbol("putBoolLn", FuncType([BoolType()], VoidType()), None),
        #     Symbol("getString", FuncType([], StringType()), None),
        #     Symbol("putString", FuncType([StringType()], VoidType()), None),
        #     Symbol("putStringLn", FuncType([StringType()], VoidType()), None),
        #     Symbol("putLn", FuncType([], VoidType()), None)
        input = """
func main() {
    x := getInt()
    putInt(x)
    putIntLn(x)
    y := getFloat()
    putFloat(y)
    putFloatLn(y)
    z := getBool()
    putBool(z)
    putBoolLn(z)
    t := getString()
    putString(t)
    putStringLn(t)
    putLn()
}
"""
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 497))

    def test_498(self):
        input = """
var x int = getInt()
var y float = getFloat()
var z boolean = getBool()
var t string = getString()
func main() {
    putInt(x)
    putIntLn(x)
    putFloat(y)
    putFloatLn(y)
    putBool(z)
    putBoolLn(z)
    putString(t)
    putStringLn(t)
    putLn()
}
"""
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 498))

    def test_499(self):
        input = Program([VarDecl("a",IntType(),None),VarDecl("b",FloatType(),None),VarDecl("a",IntType(),None)])
        expect = """Redeclared Variable: a\n"""
        self.assertTrue(TestChecker.test(input, expect, 499))

    def test_500(self):
        input = """
var x int = getInt() + getInt() + getInt() + getInt() + getInt() + getInt() + getInt()
var y float = getFloat() - getFloat() + getFloat() - getFloat() + getFloat() - getFloat() + getFloat()
var z boolean = getBool() || getBool() || getBool() && getBool() || getBool() || getBool()
var t string = getString() + getString() + getString() + getString() + getString() + getString() + getString()
func main() {
    putInt(x)
    putIntLn(x)
    putFloat(y)
    putFloatLn(y)
    putBool(z)
    putBoolLn(z)
    putString(t)
    putStringLn(t)
    putLn()
}
"""
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 500))

    def test_501(self):
        input = Program([VarDecl("a",IntType(),FloatLiteral(1.2))])
        expect = """Type Mismatch: VarDecl(a,IntType,FloatLiteral(1.2))\n"""
        self.assertTrue(TestChecker.test(input, expect, 501))

    def test_502(self):
        input = Program([VarDecl("a",IntType(),Id("b"))])
        expect = """Undeclared Identifier: b\n"""
        self.assertTrue(TestChecker.test(input, expect, 502))

    def test_503(self):
        input = """
    type A struct {
        a int
    }
    type A struct {
        b int
    }
"""
        expect = """Redeclared Type: A\n"""
        self.assertTrue(TestChecker.test(input, expect, 503))
    
    def test_504(self):
        input = """var a Car = 10;"""
        expect = "Undeclared Type: Car\n"
        self.assertTrue(TestChecker.test(input,expect,504))

    def test_504(self):
        input = """
func main () {
    var a Car = 10;
}
"""
        expect = "Undeclared Type: Car\n"
        self.assertTrue(TestChecker.test(input,expect,504))
    
    def test_505(self):
        input = """
func main () Car {
    var a Car = 10;
    return a;
}
"""
        expect = "Undeclared Type: Car\n"
        self.assertTrue(TestChecker.test(input,expect,505))

    def test_506(self):
        input = """
        func main () Car {
            const a = Car { age: 3 };
        }
"""
        expect = "Undeclared Type: Car\n"
        self.assertTrue(TestChecker.test(input,expect,506))

    def test_507(self):
        input = """
         const a = Car { age: 3 };
"""
        expect = "Undeclared Type: Car\n"
        self.assertTrue(TestChecker.test(input,expect,507))

#     def test_508(self):
#         input = """
#             func main () {
#                 var a = [1][3] int { {1,2,3} };
#                 var x = a[0][0][0];
#             }
# """
#         expect = "Type Mismatch: ArrayLiteral([IntLiteral(3),IntLiteral(4)],IntType,[[IntLiteral(1),IntLiteral(2),IntLiteral(3)]])\n"
#         self.assertTrue(TestChecker.test(input,expect,508))
    
    def test_509(self):
        input = """     
                const c = 5;
                type Student struct {
                    name string
                    age [c] int
                }
                """
        expect = """"""
        self.assertTrue(TestChecker.test(input,expect,509))

    # def test_510(self):
    #     input = """
    #     func foo() {
    #         return
    #     }
    #     func main(a int ) int {
    #         return foo();
    #     }
    #     """
    #     expect = """Type Mismatch: Return(FuncCall(foo,[]))\n"""
    #     self.assertTrue(TestChecker.test(input, expect, 510))

    # def test_511(self):
    #     input = """
    #     func foo() {
    #         return
    #     }
    #     func main(a int) {
    #         return foo();
    #     }
    #     """
    #     expect = """Type Mismatch: Return(FuncCall(foo,[]))\n"""
    #     self.assertTrue(TestChecker.test(input, expect, 511))

    # def test_512(self):
    #     input = """     
    #             const c = 5;
    #             func main(a int) [c] int {
    #                 return [4] int {1,2,3,4,5};
    #             }
    #             """
    #     expect = """Type Mismatch: Return(ArrayLiteral([IntLiteral(4)],IntType,[IntLiteral(1),IntLiteral(2),IntLiteral(3),IntLiteral(4),IntLiteral(5)]))\n"""
    #     self.assertTrue(TestChecker.test(input,expect,512))

    def test_513(self):
        input = """
            func main(a int) [c] int {
                    return [4] int {1,2,3,4,5};
                }
        """
        expect = """Undeclared Identifier: c\n"""
        self.assertTrue(TestChecker.test(input,expect,513))

    def test_514(self):
        input = """
var a int = 1;
func a() int {
    return 1;
}
"""
        expect = """Redeclared Function: a\n"""
        self.assertTrue(TestChecker.test(input, expect, 514))

    def test_515(self):
        input = """
func main() {
    for i := 0; i < 10; i += 1 {
        return;
    }
    var i int;
    return;
}
"""
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 515))

    # def test_516(self):
    #     input = """
    #     func main() {
    #         for var i = 0; i < 10; i += 1 {
    #             return;
    #         }
    #         var i int;
    #         return;
    #     }
    #     func main2() {
    #         for i, val := range [3]int{1, 2, 3} {
    #             return;
    #         }
    #         var i int;
    #         var val int;
    #         return;
    #     }
    #     """
    #     expect = """Undeclared Identifier: i\n"""
    #     self.assertTrue(TestChecker.test(input, expect, 516))

    # def test_517(self):
    #     input = """
    #     func foo() {
    #         return foo();
    #     }
    #     """
    #     expect = """Type Mismatch: Return(FuncCall(foo,[]))\n"""
    #     self.assertTrue(TestChecker.test(input, expect, 517))

    def test_518(self):
        input = """
func main() {
    for var i = 0.0; i < 10; i += 1 {
        continue;
    }
    var i int;
    return;
}
"""
        expect = """Type Mismatch: BinaryOp(Id(i),<,IntLiteral(10))\n"""
        self.assertTrue(TestChecker.test(input, expect, 518))

    def test_519(self):
        input = """
var main = 12;
func main() {
    return;
}
"""
        expect = """Redeclared Function: main\n"""
        self.assertTrue(TestChecker.test(input, expect, 519))

    def test_520(self):
        input = """
type A struct {
    a int
}
func A() int {
    return 1;
}
"""
        expect = """Redeclared Function: A\n"""
        self.assertTrue(TestChecker.test(input, expect, 520))

    def test_521(self):
        input = """
func A() int {
    return 1;
}
type A struct {
    a int
}
"""
        expect = """Redeclared Type: A\n"""
        self.assertTrue(TestChecker.test(input, expect, 521))

    def test_522(self):
        input = """
        var a main;
        const b  = 2;
        func main() {
            return
        }
        """
        expect = """Undeclared Type: main\n"""
        self.assertTrue(TestChecker.test(input, expect, 522))

    # def test_523(self):
    #     input = """
    #         func main() {
    #         a:=putInt(1);

    #     }
    #     """
    #     expect = """Type Mismatch: Assign(Id(a),FuncCall(putInt,[IntLiteral(1)]))\n"""
    #     self.assertTrue(TestChecker.test(input, expect, 523))

    def test_524(self):
        input = """func main() int { const xx = 1%2; return [1]int{1}[xx]; };"""
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 524))

    # def test_525(self):
    #     input = """const a = 3%2; var x = [a]int{ 1 }; const y = -1; var b = [y]int {};"""
    #     expect = """"""
    #     self.assertTrue(TestChecker.test(input, expect, 525))
    
    # def test_526(self):
    #     input = """const xx = false; var bruh [3][xx] int = [3][4] bool { {  true, true, false } };"""
    #     expect = """Type Mismatch: VarDecl(bruh,ArrayType(IntType,[IntLiteral(3),Id(xx)]),ArrayLiteral([IntLiteral(3),IntLiteral(4)],Id(bool),[[BooleanLiteral(true),BooleanLiteral(true),BooleanLiteral(false)]]))\n"""
    #     self.assertTrue(TestChecker.test(input, expect, 526))

    # def test_527(self):
    #     input = """const xx = false; const yy = true; var bruh [3][xx] int = [3][yy] bool { {  true, true, false } };"""
    #     expect = """Type Mismatch: VarDecl(bruh,ArrayType(IntType,[IntLiteral(3),Id(xx)]),ArrayLiteral([IntLiteral(3),Id(yy)],Id(bool),[[BooleanLiteral(true),BooleanLiteral(true),BooleanLiteral(false)]]))\n"""
    #     self.assertTrue(TestChecker.test(input, expect, 527))

    def test_528(self):
        input = """type A struct {
            a int
        }
        var a A = A{ a: 1 }
        var b A = a
        """
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 528))

    def test_529(self):
        input = """type A struct {
            a int
        }
        type B interface {
            get() int
        }
        func (a A) get() int {
            return a.a
        }
        var a B = A{ a: 1 }
        var b B = a
        """
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 529))

    def test_530(self):
        input = """type A struct {
            a int
        }
        type B interface {
            get() int
        }
        type C interface {
            get() int
        }
        func (a A) get() int {
            return a.a
        }
        var a B = A{ a: 1 }
        var b C = a
        """
        expect = """Type Mismatch: VarDecl(b,Id(C),Id(a))\n"""
        self.assertTrue(TestChecker.test(input, expect, 530))

    def test_531(self):
        input = """type A struct {
            a int
        }
        type B interface {
            get(x int) int
        }
        func (a A) get() int {
            return a.a
        }
        var a B = A{ a: 1 }
        var b B = a
        """
        expect = """Type Mismatch: VarDecl(a,Id(B),StructLiteral(A,[(a,IntLiteral(1))]))\n"""
        self.assertTrue(TestChecker.test(input, expect, 531))
    
    def test_532(self):
        input = """type A struct {
            a int
        }
        type B interface {
            get(x float) int
        }
        func (a A) get(x int) int {
            return a.a
        }
        var a B = A{ a: 1 }
        var b B = a
        """
        expect = """Type Mismatch: VarDecl(a,Id(B),StructLiteral(A,[(a,IntLiteral(1))]))\n"""
        self.assertTrue(TestChecker.test(input, expect, 532))

    def test_533(self):
        input = """type A struct {
            a int
        }
        type B interface {
            get(x int) int
        }
        func (a A) get(x int) float {
            return a.a
        }
        var a B = A{ a: 1 }
        var b B = a
        """
        expect = """Type Mismatch: Return(FieldAccess(Id(a),a))\n"""
        self.assertTrue(TestChecker.test(input, expect, 533))

    def test_534(self):
        input = """type A struct {
            a int
        }
        type B struct {
            a float
        }
        var a B = A{ a: 1 }
        var b B = a
        """
        expect = """Type Mismatch: VarDecl(a,Id(B),StructLiteral(A,[(a,IntLiteral(1))]))\n"""
        self.assertTrue(TestChecker.test(input, expect, 534))

    def test_535(self): # Note: HMMMMM
        input = """
func main() {
    a[123] := 10;
}
"""
        expect = """Undeclared Identifier: a\n"""
        self.assertTrue(TestChecker.test(input, expect, 535))

    def test_536(self):
        input = """
type A struct {
            a int
        }
func (a A) get() int {
    return a.a
}
func (a A) get() int {
    return a.a
}
"""
        expect = """Redeclared Method: get\n"""
        self.assertTrue(TestChecker.test(input, expect, 536))

#     def test_537(self): # Note: HMMM
#         input = """
#         func (a A) get() int {
#             return a.a
#         }
# """
#         expect = """Type Mismatch: MethodDecl(a,Id(A),FuncDecl(get,[],IntType,Block([Return(FieldAccess(Id(a),a))])))\n"""
#         self.assertTrue(TestChecker.test(input, expect, 537))
    
    def test_538(self):
        input = """
func aaa() int {
    return 123
}
type aaa interface {
    a() int
}
"""
        expect = """Redeclared Type: aaa\n"""
        self.assertTrue(TestChecker.test(input, expect, 538))

#     def test_539(self):
#         input = """
#         func main() {
#             a := [2][3] int { {1,2,3},{1,2,3} };
#             a[0][0] := 1.2;
#         }
#         """ 
#         input = Program([
#             FuncDecl(
#                 "main",
#                 [],                     # no parameters
#                 VoidType(),
#                 Block([
#                     # a := [2][3]int { {1,2,3}, {1,2,3} }
#                     VarDecl(
#                         "a",
#                         None,
#                         ArrayLiteral(
#                             [IntLiteral(2), IntLiteral(3)],
#                             IntType(),
#                             [
#                                 [IntLiteral(1), IntLiteral(2), IntLiteral(3)],
#                                 [IntLiteral(1), IntLiteral(2), IntLiteral(3)]
#                             ]
#                         )
#                     ),
#                     # a[0][0] := 1.2
#                     Assign(
#                         ArrayCell(
#                             ArrayCell(Id("a"), [IntLiteral(0)]),
#                             [IntLiteral(0)]
#                         ),
#                         FloatLiteral(1.2)
#                     )
#                 ])
#             )
#         ])

#         expect = """Type Mismatch: Assign(ArrayCell(Id(a),[IntLiteral(0),IntLiteral(0)]),FloatLiteral(1.2))\n"""
#         "Type Mismatch: Assign(ArrayCell(ArrayCell(Id(a),[IntLiteral(0)]),[IntLiteral(0)]),FloatLiteral(1.2))
# "
#         self.assertTrue(TestChecker.test(input, expect, 539))

    def test_540(self):
        input = """
func main() {
    for true {
        break;
    }
}
"""
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 540))

    def test_541(self):
        input = """
func main() {
    for true {
        break;
    }
    return 1;
}
"""
        expect = """Type Mismatch: Return(IntLiteral(1))\n"""
        self.assertTrue(TestChecker.test(input, expect, 541))

    def test_542(self):
        input = """
func a() {
    return;
}
func main() int {
    return a()+1;
}
"""
        expect = """Type Mismatch: FuncCall(a,[])\n"""
        self.assertTrue(TestChecker.test(input, expect, 542))

    def test_543(self):
        input = """
func a() {
    return;
}
func main() int {
    return 1*a();
}
"""
        expect = """Type Mismatch: FuncCall(a,[])\n"""
        self.assertTrue(TestChecker.test(input, expect, 543))
    
    def test_544(self):
        input = """
func a() {
    return;
}
func main() int {
    return a()||true;
}
"""
        expect = """Type Mismatch: FuncCall(a,[])\n"""
        self.assertTrue(TestChecker.test(input, expect, 544))

    def test_545(self):
        input = """
func a() {
    return;
}
func main() int {
    return false&&a();
}
"""
        expect = """Type Mismatch: FuncCall(a,[])\n"""
        self.assertTrue(TestChecker.test(input, expect, 545))

    def test_546(self):
        input = """
func main() boolean {
    return false + true;
}
"""
        expect = """Type Mismatch: BinaryOp(BooleanLiteral(false),+,BooleanLiteral(true))\n"""
        self.assertTrue(TestChecker.test(input, expect, 546))

    def test_547(self):
        input = """
func main() string {
    return "false" - "true";
}
"""
        expect = """Type Mismatch: BinaryOp(StringLiteral("false"),-,StringLiteral("true"))\n"""
        self.assertTrue(TestChecker.test(input, expect, 547))


    def test_548(self):
        input = """
func main() int {
    return -main();
}
"""
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 548))

    def test_549(self):
        input = """
func main() int {
    return -"main()";
}
"""
        expect = """Type Mismatch: UnaryOp(-,StringLiteral("main()"))\n"""
        self.assertTrue(TestChecker.test(input, expect, 549))
    
    def test_550(self):
        input = """
func main() boolean {
    return !"main()";
}
"""
        expect = """Type Mismatch: UnaryOp(!,StringLiteral("main()"))\n"""
        self.assertTrue(TestChecker.test(input, expect, 550))

    def test_551(self):
        input = """
func main() string {
    return "false" % "true";
}
"""
        expect = """Type Mismatch: BinaryOp(StringLiteral("false"),%,StringLiteral("true"))\n"""
        self.assertTrue(TestChecker.test(input, expect, 551))

    def test_552(self):
        input = """
var x = 1 || true;
"""
        expect = """Type Mismatch: BinaryOp(IntLiteral(1),||,BooleanLiteral(true))\n"""
        self.assertTrue(TestChecker.test(input, expect, 552))

    def test_553(self):
        input = """
var x = false && 1;
"""
        expect = """Type Mismatch: BinaryOp(BooleanLiteral(false),&&,IntLiteral(1))\n"""
        self.assertTrue(TestChecker.test(input, expect, 553))

    def test_554(self):
        input = """
type A struct {
    a int
}
type B interface {
    get() int
}
func (a A) get() int {
    return a.a
}
func main() {
    a:="hello"
    a:="hello"
    var b B = A { a: 12 }
    b :=  A { a: 12 }
}
"""
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 554))

    def test_555(self):
        input = """
type A struct {
    a int
}
type B interface {
    get(x int) int
}
func (a A) get(x int) int {
    return a.a
}
func main() {
    var b B = A { a: 12 }
    b :=  A { a: 12 }
    x := b.get(1, 2)
}
"""
        expect = """Type Mismatch: MethodCall(Id(b),get,[IntLiteral(1),IntLiteral(2)])\n"""
        self.assertTrue(TestChecker.test(input, expect, 555))

    def test_556(self):
        input = """
type A struct {
    a int
}
type B interface {
    get(x int) int
}
func (a A) get(x int) int {
    return a.a
}
func main() {
    var b B = A { a: 12 }
    b :=  A { a: 12 }
    x := b.get(1.2)
}
"""
        expect = """Type Mismatch: MethodCall(Id(b),get,[FloatLiteral(1.2)])\n"""
        self.assertTrue(TestChecker.test(input, expect, 556))

#     def test_556(self):
#         input = """
# func main() {
#     const x = 10.1
#     a := [12][10]int { {1,2,3} };
#     a[x][0] := 1.2
# }
# """
#         expect = """Type Mismatch: ArrayCell(Id(a),[Id(x),IntLiteral(0)])\n"""
#         self.assertTrue(TestChecker.test(input, expect, 556))

    def test_557(self):
        input = """

var a = A { a: 12 };
var b = a.a;
type A struct {
    a int
}
"""
        expect = """"""
        self.assertTrue(TestChecker.test(input, expect, 557))

    def test_558(self):
        input = """

        func a() {
            return
        }
        var x = !a();
"""
        expect = """Type Mismatch: FuncCall(a,[])\n"""
        self.assertTrue(TestChecker.test(input, expect, 558))

    def test_559(self):
        input = """
func a() int {
    return
}
"""
        expect = """Type Mismatch: Return()\n"""
        self.assertTrue(TestChecker.test(input, expect, 559))  