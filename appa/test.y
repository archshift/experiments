%token plus
%token lp
%token rp
%token int

%%

S : E;
E : E plus lp E rp | int;