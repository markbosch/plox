# pLox

pLox is a `Python` implementation of the language [Lox](https://github.com/munificent/craftinginterpreters) based on the book from Robert Nystrom's [Crafting Interpreters](https://www.craftinginterpreters.com/).

The book implements the language in `Java` (Part 1) and `C` (Part 2). pLox is a `Python` 'translation' of the Java code from Part 1. Just for fun and to learn some `Python` :-). 

For more details, see: [The Lox Language](https://www.craftinginterpreters.com/the-lox-language.html)

## Interpreter

Running pLox without arguments will yield a REPL.

``` shell
python -m lox
```

REPL:

``` shell
> print "Hello, World!";
Hello, World!
>
```

Executing a file can be done by passing a file as argument.

``` shell
> python -m lox myfile.plox
```

## Examples

String variable

``` shell
> var foo = "foo";
> print foo;
foo
```

Simple addition

``` shell
> print 42 + 1337;
1379
```

Simple for-loop

``` shell
> for (var i = 0; i < 10; i = i + 1) { print i; }
0
1
.
9
```

Recursive Fibonacci function

``` shell
> fun fib(n) { if (n < 2) { return n; } return fib(n - 1) + fib(n - 2); }
> print fib(15);
610
```

Class

``` shell
> class Point { init(x, y) { this.x = x; this.y = y; } }
> var point = Point(10, 12);
> print point.x;
10
> print point.y;
12
```

Inheritance

``` shell
> class Foo { spam() { print "foo"; } }
> class Bar < Foo { spam() { super.spam(); print "bar"; } }
> var bar = Bar();
> bar.spam();
foo
bar
```