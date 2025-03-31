// 2212615
grammar MiniGo;

@lexer::header {
from lexererr import *
}

@lexer::members {
def emit(self):
    self.last_token_type = self.type
    if self.last_token_type == self.UNCLOSE_STRING:       
        result = super().emit();
        raise UncloseString(result.text);
    elif self.last_token_type == self.ILLEGAL_ESCAPE:
        result = super().emit();
        raise IllegalEscape(result.text);
    elif self.last_token_type == self.ERROR_CHAR:
        result = super().emit();
        raise ErrorToken(result.text); 
    else:
        return super().emit();
}

options{
	language = Python3;
}

program: many_declarations? EOF;

many_declarations: declaration many_declarations | declaration;

declaration: (
		varDeclaration
		| constDeclaration
		| structDeclaration
		| interfaceDeclaration
	) SEMI
	| ( funcDeclaration | methodDeclaration) SEMI?;

// Variable Declaration
varDeclaration:
	VAR ID typeSpec (ASSIGN expression)?
	| VAR ID ASSIGN expression;

// Constant Declaration
constDeclaration: CONST ID ASSIGN expression;

// Function Declaration
funcDeclaration:
	FUNC ID LPAREN paramList? RPAREN typeSpec? block;
paramList: param (COMMA paramList)?;
param: multiID typeSpec;
multiID: ID (COMMA multiID)?;

// Method Declaration
methodDeclaration:
	FUNC methodReceiver ID LPAREN paramList? RPAREN typeSpec? block;
methodReceiver: LPAREN ID ID RPAREN;

// Struct Declaration
structDeclaration: TYPE ID STRUCT LBRACE structFields RBRACE;
structFields: field SEMI structFields?;
field: ID typeSpec;

// Interface Declaration
interfaceDeclaration:
	TYPE ID INTERFACE LBRACE methodSignatures RBRACE;
methodSignatures: methodSignature SEMI methodSignatures?;
methodSignature: ID LPAREN paramList? RPAREN typeSpec?;

// Statements
block: LBRACE stmtList RBRACE;
stmtList: statement stmtList | statement;
statement:
	(
		| assignStmt
		| breakStmt
		| continueStmt
		| callStmt
		| returnStmt
		| varDeclaration
		| constDeclaration
		| ifStmt 
		| forStmt
	) SEMI;

assignStmt: lhs assignmentOp expression;
lhs:
	ID
	| lhs LBRACK expression RBRACK // Array element access
	| lhs DOT ID; // Struct field access
assignmentOp:
	DECLARE
	| ADD_ASSIGN
	| SUB_ASSIGN
	| MUL_ASSIGN
	| DIV_ASSIGN
	| MOD_ASSIGN;

// If Statement
ifStmt:
	IF LPAREN expression RPAREN block (ELSE ifStmt)?
	| ifElseStmt;
ifElseStmt: IF LPAREN expression RPAREN block (ELSE block)?;

// For Statement
forStmt: forExpr | forLoop | forRange;
forExpr: FOR expression block;
forLoop: FOR (scalarDecl | scalarAssign) SEMI expression SEMI scalarAssign block;
forRange: FOR (ID COMMA ID | UNDERSCORE COMMA ID) DECLARE RANGE expression block;
scalarDecl: VAR ID typeSpec? ASSIGN expression;
scalarAssign: ID assignmentOp expression;

// Other Statements
breakStmt: BREAK;
continueStmt: CONTINUE;
callStmt: funcCall | methodCall;
returnStmt: RETURN expression?;

// Types
primitiveType: INT | FLOAT | STRING | BOOLEAN;
baseType: primitiveType | ID;
typeSpec: arrayType | baseType;

// Literals
literal: notArrayLiteral | arrayLiteral;
notArrayLiteral:
	integer
	| FLOAT_LIT
	| STR_LIT
	| TRUE
	| FALSE
	| NIL
	| structLiteral;
arrayLiteral: arrayType arrayBody;
arrayBody: LBRACE arrayList RBRACE;
arrayType: LBRACK arrayDim RBRACK (arrayType | baseType);
arrayDim: integer | ID;
arrayList: arrayMember (COMMA arrayList)?;
arrayMember: notArrayLiteral | ID | arrayBody;
structLiteral: ID LBRACE structElements? RBRACE;
structElements: structElement (COMMA structElements)?;
structElement: ID COLON expression;

// Expressions
exprList: expression COMMA exprList | expression;
expression: expression OR expr1 | expr1;
expr1: expr1 AND expr2 | expr2;
expr2: expr2 compOp expr3 | expr3;
compOp:
	EQUAL
	| NOTEQUAL
	| LESS
	| LESSEQUAL
	| GREATER
	| GREATEREQUAL;
expr3: expr3 addOp expr4 | expr4;
addOp: ADD | SUB;
expr4: expr4 mulOp expr5 | expr5;
mulOp: MUL | DIV | MOD;
expr5: (NOT | SUB) expr5 | expr6;
expr6:
	expr6 LBRACK expression RBRACK
	| expr6 DOT (ID | funcCall)
	| expr7;
expr7:
	literal
	| ID
	| LPAREN expression RPAREN
	| funcCall;
funcCall: ID LPAREN exprList? RPAREN;
methodCall: expr6 DOT funcCall;

integer: DEC_LIT | HEX_LIT | BIN_LIT | OCT_LIT;

// !-----------------LEXER-----------------!
IF: 'if';
ELSE: 'else';
FOR: 'for';
RETURN: 'return';
FUNC: 'func';
TYPE: 'type';
STRUCT: 'struct';
INTERFACE: 'interface';
STRING: 'string';
INT: 'int';
FLOAT: 'float';
VAR: 'var';
CONTINUE: 'continue';
BREAK: 'break';
RANGE: 'range';
NIL: 'nil';
TRUE: 'true';
FALSE: 'false';
BOOLEAN: 'boolean';
CONST: 'const';

ADD: '+';
SUB: '-';
MUL: '*';
DIV: '/';
MOD: '%';

EQUAL: '==';
NOTEQUAL: '!=';
LESS: '<';
LESSEQUAL: '<=';
GREATER: '>';
GREATEREQUAL: '>=';

DECLARE: ':=';
ASSIGN: '=';
ADD_ASSIGN: '+=';
SUB_ASSIGN: '-=';
MUL_ASSIGN: '*=';
DIV_ASSIGN: '/=';
MOD_ASSIGN: '%=';

AND: '&&';
OR: '||';
NOT: '!';
DOT: '.';

LPAREN: '(';
RPAREN: ')';
LBRACE: '{';
RBRACE: '}';
LBRACK: '[';
RBRACK: ']';
COMMA: ',';
SEMI: ';';
COLON: ':';

DEC_LIT: '0' | [1-9] [0-9]*;
BIN_LIT: '0' [bB] [01]+;
OCT_LIT: '0' [oO] [0-7]+;
HEX_LIT: '0' [xX] [0-9a-fA-F]+;
FLOAT_LIT: [0-9]+ '.' [0-9]* ([eE] [+-]? [0-9]+)?;

fragment ESC_LETTER: [ntr"\\];
fragment ESCAPE: '\\' ESC_LETTER;
fragment STR_CHAR: ~[\n"\\] | ESCAPE;
STR_LIT: '"' STR_CHAR* '"';
UNDERSCORE: '_';

ID: [a-zA-Z_][a-zA-Z_0-9]*;

NEWLINE:
	'\r'? '\n' {
    literal_tokens = [
        self.DEC_LIT, self.HEX_LIT, self.BIN_LIT, self.OCT_LIT, self.FLOAT_LIT, self.BOOLEAN, self.STR_LIT
    ]
    type_tokens = [
        self.STRING, self.INT, self.FLOAT, self.NIL, self.TRUE, self.FALSE
    ]
    statement_tokens = [
        self.RETURN, self.CONTINUE, self.BREAK
    ]
    bracket_tokens = [
        self.RPAREN, self.RBRACK, self.RBRACE
    ]
    identifier_tokens = [
        self.ID
    ]
    
    if hasattr(self, 'last_token_type') and self.last_token_type in (
        literal_tokens + type_tokens + statement_tokens + bracket_tokens + identifier_tokens
    ):
        self.text = ';'
        self.type = self.SEMI
    else:
        self.skip()
};

WS: [ \t\f\r]+ -> skip;
COMMENT: '//' ~[\r\n]* -> skip;
BLOCK_COMMENT: '/*' (BLOCK_COMMENT | .)*? '*/' -> skip;

UNCLOSE_STRING:
	'"' STR_CHAR* ('\r\n' | '\n' | EOF) {
if (len(self.text) >= 2 and self.text[-1] == '\n' and self.text[-2] == '\r'):
    raise UncloseString(self.text[:-2])  # Case \r\n
elif (self.text[-1] == '\n'):
    raise UncloseString(self.text[:-1])  # Case \n
else:
    raise UncloseString(self.text)    # Case EOF
};
fragment ESCAPE_ILLEGAL: '\\' ~[ntr"\\];
ILLEGAL_ESCAPE:
	'"' STR_CHAR* ESCAPE_ILLEGAL {
    raise IllegalEscape(self.text)
};
ERROR_CHAR: . {raise ErrorToken(self.text)};