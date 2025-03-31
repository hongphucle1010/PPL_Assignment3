from MiniGoVisitor import MiniGoVisitor
from MiniGoParser import MiniGoParser
from AST import *
from functools import reduce
from typing import List, Tuple, Any


class ASTGeneration(MiniGoVisitor):
    #! ------------------ Literal ------------------
    def visitLiteral(self, ctx: MiniGoParser.LiteralContext) -> Literal:
        if ctx.notArrayLiteral():
            return self.visitNotArrayLiteral(ctx.notArrayLiteral())
        if ctx.arrayLiteral():
            return self.visitArrayLiteral(ctx.arrayLiteral())
        assert False, "This should not be literal"

    def visitNotArrayLiteral(self, ctx: MiniGoParser.NotArrayLiteralContext) -> Literal:
        if ctx.integer():
            return self.visitInteger(ctx.integer())
        if ctx.FLOAT_LIT():
            return FloatLiteral(float(ctx.FLOAT_LIT().getText()))
        if ctx.STR_LIT():
            return StringLiteral(ctx.STR_LIT().getText())
        if ctx.TRUE() or ctx.FALSE():
            return BooleanLiteral(ctx.TRUE() != None)
        if ctx.NIL():
            return NilLiteral()
        if ctx.structLiteral():
            return self.visitStructLiteral(ctx.structLiteral())
        assert False, "This should not be notArrayLiteral"

    def visitInteger(self, ctx: MiniGoParser.IntegerContext) -> IntLiteral:
        if ctx.DEC_LIT():
            return IntLiteral(int(ctx.DEC_LIT().getText()))
        if ctx.HEX_LIT():
            return IntLiteral(int(ctx.HEX_LIT().getText(), 16))
        if ctx.OCT_LIT():
            return IntLiteral(int(ctx.OCT_LIT().getText(), 8))
        if ctx.BIN_LIT():
            return IntLiteral(int(ctx.BIN_LIT().getText(), 2))
        assert False, "This should not be integer"

    def visitStructLiteral(
        self, ctx: MiniGoParser.StructLiteralContext
    ) -> StructLiteral:
        struct_elements = (
            self.visitStructElements(ctx.structElements())
            if ctx.structElements()
            else []
        )
        return StructLiteral(ctx.ID().getText(), struct_elements)

    def visitStructElements(
        self, ctx: MiniGoParser.StructElementsContext
    ) -> List[Tuple[str, Expr]]:
        suffix = (
            self.visitStructElements(ctx.structElements())
            if ctx.structElements()
            else []
        )
        return [self.visit(ctx.structElement())] + suffix

    def visitStructElement(
        self, ctx: MiniGoParser.StructElementContext
    ) -> Tuple[str, Expr]:
        expression = self.visit(ctx.expression())
        return (ctx.ID().getText(), expression)

    def visitArrayLiteral(self, ctx: MiniGoParser.ArrayLiteralContext) -> ArrayLiteral:
        array_type: ArrayType = self.visit(ctx.arrayType())
        array_values = self.visit(ctx.arrayBody())
        return ArrayLiteral(array_type.dimens, array_type.eleType, array_values)

    def visitArrayType(self, ctx: MiniGoParser.ArrayTypeContext) -> ArrayType:
        if ctx.baseType():
            dim: List[Expr] = [self.visit(ctx.arrayDim())]
            type: Type = self.visit(ctx.baseType())
            return ArrayType(dim, type)
        if ctx.arrayType():
            dim: List[Expr] = [self.visit(ctx.arrayDim())]
            arrayType: ArrayType = self.visit(ctx.arrayType())
            dim += arrayType.dimens
            return ArrayType(dim, arrayType.eleType)
        assert False, "This should not be arrayType"

    def visitArrayDim(self, ctx: MiniGoParser.ArrayDimContext) -> Expr:
        if ctx.ID():
            return Id(ctx.ID().getText())
        return self.visit(ctx.integer())

    def visitBaseType(self, ctx: MiniGoParser.BaseTypeContext) -> Type:
        if ctx.primitiveType():
            return self.visit(ctx.primitiveType())
        return Id(ctx.ID().getText())

    def visitPrimitiveType(self, ctx: MiniGoParser.PrimitiveTypeContext) -> Type:
        if ctx.INT():
            return IntType()
        if ctx.FLOAT():
            return FloatType()
        if ctx.STRING():
            return StringType()
        if ctx.BOOLEAN():
            return BoolType()
        assert False, "This should not be primitiveType"

    def visitTypeSpec(self, ctx: MiniGoParser.TypeSpecContext) -> Type:
        if ctx.baseType():
            return self.visit(ctx.baseType())
        if ctx.arrayType():
            return self.visit(ctx.arrayType())
        assert False, "This should not be typeSpec"

    def visitArrayBody(self, ctx: MiniGoParser.ArrayBodyContext) -> List[Any]:
        return self.visit(ctx.arrayList())

    def visitArrayList(self, ctx: MiniGoParser.ArrayListContext) -> List[Any]:
        suffix: List[Any] = self.visit(ctx.arrayList()) if ctx.arrayList() else []
        return [self.visit(ctx.arrayMember())] + suffix

    def visitArrayMember(self, ctx: MiniGoParser.ArrayMemberContext) -> Any:
        if ctx.arrayBody():
            return self.visit(ctx.arrayBody())
        if ctx.ID():
            return Id(ctx.ID().getText())
        return self.visit(ctx.notArrayLiteral())

    #! ------------------ Expression ------------------
    def visitExprList(self, ctx: MiniGoParser.ExprListContext) -> List[Expr]:
        exprList: List[Expr] = self.visit(ctx.exprList()) if ctx.exprList() else []
        return [self.visit(ctx.expression())] + exprList

    def visitExpression(self, ctx: MiniGoParser.ExpressionContext) -> Expr:
        if ctx.expression():
            op = ctx.OR().getText()
            left = self.visit(ctx.expression())
            right = self.visit(ctx.expr1())
            return BinaryOp(op, left, right)
        return self.visit(ctx.expr1())

    def visitExpr1(self, ctx: MiniGoParser.Expr1Context) -> Expr:
        if ctx.expr1():
            op = ctx.AND().getText()
            left = self.visit(ctx.expr1())
            right = self.visit(ctx.expr2())
            return BinaryOp(op, left, right)
        return self.visit(ctx.expr2())

    def visitExpr2(self, ctx: MiniGoParser.Expr2Context) -> Expr:
        if ctx.expr2():
            op = self.visit(ctx.compOp())
            left = self.visit(ctx.expr2())
            right = self.visit(ctx.expr3())
            return BinaryOp(op, left, right)
        return self.visit(ctx.expr3())

    def visitCompOp(self, ctx: MiniGoParser.CompOpContext) -> str:
        return ctx.getText()

    def visitExpr3(self, ctx: MiniGoParser.Expr3Context) -> Expr:
        if ctx.expr3():
            op = self.visit(ctx.addOp())
            left = self.visit(ctx.expr3())
            right = self.visit(ctx.expr4())
            return BinaryOp(op, left, right)
        return self.visit(ctx.expr4())

    def visitAddOp(self, ctx: MiniGoParser.AddOpContext) -> str:
        return ctx.getText()

    def visitExpr4(self, ctx: MiniGoParser.Expr4Context) -> Expr:
        if ctx.expr4():
            op = self.visit(ctx.mulOp())
            left = self.visit(ctx.expr4())
            right = self.visit(ctx.expr5())
            return BinaryOp(op, left, right)
        return self.visit(ctx.expr5())

    def visitMulOp(self, ctx: MiniGoParser.MulOpContext) -> str:
        return ctx.getText()

    def visitExpr5(self, ctx: MiniGoParser.Expr5Context) -> Expr:
        if ctx.expr5():
            op = ctx.getChild(0).getText()
            body = self.visit(ctx.expr5())
            return UnaryOp(op, body)
        return self.visit(ctx.expr6())

    def visitExpr6(self, ctx: MiniGoParser.Expr6Context) -> Expr:
        if ctx.LBRACK():
            exp6 = self.visit(ctx.expr6())
            expression = self.visit(ctx.expression())
            if isinstance(exp6, ArrayCell):
                exp6.idx.append(expression)
                return exp6
            return ArrayCell(exp6, [expression])
        if ctx.DOT():
            exp6 = self.visit(ctx.expr6())
            if ctx.ID():
                return FieldAccess(exp6, ctx.ID().getText())
            func_call: FuncCall = self.visit(ctx.funcCall())
            return MethCall(exp6, func_call.funName, func_call.args)
        return self.visit(ctx.expr7())

    def visitFuncCall(self, ctx: MiniGoParser.FuncCallContext) -> FuncCall:
        suffix: List[Expr] = self.visit(ctx.exprList()) if ctx.exprList() else []
        return FuncCall(ctx.ID().getText(), suffix)

    def visitExpr7(self, ctx: MiniGoParser.Expr7Context) -> Expr:
        if ctx.literal():
            return self.visit(ctx.literal())
        if ctx.ID():
            return Id(ctx.ID().getText())
        if ctx.LPAREN():
            return self.visit(ctx.expression())
        if ctx.funcCall():
            return self.visit(ctx.funcCall())
        assert False, "This should not be expr7"

    def visitMethodCall(self, ctx: MiniGoParser.MethodCallContext) -> MethCall:
        exp6 = self.visit(ctx.expr6())
        func_call: FuncCall = self.visit(ctx.funcCall())
        return MethCall(exp6, func_call.funName, func_call.args)

    #! ------------------ Declaration ------------------
    def visitProgram(self, ctx: MiniGoParser.ProgramContext) -> Program:
        decls: List[Decl] = (
            self.visit(ctx.many_declarations()) if ctx.many_declarations() else []
        )
        return Program(decls)

    def visitMany_declarations(
        self, ctx: MiniGoParser.Many_declarationsContext
    ) -> List[Decl]:
        suffix: List[Decl] = (
            self.visit(ctx.many_declarations()) if ctx.many_declarations() else []
        )
        return [self.visit(ctx.declaration())] + suffix

    def visitDeclaration(self, ctx: MiniGoParser.DeclarationContext) -> Decl:
        if ctx.varDeclaration():
            return self.visit(ctx.varDeclaration())
        if ctx.constDeclaration():
            return self.visit(ctx.constDeclaration())
        if ctx.structDeclaration():
            return self.visit(ctx.structDeclaration())
        if ctx.interfaceDeclaration():
            return self.visit(ctx.interfaceDeclaration())
        if ctx.funcDeclaration():
            return self.visit(ctx.funcDeclaration())
        if ctx.methodDeclaration():
            return self.visit(ctx.methodDeclaration())
        assert False, "This should not be declaration"

    def visitVarDeclaration(self, ctx: MiniGoParser.VarDeclarationContext) -> VarDecl:
        name = ctx.ID().getText()
        type = self.visit(ctx.typeSpec()) if ctx.typeSpec() else None
        init = self.visit(ctx.expression()) if ctx.expression() else None
        return VarDecl(name, type, init)

    def visitConstDeclaration(
        self, ctx: MiniGoParser.ConstDeclarationContext
    ) -> ConstDecl:
        name = ctx.ID().getText()
        type = None
        init: Expr = self.visit(ctx.expression())
        return ConstDecl(name, type, init)

    def visitFuncDeclaration(
        self, ctx: MiniGoParser.FuncDeclarationContext
    ) -> FuncDecl:
        name = ctx.ID().getText()
        params: List[ParamDecl] = self.visit(ctx.paramList()) if ctx.paramList() else []
        returnType = self.visit(ctx.typeSpec()) if ctx.typeSpec() else VoidType()
        block: Block = self.visit(ctx.block())
        return FuncDecl(name, params, returnType, block)

    def visitParamList(self, ctx: MiniGoParser.ParamListContext) -> List[ParamDecl]:
        suffix: List[ParamDecl] = self.visit(ctx.paramList()) if ctx.paramList() else []
        return self.visit(ctx.param()) + suffix

    def visitParam(self, ctx: MiniGoParser.ParamContext) -> List[ParamDecl]:
        ids: List[str] = self.visit(ctx.multiID())
        type: Type = self.visit(ctx.typeSpec())
        return [ParamDecl(id, type) for id in ids]

    def visitMultiID(self, ctx: MiniGoParser.MultiIDContext) -> List[str]:
        suffix: List[str] = self.visit(ctx.multiID()) if ctx.multiID() else []
        return [ctx.ID().getText()] + suffix

    def visitMethodDeclaration(
        self, ctx: MiniGoParser.MethodDeclarationContext
    ) -> MethodDecl:
        receiver_name, receiver_type = self.visit(ctx.methodReceiver())
        method_name = ctx.ID().getText()
        params: List[ParamDecl] = self.visit(ctx.paramList()) if ctx.paramList() else []
        returnType = self.visit(ctx.typeSpec()) if ctx.typeSpec() else VoidType()
        block: Block = self.visit(ctx.block())
        func = FuncDecl(method_name, params, returnType, block)
        return MethodDecl(receiver_name, receiver_type, func)

    def visitMethodReceiver(
        self, ctx: MiniGoParser.MethodReceiverContext
    ) -> Tuple[str, Id]:
        name: str = ctx.ID(0).getText()
        type: str = Id(ctx.ID(1).getText())
        return (name, type)

    def visitStructDeclaration(
        self, ctx: MiniGoParser.StructDeclarationContext
    ) -> StructType:
        name = ctx.ID().getText()
        fields: List[Tuple[str, Type]] = self.visit(ctx.structFields())
        return StructType(name, fields, [])

    def visitStructFields(
        self, ctx: MiniGoParser.StructFieldsContext
    ) -> List[Tuple[str, Type]]:
        suffix: List[Tuple[str, Type]] = (
            self.visit(ctx.structFields()) if ctx.structFields() else []
        )
        return [self.visit(ctx.field())] + suffix

    def visitField(self, ctx: MiniGoParser.FieldContext) -> Tuple[str, Type]:
        id = ctx.ID().getText()
        type = self.visit(ctx.typeSpec())
        return (id, type)

    def visitInterfaceDeclaration(
        self, ctx: MiniGoParser.InterfaceDeclarationContext
    ) -> InterfaceType:
        name = ctx.ID().getText()
        methods: List[Prototype] = self.visit(ctx.methodSignatures())
        return InterfaceType(name, methods)

    def visitMethodSignatures(
        self, ctx: MiniGoParser.MethodSignaturesContext
    ) -> List[Prototype]:
        suffix: List[Prototype] = (
            self.visit(ctx.methodSignatures()) if ctx.methodSignatures() else []
        )
        return [self.visit(ctx.methodSignature())] + suffix

    def visitMethodSignature(
        self, ctx: MiniGoParser.MethodSignatureContext
    ) -> Prototype:
        name = ctx.ID().getText()
        params: List[ParamDecl] = self.visit(ctx.paramList()) if ctx.paramList() else []
        param_types: List[Type] = [param.parType for param in params]
        returnType = self.visit(ctx.typeSpec()) if ctx.typeSpec() else VoidType()
        return Prototype(name, param_types, returnType)

    #! ------------------ Statement ------------------
    def visitBlock(self, ctx: MiniGoParser.BlockContext) -> Block:
        stmts: List[BlockMember] = self.visit(ctx.stmtList())
        return Block(stmts)

    def visitStmtList(self, ctx: MiniGoParser.StmtListContext) -> List[BlockMember]:
        suffix: List[BlockMember] = self.visit(ctx.stmtList()) if ctx.stmtList() else []
        return [self.visit(ctx.statement())] + suffix

    def visitStatement(self, ctx: MiniGoParser.StatementContext) -> BlockMember:
        if ctx.assignStmt():
            return self.visit(ctx.assignStmt())
        if ctx.breakStmt():
            return self.visit(ctx.breakStmt())
        if ctx.continueStmt():
            return self.visit(ctx.continueStmt())
        if ctx.callStmt():
            return self.visit(ctx.callStmt())
        if ctx.returnStmt():
            return self.visit(ctx.returnStmt())
        if ctx.varDeclaration():
            return self.visit(ctx.varDeclaration())
        if ctx.constDeclaration():
            return self.visit(ctx.constDeclaration())
        if ctx.ifStmt():
            return self.visit(ctx.ifStmt())
        if ctx.forStmt():
            return self.visit(ctx.forStmt())
        print("This statement is: ", ctx.getText())
        # assert False, "This should not be statement"

    def visitAssignStmt(self, ctx: MiniGoParser.AssignStmtContext) -> Assign:
        lhs = self.visit(ctx.lhs())
        op = self.visit(ctx.assignmentOp())  # op is +=, -=, *=, /=, %=
        rhs = self.visit(ctx.expression())
        rhs = rhs if op == ":=" else BinaryOp(op[0], lhs, rhs)
        return Assign(lhs, rhs)

    def visitLhs(self, ctx: MiniGoParser.LhsContext) -> LHS:
        if ctx.LBRACK():
            lhs = self.visit(ctx.lhs())
            expression = self.visit(ctx.expression())
            if isinstance(lhs, ArrayCell):
                lhs.idx.append(expression)
                return lhs
            return ArrayCell(lhs, [expression])
        if ctx.DOT():
            lhs: LHS = self.visit(ctx.lhs())
            return FieldAccess(lhs, ctx.ID().getText())
        return Id(ctx.ID().getText())

    def visitAssignmentOp(self, ctx: MiniGoParser.AssignmentOpContext) -> str:
        return ctx.getText()

    def visitIfStmt(self, ctx: MiniGoParser.IfStmtContext) -> If:
        if ctx.ifElseStmt():
            return self.visit(ctx.ifElseStmt())
        expression = self.visit(ctx.expression())
        block: Block = self.visit(ctx.block())
        if_stmt = self.visit(ctx.ifStmt()) if ctx.ifStmt() else None
        return If(expression, block, if_stmt)

    def visitIfElseStmt(self, ctx: MiniGoParser.IfElseStmtContext) -> If:
        expression = self.visit(ctx.expression())
        if ctx.ELSE():
            then = ctx.block(0)
            else_block = ctx.block(1)
            return If(expression, self.visit(then), self.visit(else_block))
        return If(expression, self.visit(ctx.block()), None)

    def visitForStmt(self, ctx: MiniGoParser.ForStmtContext) -> Stmt:
        for_stmt = self.visit(ctx.getChild(0))
        return for_stmt

    def visitForExpr(self, ctx: MiniGoParser.ForExprContext) -> ForBasic:
        expr = self.visit(ctx.expression())
        block: Block = self.visit(ctx.block())
        return ForBasic(expr, block)

    def visitForLoop(self, ctx: MiniGoParser.ForLoopContext) -> ForStep:
        expr = self.visit(ctx.expression())
        block: Block = self.visit(ctx.block())
        if ctx.scalarDecl():
            init = self.visit(ctx.scalarDecl())
            step = self.visit(ctx.scalarAssign(0))
            return ForStep(init, expr, step, block)
        init = self.visit(ctx.scalarAssign(0))
        step = self.visit(ctx.scalarAssign(1))
        return ForStep(init, expr, step, block)

    def visitForRange(self, ctx: MiniGoParser.ForRangeContext) -> ForEach:
        id = Id(ctx.getChild(1).getText())
        value = Id(ctx.getChild(3).getText())
        expr = self.visit(ctx.expression())
        block: Block = self.visit(ctx.block())
        return ForEach(id, value, expr, block)

    def visitScalarDecl(self, ctx: MiniGoParser.ScalarDeclContext) -> VarDecl:
        id = ctx.ID().getText()
        type = self.visit(ctx.typeSpec()) if ctx.typeSpec() else None
        init = self.visit(ctx.expression())
        return VarDecl(id, type, init)

    def visitScalarAssign(self, ctx: MiniGoParser.ScalarAssignContext) -> Assign:
        id = Id(ctx.ID().getText())
        op = self.visit(ctx.assignmentOp())
        expr = self.visit(ctx.expression())
        return Assign(id, expr) if op == ":=" else Assign(id, BinaryOp(op[0], id, expr))

    def visitBreakStmt(self, ctx: MiniGoParser.BreakStmtContext) -> Break:
        return Break()

    def visitContinueStmt(self, ctx: MiniGoParser.ContinueStmtContext) -> Continue:
        return Continue()

    def visitCallStmt(self, ctx: MiniGoParser.CallStmtContext):
        if ctx.methodCall():
            return self.visit(ctx.methodCall())
        return self.visit(ctx.funcCall())

    def visitReturnStmt(self, ctx: MiniGoParser.ReturnStmtContext) -> Return:
        return_val = self.visit(ctx.expression()) if ctx.expression() else None
        return Return(return_val)
