"""Source-relink immediate Kirby suction and original inhale friction privately."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_ff_current_component_v2 import qualified
from private_build_outputs_v1 import validate
from check_tmnt_render_oa import address,location
from prepare_cv3_dmc_mirror import prepare as mirror
J=R/'build/kirby-owner-main-1101-v2';O=R/'build/kirby-approach-owner-1101-v3'
PIN='c864e46a8f333ab7a936c8d8f330944041a3eff12bc6dd4d9ba96892144ff3c7'
DONOR=Path("C:/NES/Kirby's Adventure (USA) (Rev 1).nes")
DPIN='a7a742f5288cd4ab220f530ee7c8d0e3714b8bf107e89c9bf03039217fec5829'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def change(text,old,new):
    assert text.count(old)==1,old[:80]
    return text.replace(old,new)

HELPER='''
; Original bank18 ACF6 Ontick calls bank21 8049/872A every update,
; including the eight-update pose opening. Ground friction is14/256.
; Existing underwater B is the water gun, and Up/Down are float/slide.
.proc KbInhaleFriction
 lda KbVariant
 ora KbCopy
 ora KbMouth
 ora KbFloat
 ora MmUnderwater
 bne Ordinary
 lda KbAction
 cmp #5
 beq Ordinary
 lda SavedJoypadBits
 and #B_Button|Up_Dir|Down_Dir
 cmp #B_Button
 bne Ordinary
 lda #0
 sta KbDash
 sta KbDashWindow
 sec
 rts
Ordinary:
 lda KbDashWindow
 beq Done
 dec KbDashWindow
Done:
 clc
 rts
.endproc
.assert *-KbInhaleFriction=53,lderror,"Funded53B inhale selector changed"
.res 1,$ea
'''

def run(cmd):
    g=validate(cmd,O,cwd=R);p=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
    q=dict(command=cmd,guard=g,returncode=p.returncode,stderr=p.stderr)
    assert p.returncode==0,p.stderr
    return q

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--reuse-compiled-object',action='store_true');args=ap.parse_args()
    assert sha(J/'candidate.nes')==PIN and sha(DONOR)==DPIN
    old=qualified(J/'candidate.nes');O.mkdir(exist_ok=True)
    source=R/'build/bt-ready-menu-1031-v2/joint/src/kirby_core.s';core=source.read_text()
    assert core==(R/'src/kirby_core.s').read_text()
    core=change(core,'Horizontal:\n  lda KbDashWindow\n  jeq Direction\n  dec KbDashWindow\nDirection:',
        'Horizontal:\n  jsr KbInhaleFriction\n  jcs Friction\n  .res 3,$ea ; preserve Direction and all subsequent public PCs\nDirection:')
    start=core.index('.proc KbMovement\n');end=core.index('.endproc',start);part=core[start:end]
    short=[('jeq','Dry',1),('jne','Ordinary',1),('jeq','NoHurt',1),('jeq','NoHeal',1),('jeq','NoCooldown',1),('jne','AirSync',1),('jeq','Input',2),('jne','WallReady',1),('jeq','WallReady',1),('jeq','Controlled',1),('jeq','DryInput',1),('jeq','NotSlide',2),('jne','NotSlide',2),('jne','NotSliding',1),('jeq','EndSlide',1)]
    assert sum(n for _,_,n in short)==18
    for op,target,n in short:
      needle=f'  {op} {target}\n';assert part.count(needle)==n,(op,target,part.count(needle));part=part.replace(needle,f'  b{op[1:]} {target}\n')
    core=core[:start]+part+HELPER+core[end:]
    core+='\n.export KbInhaleFriction\nKbInhaleFriction=KbMovement::KbInhaleFriction\n.assert .sizeof(KbMovement)=1519,lderror,"Original Movement public span moved"\n'
    weapons=change((J/'kirby_weapons.s').read_text(),
      'Pull:\n  lda KbActionAge\n  jne Update\n  jsr Suction\n  jmp Update\nStopInhale:',
      'Pull:\n  ; Original eight-update wait changes the pose, not suction collision.\n  jsr Suction\n  jmp Update\n  .res 8,$ea ; unreachable original-age-gate footprint\nStopInhale:')
    entry=R/'build/hogan-thomas-current/src/kirby.s';assert entry.read_text().endswith('.include "kirby_world_palette.s"\n')
    previous={n:sha(O/n)for n in['kirby_core.s','kirby_weapons.s','kirby.s']if(O/n).exists()}
    (O/'kirby_core.s').write_text(core);(O/'kirby_weapons.s').write_text(weapons)
    (O/'kirby.s').write_text(entry.read_text())
    cmd=json.loads((J/'main-build.json').read_text())['command'].copy();cmd[1:1]=['-I',str(O)]
    for key,n in[('-o','main.o'),('--create-full-dep','main.dep')]:cmd[cmd.index(key)+1]=str(O/n)
    if args.reuse_compiled_object:
      receipt=json.loads((O/'main-build.json').read_text());assert receipt['command']==cmd and receipt['returncode']==0
      assert previous=={n:sha(O/n)for n in['kirby_core.s','kirby_weapons.s','kirby.s']}
      receipt.update(reused_owned_unqualified_object=True,object_sha256=sha(O/'main.o'),source_hashes=previous)
    else:receipt=run(cmd)
    (O/'main-build.json').write_text(json.dumps(receipt,indent=2)+'\n')
    dep=(O/'main.dep').read_text().replace('\\ ',' ').replace('\\','/')
    assert all(str(O).replace('\\','/')+'/'+n in dep for n in['kirby.s','kirby_core.s','kirby_weapons.s'])
    cfg=(J/'candidate.cfg').read_text().replace(str(J).replace('\\','/'),str(O).replace('\\','/')).replace(str(J),str(O))
    (O/'candidate.cfg').write_text(cfg)
    for ref in re.findall(r'file="([^"]+)"',cfg):
      if ref and ref!='%O':
       p=Path(ref).resolve();assert p.is_relative_to(O);p.parent.mkdir(parents=True,exist_ok=True)
    cmd=json.loads((J/'link.json').read_text())['command'].copy()
    for i,arg in enumerate(cmd):
      if arg==str(J/'main.o'):cmd[i]=str(O/'main.o')
    for key,n in[('-C','candidate.cfg'),('-o','candidate.nes'),('-Ln','candidate.lbl')]:cmd[cmd.index(key)+1]=str(O/n)
    cmd[cmd.index('--ld-args')+1]='--dbgfile,'+str(O/'candidate.dbg')
    if'-m'in cmd:cmd[cmd.index('-m')+1]=str(O/'candidate.map')
    (O/'link.json').write_text(json.dumps(run(cmd),indent=2)+'\n')
    dbg=O/'candidate.dbg';keep={b'version',b'info',b'file',b'lib',b'mod',b'seg',b'scope',b'sym'}
    dbg.write_bytes(b''.join(x for x in dbg.read_bytes().splitlines(keepends=True)if x.split(b'\t',1)[0]in keep))
    mirror(R,O/'candidate.nes');new=qualified(O/'candidate.nes')
    spans=[('1519B original Movement source with18 near branches funding53B selector plus1EA',location(old,'KbMovement'),1519),('Pull fixed14B',location(old,'KbWeapons::Pull'),14)]
    # InjuryStart is the one other procedure using a private Movement leaf.
    at=location(old,'KbInjuryStart');size=int(old['syms']['KbInjuryStart']['size'],0)
    target=address(old,'KbMovement::NegateX');dest=address(new,'KbMovement::NegateX');pat=bytes([0x20,target&255,target>>8])
    body=old['raw'][at:at+size];assert body.count(pat)==1;operand=at+body.index(pat)+1
    assert target>>8==dest>>8 and new['raw'][operand-1:operand+2]==bytes([0x20,dest&255,dest>>8])
    spans.append(('actual KbInjuryStart JSR NegateX low operand relocation',operand,1))
    changed=[i for i,(a,b)in enumerate(zip(old['raw'],new['raw']))if a!=b]
    assert len(old['raw'])==len(new['raw']) and all(any(lo<=i<lo+n for _,lo,n in spans)for i in changed)
    moved={n for n,s in old['syms'].items()if n not in new['syms']or any(s.get(k)!=new['syms'][n].get(k)for k in['val','seg'])}
    assert all(n.startswith('KbMovement::')for n in moved),sorted(moved)[:20]
    layouts=[]
    for sid,s in old['segs'].items():
      z=new['segs'][sid];changes={k:[s.get(k),z.get(k)]for k in['name','start','size','ooffs','addrsize','type']if s.get(k)!=z.get(k)}
      assert not changes,(s['name'],changes)
    raw=DONOR.read_bytes();r21=raw[16+0x21*8192:16+0x22*8192];r18=raw[16+0x18*8192:16+0x19*8192]
    assert r18[0xcd7:0xcf6].hex()=='1a46881a11e10509d08c9d0d021e0d040108f6ac18d04bde01d8dc8f009009'
    assert r18[0xcf6:0xcf9]==bytes.fromhex('204980')and r18[0xd24:0xd2f]==bytes.fromhex('a9002052ad202fad4c5b80')
    assert r21[0x49:0x5b].hex()=='202a8720748820cd952021902016904c4a90'
    assert r21[0x72a:0x73e].hex()=='201281aef705f002a201bc3c87a9004c97850a13'
    donor=dict(ROM_sha256=DPIN,primary_annotation='https://github.com/Nathan-R-Og/kirbyadventure/blob/master/src/prg/bank18.asm',script_bank18_ACD7_ACF6=r18[0xcd7:0xcf6].hex(),immediate_Ontick_ACF6_AD2F=r18[0xcf6:0xd2f].hex(),bank21_8049_805B=r21[0x49:0x5b].hex(),bank21_872A_873E=r21[0x72a:0x73e].hex(),friction_kernel_8597_8629=r21[0x597:0x629].hex(),friction_table_indices=list(r21[0x73c:0x73e]),friction=[r21[0x64e+i]for i in r21[0x73c:0x73e]],interpretation='WAIT8 applies pose; ONTICK calls velocity friction and publishes inhale hitbox every tick. Ground has14/256 drag and no directional acceleration;9 is water context, while port waterB is independently its existing gun.')
    assert donor['friction']==[14,9]
    (O/'donor-inhale-witness.json').write_text(json.dumps(donor,indent=2)+'\n')
    # Compact rollback permits exact baseline comparison without another ROM/DBG.
    changes=[];start=None
    for i in changed:
      if start is None:start=prev=i
      elif i==prev+1:prev=i
      else:changes.append(dict(start=start,old=old['raw'][start:prev+1].hex(),new=new['raw'][start:prev+1].hex()));start=prev=i
    if start is not None:changes.append(dict(start=start,old=old['raw'][start:prev+1].hex(),new=new['raw'][start:prev+1].hex()))
    (O/'rollback-witness.json').write_text(json.dumps(dict(original_ROM_sha256=PIN,changes=changes,moved_symbols={},added_symbols=[n for n in new['syms']if n not in old['syms']]),indent=2)+'\n')
    q=dict(passed=True,source_owner_relinked=True,native_emulator=False,installed=False,base_ROM_sha256=PIN,ROM_sha256=sha(O/'candidate.nes'),changed_bytes=len(changed),source_intervals=[dict(role=n,start=lo,bytes=size)for n,lo,size in spans],existing_public_symbol_addresses_exact=True,moved_internal_symbols=sorted(moved),segment_changes=layouts,other_owner_header_CHR_bytes_exact=True,source_friction_selector_bytes=53,near_branch_funding=dict(branches=18,bytes=54,selector=53,pad=1),all_c864_Kirby_fixes_retained=True,
      bindings={str(p.resolve()):sha(p)for p in[Path(__file__),source,entry,R/'tools/prepare_cv3_dmc_mirror.py',J/'candidate.nes',J/'candidate.dbg',J/'main-build.json',J/'link.json',J/'candidate.cfg',J/'kirby_weapons.s',J/'kirby_dispatch.s',J/'doki-component.o',O/'kirby.s',O/'kirby_core.s',O/'kirby_weapons.s',O/'main-build.json',O/'main.dep',O/'link.json',O/'candidate.cfg',O/'candidate.nes',O/'candidate.dbg',O/'rollback-witness.json',O/'donor-inhale-witness.json']})
    (O/'owner-link.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))

if __name__=='__main__':main()
