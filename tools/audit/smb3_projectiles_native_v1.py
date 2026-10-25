"""Native staged SMB3 projectile contacts, with real menu/launch/damage paths."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,sys
import numpy as np
from PIL import Image,ImageDraw
from check_tmnt_render_oa import load,address,location
from observe_chip_committed_write import lua

ROOT=Path(__file__).resolve().parents[2]


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--emulator',type=Path,required=True);p.add_argument('--variant',type=int,default=0)
    p.add_argument('--observe-baseline',action='store_true');p.add_argument('--focus',default='')
    a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT)
    out.mkdir(parents=True,exist_ok=False);b=load(a.rom)
    names=['PauseSkip','M3Weapons','M3Throw','M3AdvanceShot','M3ShotEnemies','M3DefeatEnemy',
           'HandleEnemyFBallCol','StnE','RunBowser','BowserGfxHandler','NonMaskableInterrupt',
           'IrqScrollSplit','M3DrawWorld','MetaspriteRenderLoop','M3Graphics','DrawAllMetasprites','RosterOamReady','RlNativeRenderDispatch']
    hooks={}
    for n in names:
        at=location(b,n)
        hooks[n]=dict(address=address(b,n),physical_bank=(at-16)//8192,bytes=list(b['raw'][at:at+3]))
    n='NonMaskableInterrupt';delta=int(b['syms'][n]['size'],0)-1;at=location(b,n)+delta
    hooks['NmiReturn']=dict(address=address(b,n)+delta,physical_bank=(at-16)//8192,bytes=list(b['raw'][at:at+1]))
    fixture=ROOT/'tools/audit/smb3_projectiles_native_v1.lua'
    guard_source=ROOT/'tools/audit/z2_platform_native_qa.lua';guard_text=guard_source.read_text()
    guard=guard_text[guard_text.index('local savedNmi=nil'):guard_text.index('local function seed(q)')]
    text=fixture.read_text().replace('-- NMI_GUARD_INSERT',guard)
    used=set(re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'",text))
    cases=[]
    for mode in [0,1]:
        for face in [1,2]:
            for enemy,hp,label in [(6,5,'goomba'),(2,5,'buzzy'),(12,5,'podoboo'),(45,5,'bowser-hit'),(45,1,'bowser-defeat')]:
                for kind in [1,2]:
                    cases.append(dict(name=f'{label}-{"fire" if kind==1 else "hammer"}-face{face}-mode{mode}',enemy=enemy,hp=hp,kind=kind,face=face,mode=mode))
    if a.focus:cases=[q for q in cases if a.focus in q['name']]
    assert cases
    navigation={}
    tables={name:list(b['raw'][location(b,'X5Menu'+name):location(b,'X5Menu'+name)+19])for name in ['Up','Down','Left','Right']}
    for start in range(19):
        queue=[(start,[])];seen={start}
        for node,path in queue:
            if node==16:
                navigation[str(start)]=path[0]if path else 'a';break
            for name,table in tables.items():
                nxt=table[node]
                if nxt not in seen:seen.add(nxt);queue.append((nxt,path+[name.lower()]))
        else:raise AssertionError(('Menu unreachable',start))
    cfg=dict(cases=cases,hooks=hooks,variant=a.variant,observe=int(a.observe_baseline),menu_next=navigation,
             ram={n:address(b,n) for n in used if n in b['syms']},
             smc_fields=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2])
    cfg['body_records']={};cfg['shot_records']={}
    def record(ptr,base):
        at=base+ptr;size=b['raw'][at];assert size%4==0 and size<128
        return [list(b['raw'][at+i:at+i+4])for i in range(1,size+1,4)]
    for face in ['Right','Left']:
        n='M3Frame'+face+'Lo';lo=location(b,n);hi=location(b,'M3Frame'+face+'Hi')
        base=lo-address(b,n)
        for i in range(81):
            ptr=b['raw'][lo+i]+256*b['raw'][hi+i]
            cfg['body_records'][str(ptr)]=record(ptr,base)
    for kind in ['Fire','Hammer']:
        for i in range(4):
            n='M3'+kind+str(i);ptr=address(b,n);base=location(b,n)-ptr
            cfg['shot_records'][str(ptr)]=dict(kind=1 if kind=='Fire'else 2,parts=record(ptr,base))
    cfg['body_bank']=(location(b,'M3ArtBegin')-16)//8192
    cfg['shot_bank']=(location(b,'M3WorldArtBegin')-16)//8192
    raw_chr=out/'expected-chr.bin';raw_chr.write_bytes(b['raw'][16+1048576:]);cfg['raw_chr']=raw_chr.as_posix()
    code=b['raw'];irq=location(b,'IrqScrollSplit')
    cfg['irq_scroll_stores']=[address(b,'IrqScrollSplit')+i for i in range(68-2) if code[irq+i:irq+i+3] in [bytes.fromhex('8d0520'),bytes.fromhex('8e0520')]]
    script=out/'run.lua';script.write_text('SMB3_PROJECTILES_NATIVE_CONFIG='+lua(cfg)+'\n'+text)
    with(out/'host.log').open('w')as log:
        result=subprocess.run([sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(out),'--emulator',str(a.emulator),str(script),str(a.rom.resolve()),'--timeout','150','--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    proof=json.loads((out/'proof.json').read_text())if(out/'proof.json').exists()else dict(passed=False)
    pixels=[];images=[]
    for raw in sorted(out.glob('*.argb')):
        v=np.frombuffer(raw.read_bytes(),dtype='<u4').reshape(240,256)
        rgb=np.stack(((v>>16)&255,(v>>8)&255,v&255),axis=2).astype(np.uint8)
        Image.fromarray(rgb).save(raw.with_suffix('.png'));images.append(raw.with_suffix('.png'))
        pixels.append(dict(file=raw.name,sha256=sha(raw)))
    if images:
        sheet=Image.new('RGB',(4*256,((len(images)+3)//4)*256),(24,28,36));draw=ImageDraw.Draw(sheet)
        for i,path in enumerate(images):
            with Image.open(path)as im:sheet.paste(im,(i%4*256,i//4*256+16))
            draw.text((i%4*256+2,i//4*256),path.stem,fill='white')
        sheet.save(out/'overview.png')
    proof.update(ROM_sha256=sha(a.rom),ROM_path=str(a.rom),emulator_exit=result.returncode,
                 fixture_sha256=sha(fixture),runner_sha256=sha(Path(__file__)),
                 imported_NMI_guard_source_sha256=sha(guard_source),emulator_sha256=sha(a.emulator),
                 generated_script_sha256=sha(script),physical_PPU_files=pixels,
                 passed=result.returncode==0 and proof.get('passed',False),accepted=False,goal_complete=False)
    (out/'native-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(dict(passed=proof['passed'],emulator_exit=result.returncode,cases=len(proof.get('cases',[])),pixels=len(pixels),output=str(out))),flush=True)
    raise SystemExit(0 if proof['passed']else 1)


if __name__=='__main__':main()
