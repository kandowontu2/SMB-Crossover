"""Relink one actual source owner with a private Kirby override and1B pad."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from private_build_outputs_v1 import validate
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
from prepare_kirby_contact_repair_1101_v1 import repair_source
from prepare_cv3_dmc_mirror import prepare as prepare_mirror
from prepare_kirby_body_ingress_1101_v2 import repair_body_boundary,repair_body_guard,repair_red_range
O=R/'build/kirby-owner-main-1101-v2';BASE=R/'build/karnov-host-resource-base-1101-v1';V1=R/'build/kirby-inhale-shell-fix-1101-v1'
PIN='99bf88c8d971f1305f965a21833703c7a11aafa6a24febd9f3bfb7c87ba4bbda';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def run(cmd):
    guard=validate(cmd,O,cwd=R);p=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
    row=dict(command=cmd,guard=guard,returncode=p.returncode,stderr=p.stderr);assert p.returncode==0,p.stderr;return row

def ranges(old,new):
    starts=[];at=None
    for i,(a,b)in enumerate(zip(old,new)):
        if a!=b and at is None:at=i
        if a==b and at is not None:starts.append((at,i));at=None
    if at is not None:starts.append((at,len(old)))
    return starts

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--reuse-compiled-object',action='store_true');args=ap.parse_args()
    assert sha(BASE/'candidate.nes')==PIN;old=qualified(BASE/'candidate.nes');assert hashlib.sha256(old['raw']).hexdigest()==PIN
    O.mkdir(parents=True,exist_ok=True);actual=R/'build/bt-ready-menu-1031-v2/joint/src/kirby_weapons.s';canonical=R/'src/kirby_weapons.s'
    negative=O/'negative-cbaf-owner-link.json'
    if(O/'owner-link.json').exists()and not negative.exists():
        current=json.loads((O/'owner-link.json').read_text());assert current['ROM_sha256']=='cbafb6300953a12743eedca48594679c0f2129f2cdddd645912342c0995028b4'
        negative.write_text((O/'owner-link.json').read_text());(O/'negative-cbaf-Main-CPU.json').write_text((O/'Main-CPU.json').read_text());(O/'negative-cbaf-Main-checker.py').write_text((R/'tools/audit/check_kirby_owner_main_1101_v2.py').read_text())
    if(O/'owner-link.json').exists()and not(O/'negative-e055-owner-link.json').exists():
        current=json.loads((O/'owner-link.json').read_text());assert current['ROM_sha256']=='e055510b15eb554c9de1415ca34219cd213aaa9655362085817ed69fa55f1864'
        for source,target in[('owner-link.json','negative-e055-owner-link.json'),('Main-CPU.json','negative-e055-Main-CPU.json'),('foreign-body-CPU.json','negative-e055-foreign-body-CPU.json')]: (O/target).write_text((O/source).read_text())
        for source,target in[('check_kirby_owner_main_1101_v2.py','negative-e055-Main-checker.py'),('check_kirby_foreign_body_1101_v2.py','negative-e055-foreign-checker.py')]: (O/target).write_text((R/'tools/audit'/source).read_text())
    assert actual.read_text()==canonical.read_text();src=repair_source(actual.read_text())
    assert src==(V1/'fixed-source.s').read_text()
    src=repair_red_range(src)
    src+='\n.pushseg\n.segment "KIRBY_ABILITIES"\n; Exact owner pad: later SMB2/Meta Knight/audio/public owners do not move.\n.byte $ea\n.assert *=$abbd,lderror,"Kirby repaired weapons owner cut moved"\n.popseg\n.export KbBodyDispatch\n'
    previous_source=(O/'kirby_weapons.s').read_text()if(O/'kirby_weapons.s').exists()else None
    if previous_source!=src:(O/'kirby_weapons.s').write_text(src)
    dispatch_source=R/'build/bt-ready-menu-1031-v2/joint/src/kirby_dispatch.s';(O/'kirby_dispatch.s').write_text(repair_body_guard(dispatch_source.read_text()))
    compile_cmd=json.loads((BASE/'main-build.json').read_text())['command'].copy();compile_cmd[1:1]=['-I',str(O)]
    for key,target in[('-o','main.o'),('--create-full-dep','main.dep')]:compile_cmd[compile_cmd.index(key)+1]=str(O/target)
    if args.reuse_compiled_object:
        compile_receipt=json.loads((O/'main-build.json').read_text());assert compile_receipt['command']==compile_cmd and compile_receipt['returncode']==0 and previous_source==src
        compile_receipt.update(reused_owned_unfinished_product=True,product_sha256=sha(O/'main.o'),source_sha256=sha(O/'kirby_weapons.s'))
    else:compile_receipt=run(compile_cmd)
    (O/'main-build.json').write_text(json.dumps(compile_receipt,indent=2)+'\n')
    dep=(O/'main.dep').read_text();assert str(O).replace('\\','/')+'/kirby_weapons.s'in dep.replace('\\ ',' ').replace('\\','/'),dep[-1000:]
    doki=R/'build/doki-current-component-1101-v1';boundary=doki/'src/smb2_current_boundaries.s'
    (O/'kb-body-boundary.s').write_text(repair_body_boundary(boundary.read_text()))
    entry=(doki/'src/component.s').read_text();needle='.include "smb2_current_boundaries.s"';assert entry.count(needle)==1
    (O/'doki-component.s').write_text(entry.replace(needle,'.include "kb-body-boundary.s"'))
    doki_cmd=json.loads((doki/'component-build.json').read_text())['command'].copy();doki_cmd[1:1]=['-I',str(O)];at=doki_cmd.index(str(doki/'src/component.s'));doki_cmd[at]=str(O/'doki-component.s')
    for key,target in[('-o','doki-component.o'),('-l','doki-component.lst')]:doki_cmd[doki_cmd.index(key)+1]=str(O/target)
    (O/'doki-build.json').write_text(json.dumps(run(doki_cmd),indent=2)+'\n')
    link_cmd=json.loads((BASE/'terrain-final-link.json').read_text())['command'].copy()
    # The owning linker declares kernel/options side-output files. Redirect
    # those declared products too; a read-only base CFG cannot safely remain
    # the active output recipe even when the cartridge -o is private.
    config=(BASE/'candidate.cfg').read_text().replace(str(BASE).replace('\\','/'),str(O).replace('\\','/')).replace(str(BASE),str(O))
    (O/'candidate.cfg').write_text(config);link_cmd[link_cmd.index('-C')+1]=str(O/'candidate.cfg')
    for path in re.findall(r'file="([^"]+)"',config):
        if path and path!='%O':
            target=Path(path).resolve();assert target.is_relative_to(O.resolve()),path;target.parent.mkdir(parents=True,exist_ok=True)
    for i,arg in enumerate(link_cmd):
        if arg==str(BASE/'main.o'):link_cmd[i]=str(O/'main.o')
        elif arg==str(doki/'component.o'):link_cmd[i]=str(O/'doki-component.o')
    for key,target in[('-o','candidate.nes'),('-Ln','candidate.lbl')]:link_cmd[link_cmd.index(key)+1]=str(O/target)
    pos=link_cmd.index('--ld-args')+1;assert'--dbgfile,'in link_cmd[pos];link_cmd[pos]='--dbgfile,'+str(O/'candidate.dbg')
    if '-m'in link_cmd:link_cmd[link_cmd.index('-m')+1]=str(O/'candidate.map')
    link_receipt=run(link_cmd);(O/'link.json').write_text(json.dumps(link_receipt,indent=2)+'\n')
    dbg=O/'candidate.dbg';keep={b'version',b'info',b'file',b'lib',b'mod',b'seg',b'scope',b'sym'};dbg.write_bytes(b''.join(line for line in dbg.read_bytes().splitlines(keepends=True)if line.split(b'\t',1)[0]in keep))
    prepare_mirror(R,O/'candidate.nes');new=qualified(O/'candidate.nes')
    assert len(old['raw'])==len(new['raw'])
    proven=bytearray((V1/'fixed.bin').read_bytes()+b'\xea');v1=json.loads((V1/'fixed-assembly.json').read_text());lo=v1['labels']['KbWeapons::NotArc']-0xa000;hi=v1['labels']['KbWeapons::NotReturn']-0xa000
    matches=list(re.finditer(b'\xc9\x18',proven[lo:hi]));assert len(matches)==1;proven[lo+matches[0].start()+1]=32
    assert new['raw'][16+74*8192:16+74*8192+3005]==proven,'Actual owner differs from the source-proven weapon island plus exact red32 immediate'
    placement=lambda b:{i:{k:s.get(k)for k in['name','start','size','ooffs','addrsize','type']}for i,s in b['segs'].items()}
    assert placement(old)==placement(new),'Segment placement/extent changed'
    cuts=ranges(old['raw'],new['raw']);bank74=(16+74*8192,16+75*8192);outside=[]
    for lo,hi in cuts:
        if not(bank74[0]<=lo<hi<=bank74[1]):outside.append(dict(start=lo,end=hi,old=old['raw'][lo:hi].hex(),new=new['raw'][lo:hi].hex()))
    moved={n:dict(old=s,new=new['syms'].get(n))for n,s in old['syms'].items()if n not in new['syms']or any(s.get(k)!=new['syms'][n].get(k)for k in['val','seg'])}
    assert all(v['new']is not None for v in moved.values()),'Original native symbol removed'
    assert all('seg'in v['old']and old['segs'][v['old']['seg']]['name']=='"KIRBY_ABILITIES"'for v in moved.values()),list(moved)[:20]
    assert address(old,'S2HostAudioBegin')==address(new,'S2HostAudioBegin')==0xbcb7
    assert all(address(old,n)==address(new,n)for n in old['syms']if n.startswith(('S2','Mk','KbDraw','KbBodyDispatch','KbWeaponsDispatch'))and n not in moved)
    # Every outside-owner change must be an actual native operand pointing
    # to one of the moved public Kirby imports. Preserve each opcode/bank.
    expected=[]
    for parent,target in[('KbMovement','KbAbilityMove'),('KbInjuryStart','KbDropCopy')]:
        s=old['syms'][parent];at=location(old,parent);size=int(s['size'],0);before=old['raw'][at:at+size];after=new['raw'][at:at+size]
        oldtarget=address(old,target);newtarget=address(new,target)
        # Farcall target operands are split LDA#lo/STA+LDA#hi/STA.
        pat=b'\xa9'+bytes([oldtarget&255])+b'\x8d\x6c\x01\xa9'+bytes([oldtarget>>8])+b'\x8d\x6d\x01'
        matches=list(re.finditer(re.escape(pat),before));assert len(matches)==1,(parent,target,matches)
        start=matches[0].start();expected.extend([(at+start+1,oldtarget&255,newtarget&255),(at+start+6,oldtarget>>8,newtarget>>8)])
        for off,a,b in expected:
            if at<=off<at+size:assert after[off-at]==b and before[off-at]==a
    outside_bytes=[(i,old['raw'][i],new['raw'][i])for lo,hi in cuts for i in range(lo,hi)if not bank74[0]<=i<bank74[1]]
    assert outside_bytes==sorted((i,a,b)for i,a,b in expected if a!=b),('Unexplained outside owner writes',len(outside_bytes),outside_bytes[:12],expected)
    boundary_at=location(old,'S2BoundaryBody');boundary_pc=address(new,'S2BoundaryBody');dispatch=address(new,'KbBodyDispatch');before=old['raw'][boundary_at:boundary_at+49];after=new['raw'][boundary_at:boundary_at+49]
    assert after[:11]==before[:11]and after[11:29]==bytes([0x4c,dispatch&255,dispatch>>8])+bytes([234])*15 and after[29:]==before[29:]
    allowed74=[(bank74[0],bank74[0]+3005),(boundary_at+11,boundary_at+29)]
    internal=[]
    for parent,target,opcode in[('KbWeaponsDispatch','KbWeapons',0x4c),('KbBodyDispatch','KbBodyContact',0x20)]:
        at=location(old,parent);size=int(old['syms'][parent]['size'],0);pattern=bytes([opcode,address(old,target)&255,address(old,target)>>8]);body=old['raw'][at:at+size];hits=list(re.finditer(re.escape(pattern),body));assert len(hits)==1
        operand=at+hits[0].start()+1;want=address(new,target).to_bytes(2,'little')
        if parent=='KbBodyDispatch':
            assert new['syms'][parent]['size']==old['syms'][parent]['size'];newbody=new['raw'][at:at+size];newhits=list(re.finditer(re.escape(bytes([opcode])+want),newbody));assert len(newhits)==1
            newoperand=at+newhits[0].start()+1;allowed74.append((at,at+size))
        else:newoperand=operand;assert new['raw'][operand:operand+2]==want;allowed74.append((operand,operand+2))
        internal.append(dict(parent=parent,target=target,old_operand=operand,new_operand=newoperand,old=address(old,target),new=address(new,target)))
    assert all(any(a<=i<b for a,b in allowed74)for lo,hi in cuts for i in range(lo,hi)if bank74[0]<=i<bank74[1]),'Unowned B74 change'
    rollback=dict(original_ROM_sha256=PIN,changes=[dict(start=lo,old=old['raw'][lo:hi].hex(),new=new['raw'][lo:hi].hex())for lo,hi in cuts],moved_symbols=moved,added_symbols=[n for n in new['syms']if n not in old['syms']])
    (O/'rollback-witness.json').write_text(json.dumps(rollback,indent=2)+'\n')
    output=sha(O/'candidate.nes');assert sha(BASE/'candidate.nes')==PIN
    inputs=[Path(arg)for arg in link_cmd if arg.endswith('.o')and Path(arg).resolve()!=O/'main.o']
    report=dict(passed=True,source_owner_relinked=True,native=False,installed=False,base_ROM_sha256=PIN,ROM_sha256=output,changed_bytes=sum(hi-lo for lo,hi in cuts),B74_changed_bytes=sum(1 for lo,hi in cuts for i in range(lo,hi)if bank74[0]<=i<bank74[1]),outside_owner_changes=outside,precise_external_relocations=[dict(offset=i,old=a,new=b)for i,a,b in expected if a!=b],source_cut_preserved=0xabbd,S2HostAudioBegin=0xbcb7,all_segment_layouts_exact=True,B74_after_weapon_exact_except_body_tail_and_two_native_operands=True,internal_dispatch_relocations=internal,S2BoundaryBody=dict(CPU=boundary_pc,bytes=49,Own_branch_bytes_exact=True,foreign_tail='same-bank JMP KbBodyDispatch+15EA'),moved_native_symbols={n:dict(old=v['old']['val'],new=v['new']['val'])for n,v in moved.items()},added_symbols=rollback['added_symbols'],owning_source=str(actual),owning_entrypoint=str(BASE/'entrypoint.s'),all_other_linked_objects_read_only=True,
      bindings={str(p.resolve()):sha(p)for p in[Path(__file__),R/'tools/prepare_cv3_dmc_mirror.py',R/'tools/audit/prepare_kirby_contact_repair_1101_v1.py',R/'tools/audit/prepare_kirby_body_ingress_1101_v2.py',R/'tools/reference/kirby_shell_contact_1101_v1.inc',BASE/'entrypoint.s',BASE/'candidate.cfg',BASE/'main-build.json',BASE/'terrain-final-link.json',actual,dispatch_source,boundary,doki/'src/component.s',doki/'component-build.json',V1/'binding.json',O/'kirby_weapons.s',O/'kirby_dispatch.s',O/'main-build.json',O/'main.dep',O/'doki-component.s',O/'kb-body-boundary.s',O/'doki-build.json',O/'link.json',O/'candidate.cfg',O/'candidate.nes',O/'candidate.dbg',O/'rollback-witness.json']+inputs})
    (O/'owner-link.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k not in['bindings','moved_native_symbols','added_symbols']}))
if __name__=='__main__':main()
