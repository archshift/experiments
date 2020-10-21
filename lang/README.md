## Tiny Language

### Example:

```
f(x) :=
    a + b

f(x) :=
    if a then g(x)
    else if a is (
        1 then h(x),
        2 then b(x),
        3 then a(x),
        else unreachable
    )

map(what, iter) :=
    what(*iter) -> map(what, iter->...)

print!(args) :=
    let strjoin :=
        reduce(
            \(acc, s) := acc -> s,
            "",
            ...
        );
    syscall!(SYS_PRINT, strjoin(args))
```

Operator expressions:
- Binary `+ - * / %`: standard arithmetic operators
- Binary `->`: New list
- Postfix `->...`: List tail
- Prefix `*`: List head

Literals:
- `"string"`: String
- `123456789`: Decimal number
- `0x12345f`: Hex number

Expressions:
- `name(args) := expr`: Define pure function, yields the function
- `\(args) := expr`: Define unnamed function
- `var := expr`: Define variable, yields the variable
- Operator expressions
- `if b then expr1 else expr2`: If statement yielding one of two expressions
- `if b is ( 1 then a, 2 then b, else c )`: Case statement
- `name(args)`: Pure function call
- `name!(args)`: Unpure function call
- `name(arg1, ...)`: Partial function call
- `a.member := expr`: Assign to member, yields the struct
- `do expr1; expr2`: Evaluates `expr1` and discards the result, yields `expr2` 
- `let expr1; expr2`: Evaluates `expr1` and discards the result, yields `expr2` 

Standard functions:
- `map(fn, iter)`: Maps function to list
- `reduce(fn, start, iter)`: Reduces list to a val
- `filter(fn, iter)`: Keeps only selected items
- `print!(anything)`: Prints the argument
- `debug(anything)`: Prints the argument to the debug log
