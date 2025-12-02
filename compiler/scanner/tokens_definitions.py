import re

KEYWORDS = ( "break", "else", "if", "int", "repeat", "return", "until", "void") # letting the first 8 ones get initialized 
SYMBOLS = {";", ":", ",", "[", "]", "(", ")", "{", "}", "+", "-", "*", "=", "<", "==", "$"}

TOKEN_REGEX = {
    "NUM": r'\d+',
    "ID": r'[A-Za-z][A-Za-z0-9]*',
    "SYMBOL": r'(==|[;:,\[\]\(\)\{\}\+\-\*=<])',
    "WHITESPACE": r'[ \n\r\t\v\f]+',
    "COMMENT_START": r'/\*',
    "COMMENT_END": r'\*/',
}
