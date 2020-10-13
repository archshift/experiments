%union {
	ast_program prgm;
	ast_expr_list expr_list;
	ast_expr expr;
	ast_literal lit;
	ast_ident ident;
	ast_ident_list ident_list;
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
	: decl_list				{ $$ = (ast_program) { .exprs = $1 } }
	;

decl_list
	: decl decl_list			{ $$ = (expr_list) { .head = $1, .tail = $2 } }
	| decl                                  { $$ = (expr_list) { .head = $1 } }
	;

decl
	: IDENT ":=" expr			{ $$ = (expr) { .type = EXPR_VAR_DECL, .name = $1, .val = $3 } }
	| IDENT "(" ident_list ")" ":=" expr	{ $$ = (expr) { .type = EXPR_FN_DECL, .name = $1, .val = $6 } }
	| LAMBDA "(" ident_list ")" ":=" expr	{ $$ = (expr) { .type = EXPR_VAR_DECL, .name = NULL, .val = $6 } }
	;

ident_list
	: IDENT ident_list			{ $$ = (ident_list) { .head = $1, .tail = $2 } }
	| IDENT					{ $$ = (ident_list) { .head = $1 } }
	;

expr
	: expr "+" expr				{ $$ = (expr) { .type = EXPR_BINOP, .left = $1, .op = OP_ADD, .right = $3 } }
	| expr "-" expr				{ $$ = (expr) { .type = EXPR_BINOP, .left = $1, .op = OP_SUB, .right = $3 } }
	| expr "*" expr				{ $$ = (expr) { .type = EXPR_BINOP, .left = $1, .op = OP_MUL, .right = $3 } }
	| expr "->" expr			{ $$ = (expr) { .type = EXPR_BINOP, .left = $1, .op = OP_PREPEND, .right = $3 } }
	| "*" expr				{ $$ = (expr) { .type = EXPR_UNARY, .op = OP_HEAD, .inner = $2 } }
	| expr "->" "..."			{ $$ = (expr) { .type = EXPR_UNARY, .op = OP_TAIL, .inner = $1 } }
	| LITERAL				{ $$ = (expr) { .type = EXPR_LITERAL, .literal = $1 } }
	| IDENT					{ $$ = (expr) { .type = EXPR_IDENT, .ident = $1 } }
	;

