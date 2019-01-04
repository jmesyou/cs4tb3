/**
 *	name: James You
 */

		char str[256];
		int depth = 0;
%%
[a-zA-Z0-9"./"]{256,}$ {
	fprintf(stderr, "pathname too long\n");
	yyterminate();
}

[a-zA-Z0-9"."]{15,} {
	fprintf(stderr, "component too long\n");
  yyterminate();
}

[^a-zA-Z0-9\n"./"] {
	fprintf(stderr, "invalid character\n");
	yyterminate();
}

"/"{2,} {
	yyless(1);
}

"/"$

"/" {
	strcat(str, "/");
}

"."{3,}[a-zA-Z0-9"."]* {
	depth += 1;
	strcat(str, yytext);
}

"."{2} {
	if (depth == 0) {
		fprintf(stderr, "malformed pathname\n");
		yyterminate();
	}
	depth -= 1;
	int idx = strlen(str) - 1;
	while(str[idx] == '/') {
		str[idx] = 0;
		idx--;
	}
	while(str[idx] != '/' && idx >= 0) {
		str[idx] = 0;
		idx--;
	}

	if (idx > 0)
		str[idx] = 0;
}

".""/"*


[a-zA-Z0-9"."]{1,14} {
	depth += 1;
	strcat(str, yytext);
}

"\n" {
	strcat(str, "\n");
	fprintf(stdout, str);
	memset(str, 0, strlen(str));
}

<<EOF>> {
	yyterminate();
}
%%

int yywrap() {
	return 1;
}

int main(int argc, char **argv)
{
  ++argv;
	--argc;	/* skip over program name */
	if ( argc > 0 )
	   yyin = fopen( argv[0], "r" );
	else
	   yyin = stdin;

  yylex();
	return 0;
}
