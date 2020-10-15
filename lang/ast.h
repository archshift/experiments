#pragma once

#include <stdint.h>
#include <stdlib.h>

struct ast_program_s;
struct ast_expr_s;
struct ast_expr_list_s;
struct ast_literal_s;
struct ast_ident_s;

#define NEW(s, ...) ({ \
    s *_ptr = (s *)malloc(sizeof(s)); \
    s _rval = __VA_ARGS__; \
    *_ptr = _rval; \
    _ptr; })

typedef struct ast_program_s {
    struct ast_expr_list_s *exprs;
} ast_program;

enum ast_expr_type {
    AST_EXPR_BINOP,
    AST_EXPR_UNARY,
    AST_EXPR_VAR_DECL,
    AST_EXPR_FN_DECL,
    AST_EXPR_LITERAL,
    AST_EXPR_IDENT,
};

enum ast_operator {
    AST_OP_MUL,
    AST_OP_DIV,
    AST_OP_ADD,
    AST_OP_SUB,
    AST_OP_MOD,
    AST_OP_PREPEND,
    AST_OP_HEAD,
    AST_OP_TAIL,
};

typedef struct ast_expr_s {
    enum ast_expr_type ty;
    union {
        struct ast_literal_s *literal;
        struct ast_ident_s *ident;
        struct {
            enum ast_operator *op;
            struct ast_expr_s *left, *right;
        };
        struct {
            struct ast_ident_s *name;
            struct ast_expr_s *val;
        };
        struct {
            enum ast_operator *op;
            struct ast_expr_s *inner;
        };
    };
} ast_expr;

typedef struct ast_expr_list_s {
    struct ast_expr_s *head;
    struct ast_expr_list_s *tail;
} ast_expr_list;

enum ast_literal_type {
    AST_LITERAL_INT,
    AST_LITERAL_STRING,
};

typedef struct ast_literal_s {
    enum ast_literal_type ty;
    union {
        char *str;
        uint64_t num;
    };
} ast_literal;

typedef struct ast_ident_s {
    char *name;
} ast_ident;

typedef struct {
    struct ast_ident_s *head;
    struct ast_ident_list_s *tail;
} ast_ident_list;