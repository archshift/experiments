.PHONY: lang
lang:
	bison -Wcounterexamples lang.y
	bison -d lang.y
	flex --header-file=lex.yy.h lang.l
	gcc main.c lang.tab.c lex.yy.c ast.c -g -o lang