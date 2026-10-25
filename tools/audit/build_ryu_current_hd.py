"""Fit the reviewed Ryu predicate onto GO using an unchanged-size tail dispatch."""
from pathlib import Path
import argparse,configparser,hashlib,importlib.util,json,re,shutil,subprocess
R=Path(__file__).resolve().parents[2];V=R/'build/verification';O=V/'ryu-current-hd';C=O/'source'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    global O,C
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--tag',default='ryu-current-hl');args=parser.parse_args()
    assert re.fullmatch('[a-z0-9-]+',args.tag);O=V/args.tag;C=O/'source'
    parent=R/'build/checkpoints/weapons-source-go/manifest.json';p=json.loads(parent.read_text())
    assert all(sha(R/f'build/smb-crossover-{m}.nes')==h for m,h in p['ROMs'].items())
    assert not O.exists();C.mkdir(parents=True)
    seed=json.loads((R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json').read_text())
    names=set(seed['source_hashes'])|{q.relative_to(R).as_posix()for q in(R/'src').rglob('*')if q.is_file()}
    before={n:sha(R/n)for n in names}
    for n in names:
        d=C/n;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/n,d)
    for n in seed['generated11']:
        d=C/'build/generated'/n;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/'build/generated'/n,d)
    old=V/'agent49-ryu-motion-h-a/source-f/src/ryu_side_overlap.s'
    assert sha(old)=='a3e07e833674a46570a8909efbd113dbed2ecfa5e4a9bdaf02edf3a30c0f9927'
    leaf=old.read_text()+'''
; GO has six extra cold-init bytes for Cheats. Retain its original15-byte
; SAMUS gate and42-byte stomp policy; perform the C-only dispatch in this bank.
.pushseg
.segment "RYU_SIDE_COLD"
.proc RyuSourceSideDispatch
  ; These are the frozen predicate's first source guards, before its costly
  ; scratch save. The sole public caller consumes only carry.
  cpy RyWallResolved
  beq Done
  lda Player_State
  beq Native
  lda RyWallSide
  beq Predicate
  sec
Done:
  rts
Predicate:
  jsr RyuSourceSideAdmission
  bcs Done
Native:
  farcall SamusStopAtWallBanked::NativeGuest
  rts
.endproc
.assert * <= $ba00,error,"Ryu admission and dispatch exceed reserved768bytes"
.popseg
'''
    (C/'src/ryu_side_overlap.s').write_text(leaf)
    q=C/'src/samus_collision_ram.s';s=q.read_text();a=s.index('.proc SamusRyuWallHandled\n');b=s.index('.endproc',a)+len('.endproc')
    s=s[:a]+'''.proc SamusRyuWallHandled
  ; Sole predecessor supplies Y=R0 and consumes C only. No incoming A is
  ; required by the predicate or NativeGuest. Avoid the unused SafecallA save.
  lda #.lobyte(RyuSourceSideDispatch)
  SMC_StoreLowByte FarcallJmpTarget, a
  lda #.hibyte(RyuSourceSideDispatch)
  SMC_StoreHighByte FarcallJmpTarget, a
.if ::MAPPER_MMC5
  lda #.bank(RyuSourceSideDispatch) | MMC5_PRG_ROM
.else
  lda #.bank(RyuSourceSideDispatch)
.endif
  jmp FarCallCommon
  .assert *-SamusRyuWallHandled=15,error,"Keep the original SAMUS gate span"
.endproc'''+s[b:];q.write_text(s)
    q=C/'src/entrypoint.s';q.write_text(q.read_text()+'\n.if ::ENABLE_CROSSOVER\n.include "ryu_side_overlap.s"\n.endif\n')
    q=C/'smb1base.cfg';s=q.read_text();anchor='    SCORE_POPUP_COLD: load=XG_SOPHIA_A_TAIL_MEM, type=ro, optional=yes, start=$bfc0;';assert s.count(anchor)==1
    q.write_text(s.replace(anchor,'    RYU_SIDE_COLD: load=XG_SOPHIA_A_TAIL_MEM, type=ro, optional=yes, start=$b700;\n'+anchor))
    prep=dict(parent_manifest_sha256=sha(parent),parent_ROMs=p['ROMs'],source_before=before,predicate_source_sha256=sha(old),modified_files={q.relative_to(C).as_posix():sha(q)for q in C.rglob('*')if q.is_file()and'build'not in q.relative_to(C).parts and(not(R/q.relative_to(C)).exists()or sha(q)!=sha(R/q.relative_to(C)))},scope='Private GO+literal frozen725B Ryu predicate, C-only dispatch with source guards, original15B gate. Stomp policy and cold Cheats initialization untouched. No admission or route transfer claim.',goal_complete=False)
    (O/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n')
    cfg=configparser.ConfigParser();cfg.optionxform=str;cfg.read(C/'build_options.ini');options={n:v for sec in cfg.values()for n,v in sec.items()}
    spec=importlib.util.spec_from_file_location('ryu_hd_image',V/'agent49g-samus-crouch-fix-proposal-b/image.py');im=importlib.util.module_from_spec(spec);spec.loader.exec_module(im)
    builds=[]
    for mapper,base in [('mmc3',False),('mmc5',False),('mmc3',True),('mmc5',True)]:
        stem=f'smb-crossover-{mapper}'+('-baseline'if base else'');obj=C/'build/objects'/stem;obj.mkdir(parents=True)
        for n in('main.c','entrypoint.s'):shutil.copyfile(C/'src'/n,obj/n)
        opts=dict(options,MAPPER_MMC3=str(int(mapper=='mmc3')),MAPPER_MMC5=str(int(mapper=='mmc5')),ENABLE_CROSSOVER=str(int(not base)))
        cmd=[str(R/'tools/Windows/cc65/bin/cl65.exe'),'--cpu','6502x','-t','nes','-g','-Oisr','-vm','-T','-C','smb1base.cfg','--ld-args',f'--dbgfile,build/{stem}.dbg','--include-dir','.','--asm-include-dir','.','--asm-include-dir','src','--bin-include-dir','.','-m',f'build/{stem}.map','-Ln',f'build/{stem}.lbl','-o',f'build/{stem}.nes']
        for n,v in opts.items():cmd+=['--asm-define',f'{n}={v}','-D',f'{n}={v}']
        cmd += [str(obj/'main.c'),str(obj/'entrypoint.s')]
        with(O/(stem+'.log')).open('wb')as f:z=subprocess.run(cmd,cwd=C,stdout=f,stderr=subprocess.STDOUT)
        assert z.returncode==0,stem
        a=(R/f'build/{stem}.nes').read_bytes();b=(C/f'build/{stem}.nes').read_bytes();layout={}
        if base:assert a==b
        else:
            old,new=im.Image(R/f'build/{stem}.nes'),im.Image(C/f'build/{stem}.nes')
            assert old.ram==new.ram
            globals=lambda i:{(s['name'],s['val'])for s in i.data['sym']if s.get('scope')==1 and'seg'in s and'val'in s}
            assert globals(old)<=globals(new),'All existing public addresses must remain fixed'
            assert a[:16]==b[:16]and a[16+512*1024:]==b[16+512*1024:]
            banks=sorted({(i-16)//8192 for i,(x,y)in enumerate(zip(a,b))if x!=y});assert banks==[10,36],banks
            def code(i,n):
                s=i.sym(n);g=i.segs[s['seg']];o=g['ooffs']+s['val']-g['start'];return i.raw[o:o+s['size']]
            frozen=im.Image(V/f'agent49-ryu-motion-h-a/source-f/build/{stem}.nes')
            assert code(frozen,'RyuSourceSideAdmission')==code(new,'RyuSourceSideAdmission')
            assert code(old,'GuestSourceStompPolicy')==code(new,'GuestSourceStompPolicy')
            layout=dict(changed_banks=banks,all_old_global_PC_RAM_header_CHR_unchanged=True,predicate_literal_frozen_F=True,predicate_size=new.sym('RyuSourceSideAdmission')['size'],dispatch_size=new.sym('RyuSourceSideDispatch')['size'],gate_size=new.sym('SamusRyuWallHandled')['size'])
        builds.append(dict(stem=stem,ROM_sha256=sha(C/f'build/{stem}.nes'),layout=layout));print(stem,'PASS',layout,flush=True)
    assert before=={n:sha(R/n)for n in names}
    (O/'build.json').write_text(json.dumps(dict(passed=True,builds=builds,installed=False,goal_complete=False),indent=2)+'\n')


if __name__=='__main__':main()
