"""Two exact immediate operands extend existing noninventory UI fast paths."""
from pathlib import Path
import difflib,hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
P=R/'build/current-character-composition-v2'
O=R/'build/new-roster-ui-fastpath-1030-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    hp=P/'source-stage-handoff-v2.json'
    assert sha(hp)=='131d238ed8669a294d348dae2123557c8562b4bbe418e7fd76ab2fb5e4b7ee0a'
    h=json.loads(hp.read_text())
    for p,v in h['bindings'].items():assert sha(p)==v,p
    assert not O.exists();O.mkdir()
    b=scoped_load(P/'joint/candidate.nes');raw=bytearray(b['raw']);changes=[];patch=[]
    for name,path,old,new in[('X5OwnInventoryUi','x5_bounce.s',20,33),('InventorySupported','inventory.s',28,33)]:
        at=location(b,name);size=int(b['syms'][name]['size'],0)
        before=bytes(raw[at:at+size]);needle=bytes([0xe0,old]);assert before.count(needle)==1,(name,size)
        off=at+before.index(needle)+1;assert raw[off]==old;raw[off]=new
        source=P/'joint/src'/path;text=source.read_text()
        a=text.index('.proc '+name);z=text.index('.endproc',a)+len('.endproc')
        part=text[a:z];needle=f'cpx #{old}\n';assert part.count(needle)==1
        part=part.replace(needle,f'cpx #{new}\n');updated=text[:a]+part+text[z:]
        patch+=list(difflib.unified_diff(text.splitlines(True),updated.splitlines(True),
            fromfile='parent/joint/src/'+path,tofile='candidate/joint/src/'+path))
        (O/path).write_text(updated,newline='\n')
        changes.append(dict(symbol=name,PC=address(b,name),file_offset=off,before=old,after=new,source=str(source),source_sha256=sha(source)))
    diffs=[i for i,(a,z)in enumerate(zip(b['raw'],raw))if a!=z]
    assert diffs==sorted(x['file_offset']for x in changes)
    (O/'candidate.nes').write_bytes(raw)
    (O/'candidate.dbg').write_bytes((P/'joint/candidate.dbg').read_bytes())
    (O/'source.patch').write_text(''.join(patch),newline='\n')
    proof=dict(status='TWO_BYTE_PRIVATE_SOURCE_CONTROLS_PENDING',native=False,admitted=False,
        candidate_sha256=sha(O/'candidate.nes'),parent_sha256=sha(P/'joint/candidate.nes'),
        source_handoff_sha256=sha(hp),changes=changes,
        unchanged_header_CHR_all_other_ROM_bytes_and_all_public_entry_PCs=True,
        no_new_RAM_PRG_CHR_lease=True,
        limits=['The existing fast paths are extended, not yet proven equivalent for newraw20..32.',
            'Must qualify actual UI output/flags/state/wholeMain/ISR before adoption. No performance or native claim.'],
        bindings={str(p.resolve()):sha(p)for p in[Path(__file__),hp,P/'joint/candidate.nes',P/'joint/candidate.dbg',
            P/'joint/src/x5_bounce.s',P/'joint/src/inventory.s',O/'candidate.nes',O/'candidate.dbg',O/'source.patch',O/'x5_bounce.s',O/'inventory.s']})
    (O/'source-closure.json').write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(candidate=proof['candidate_sha256'],changes=changes)),flush=True)


if __name__=='__main__':main()
