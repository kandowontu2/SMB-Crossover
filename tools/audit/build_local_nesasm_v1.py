"""Build the pinned source-recommended NESASM using the existing local GCC."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
from acquire_nesasm_source_v1 import ROOT,OUT as SOURCE,bind

OUT=ROOT/'build/nesasm-local-v1'
GCC=Path('C:/Strawberry/c/bin/gcc.exe')


def main():
    assert not(OUT/'proof.json').exists(),'Keep the compiled tool proof immutable'
    acquisition=SOURCE/'acquisition.json'
    a=json.loads(acquisition.read_text())
    assert a['commit']=='229033a4b76466b447ad47704808a4d03c493cee'
    for row in a['files']:
        assert bind(row['path'])['sha256']==row['sha256']
    make=(SOURCE/'source/Makefile').read_text()
    objects=re.search(r'OBJS\s*=\s*(.*?)(?:\n\n)',make,re.S)[1].replace('\\\n',' ')
    sources=[SOURCE/'source'/word.replace('.o','.c')for word in objects.split()]
    assert len(sources)==17 and all(p.is_file()for p in sources)
    OUT.mkdir(exist_ok=True)
    command=[str(GCC),'-O2','-std=gnu89','-fcommon','-o',str(OUT/'nesasm.exe')]+[str(p)for p in sources]
    run=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
    (OUT/'compile.log').write_text(run.stdout+run.stderr)
    assert not run.returncode,run.stderr[-3000:]
    version=subprocess.run([str(OUT/'nesasm.exe')],cwd=OUT,capture_output=True,text=True)
    (OUT/'usage.log').write_text(version.stdout+version.stderr)
    assert 'NES Assembler' in version.stdout or 'NES Assembler' in version.stderr
    result=dict(status='Pinned NESASM compiled locally from source; no downloaded executable',
        repository=a['repository'],commit=a['commit'],acquisition=bind(acquisition),tool=bind(__file__),
        compiler=bind(GCC),executable=bind(OUT/'nesasm.exe'),command=command,
        source_files=a['files'],compile_log=bind(OUT/'compile.log'),usage=bind(OUT/'usage.log'),
        portability_flags='GNU89 language mode and common-symbol behavior for original C source; source text unchanged.',
        ROM_assembly_test=False)
    (OUT/'proof.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(executable=result['executable'],proof=bind(OUT/'proof.json'))))


if __name__=='__main__':
    main()
