lexer grammar MiniLangLexer;

// Comments
COMMENT : '/*' .*? '*/' -> skip;

INVALID_TOKEN: [0-9]+[a-zA-Z] -> skip;

// Numbers
NUM : [0-9]+;

// Keywords
KEYWORD : 'void' | 'int' | 'if' | 'else' | 'repeat' | 'break' | 'until' | 'return';

// Identifiers
INVALID_ID : [A-Za-z][A-Za-z0-9]*~([A-Za-z0-9 \n\r\t\f] | '(' | ')' | '{' | '}' | '[' | ']' | '+' | '-' | '*' | '/' | '=' | '<' | ';' | ',') -> skip;
ID : [A-Za-z][A-Za-z0-9]*;

MULTILINE_COMMENT_OPEN : '/*'  -> skip, pushMode(COMMENT_OPEN);
MULTILINE_COMMENT_CLOSE : '*/'  -> skip;
SINGLELINE_COMMENT : '/' '/' -> skip;
SLASH_DIGIT : '/' [0-9] -> skip;

// Symbols
INVALID_SYMBOL : (SYMBOL_START)~([A-Za-z0-9 \n\r\t\f] | '(' | ')' | '{' | '}' | '[' | ']' | '+' | '-' | '*' | '/' | '=' | '<' | ';' | ',' | '!') -> skip;
SYMBOL : SYMBOL_START;

fragment
SYMBOL_START : '==' | '(' | ')' | '{' | '}' | '[' | ']' | '+' | '-' | '*' | '/' | '=' | '<' | ';' | ',';

// Whitespace
WHITESPACE : [ \n\r\t\f]+ -> skip;

mode COMMENT_OPEN;
COMMENT_OPEN_SKIP : . -> skip;