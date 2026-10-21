"""Real Mesen native firebar producer with actual Sophia body publication."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import stat
import sys

R = Path(__file__).resolve().parents[2]
D = R / 'build/verification/root49-sophia-source-body-hs'
H = R / 'build/verification/agent-lsr-link-firebar-h'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mapper',required=True,choices=['mmc3','mmc5'])
    args = parser.parse_args()
    folder = D / ('native-hp-'+args.mapper)
    assert not folder.exists()
    imfile = R / 'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py'
    spec = importlib.util.spec_from_file_location('sophia_native_metadata', imfile)
    m = importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    rom = D / 'source/build' / ('smb-crossover-'+args.mapper+'.nes')
    im = m.Image(rom)
    core = D / 'component-hp.lua'
    parent = H / 'component-d.lua'
    assert sha(parent) == 'fdb31426a57536acc035bdc8071c4a14fe28f7bd3e0ea83c3784bfef3f603dee'
    body = parent.read_text()
    a = " for i=0,5 do w('Enemy_Flag',0,i)end"
    b = a + "\n for _,n in ipairs({'XgWall','XgCeiling','XgWallContact','XgWallLock','XgHoverActive','MmDeathFlag','XgRise'})do w(n,0)end"
    assert body.count(a)==1;body=body.replace(a,b)
    a = "  check(pre.pieceY==active.pieceY,'SETUP actual native piece Y');"
    b = "  if active.char==11 then check(pre.top==129 and pre.bottom==144,'Actual Sophia flat body projection')end\n"+a
    assert body.count(a)==1;body=body.replace(a,b)
    if core.exists():assert core.read_text()==body
    else:core.write_text(body)
    proc=im.sym('ProcFirebar');h=im.hook('ProcFirebar');entry=im.hook('FirebarCollision')['address']
    size=im.sym('DrawFirebar_Collision')['val']-proc['val']
    buf=im.raw[h['rom_offset']:h['rom_offset']+size];needle=bytes([0x20,entry&255,entry>>8])
    calls=[proc['val']+k+3 for k in range(len(buf)-2)if buf[k:k+3]==needle]
    assert len(calls)==1
    hooks={n:im.hook(label)for n,label in [('entry','FirebarCollision'),('chg','ChgSDir'),('injury','ForceInjury')]}
    hooks['after']=im.hook('ProcFirebar',delta=calls[0]-proc['val'])
    for n,h in hooks.items():h['name']=n
    interrupts=[]
    for n in ['NonMaskableInterrupt','IrqScrollSplit']:
        h=im.hook(n);h.update(name=n,change=1);interrupts.append(h)
        h=im.hook(n,delta=im.sym(n)['size']-1);assert h['bytes'][0]==0x40
        h.update(name=n+'-RTI',change=-1);interrupts.append(h)
    cases=[]
    def add(name,**kw):
        c=dict(name=name,char=11,mode=0,x=112,dir=1,dx=0,pieceY=107,reject=True,admitted=True)
        c.update(kw);cases.append(c)
    for mode in [0,1]:
        for direction in [1,2]:
            for yy in [105,106,107,115,116,117,129,136,143]:
                admitted=any(abs(v-yy)<8 for v in [112,124,136])
                add('flat-%s-facing%s-y%s'%(mode,direction,yy),mode=mode,dir=direction,
                    x=112 if direction==1 else 140,pieceY=yy,admitted=admitted,
                    reject=admitted and (yy+13<129 or yy-3>144))
    for dx in [-8,-7,7,8]:add('horizontal-edge-'+str(dx),dx=dx,admitted=abs(dx)<8,reject=abs(dx)<8)
    for char in [0,1,2,3,5,10]:add('foreign-'+str(char),char=char,reject=False)
    total=owned=0;todo=[R]
    while todo:
        with os.scandir(todo.pop())as entries:
            for e in entries:
                try:s=e.stat(follow_symlinks=False)
                except FileNotFoundError:continue
                if getattr(s,'st_file_attributes',0)&0x400:continue
                if stat.S_ISDIR(s.st_mode):todo.append(e.path)
                elif stat.S_ISREG(s.st_mode):
                    total+=s.st_size
                    if 'root49-sophia-source-body-hl' in e.path:owned+=s.st_size
    assert total+20000000<60000000000 and owned+20000000<500000000,(total,owned)
    folder.mkdir()
    cfg=dict(out=folder.as_posix()+'/',cases=cases,candidate=True,interrupts=interrupts,**hooks)
    wrapper=D/('wrapper-hp-'+args.mapper+'.lua')
    wrapper.write_text('L='+m.lua(im.ram)+'\nCFG='+m.lua(cfg)+'\ndofile('+m.lua(core.as_posix())+')\n')
    bind=dict(status='PREPARED_NATIVE_COMPONENT_NOT_ROUTE',mapper=args.mapper,ROM=im.metadata(),
        source_preparation_sha256=sha(D/'preparation.json'), core_sha256=sha(core),
        wrapper_sha256=sha(wrapper), cfg=cfg, workspace_bytes=total, phase_bytes=owned,
        script_sha256=sha(__file__))
    (folder/'binding.json').write_text(json.dumps(bind,indent=2)+'\n')
    sys.path.insert(0,str(R/'tools'));import run_mesen
    rc=run_mesen.run(wrapper,rom,timeout=180,emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
    bind.update(exit=rc,result=json.loads((folder/'result.json').read_text())if(folder/'result.json').exists()else None,
        files={p.name:sha(p)for p in folder.iterdir()if p.is_file()})
    (folder/'actual.json').write_text(json.dumps(bind,indent=2)+'\n')
    print(json.dumps(dict(exit=rc,result=bind['result'],path=str(folder))))
    raise SystemExit(rc)


if __name__=='__main__':main()
