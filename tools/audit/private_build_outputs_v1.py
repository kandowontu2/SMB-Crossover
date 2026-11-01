"""Reject cc65 recipes that could write outside a new private build root.

Validate BEFORE invoking the compiler/linker. Inherited command logs describe
their original outputs; path substitution alone is not sufficient isolation.
"""
from pathlib import Path
import re


class UnsafeBuildOutput(ValueError):pass


def _inside(value,root,cwd,kind):
    value=str(value)
    if not value or '%'in value or value.startswith('@'):
        raise UnsafeBuildOutput(f'Unresolved {kind}: {value!r}')
    path=Path(value)
    if not path.is_absolute():path=Path(cwd)/path
    path=path.resolve();root=Path(root).resolve()
    if path==root or not path.is_relative_to(root):
        raise UnsafeBuildOutput(f'{kind} escapes private root: {path}')
    return str(path)


def validate(command,private_root,*,cwd):
    """Return actual declared outputs, or raise without executing anything.

    Supports ca65 assembly and cl65/ld65 object-only links. Response files,
    implicit compilation and unknown linker pass-through options fail closed.
    MEMORY file outputs from the actual linker config are checked as well.
    """
    try:
        from .build_storage_guard_v1 import preflight
    except ImportError:
        from build_storage_guard_v1 import preflight
    preflight(private_root=private_root,reserved_bytes=32_000_000,reserved_files=16)
    args=[str(v)for v in command]
    if not args:raise UnsafeBuildOutput('Empty command')
    tool=Path(args[0]).stem.lower()
    if tool not in['ca65','cl65','ld65']:
        raise UnsafeBuildOutput(f'Unsupported build tool: {tool}')
    if any(v.startswith('@')for v in args[1:]):
        raise UnsafeBuildOutput('Response files need explicit expansion before validation')
    outputs=[];configs=[]
    flags={'-o','--output','--create-dep','--create-full-dep','-Ln','--dbgfile',
           '--mapfile','-m','-l','--listing'}
    i=1
    while i<len(args):
        arg=args[i]
        if arg in flags:
            if i+1==len(args):raise UnsafeBuildOutput(f'Missing value after {arg}')
            outputs.append(dict(kind=arg,path=_inside(args[i+1],private_root,cwd,arg)))
            i+=2;continue
        if arg in['-C','--config']:
            if i+1==len(args):raise UnsafeBuildOutput(f'Missing value after {arg}')
            p=Path(args[i+1]);configs.append(p if p.is_absolute()else Path(cwd)/p)
            i+=2;continue
        if arg=='--ld-args':
            if i+1==len(args):raise UnsafeBuildOutput('Missing --ld-args value')
            values=args[i+1].split(',');j=0
            while j<len(values):
                flag=values[j]
                if flag not in flags or j+1==len(values):
                    raise UnsafeBuildOutput(f'Unclassified linker passthrough: {args[i+1]}')
                outputs.append(dict(kind='--ld-args '+flag,path=_inside(values[j+1],private_root,cwd,flag)))
                j+=2
            i+=2;continue
        matched=False
        for flag in flags:
            if arg.startswith(flag+'='):
                outputs.append(dict(kind=flag,path=_inside(arg[len(flag)+1:],private_root,cwd,flag)))
                matched=True;break
        if matched:i+=1;continue
        if arg.startswith('-Wl'):
            raise UnsafeBuildOutput('Expand -Wl outputs before validation')
        if tool in['cl65','ld65']and not arg.startswith('-')and Path(arg).suffix.lower()in['.s','.asm','.c','.cc','.cpp']:
            raise UnsafeBuildOutput('Use explicit assembly commands; implicit compile outputs are not isolated')
        i+=1
    if not any(o['kind']in['-o','--output']for o in outputs):
        raise UnsafeBuildOutput('An explicit private primary output is required')
    if tool in['cl65','ld65']:
        if len(configs)!=1:raise UnsafeBuildOutput('Exactly one explicit linker config is required')
        cfg=configs[0].resolve()
        # Read-only external configs are allowed only when every named file
        # output in them is private. Never rewrite a frozen original config.
        source=cfg.read_text()
        source=re.sub(r'#[^\n]*','',source)
        for match in re.finditer(r'\bfile\s*=\s*("[^"]*"|[^,;\s}]+)',source):
            value=match.group(1).strip('"')
            if value in['','%O']:continue
            outputs.append(dict(kind='MEMORY file',path=_inside(value,private_root,cwd,'MEMORY file')))
    return dict(tool=tool,private_root=str(Path(private_root).resolve()),outputs=outputs,
                outputs_validated_before_execution=True)
