%code requires {
    #include "ast.h"
}

%union {
    ast_program *prgm;
    ast_expr_list *expr_list;
    ast_expr *expr;
    ast_literal *lit;
    ast_ident *ident;
    ast_ident_list *ident_list;
    const char *str;
}

%token
    PLUS "+"
    MINUS "-"
    STAR "*"
    DIV "/"
    MOD "%"
    LAMBDA "\\"
    ARROW "->"
    ASSIGN ":="
    ELLIPSE "..."
    LPAREN "("
    RPAREN ")"
%token <lit> LITERAL
%token <ident> IDENT

%type <prgm> program
%type <expr_list> decl_list
%type <ident_list> ident_list
%type <expr> expr decl

%right ASSIGN
%right ARROW
%left PLUS MINUS
%left STAR DIV MOD

%%

program
    : decl_list								{ $$ = NEW(ast_program, { .exprs = $1 }); }
    ;

decl_list
    : decl decl_list						{ $$ = NEW(ast_expr_list, { .head = $1, .tail = $2 }); }
    | decl                                  { $$ = NEW(ast_expr_list, { .head = $1 }); }
    ;

decl
    : IDENT ":=" expr						{ $$ = NEW(ast_expr, { .ty = AST_EXPR_VAR_DECL, .name = $1, .val = $3 }); }
    | IDENT "(" ident_list ")" ":=" expr	{ $$ = NEW(ast_expr, { .ty = AST_EXPR_FN_DECL, .name = $1, .val = $6 }); }
    | LAMBDA "(" ident_list ")" ":=" expr	{ $$ = NEW(ast_expr, { .ty = AST_EXPR_VAR_DECL, .name = NULL, .val = $6 }); }
    ;

ident_list
    : IDENT ident_list						{ $$ = NEW(ast_ident_list, { .head = $1, .tail = $2 }); }
    | IDENT									{ $$ = NEW(ast_ident_list, { .head = $1 }); }
    ;

expr
    : expr "+" expr							{ $$ = NEW(ast_expr, { .ty = AST_EXPR_BINOP, .left = $1, .op = AST_OP_ADD, .right = $3 }); }
    | expr "-" expr							{ $$ = NEW(ast_expr, { .ty = AST_EXPR_BINOP, .left = $1, .op = AST_OP_SUB, .right = $3 }); }
    | expr "*" expr							{ $$ = NEW(ast_expr, { .ty = AST_EXPR_BINOP, .left = $1, .op = AST_OP_MUL, .right = $3 }); }
    | expr "/" expr							{ $$ = NEW(ast_expr, { .ty = AST_EXPR_BINOP, .left = $1, .op = AST_OP_DIV, .right = $3 }); }
    | expr "%" expr							{ $$ = NEW(ast_expr, { .ty = AST_EXPR_BINOP, .left = $1, .op = AST_OP_MOD, .right = $3 }); }
    | expr "->" expr						{ $$ = NEW(ast_expr, { .ty = AST_EXPR_BINOP, .left = $1, .op = AST_OP_PREPEND, .right = $3 }); }
    | "*" expr								{ $$ = NEW(ast_expr, { .ty = AST_EXPR_UNARY, .op = AST_OP_HEAD, .inner = $2 }); }
    | expr "->" "..."						{ $$ = NEW(ast_expr, { .ty = AST_EXPR_UNARY, .op = AST_OP_TAIL, .inner = $1 }); }
    | LITERAL								{ $$ = NEW(ast_expr, { .ty = AST_EXPR_LITERAL, .literal = $1 }); }
    | IDENT									{ $$ = NEW(ast_expr, { .ty = AST_EXPR_IDENT, .ident = $1 }); }
    ;

