"""Source-built same-size correction for fourth-row menu cursor commands."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
PARENT=ROOT/'build/pit-retold-host-v3'
OUT=ROOT/'build/menu-fourth-row-fix-v2'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    assert not(OUT/'candidate.nes').exists(),'Preserve prior candidates'
    proof=json.loads((PARENT/'build-proof.json').read_text())
    assert sha(PARENT/'candidate.nes')==proof['candidate']=='ac126b545ceb0c27f4843dbbf2eed647f07288a74a7a036d6769db6e3df0b1d2'
    for path,digest in proof['actual_dependencies'].items():assert sha(path)==digest,path
    source=ROOT/'src/menu_vram_budget.s';before=source.read_text()
    old=' cmp #$20\n beq Cursor\n cmp #$21\n beq Cursor\n cmp #$23'
    # Skip the following two 2-byte instructions for an out-of-range low
    # address. This preserves every existing label and the exact8-byte span.
    new=' cmp #$20\n bcc *+6\n cmp #$23\n bcc Cursor\n cmp #$23'
    assert before.count(old)==1
    (OUT/'src').mkdir(parents=True)
    (OUT/'src/menu_vram_budget.s').write_text(before.replace(old,new),newline='\n')
    commands=[]
    for original in proof['commands']:
        command=list(original)
        if Path(command[0]).name.lower()=='ca65.exe':
            command[1:1]=['-I',str(OUT/'src')]
            for key in ['-o','--create-full-dep']:
                idx=command.index(key)+1;command[idx]=str(OUT/Path(command[idx]).name)
        else:
            for i,arg in enumerate(command):
                if arg.startswith('--dbgfile,'):
                    command[i]='--dbgfile,'+str(OUT/'candidate.dbg')
                elif arg in [str(PARENT/n)for n in ['main.o','skin.o','gb.o','candidate.nes','candidate.lbl']]:
                    command[i]=str(OUT/Path(arg).name)
        result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
        assert result.returncode==0,result.stdout+result.stderr
        commands.append(command)
    sys.path.insert(0,str(ROOT/'tools'))
    from prepare_cv3_dmc_mirror import prepare
    prepare(ROOT,OUT/'candidate.nes')
    a,b=[p.read_bytes()for p in [PARENT/'candidate.nes',OUT/'candidate.nes']]
    changes=[dict(offset=i,bank=(i-16)//8192,before=x,after=y)for i,(x,y)in enumerate(zip(a,b))if x!=y]
    assert len(a)==len(b)and 0<len(changes)<=8
    assert a[:16]==b[:16]and a[1048592:]==b[1048592:],'No mapper/CHR change'
    assert(PARENT/'candidate.lbl').read_bytes()==(OUT/'candidate.lbl').read_bytes(),'Every linked label remains exact'
    report=dict(source_built=True,parent=sha(PARENT/'candidate.nes'),candidate=sha(OUT/'candidate.nes'),
        changes=changes,all_linked_labels_byte_exact=True,CHR_and_header_exact=True,
        correction='The exact-size cursor range accepts20/21/22 for all four menu rows; all other queue shapes retain their existing validation.',
        commands=commands,bindings={str(p):sha(p)for p in [Path(__file__),source,OUT/'src/menu_vram_budget.s',
            PARENT/'build-proof.json',PARENT/'candidate.nes',OUT/'candidate.nes',OUT/'candidate.lbl',OUT/'candidate.dbg']},
        native_run=False)
    (OUT/'build-proof.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(candidate=report['candidate'],changes=changes,all_labels_exact=True)))


if __name__=='__main__':main()
