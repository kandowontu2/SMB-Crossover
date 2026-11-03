"""Expose101's exact generated footer and finite typed resident readers."""
import json
from pathlib import Path
import measure_dkjr_prince_owner_1103_v101 as P
import check_hogan_current_bounded_v1 as N

A,R,O=P.A,P.R,P.O


def main():
    q=json.loads((O/'native-combined-owner-v101-measurement.json').read_text());source=(O/'native-combined-owner-v101.s').read_text()
    marker=' .if (*-CoCold)<$213\n';assert source.count(marker)==1
    source=source.replace(marker,'CoDataEnd:\n'+marker)
    source+='\n.export CoDataEnd,CoExCookie,CoBBCookie,CoCommitBank,CoCheckBank\n'
    cfg=(O/'native-combined-owner-v101.cfg').read_text().replace('native-combined-extra-v101.bin','native-combined-extra-v108.bin')
    blob,L=A.assemble('native-combined-owner-v108',source,cfg)
    assert blob==(O/'native-combined-owner-v101.bin').read_bytes()
    assert (O/'native-combined-extra-v108.bin').read_bytes()==(O/'native-combined-extra-v101.bin').read_bytes()
    low,high=L['CoDataEnd'],L['CoOwnerEnd'];assert(low,high)==(0xb002,0xb013)
    assert blob[low-0xae00:high-0xae00]==bytes([234])*17
    mem={}
    for path,at in [(O/'native-combined-owner-v101.bin',0xae00),(O/'native-combined-extra-v101.bin',0xab72),(O/'native-combined-selector-v101.bin',0xa740)]:mem.update({at+i:v for i,v in enumerate(path.read_bytes())})
    sizes={'imp':1,'acc':1,'imm':2,'zpg':2,'zpx':2,'zpy':2,'inx':2,'iny':2,'rel':2,'abs':3,'abx':3,'aby':3,'ind':3}
    roots=[L[n]for n in ['CoCold','CoRetire','CoCheckCode','CoRetireOwners','PrTypedWorker','PrCopyLive']]+[q['selector_labels']['ExDispatch'],q['selector_labels']['PrFamily']]
    todo=list(roots);reached={};opaque=set()
    while todo:
        pc=todo.pop()
        if pc in reached:continue
        if pc not in mem:opaque.add(pc);continue
        assert not low<=pc<high,('footer reached',hex(pc))
        name,mode=N.NesMPU.disassemble[mem[pc]];assert name not in ['???','BRK'],(pc,name)
        size=sizes[mode];operand=mem.get(pc+1,0)+(mem.get(pc+2,0)*256 if size==3 else 0);nxt=pc+size
        reached[pc]=(name,mode,operand)
        if name=='JSR':todo.extend([operand,nxt])
        elif name=='JMP':assert mode=='abs';todo.append(operand)
        elif mode=='rel':todo.extend([nxt,nxt+operand-(256 if operand&128 else 0)])
        elif name not in ['RTS','RTI']:todo.append(nxt)
    direct=[];indexed=[];indirect=[]
    for pc,(name,mode,base)in sorted(reached.items()):
        if mode=='abs'and low<=base<high:direct.append(dict(PC=pc,operation=name,address=base))
        if mode in ['abx','aby']and base<high and base+255>=low:
            assert base==L['CoSmc']and mode=='abx'and name=='LDY',(hex(pc),name,mode,hex(base))
            assert base+4<low
            indexed.append(dict(PC=pc,operation=name,base=base,X_domain=[0,1,2,3,4],last_address=base+4))
        if mode in ['inx','iny']:
            assert mode=='iny'and base==8 and andname(name),('new indirect reader',pc,name,mode,base)
            indirect.append(dict(PC=pc,operation=name,zero_page_pointer=base,Y_domain=list(range(16))))
    assert not direct and len(indexed)==2 and len(indirect)==1+1
    # Exact tables give all immutable R5/R6 cookie sources. Each indirect
    # header reader/committer usesLDY15/DEY/BPL, hence never beyondcookie+15.
    cookies=[L['CoExCookie'],L['PrCookie'],L['CoBBCookie'],q['selector_labels']['DkCookie']]
    cookie_ranges=[[at,at+16]for at in cookies]
    assert all(not(a<high and b>low)for a,b in cookie_ranges)
    assert L['CoBBCookie']+16==low
    assert 'CoSelectIndex:\n lda CoCookieLo,x\n sta R5\n lda CoCookieHi,x\n sta R6' in source
    assert 'CoRetireLoop:\n txa\n pha\n jsr CoSelectIndex\n jsr CoCheckHeaders' in source
    assert source.count(' ldy #15\n')==2
    out=dict(passed=True,qualified=False,ROM_written=False,shared_source_written=False,allocation_claimed=False,
        measured_manager_file_bytes=len(blob),compiled_code_data_end=low,existing_extent_end=high,
        generated_footer_half_open=[low,high],generated_footer_bytes=high-low,
        extra_unused_owned_extent=[0xabd1,0xabd4],selector_unused_owned_extent=[0xa7f0,0xa7f2],
        compiled_resident_roots=len(roots),compiled_resident_instructions=len(reached),direct_footer_accesses=direct,
        possible_indexed_aliases=indexed,typed_indirect_cookie_reads=indirect,cookie_half_open=cookie_ranges,
        opaque_existing_native_targets=sorted(opaque),
        scope='Byte-identical label-only reassembly of101 proves new17B nonexecuted EAfooter B002..B013 after bothcookies, inside existing531Bmanager. Eight compiledresident roots cannot fetch it; no absolute directaccess, onlytwo indexedSMC aliases boundedX0..4, and both R5indirect cookie operations boundY0..15. Full externalcaller/literal/producer closure and root grant are still required before reusing anybytes. This is source-generated padding, not blank-byte discovery, performance change, shared grant or candidate.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in [Path(__file__),O/'native-combined-owner-v101-measurement.json',O/'native-combined-owner-v101.s',O/'native-combined-owner-v101.bin',O/'native-combined-extra-v101.bin',O/'native-combined-selector-v101.bin',O/'native-combined-owner-v108.s',O/'native-combined-owner-v108.bin',O/'native-combined-owner-v108.lbl']})
    (O/'native-combined-padding-v108.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in ['passed','compiled_code_data_end','generated_footer_half_open','generated_footer_bytes','extra_unused_owned_extent','selector_unused_owned_extent','compiled_resident_instructions']}))


def andname(name):return name in ['LDA','CMP']


if __name__=='__main__':main()
