import dis, sys, os, io, types, marshal, argparse, opcode


def _load(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".py":
        with open(path, "r", encoding="utf-8") as f:
            return compile(f.read(), path, "exec")
    if ext == ".pyc":
        with open(path, "rb") as f:
            f.read(16)
            data = f.read()
        try:
            return marshal.loads(data)
        except ValueError:
            return marshal.loads(data[8:])
    sys.exit(f"error: unsupported extension '{ext}'")


def _dump(code, name=None):
    print(f"\n[{name or code.co_name}]")
    for i in dis.get_instructions(code):
        val = (f"<code '{i.argval.co_name}'>" if isinstance(i.argval, types.CodeType)
               else repr(i.argval)) if i.argval is not None else ""
        print(f"  {i.opname:<30} {val}" if val else f"  {i.opname}")
    for c in code.co_consts:
        if isinstance(c, types.CodeType):
            _dump(c)


def _dump_all():
    print(f"Python version: {sys.version.split()[0]}\n")
    print(f"[all opcodes — {len(opcode.opmap)} total]\n")
    for name, code in sorted(opcode.opmap.items(), key=lambda x: x[1]):
        suffix = "  (arg)" if code >= opcode.HAVE_ARGUMENT else ""
        print(f"  {name:<35} {code}{suffix}")


def _repl():
    print(f"Python version: {sys.version.split()[0]}\n")
    while True:
        lines = []
        try:
            while True:
                line = input("... " if lines else ">>> ")
                if line.strip().lower() in ("q", "quit", "exit"):
                    return
                if not line and lines:
                    break
                lines.append(line)
        except (EOFError, KeyboardInterrupt):
            return
        src = "\n".join(lines)
        if src.strip():
            try:
                _dump(compile(src, "<snippet>", "exec"), "<snippet>")
            except SyntaxError as e:
                print(f"SyntaxError: {e}")


def main():
    p = argparse.ArgumentParser(prog="opcode_dumper")
    p.add_argument("file",       nargs="?",          help=".py or .pyc file")
    p.add_argument("-s", "--snippet", metavar="CODE", help="inline source snippet")
    p.add_argument("-r", "--repl",    action="store_true")
    p.add_argument("-a", "--all",     action="store_true", help="list every opcode")
    p.add_argument("-o", "--out",     metavar="PATH",  help="write output to file")
    args = p.parse_args()

    buf = None
    if args.out:
        buf, sys.stdout = io.StringIO(), io.StringIO()

    if args.all:
        _dump_all()
    elif args.repl:
        _repl()
    elif args.snippet:
        try:
            print(f"Python version: {sys.version.split()[0]}")
            _dump(compile(args.snippet, "<snippet>", "exec"), "<snippet>")
        except SyntaxError as e:
            sys.exit(f"SyntaxError: {e}")
    elif args.file:
        if not os.path.isfile(args.file):
            sys.exit(f"error: {args.file}: no such file")
        print(f"Python version: {sys.version.split()[0]}")
        _dump(_load(args.file), "<module>")
    else:
        p.print_help()

    if args.out:
        out = sys.stdout.getvalue()
        sys.stdout = buf
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"written to {args.out}")


if __name__ == "__main__":
    main()
          
