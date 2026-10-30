"""Remove the redundant false-owner Rogue UI trip; preserve owned paths."""
from pathlib import Path
import json
import subprocess
import sys

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
import prepare_rogue_menu_priority_v1 as priority
import prepare_rogue_current_parity_v1 as parity

O=R/'build/rogue-current-menu-v8'
U=R/'build/rogue-dawn-host-ui-v1'


def source(out):
    deps=priority.source(out)
    compiled=parity.base.dependencies(U/'weapon-object.dep')
    ui=next(p for p in compiled if p.name=='rogue_dawn_host_ui_v1.s')
    imports=next(p for p in compiled if p.name=='ui-imports.inc')
    text=parity.once(ui.read_text(),' WxTail RdLifeUi',' WxTail X5BounceUiDispatch')
    parity.base.put(out/'src/rogue_dawn_host_ui_v1.s',text)
    parity.base.put(out/'src/ui-imports.inc',imports.read_text()+'\n.import X5BounceUiDispatch\n')
    entry=out/'entrypoint.s'
    assert '.export X5BounceUiDispatch'not in entry.read_text()
    parity.base.put(entry,entry.read_text()+'\n.export X5BounceUiDispatch\n')
    return deps+[Path(__file__).resolve(),Path(priority.__file__),ui,imports,
                 out/'src/rogue_dawn_host_ui_v1.s',out/'src/ui-imports.inc',
                 R/'build/rogue-current-menu-v7/capacity-negative.json',
                 R/'build/rogue-current-menu-v7/driver-failed-build.py']


def link(cmd,out):
    parity.link(cmd,out)
    original=json.loads((U/'build.json').read_text())['commands'][0]
    build=original.copy()
    build[1:1]=['-I',str(out/'src')]
    build[build.index('-o')+1]=str(out/'rogue-aux.o')
    build[build.index('--create-full-dep')+1]=str(out/'rogue-aux.dep')
    p=subprocess.run(build,cwd=R,capture_output=True,text=True)
    parity.base.put(out/'aux-build.json',json.dumps(dict(command=build,returncode=p.returncode,
                    stdout=p.stdout,stderr=p.stderr),indent=2)+'\n')
    assert p.returncode==0,p.stderr[-6000:]
    assert cmd.count(str(U/'weapon-object.o'))==1
    cmd[cmd.index(str(U/'weapon-object.o'))]=str(out/'rogue-aux.o')
    deps=parity.base.dependencies(out/'rogue-aux.dep')
    assert out/'src/rogue_dawn_host_ui_v1.s'in deps
    assert out/'src/ui-imports.inc'in deps
    parity.EXTRA.extend(deps+[out/'aux-build.json',out/'rogue-aux.dep',U/'build.json'])


if __name__=='__main__':
    parity.base.main(output=O,source_hook=source,link_hook=link,
        extra_dependencies=[Path(__file__).resolve(),O/'backend-composition.json'])
