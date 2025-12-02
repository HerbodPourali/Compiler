grammar CMinus;

// Import tokens from CMinusLexer
options {
    tokenVocab = CMinusLexer;
}

// Parser Rules (Grammar Productions) - Following grammer.txt exactly
program: declarationList;

declarationList: declaration declarationList | /* epsilon */;

declaration: declarationInitial declarationPrime;

declarationInitial: typeSpecifier ID;

declarationPrime: funDeclarationPrime | varDeclarationPrime;

varDeclarationPrime: LBRACKET NUM RBRACKET SEMICOLON | SEMICOLON;

funDeclarationPrime: LPAREN params RPAREN compoundStmt;

typeSpecifier: INT | VOID;

params: INT ID paramPrime paramList | VOID;

paramList: COMMA param paramList | /* epsilon */;

param: declarationInitial paramPrime;

paramPrime: LBRACKET RBRACKET | /* epsilon */;

compoundStmt: LBRACE declarationList statementList RBRACE;

statementList: statement statementList | /* epsilon */;

statement: expressionStmt | compoundStmt | selectionStmt | iterationStmt | returnStmt;

expressionStmt: expression SEMICOLON | BREAK SEMICOLON | SEMICOLON;

selectionStmt: IF LPAREN expression RPAREN statement ELSE statement;

iterationStmt: REPEAT statement UNTIL LPAREN expression RPAREN;

returnStmt: RETURN returnStmtPrime;

returnStmtPrime: SEMICOLON | expression SEMICOLON;

expression: simpleExpressionZegond | ID b;

b: ASSIGN expression | LBRACKET expression RBRACKET h | simpleExpressionPrime;

h: ASSIGN expression | g d c;

simpleExpressionZegond: additiveExpressionZegond c;

simpleExpressionPrime: additiveExpressionPrime c;

c: relop additiveExpression | /* epsilon */;

relop: LT | EQ;

additiveExpression: term d;

additiveExpressionPrime: termPrime d;

additiveExpressionZegond: termZegond d;

d: addop term d | /* epsilon */;

addop: PLUS | MINUS;

term: factor g;

termPrime: factorPrime g;

termZegond: factorZegond g;

g: MULTIPLY factor g | /* epsilon */;

factor: LPAREN expression RPAREN | ID varCallPrime | NUM;

varCallPrime: LPAREN args RPAREN | varPrime;

varPrime: LBRACKET expression RBRACKET | /* epsilon */;

factorPrime: LPAREN args RPAREN | /* epsilon */;

factorZegond: LPAREN expression RPAREN | NUM;

args: argList | /* epsilon */;

argList: expression argListPrime;

argListPrime: COMMA expression argListPrime | /* epsilon */; 