"""
* @author nhphung
"""

from AST import *
from AST import Prototype as AST_Prototype
from Visitor import *
from Utils import Utils
from StaticError import *
from functools import reduce

import logging


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
    def __init__(self, name, mtype: Union[Type, MType, "Symbol"], value=None):
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
        # logging.basicConfig(
        #     level=logging.DEBUG,
        #     format="%(relativeCreated)dms - %(levelname)s - %(message)s",
        # )

        self.haveNotGotEntireProgramTypes = (
            True  # This is used to check if scan for the first or second time
        )
        self.ast = ast
        self.struct: dict[str, StructType] = {}
        self.function_current: FuncDecl = None
        # self.global_envi: List[List[Symbol]] = [[]]
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

    def check(self):
        return self.visit(self.ast, self.global_envi)

    def look_scope(self, c: List[List[Symbol]]):
        [print(symbol.name) for scope in c for symbol in scope]

    @staticmethod
    def addToScope(c: List[List[Symbol]], symbol: Symbol):
        logging.debug(f"Adding to scope: {symbol.name}")
        return [[symbol] + c[0]] + c[1:]

    def getIdValue(self, id: Id, c: List[List[Symbol]]):
        logging.debug(f"Getting Id value: {id.name}")
        for scope in c:
            for symbol in scope:
                if symbol.name == id.name:
                    return symbol.value
        return None

    def visitStatement(self, ast: AST, c: List[List[Symbol]]):
        if isinstance(ast, (FuncCall, MethCall)):
            res = self.visit(ast, c)
            if not (res is None or isinstance(res, VoidType)):
                raise TypeMismatch(ast)
            return c
        elif isinstance(ast, (VarDecl, ConstDecl)):
            return StaticChecker.addToScope(c, self.visit(ast, c))
        elif isinstance(ast, Assign):
            lhs = ast.lhs
            if isinstance(lhs, Id):
                declared = False
                for scope in c:
                    for symbol in scope:
                        if symbol.name == lhs.name:
                            declared = True
                if declared:
                    self.visit(ast, c)
                    return c
                else:
                    varDecl = VarDecl(lhs.name, None, ast.rhs)
                    return StaticChecker.addToScope(c, self.visit(varDecl, c))
            else:
                self.visit(ast, c)
                return c
        else:
            self.visit(ast, c)
            return c

    def evaluate(self, ast: AST, c: List[List[Symbol]]):
        logging.debug(f"Evaluating: {ast}")
        logging.debug(f"Evaluating type: {type(ast)}")
        self.visit(
            ast, c
        )  # Visit for the only purpose: Checking if valid for evaluation
        if isinstance(ast, (IntLiteral, FloatLiteral, BooleanLiteral, StringLiteral)):
            return ast.value
        elif isinstance(ast, Id):
            return self.getIdValue(ast, c)
        elif isinstance(ast, UnaryOp):
            if ast.op == "-":
                body = self.evaluate(ast.body, c)
                if isinstance(body, (int, float)):
                    return -body
                else:
                    return None
            elif ast.op == "!":
                body = self.evaluate(ast.body, c)
                if isinstance(body, bool):
                    return not body
                else:
                    return None
        elif isinstance(ast, BinaryOp):
            left = self.evaluate(ast.left, c)
            right = self.evaluate(ast.right, c)
            if ast.op == "+":
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    return left + right
                elif isinstance(left, str) and isinstance(right, str):
                    return left + right
                else:
                    return None
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
                    return None
            elif ast.op == "%":
                if isinstance(left, int) and isinstance(right, int):
                    return left % right
                else:
                    return None
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
                    return None
            elif ast.op in ["&&", "||"]:
                if isinstance(left, bool) and isinstance(right, bool):
                    if ast.op == "&&":
                        return left and right
                    else:
                        return left or right
                else:
                    return None
            return None
        else:
            return None

    def visitProgram(self, ast: Program, c: List[List[Symbol]]):
        logging.debug("=" * 40)
        logging.debug("Visiting Program")
        # First loop: Check redeclare
        tmp_c = c
        for decl in ast.decl:
            if isinstance(decl, (StructType, InterfaceType)):
                type = self.visit(decl, tmp_c)
                tmp_c = StaticChecker.addToScope(tmp_c, Symbol(type.name, type, None))
            elif isinstance(decl, MethodDecl):
                self.visit(decl, tmp_c)
            else:
                tmp_c = StaticChecker.addToScope(tmp_c, self.visit(decl, tmp_c))

        self.haveNotGotEntireProgramTypes = False
        logging.debug("Enabling second pass")

        # Second loop: Check Struct field / Interface prototype decls, RHS, Func/Method params, and body
        tmp_c = c
        for decl in ast.decl:
            if isinstance(decl, (StructType, InterfaceType)):
                self.visit(decl, tmp_c)
            elif isinstance(decl, MethodDecl):
                self.visit(decl, tmp_c)
            else:
                tmp_c = StaticChecker.addToScope(tmp_c, self.visit(decl, tmp_c))

        return c

    def visitParamDecl(self, ast: ParamDecl, c: List[List[Symbol]]) -> Symbol:
        logging.debug("=" * 40)
        logging.debug(f"Visiting ParamDecl: {ast.parName}")
        # TODO Redeclared ParamDecl
        res = self.lookup(ast.parName, c[0], lambda x: x.name)
        if not res is None:
            logging.debug(f"Redeclared Parameter: {ast.parName}")
            raise Redeclared(Parameter(), ast.parName)
        return Symbol(ast.parName, self.visit(ast.parType, c), None)

    def visitVarDecl(self, ast: VarDecl, c: List[List[Symbol]]) -> Symbol:
        logging.debug("=" * 40)
        logging.debug(f"Visiting VarDecl: {ast.varName}")
        # TODO Redeclared Variable
        res = self.lookup(ast.varName, c[0], lambda x: x.name)
        if not res is None:
            logging.debug(f"Redeclared Variable: {ast.varName}")
            raise Redeclared(Variable(), ast.varName)
        if not self.haveNotGotEntireProgramTypes:
            # Check RHS
            if ast.varInit is not None:  # ← guard
                # val = self.evaluate(ast.varInit, c)
                rhs_type = self.visit(ast.varInit, c)
                if rhs_type is None:
                    return Symbol(ast.varName, self.visit(rhs_type, c), None)
                if isinstance(rhs_type, VoidType):
                    raise TypeMismatch(ast)
                if ast.varType is None:
                    return Symbol(ast.varName, self.visit(rhs_type, c), None)
                if type(rhs_type) != type(ast.varType):
                    # TODO TypeMismatch
                    if isinstance(rhs_type, IntType) and isinstance(
                        ast.varType, FloatType
                    ):
                        # Implicit conversion
                        return Symbol(ast.varName, self.visit(ast.varType, c), None)
                    if isinstance(rhs_type, StructType) and isinstance(
                        ast.varType, InterfaceType
                    ):
                        # Implicit conversion
                        return Symbol(ast.varName, self.visit(ast.varType, c), None)
                    logging.debug(f"Type mismatch: {rhs_type} != {ast.varType}")
                    raise TypeMismatch(ast)
                elif isinstance(rhs_type, ArrayType):
                    if rhs_type.eleType != ast.varType.eleType:
                        raise TypeMismatch(ast)
                    if len(rhs_type.dimens) != len(ast.varType.dimens):
                        raise TypeMismatch(ast)
                    for i in range(len(rhs_type.dimens)):
                        if self.evaluate(rhs_type.dimens[i], c) != self.evaluate(
                            ast.varType.dimens[i], c
                        ):
                            raise TypeMismatch(ast)
                elif isinstance(rhs_type, StructType):
                    if rhs_type.name != ast.varType.name:
                        raise TypeMismatch(ast)
                return Symbol(ast.varName, self.visit(ast.varType, c), None)
            else:
                return Symbol(ast.varName, self.visit(ast.varType, c), None)
        return Symbol(ast.varName, ast.varType, None)

    def visitConstDecl(self, ast: ConstDecl, c: List[List[Symbol]]) -> Symbol:
        logging.debug("=" * 40)
        logging.debug(f"Visiting ConstDecl: {ast.conName}")
        # TODO Redeclared Constant
        res = self.lookup(ast.conName, c[0], lambda x: x.name)
        if not res is None:
            logging.debug(f"Redeclared Constant: {ast.conName}")
            raise Redeclared(Constant(), ast.conName)
        if not self.haveNotGotEntireProgramTypes:
            # Check RHS
            if ast.iniExpr is not None:  # ← guard
                val = self.evaluate(ast.iniExpr, c)
                type = self.visit(ast.iniExpr, c)
                return Symbol(ast.conName, self.visit(type, c), val)
        return Symbol(ast.conName, ast.conType, ast.iniExpr)

    def visitFuncDecl(self, ast: FuncDecl, c: List[List[Symbol]]) -> Symbol:
        logging.debug("=" * 40)
        logging.debug(f"Visiting FuncDecl: {ast.name}")

        self.function_current = ast

        if self.haveNotGotEntireProgramTypes:
            res = self.lookup(ast.name, c[0], lambda x: x.name)
            if not res is None:
                raise Redeclared(Function(), ast.name)
            self.global_envi[0].append(
                Symbol(
                    ast.name,
                    MType(
                        [self.visit(type.parType, c) for type in ast.params],
                        self.visit(ast.retType, c),
                    ),
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
            self.visit(ast.body, params_scope)
            # for member in ast.body.member:
            #     if isinstance(member, (FuncCall, MethCall)):
            #         res = self.visit(member, params_scope)
            #         if not (res is None or isinstance(res, VoidType)):
            #             raise TypeMismatch(member)
            #     elif isinstance(member, Return):
            #         res = self.visit(member, params_scope)
            #         if type(res) != type(ast.retType):
            #             raise TypeMismatch(member)
            #     else:
            #         self.visit(member, params_scope)
        return Symbol(
            ast.name,
            MType(
                [self.visit(type.parType, c) for type in ast.params],
                self.visit(ast.retType, c),
            ),
        )

    def visitStructType(self, ast: StructType, c) -> Symbol:
        logging.debug("=" * 40)
        logging.debug(f"Visiting StructType: {ast.name}")
        # TODO Redeclared Field
        if self.haveNotGotEntireProgramTypes:
            res = self.lookup(ast.name, c[0], lambda x: x.name)
            if not res is None:
                raise Redeclared(Type(), ast.name)

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
                fields.append(Symbol(field_name, self.visit(field_type, c)))
            struct.fields = fields
        return ast

    def visitMethodDecl(self, ast: MethodDecl, c: List[List[Symbol]]) -> Symbol:
        logging.debug("=" * 40)
        logging.debug(f"Visiting MethodDecl: {ast.fun.name}")

        self.function_current = ast.fun

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
                lambda x: x.fun.name if isinstance(x, MethodDecl) else x[0],
            )
            if not res is None:
                raise Redeclared(Method(), ast.fun.name)
            struct.methods.append(ast)
        else:
            # Check Method params and its body
            params_scope = reduce(
                lambda acc, ele: [[self.visit(ele, acc)] + acc[0]] + acc[1:],
                ast.fun.params,
                [[], [Symbol(ast.receiver, self.visit(ast.recType, c))]] + c,
            )
            # Check Method body
            self.visit(ast.fun.body, params_scope)
            # for member in ast.fun.body.member:
            #     if isinstance(member, (FuncCall, MethCall)):
            #         res = self.visit(member, params_scope)
            #         if not (res is None or isinstance(res, VoidType)):
            #             raise TypeMismatch(member)
            #     elif isinstance(member, Return):
            #         res = self.visit(member, params_scope)
            #         if type(res) != type(ast.fun.retType):
            #             raise TypeMismatch(member)
            #     else:
            #         self.visit(member, params_scope)

        # return ast
        return Symbol(
            ast.fun.name,
            MType(
                [self.visit(type.parType, c) for type in ast.fun.params],
                self.visit(ast.fun.retType, c),
            ),
        )

    def visitPrototype(self, ast: AST_Prototype, c: List[List[Symbol]]) -> Symbol:
        logging.debug("=" * 40)
        logging.debug(f"Visiting Prototype: {ast.name}")
        # TODO Redeclared Prototype
        res = self.lookup(ast.name, c[0], lambda x: x.name)
        if not res is None:
            raise Redeclared(Prototype(), ast.name)
        return Symbol(
            ast.name,
            MType(
                map(lambda p: self.visit(p, c), ast.params), self.visit(ast.retType, c)
            ),
        )

    def visitInterfaceType(self, ast: InterfaceType, c) -> InterfaceType:
        logging.debug("=" * 40)
        logging.debug(f"Visiting InterfaceType: {ast.name}")
        # reduce(lambda acc, ele: [self.visit(ele, acc)] + acc, ast.methods, [])
        # return ast
        if self.haveNotGotEntireProgramTypes:
            res = self.lookup(ast.name, c[0], lambda x: x.name)
            if not res is None:
                raise Redeclared(Type(), ast.name)
            self.global_envi[0].append(Symbol(ast.name, ast, None))
        else:
            # Check Interface Methods
            reduce(
                lambda acc, ele: [[self.visit(ele, acc)] + acc[0]] + acc[1:],
                ast.methods,
                [[]] + c,
            )
        return ast

    def visitForBasic(self, ast: ForBasic, c: List[List[Symbol]]) -> None:
        logging.debug("=" * 40)
        logging.debug("Visiting ForBasic")
        #
        expr = self.visit(ast.cond, c)
        if not isinstance(expr, BoolType):
            raise TypeMismatch(ast)
        self.visit(ast.loop, c)
        return None

    def visitForStep(self, ast: ForStep, c: List[List[Symbol]]) -> None:
        logging.debug("=" * 40)
        logging.debug("Visiting ForStep")
        new_c = [[]] + c

        # Check init
        new_c = self.visitStatement(ast.init, new_c)

        # Check condition
        cond: Type = self.visit(ast.cond, new_c)
        if not isinstance(cond, BoolType):
            raise TypeMismatch(ast)

        # Check update
        new_c = self.visitStatement(ast.upda, new_c)

        # Check loop
        reduce(
            lambda acc, ele: (
                StaticChecker.addToScope(acc, self.visit(ele, acc))
                if isinstance(ele, (VarDecl, ConstDecl))
                else (self.visit(ele, acc), acc)[1]
            ),
            ast.loop.member,
            new_c,
        )

    def visitForEach(self, ast: ForEach, c: List[List[Symbol]]) -> None:
        logging.debug("=" * 40)
        logging.debug(f"Visiting ForEach: {ast.idx.name}")

        idx = self.visit(ast.idx, c)
        if not isinstance(idx, IntType):
            raise TypeMismatch(ast)
        value = self.visit(ast.value, c)
        arr: Type = self.visit(ast.arr, c)
        if not isinstance(arr, ArrayType):
            raise TypeMismatch(ast)
        if not isinstance(value, arr.eleType):
            raise TypeMismatch(ast)
        self.visit(ast.loop, c)

    def visitBlock(self, ast: Block, c: List[List[Symbol]]) -> None:
        logging.debug("=" * 40)
        logging.debug("Visiting Block")

        new_c = [[]] + c

        for member in ast.member:
            new_c = self.visitStatement(member, new_c)

    #! ----------- TASK 2 AND 3 ---------------------
    def visitIf(self, ast: If, c):
        logging.debug("=" * 40)
        logging.debug("Visiting If")

        # Check condition
        expr = self.visit(ast.expr, c)
        if not isinstance(expr, BoolType):
            raise TypeMismatch(ast)

        self.visit(ast.thenStmt, c)
        if ast.elseStmt is not None:
            self.visit(ast.elseStmt, c)
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

    def visitArrayType(self, ast: ArrayType, c):
        for dim in ast.dimens:
            dim = self.visit(dim, c)
            if not isinstance(dim, IntType):
                raise TypeMismatch(ast)
        return ArrayType(ast.dimens, ast.eleType)

    def visitAssign(self, ast: Assign, c: List[List[Symbol]]):
        logging.debug("=" * 40)
        logging.debug("Visiting Assign")

        lhs: Type = self.visit(ast.lhs, c)
        rhs: Type = self.visit(ast.rhs, c)

        if isinstance(lhs, VoidType):
            logging.debug(f"Type mismatch in assignment: {ast}")
            raise TypeMismatch(ast)

        if isinstance(rhs, VoidType):
            raise TypeMismatch(ast)

        if type(lhs) != type(rhs):
            if isinstance(lhs, FloatType) and isinstance(rhs, IntType):
                return None
            if isinstance(lhs, InterfaceType) and isinstance(rhs, StructType):
                return None
            raise TypeMismatch(ast)
        else:
            if isinstance(lhs, ArrayType) and isinstance(rhs, ArrayType):
                if lhs.eleType != rhs.eleType:
                    raise TypeMismatch(ast)
                if len(lhs.dimens) != len(rhs.dimens):
                    raise TypeMismatch(ast)
                for i in range(len(lhs.dimens)):
                    if self.evaluate(lhs.dimens[i], c) != self.evaluate(
                        rhs.dimens[i], c
                    ):
                        raise TypeMismatch(ast)
        return c

    def visitContinue(self, ast, c):
        logging.debug("=" * 40)
        logging.debug("Visiting Continue")
        return VoidType()

    def visitBreak(self, ast: Break, c):
        logging.debug("=" * 40)
        logging.debug("Visiting Break")
        return VoidType()

    def visitReturn(self, ast: Return, c):
        logging.debug("=" * 40)
        logging.debug("Visiting Return")
        expr: Type = self.visit(ast.expr, c) if ast.expr else VoidType()
        if ast.expr is not None and isinstance(expr, VoidType):
            logging.debug(f"Type mismatch in return statement: {ast}")
            raise TypeMismatch(ast)

        if type(expr) != type(self.function_current.retType):
            raise TypeMismatch(ast)
        return expr

    def visitBinaryOp(self, ast: BinaryOp, c):
        logging.debug("=" * 40)
        logging.debug(f"Visiting BinaryOp: {ast.op}")

        lhs = self.visit(ast.left, c)
        if isinstance(lhs, VoidType):
            raise TypeMismatch(ast)
        rhs = self.visit(ast.right, c)
        if isinstance(rhs, VoidType):
            raise TypeMismatch(ast)

        if ast.op == "+":
            if isinstance(lhs, IntType) and isinstance(rhs, IntType):
                return IntType()
            elif isinstance(lhs, FloatType) and isinstance(rhs, FloatType):
                return FloatType()
            elif isinstance(lhs, StringType) and isinstance(rhs, StringType):
                return StringType()
            elif isinstance(lhs, IntType) and isinstance(rhs, FloatType):
                return FloatType()
            elif isinstance(lhs, FloatType) and isinstance(rhs, IntType):
                return FloatType()
            else:
                logging.debug(f"Type mismatch in binary operation: {ast}")
                raise TypeMismatch(ast)
        elif ast.op in ["-", "*", "/"]:
            if isinstance(lhs, IntType) and isinstance(rhs, IntType):
                return IntType()
            elif isinstance(lhs, FloatType) and isinstance(rhs, FloatType):
                return FloatType()
            elif isinstance(lhs, IntType) and isinstance(rhs, FloatType):
                return FloatType()
            elif isinstance(lhs, FloatType) and isinstance(rhs, IntType):
                return FloatType()
            else:
                logging.debug(f"Type mismatch in binary operation: {ast}")
                raise TypeMismatch(ast)
        elif ast.op == "%":
            if isinstance(lhs, IntType) and isinstance(rhs, IntType):
                return IntType()
            else:
                logging.debug(f"Type mismatch in binary operation: {ast}")
                raise TypeMismatch(ast)
        elif ast.op in ["==", ">", "<", ">=", "<=", "!="]:
            if type(lhs) == type(rhs):
                return BoolType()
            else:
                logging.debug(f"Type mismatch in binary operation: {ast}")
                raise TypeMismatch(ast)
        elif ast.op in ["&&", "||"]:
            if isinstance(lhs, BoolType) and isinstance(rhs, BoolType):
                return BoolType()
            else:
                logging.debug(f"Type mismatch in binary operation: {ast}")
                raise TypeMismatch(ast)
        return None

    def visitUnaryOp(self, ast: UnaryOp, c):
        logging.debug("=" * 40)
        logging.debug(f"Visiting UnaryOp: {ast.op}")
        body = self.visit(ast.body, c)
        if isinstance(body, VoidType):
            raise TypeMismatch(ast)
        if ast.op == "-":
            if isinstance(body, (IntType, FloatType)):
                return body
            else:
                logging.debug(f"Type mismatch in unary operation: {ast}")
                raise TypeMismatch(ast)
        elif ast.op == "!":
            if isinstance(body, BoolType):
                return BoolType()
            else:
                logging.debug(f"Type mismatch in unary operation: {ast}")
                raise TypeMismatch(ast)
        return None

    def visitFuncCall(self, ast: FuncCall, c: List[List[Symbol]]):
        logging.debug("=" * 40)
        logging.debug(f"Visiting FuncCall: {ast.funName}")

        # Check if the function id is declared
        func = self.lookup(ast.funName, c[-1], lambda x: x.name)
        if func is None:
            logging.debug(f"Undeclared Function: {ast.funName}")
            raise Undeclared(Function(), ast.funName)

        # Check if the function id is declared as a function
        if not isinstance(func.mtype, MType):
            raise Undeclared(Function(), ast.funName)

        # Check numbers of arguments
        if len(ast.args) != len(func.mtype.partype):
            logging.debug(f"Type mismatch in function call arguments: {ast}")
            raise TypeMismatch(ast)

        # Check types of each argument
        params = []
        for i in range(len(ast.args)):
            arg = self.visit(ast.args[i], c)
            if not type(arg) == type(func.mtype.partype[i]):
                raise TypeMismatch(ast)
            params.append(arg)

        return func.mtype.rettype

    def visitMethCall(self, ast: MethCall, c: List[List[Symbol]]):
        logging.debug("=" * 40)
        logging.debug(f"Visiting MethCall: {ast.metName}")

        # Get receiver type
        receiver: Type = self.visit(ast.receiver, c)
        if isinstance(receiver, StructType):
            for method in receiver.methods:
                if ast.metName == method.fun.name:
                    if len(ast.args) != len(method.fun.params):
                        logging.debug(f"Type mismatch in method call arguments: {ast}")
                        raise TypeMismatch(ast)

                    params = []
                    for i in range(len(ast.args)):
                        arg = self.visit(ast.args[i], c)
                        if not type(arg) == type(method.fun.params[i].parType):
                            raise TypeMismatch(ast)
                        params.append(arg)
                    return method.fun.retType
            logging.debug(f"Undeclared Method: {ast.metName}")
            raise Undeclared(Method(), ast.metName)
        elif isinstance(receiver, InterfaceType):
            for method in receiver.methods:
                if ast.metName == method.name:
                    if len(ast.args) != len(method.params):
                        logging.debug(f"Type mismatch in method call arguments: {ast}")
                        raise TypeMismatch(ast)
                    for i in range(len(ast.args)):
                        arg = self.visit(ast.args[i], c)
                        if not type(arg) == type(method.params[i]):
                            raise TypeMismatch(ast)
                    return method.retType
            logging.debug(f"Undeclared Method: {ast.metName}")
            raise Undeclared(Method(), ast.metName)
        else:
            logging.debug(f"Receiver type: {type(receiver)}")
            raise TypeMismatch(ast)

    def visitId(self, ast: Id, c: List[List[Symbol]]):
        logging.debug("=" * 40)
        logging.debug(f"Visiting Id: {ast.name}")

        for scope in c:
            for symbol in scope:
                if symbol.name == ast.name:
                    return symbol.mtype
        logging.debug(f"Undeclared Identifier: {ast.name}")
        raise Undeclared(Identifier(), ast.name)

    def visitArrayCell(self, ast: ArrayCell, c: List[List[Symbol]]):
        logging.debug("=" * 40)
        logging.debug("Visiting ArrayCell")

        array = self.visit(ast.arr, c)
        if not isinstance(array, ArrayType):
            logging.debug(f"Type mismatch in array access: {ast}")
            raise TypeMismatch(ast)
        accessIndex = []

        for i in ast.idx:
            type = self.visit(i, c)
            if not isinstance(type, IntType):
                raise TypeMismatch(ast)
            accessIndex.append(type)

        if len(array.dimens) < len(accessIndex):
            return ArrayType(
                array.dimens[len(accessIndex) :],
                array.eleType,
            )
        elif len(array.dimens) == len(accessIndex):
            return array.eleType
        else:
            raise TypeMismatch(ast)

    def visitFieldAccess(self, ast: FieldAccess, c: List[List[Symbol]]):
        logging.debug("=" * 40)
        logging.debug(f"Visiting FieldAccess: {ast.field}")
        receiver = self.visit(ast.receiver, c)
        if not isinstance(receiver, (StructType, InterfaceType)):
            logging.debug(f"Type mismatch in field access: {ast}. Receiver: {receiver}")
            raise TypeMismatch(ast)
        struct = self.struct.get(receiver.name)
        if struct is None:
            raise Undeclared(Type(), receiver.name)
        for field_name, field_type in struct.elements:
            if ast.field == field_name:
                return field_type
        logging.debug(f"Undeclared Field: {ast.field}")
        raise Undeclared(Field(), ast.field)

    def visitIntLiteral(self, ast: IntLiteral, c):
        logging.debug("=" * 40)
        logging.debug(f"Visiting IntLiteral: {ast.value}")
        return IntType()

    def visitFloatLiteral(self, ast: FloatLiteral, c):
        logging.debug("=" * 40)
        logging.debug(f"Visiting FloatLiteral: {ast.value}")
        return FloatType()

    def visitBooleanLiteral(self, ast: BooleanLiteral, c):
        logging.debug("=" * 40)
        logging.debug(f"Visiting BooleanLiteral: {ast.value}")
        return BoolType()

    def visitStringLiteral(self, ast: StringLiteral, c):
        logging.debug("=" * 40)
        logging.debug(f"Visiting StringLiteral: {ast.value}")
        return StringType()

    def visitArrayLiteral(self, ast: ArrayLiteral, c):
        logging.debug("=" * 40)
        logging.debug("Visiting ArrayLiteral")
        return ArrayType(ast.dimens, ast.eleType)

    def visitStructLiteral(self, ast: StructLiteral, c):
        logging.debug("=" * 40)
        logging.debug("Visiting StructLiteral")
        if self.struct.get(ast.name) is None:
            raise Undeclared(Type(), ast.name)
        return self.struct.get(ast.name)

    def visitNilLiteral(self, ast: NilLiteral, c):
        logging.debug("=" * 40)
        logging.debug("Visiting NilLiteral")
        return StructType("Nil", [], [])  
