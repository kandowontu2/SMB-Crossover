"""Bind Mini menu source funding/callers, all-byte cycle ABI and art parameters."""
import json,re
from pathlib import Path
import check_mini_mario_menu_1103_v15 as C
B,O,R,N,F,address=C.B,C.O,C.R,C.N,C.F,C.address


def main():
    original_load=C.load
    # Load the final16 recipe without mutating any original source/receipt.
    text=Path(C.__file__).read_text();before="O/'proposal.json'";assert before in text
    env=dict(C.__dict__,__name__='mini18load');exec(compile(text.replace(before,"O/'proposal-v16.json'"),__file__,'exec'),env)
    old,new,q=env['load']();raw=old['raw'];root=R/'build/menu-family-root-candidate-1102-v1'
    source=root/'producer-snapshot.py';family=json.loads((root/'mr-gimmick-family-v18.json').read_text())
    assert "stream+body+bytes([0xea])*(677-len(stream)-len(body))"in source.read_text()
    assert "bytes([0x4c,decoder_at&255,decoder_at>>8])+bytes([0xea])*46"in source.read_text()
    assert family['nametable_stream_bytes']==440 and family['decoder_bytes']==91
    codec=next(p for p in family['patches']if p['offset']==B.off(66,0xae1b))
    assert bytes.fromhex(codec['new'])==raw[B.off(66,0xae1b):B.off(66,0xb0c0)]
    assert raw[B.off(66,0xa588):B.off(66,0xa58b)]==bytes.fromhex('4cd3af')
    assert raw[B.off(66,0xa58b):B.off(66,0xa5b9)]==bytes([234])*46
    assert raw[B.off(66,0xb02e):B.off(66,0xb0c0)]==bytes([234])*146
    assert raw[B.off(66,0xad39):B.off(66,0xad7b)]==(root/'family-v18-toggle.bin').read_bytes()+bytes([234])*5
    assert raw[B.off(124,0xa000):B.off(124,0xa0d6)]==(root/'family-v18-nav.bin').read_bytes()
    # Existing finite old-reader proof is reused only over exact unchanged
    # source/compiled UI spans, not asserted as a new global indirect census.
    previous=R/'build/dkjr-menu-current-1103-v1/current-menu-funding-v5.json'
    proof=json.loads(previous.read_text());assert proof['passed']and proof['old_padding_fetches_or_reads']==0
    for rel,digest in proof['bindings'].items():
        if rel.startswith('build/menu-family-root-candidate-1102-v1/')or rel in['src/character_select.s','src/menu_vram_budget.s']:
            assert B.sha(R/rel)==digest,rel
    cycle=[];a=N.fresh(old);b=N.fresh(new)
    for value in range(256):
        for p in[0x30,0x31,0x70,0xf1]:
            pair=[]
            for initial in[a,b]:
                m=N.fork(initial);N.put(m,MarioVariant=value);z=F.invoke(m,'KmNextVariant',a=83,x=197,y=57,p=p);pair.append((m,z))
            left,zl=pair[0];right,zr=pair[1]
            if value==8:assert N.get(right,'MarioVariant')==0
            else:assert zl==zr and C.P.view(left)==C.P.view(right),(value,p,zl,zr)
            cycle.append(dict(input=value,P=p,old=N.get(left,'MarioVariant'),new=N.get(right,'MarioVariant')))
    callers=[dict(line=i,text=s.strip())for i,s in enumerate((R/'src/character_select.s').read_text().splitlines(),1)if re.search(r'\b(?:jsr|jmp|farcall)\s+QueueSelection\b',s)]
    assert len(callers)==2 and all('jsr QueueSelection'in v['text']for v in callers)
    labels=q['labels'];mapper_high=labels['MiniMapSetup']+1
    # Final DATA layout: map-tail10/name16/palette15 then low-page LDA.
    mapper_low=0xa58b+10+16+15+1
    assert new['raw'][B.off(66,mapper_high)-1]==162 and new['raw'][B.off(66,mapper_low)-1]==169
    out=dict(passed=True,source_only=True,ROM_written=False,art_allocated=False,CPU_qualified_not_native=True,
        current_input_SHA256=B.PIN,expected_memory_only_SHA256=q['expected_memory_only_SHA256'],
        exact_source_padding=dict(codec_tail=[0xb02e,0xb0c0],decoder_entry=[0xa58b,0xa5b9],Select_footprint=[0xad39,0xad7b],nav=[0xa000,0xa0d6],AltTail=[0xadee,0xadff],Km_cycle=[0xadce,0xadee]),
        source_QueueSelection_callers=callers,public_foreign_contract='JMP newgate replaces onlySTA016A. PHP/PHA then PLA/PLP restore exact incomingA/P; originalSTA016A+JMPoriginal+3 executes unchanged source. All93legacy profiles and whole public returns pass17; no externalQueue+1/+2 source ingress.',
        retained_codec_reader='EntryA588 remainsJMPAFD3. Exact unchanged91B decoder reads440B streamAE1B..AFD3, then returns before newB02Ecode.46B entry pad has no fallthrough. Reuse exact finite oldreader receipt; not an arbitrary indirect-cache claim.',
        cycle_all_byte_flag_cases=len(cycle),cycle_foreign_cases_exact=1020,cycle_new8_cases=4,
        art_parameters=dict(page_placeholder=0,allocation_claim=False,physical_PRG=66,
            low_page_immediate_CPU=mapper_low,high_page_immediate_CPU=mapper_high,
            source_pair_path='build/mini-mario-art-1103-v12/menu-portrait.chr',source_pair_SHA256=B.sha(R/'build/mini-mario-art-1103-v12/menu-portrait.chr'),
            typed_publisher='A=page&255,X=page>>8,Y=1; genuineX5SetPhysicalChr. Previewtile64 even uses pattern0 window1 offset0. Native gameplaybank1 atlas is a separate root resource binding.'),
        remaining='Root must bind allocated artpage/preimages and final shared backend then run actual menu/launch/native1-1. Newmenu IRQ/FF/hardware receipts are not implied by unchanged finite oldreader proof.',
        bindings={p.relative_to(R).as_posix():B.sha(p)for p in[Path(__file__),O/'proposal-v16.json',O/'menu-CPU-v17.json',previous,source,root/'mr-gimmick-family-v18.json',R/'tools/audit/prepare_mario_tank_candidate_1101_v5.py']})
    (O/'source-audit-v18.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(passed=True,cycle_all_byte_flag_cases=1024,art_parameters=out['art_parameters'])))


if __name__=='__main__':main()
