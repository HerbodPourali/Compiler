lexer grammar CMinusLexer;

// Comments
COMMENT : '/*' .*? '*/' -> skip;

// Keywords (individual tokens)
VOID : 'void';
INT : 'int';
IF : 'if';
ELSE : 'else';
REPEAT : 'repeat';
BREAK : 'break';
UNTIL : 'until';
RETURN : 'return';

// Multi-character symbols
EQ : '==';

// Single-character symbols
SEMICOLON : ';';
COMMA : ',';
LBRACKET : '[';
RBRACKET : ']';
LPAREN : '(';
RPAREN : ')';
LBRACE : '{';
RBRACE : '}';
PLUS : '+';
MINUS : '-';
MULTIPLY : '*';
ASSIGN : '=';
LT : '<';

// Numbers
NUM : [0-9]+;

// Identifiers
ID : [A-Za-z][A-Za-z0-9]*;

// Invalid tokens (for error handling)
INVALID_TOKEN: [0-9]+[a-zA-Z] -> skip;

// Whitespace
WHITESPACE : [ \n\r\t\f]+ -> skip; 