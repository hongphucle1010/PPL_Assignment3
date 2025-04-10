"""
* @author nhphung
"""

from AST import *
from AST import Prototype as AST_Prototype
from Visitor import *
from Utils import Utils
from StaticError import *
from functools import reduce


class MType:
    def __init__(self, partype: List[Type], rettype: Type):
        self.partype = partype
        self.rettype = rettype

    def __str__(self):
        return (
            "MType(["
            + ",".join(str(x) for x in self.partype)
            + "],"
            + str(self.rettype)
            + ")"
        )


class Symbol:
    def __init__(self, name, mtype: Union[Type, MType], value=None):
        self.name = name
        self.mtype = mtype
        self.value = value

    def __str__(self):
        return (
            "Symbol("
            + str(self.name)
            + ","
            + str(self.mtype)
            + ("" if self.value is None else "," + str(self.value))
            + ")"
        )


class StaticChecker(BaseVisitor, Utils):

    def __init__(self, ast):
        self.haveNotGotEntireProgramTypes = (
            True  # This is used to check if scan for the first or second time
        )
        self.ast = ast
        self.struct: dict[str, StructType] = {}
        self.interface: dict[str, InterfaceType] = {}
        self.global_envi = [
            [
                Symbol("getInt", MType([], IntType())),
                Symbol("putInt", MType([IntType()], VoidType())),
                Symbol("putIntLn", MType([IntType()], VoidType())),
                Symbol("getFloat", MType([], FloatType())),
                Symbol("putFloat", MType([FloatType()], VoidType())),
                Symbol("putFloatLn", MType([FloatType()], VoidType())),
                Symbol("getBool", MType([], BoolType())),
                Symbol("putBool", MType([BoolType()], VoidType())),
                Symbol("putBoolLn", MType([BoolType()], VoidType())),
                Symbol("getString", MType([], StringType())),
                Symbol("putString", MType([StringType()], VoidType())),
                Symbol("putStringLn", MType([StringType()], VoidType())),
                Symbol("putLn", MType([], VoidType())),
            ]
        ]
        self.function_current: FuncDecl = None
        self.struct_current: StructType = None

    def check(self):
        return self.visit(self.ast, self.global_envi)

    def getIdValue(self, id: Id, c: List[List[Symbol]]):
        for scope in c:
            for symbol in scope:
                if symbol.name == id.name:
                    return symbol.value
        raise Undeclared(Identifier(), id.name)

    def evaluate(self, ast: AST, c: List[List[Symbol]]):
        if isinstance(ast, (IntLiteral, FloatLiteral, BooleanLiteral, StringLiteral)):
            return ast.value
        if isinstance(ast, Id):
            return self.getIdValue(ast, c)
        if isinstance(ast, UnaryOp):
            if ast.op == "-":
                body = self.evaluate(ast.body, c)
                if isinstance(body, (int, float)):
                    return -body
                else:
                    # TODO TypeMismatch
                    pass
            elif ast.op == "!":
                body = self.evaluate(ast.body, c)
                if isinstance(body, bool):
                    return not body
                else:
                    # TODO TypeMismatch
                    pass
        if isinstance(ast, BinaryOp):
            left = self.evaluate(ast.left, c)
            right = self.evaluate(ast.right, c)
            if ast.op == "+":
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    return left + right
                elif isinstance(left, str) and isinstance(right, str):
                    return left + right
                else:
                    # TODO TypeMismatch
                    pass
            elif ast.op in ["-", "*", "/"]:
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    if ast.op == "-":
                        return left - right
                    elif ast.op == "*":
                        return left * right
                    else:
                        if right != 0:
                            return left / right
                else:
                    # TODO TypeMismatch
                    pass
            elif ast.op == "%":
                if isinstance(left, int) and isinstance(right, int):
                    return left % right
                else:
                    # TODO TypeMismatch
                    pass
            elif ast.op in ["==", ">", "<", ">=", "<=", "!="]:
                if type(left) == type(right):
                    if ast.op == "==":
                        return left == right
                    elif ast.op == ">":
                        return left > right
                    elif ast.op == "<":
                        return left < right
                    elif ast.op == ">=":
                        return left >= right
                    elif ast.op == "<=":
                        return left <= right
                    else:
                        return left != right
                else:
                    # TODO TypeMismatch
                    pass
            elif ast.op in ["&&", "||"]:
                if isinstance(left, bool) and isinstance(right, bool):
                    if ast.op == "&&":
                        return left and right
                    else:
                        return left or right
                else:
                    # TODO TypeMismatch
                    pass
            return None

    def visitProgram(self, ast: Program, c: List[List[Symbol]]):
        # First loop: Check redeclare
        reduce(
            lambda acc, ele: (
                [[self.visit(ele, acc)] + acc[0]] + acc[1:]
                if not isinstance(ele, MethodDecl)
                else (self.visit(ele, acc), acc)[
                    1
                ]  # Visit MethodDecl but keep acc unchanged
            ),
            ast.decl,
            c,
        )

        self.haveNotGotEntireProgramTypes = False

        # Second loop: Check Struct field / Interface prototype decls, RHS, Func/Method params, and body
        reduce(
            lambda acc, ele: (
                [[self.visit(ele, acc)] + acc[0]] + acc[1:]
                if not isinstance(ele, MethodDecl)
                else (self.visit(ele, acc), acc)[1]
            ),
            ast.decl,
            c,
        )

        return c

    def visitParamDecl(self, ast: ParamDecl, c: List[List[Symbol]]) -> Symbol:
        # TODO Redeclared ParamDecl
        res = self.lookup(ast.parName, c[0], lambda x: x.name)
        if not res is None:
            raise Redeclared(Parameter(), ast.parName)
        return Symbol(ast.parName, ast.parType, None)

    def visitVarDecl(self, ast: VarDecl, c: List[List[Symbol]]) -> Symbol:
        # TODO Redeclared Variable
        res = self.lookup(ast.varName, c[0], lambda x: x.name)
        if not res is None:
            raise Redeclared(Variable(), ast.varName)
        if not self.haveNotGotEntireProgramTypes:
            # Check RHS
            pass
        return Symbol(ast.varName, ast.varType, ast.varInit)

    def visitConstDecl(self, ast: ConstDecl, c: List[List[Symbol]]) -> Symbol:
        # TODO Redeclared Constant
        res = self.lookup(ast.conName, c[0], lambda x: x.name)
        if not res is None:
            raise Redeclared(Constant(), ast.conName)
        if not self.haveNotGotEntireProgramTypes:
            # Check RHS
            pass
        return Symbol(ast.conName, ast.conType, ast.iniExpr)

    def visitFuncDecl(self, ast: FuncDecl, c: List[List[Symbol]]) -> Symbol:
        if self.haveNotGotEntireProgramTypes:
            res = self.lookup(ast.name, c[0], lambda x: x.name)
            if not res is None:
                raise Redeclared(Function(), ast.name)
            self.global_envi[0].append(
                Symbol(
                    ast.name, MType([type.parType for type in ast.params], ast.retType)
                )
            )
        else:
            # Check Funct params and its body
            params_scope = reduce(
                lambda acc, ele: [[self.visit(ele, acc)] + acc[0]] + acc[1:],
                ast.params,
                [[]] + c,
            )
            # Check Function body
            reduce(
                lambda acc, ele: [[self.visit(ele, acc)] + acc[0]] + acc[1:],
                ast.body.member,
                [[]] + params_scope,
            )
        return Symbol(
            ast.name, MType([type.parType for type in ast.params], ast.retType)
        )

    def visitStructType(self, ast: StructType, c) -> Symbol:
        # TODO Redeclared Field
        if self.haveNotGotEntireProgramTypes:
            res = self.lookup(ast.name, c[0], lambda x: x.name)
            if not res is None:
                raise Redeclared(StructType(), ast.name)

            # Check if the struct is already declared (It means not redeclared but a method is associated with it)
            struct = self.struct.get(ast.name)
            if struct is None:
                struct = self.struct[ast.name] = ast

            self.global_envi[0].append(Symbol(ast.name, ast, None))
            fields = []
            for field_name, field_type in ast.elements:
                res = self.lookup(
                    field_name,
                    struct.methods + fields,
                    lambda x: x.fun.name if isinstance(x, MethodDecl) else x.name,
                )
                if not res is None:
                    raise Redeclared(Field(), field_name)
                fields.append(Symbol(field_name, field_type))
            struct.fields = fields
        return Symbol(ast.name, ast, None)

    def visitMethodDecl(self, ast: MethodDecl, c: List[List[Symbol]]) -> Symbol:
        # TODO Redeclared Method
        if self.haveNotGotEntireProgramTypes:
            # Find the struct object in the self.struct list
            struct = self.struct.get(ast.recType.name)
            if struct is None:
                struct = StructType(ast.recType.name, [], [])
                self.struct[ast.recType.name] = struct

            res = self.lookup(
                ast.fun.name,
                struct.methods + struct.elements,
                lambda x: x.fun.name if isinstance(x, MethodDecl) else x.name,
            )
            if not res is None:
                raise Redeclared(Method(), ast.fun.name)
            struct.methods.append(ast)
        else:
            # Check Method params and its body
            params_scope = reduce(
                lambda acc, ele: [[self.visit(ele, acc)] + acc[0]] + acc[1:],
                ast.fun.params,
                [[]] + c,
            )

            # Check Method body
            reduce(
                lambda acc, ele: [[self.visit(ele, acc)] + acc[0]] + acc[1:],
                ast.fun.body.member,
                [[]] + params_scope,
            )

        # return ast
        return Symbol(
            ast.fun.name,
            MType([type.parType for type in ast.fun.params], ast.fun.retType),
        )

    def visitPrototype(self, ast: AST_Prototype, c: List[List[Symbol]]) -> Symbol:
        # TODO Redeclared Prototype
        res = self.lookup(ast.name, c[0], lambda x: x.name)
        if not res is None:
            raise Redeclared(Prototype(), ast.name)
        return Symbol(ast.name, MType(ast.params, ast.retType))

    def visitInterfaceType(self, ast: InterfaceType, c) -> InterfaceType:
        # reduce(lambda acc, ele: [self.visit(ele, acc)] + acc, ast.methods, [])
        # return ast
        if self.haveNotGotEntireProgramTypes:
            res = self.lookup(ast.name, c[0], lambda x: x.name)
            if not res is None:
                raise Redeclared(InterfaceType(), ast.name)
            self.interface[ast.name] = ast
            self.global_envi[0].append(Symbol(ast.name, ast, None))
        else:
            # Check Interface Methods
            reduce(
                lambda acc, ele: [[self.visit(ele, acc)] + acc[0]] + acc[1:],
                ast.methods,
                [[]] + c,
            )
        return Symbol(ast.name, ast, None)

    def visitForBasic(self, ast: ForBasic, c: List[List[Symbol]]) -> None:
        #
        self.visit(ast.cond, c)
        self.visit(ast.loop, c)
        return None

    def visitForStep(self, ast: ForStep, c: List[List[Symbol]]) -> None:
        self.visit(Block([ast.init] + ast.loop.member + [ast.upda]), c)

    def visitForEach(self, ast: ForEach, c: List[List[Symbol]]) -> None:
        arr: Type = self.visit(ast.arr, c)
        self.visit(
            ast.loop,
            [[Symbol(ast.idx.name, IntType()), Symbol(ast.idx.name, arr)] + c[0]]
            + c[1:],
        )

    def visitBlock(self, ast: Block, c: List[List[Symbol]]) -> None:
        reduce(
            lambda acc, ele: [[self.visit(ele, acc)] + acc[0]] + acc[1:],
            ast.member,
            [[]] + c,
        )

    #! ----------- TASK 2 AND 3 ---------------------
    def visitIf(self, ast, c):
        return None

    def visitIntType(self, ast, c):
        return IntType()

    def visitFloatType(self, ast, c):
        return FloatType()

    def visitBoolType(self, ast, c):
        return BoolType()

    def visitStringType(self, ast, c):
        return StringType()

    def visitVoidType(self, ast, c):
        return VoidType()

    def visitArrayType(self, ast, c):
        return ArrayType(ast.dimensions, ast.eleType)

    def visitAssign(self, ast, c):
        return None

    def visitContinue(self, ast, c):
        return VoidType()

    def visitBreak(self, ast, c):
        return VoidType()

    def visitReturn(self, ast, c):
        return VoidType()

    def visitBinaryOp(self, ast: BinaryOp, c):
        return 

    def visitUnaryOp(self, ast, c):
        return None

    def visitFuncCall(self, ast: FuncCall, c: List[List[Symbol]]):
        for scope in c:
            for symbol in scope:
                # Process the function call
                if symbol.name == ast.name:
                    # TODO: TypeMismatch
                    pass
        raise Undeclared(Function(), ast.name)

    def visitMethCall(self, ast: MethCall, c: List[List[Symbol]]):
        receiver = self.visit(ast.receiver, c)
        if not isinstance(receiver, StructType):
            # TODO: TypeMismatch
            pass
        struct = self.struct.get(receiver.name)
        if struct is None:
            pass
        for method in struct.methods:
            if ast.metName == method.fun.name:
                return method.fun.retType
        raise Undeclared(Method(), ast.metName)
        
        
    def visitId(self, ast: Id, c: List[List[Symbol]]):
        for scope in c:
            for symbol in scope:
                if symbol.name == id.name:
                    return symbol.mtype
        raise Undeclared(Identifier(), ast.name)

    def visitArrayCell(self, ast, c):
        return None

    def visitFieldAccess(self, ast: FieldAccess, c: List[List[Symbol]]):
        receiver = self.visit(ast.receiver, c)
        if not isinstance(receiver, StructType):
            # TODO: TypeMismatch
            pass
        struct = self.struct.get(receiver.name)
        if struct is None:
            pass
        for field_name, field_type in struct.elements:
            if ast.field == field_name:
                return field_type
        raise Undeclared(Field(), ast.field)

    def visitIntLiteral(self, ast: IntLiteral, c):
        return IntType()

    def visitFloatLiteral(self, ast: FloatLiteral, c):
        return FloatType()

    def visitBooleanLiteral(self, ast: BooleanLiteral, c):
        return BoolType()

    def visitStringLiteral(self, ast: StringLiteral, c):
        return StringType()

    def visitArrayLiteral(self, ast: ArrayLiteral, c):
        return None

    def visitStructLiteral(self, ast: StructLiteral, c):
        return None

    def visitNilLiteral(self, ast: NilLiteral, c):
        return None
