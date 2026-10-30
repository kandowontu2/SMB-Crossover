"""Deduplicate exact native Ice Climber descriptors without changing pixels."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

R=Path(__file__).resolve().parents[2]
P=R/'build/parodius-chr-compact-v1'
O=R/'build/ice-pose-aliases-v2'
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from prepare_cv3_dmc_mirror import prepare


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,s):p.write_text(s,newline='\n')


def main():
    assert not O.exists() or '--resume' in sys.argv
    assert sha(P/'candidate.nes')=='c658816042a73c8d11b5ad2ac36b699222359806bd3cdcd0c94cfa1e6a1a0da1'
    old=scoped_load(P/'candidate.nes');O.mkdir(parents=True,exist_ok='--resume' in sys.argv)
    if '--resume' in sys.argv and (O/'candidate.nes').exists():
        put(O/'negative-override-not-selected.json',json.dumps(dict(
            negative='Initial include chain selected canonical Ice art instead of private aliases; size assertion rejected candidate.',
            rejected_ROM_sha256=sha(O/'candidate.nes'),
            rejected_dependency_sha256=sha(O/'main.d')),indent=2)+'\n')
    src=R/'src/ice_climbers_art.inc';text=src.read_text()
    records={};aliases={};replacement=text
    for i in range(60):
        name='IcPose'+str(i);off=location(old,name);n=old['raw'][off]
        data=old['raw'][off:off+n+1]
        assert n%4==0 and n<=32
        canonical=records.setdefault(data,name);aliases[name]=canonical
        if canonical==name:continue
        rx=r'(?m)^'+name+r':\r?\n(?:[ \t]+\.byte[^\r\n]*\r?\n)+'
        matches=re.findall(rx,replacement)
        assert len(matches)==1,(name,len(matches))
        replacement=re.sub(rx,name+' = '+canonical+' ; exact native descriptor alias\n',replacement)
    assert len(records)==19
    # Twelve17-byte descriptions exactly fill C434..C500. Keep every
    # description wholly within a CPU page, so (descriptor),Y never adds a
    # new page-crossing cycle. This retains the full721-byte saving.
    short=[(d,n)for d,n in records.items()if len(d)==17]
    assert len(short)==13
    ordered=short[:12]+[(d,n)for d,n in records.items()if n not in {n for d,n in short[:12]}]
    blocks=[]
    for data,name in ordered:
        rx=r'(?m)^'+name+r':\r?\n(?:[ \t]+\.byte[^\r\n]*\r?\n)+'
        matches=re.findall(rx,text);assert len(matches)==1
        blocks.append(matches[0])
    blocks += [n+' = '+c+' ; exact native descriptor alias\n'for n,c in aliases.items()if n!=c]
    start=text.index('IcPose0:\n');end=text.index('IcArtEnd:')
    replacement=text[:start]+''.join(blocks)+text[end:]
    put(O/'ice_climbers_art.inc',replacement)
    put(O/'ice_climbers.s',(R/'src/ice_climbers.s').read_text())
    put(O/'entrypoint.s',(P/'entrypoint.s').read_text())
    proof=json.loads((P/'build-proof.json').read_text())
    commands=[]
    for row in proof['commands']:
        cmd=row['command'].copy()
        if Path(cmd[0]).stem=='ca65':
            cmd[1:1]=['-I',str(O)]
            cmd[cmd.index('--create-full-dep')+1]=str(O/'main.d')
            cmd[cmd.index('-o')+1]=str(O/'main.o')
            cmd[-1]=str(O/'entrypoint.s')
        else:
            cmd=[str(O/'main.o')if v==str(P/'main.o')else v for v in cmd]
            for ext in ['nes','dbg','lbl','map']:
                cmd=[v.replace(str(P/('candidate.'+ext)),str(O/('candidate.'+ext)))for v in cmd]
        p=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
        commands.append(dict(command=cmd,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr))
        put(O/'compile-log.json',json.dumps(commands,indent=2)+'\n')
        assert p.returncode==0,p.stderr[-10000:]
    prepare(R,O/'candidate.nes')
    new=scoped_load(O/'candidate.nes')
    dep=(O/'main.d').read_text().replace('\\ ',' ').replace('\\','/')
    assert (O/'ice_climbers_art.inc').as_posix()in dep
    assert (O/'ice_climbers.s').as_posix()in dep
    assert address(old,'IcArtStart')==address(new,'IcArtStart')==0xc380
    assert address(old,'IcArtEnd')==0xc860 and address(new,'IcArtEnd')==0xc58f
    first=16+70*8192+0x380;last=16+70*8192+0x860
    assert old['raw'][:first]==new['raw'][:first] and old['raw'][last:]==new['raw'][last:]
    assert new['raw'][16+70*8192+0x58f:last]==b'\xff'*721
    for name,canonical in aliases.items():
        before=location(old,name);after=location(new,name)
        length=old['raw'][before]+1
        assert old['raw'][before:before+length]==new['raw'][after:after+length],name
        assert address(new,name)==address(new,canonical)
        assert (address(new,name)&255)+length<=256,('page-crossing descriptor',name)
    for name,s in old['syms'].items():
        assert name in new['syms'],name
        if re.fullmatch(r'IcPose\d+',name)or name=='IcArtEnd':continue
        assert s['val']==new['syms'][name]['val'],name
    inputs=dict(proof['source_bindings'])
    for p in [src,O/'ice_climbers_art.inc',O/'ice_climbers.s',O/'entrypoint.s',Path(__file__).resolve(),P/'candidate.nes',P/'build-proof.json']:
        inputs[str(p)]=sha(p)
    result=dict(passed=True,status='PRIVATE_SOURCE_LINKED_ICE_DESCRIPTOR_ALIAS_CPU_NATIVE_PENDING',
        parent_ROM_sha256=sha(P/'candidate.nes'),ROM_sha256=sha(O/'candidate.nes'),
        old_descriptors=60,unique_descriptors=19,aliases=aliases,
        saved_PRG_bytes=721,physical_bank=70,freed_offset_start=0x58f,freed_offset_end_exclusive=0x860,
        new_RAM=0,all_CHR_identical=True,all_runtime_instructions_identical=True,
        all_unique_descriptors_page_safe_without_padding=True,
        only_ICE_CLIMBERS_ART_bytes_change=True,all_other_named_addresses_preserved=True,
        source_bindings=inputs,commands=commands,
        limits=['Actual pointer/render/physics/foreign and native equivalence pending',
                'The interval is not yet allocated; future source producers must keep these exact aliases'])
    put(O/'build-proof.json',json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k]for k in ['ROM_sha256','saved_PRG_bytes','unique_descriptors']}))


if __name__=='__main__':main()
