%{
    #include "lang.tab.h"

    #include <string.h>
%}

%%

[a-zA-Z_][0-9a-zA-Z_]*                  { return IDENT; }
[1-9][0-9]*                             {
                                            yylval.lit = NEW(ast_literal, {
                                                .ty = AST_LITERAL_INT,
                                                .num = strtoull(yytext, NULL, 10),
                                            });
                                            if (errno == ERANGE) {
                                                return YYerror;
                                            } else {
                                                return LITERAL;
                                            }
                                        }

"+"                                     { return PLUS; }
"-"                                     { return MINUS; }
"*"                                     { return STAR; }
"/"                                     { return DIV; }
"%"                                     { return MOD; }
"\\"                                    { return LAMBDA; }
"->"                                    { return ARROW; }
