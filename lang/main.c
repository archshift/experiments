#include <stdio.h>

#include "lang.tab.h"
#include "lex.yy.h"

int main() {
    int res;
    yyscan_t scanner;
    res = yylex_init(&scanner);
    if (res) {
        printf("lex error: %d\n", res);
        exit(res);
    }

    parse_ctx_t ctx = {
        .scanner = scanner,
    };
    res = yyparse(&ctx);
    printf("parse output: %d\n", res);
    yylex_destroy(scanner);

    print_program(ctx.out_ast);
}