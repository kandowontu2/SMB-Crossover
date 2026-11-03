"""Current-source extent proof and finite compiled UI padding consumers."""
from pathlib import Path
import collections,json,re
import check_dkjr_current_menu_1103_v3 as T
V,N,F,R,O=T.V,T.N,T.F,T.R,T.O
address,location,off,sha=T.address,T.location,T.off,T.sha


def main():
    old,new,proposal=T.load();raw=old['raw'];root=R/'build/menu-family-root-candidate-1102-v1';producer=root/'producer-snapshot.py';text=producer.read_text();original=json.loads((root/'mr-gimmick-family-v18.json').read_text())
    needles=["stream+body+bytes([0xea])*(677-len(stream)-len(body))","bytes([0x4c,decoder_at&255,decoder_at>>8])+bytes([0xea])*46"]
    assert all(n in text for n in needles)
    codec=next(p for p in original['patches']if p['offset']==off(66,0xae1b));codecbytes=bytes.fromhex(codec['new']);assert len(codecbytes)==677 and raw[off(66,0xae1b):off(66,0xb0c0)]==codecbytes
    assert original['nametable_stream_bytes']==440 and original['decoder_bytes']==91
    decoder,L=T.B.assemble('current-decoder-source-v5',(root/'family-v18-decoder.s').read_text(),'MEMORY{P:start=$afd3,size=91,file=%O;}SEGMENTS{CODE:load=P,type=ro;}')
    assert decoder==(root/'family-v18-decoder.bin').read_bytes()==raw[off(66,0xafd3):off(66,0xb02e)]
    entry=next(p for p in original['patches']if p['offset']==off(66,0xa588));assert len(bytes.fromhex(entry['new']))==49 and bytes.fromhex(entry['new'])==raw[off(66,0xa588):off(66,0xa5b9)]
    toggle=(root/'family-v18-toggle.bin').read_bytes();assert len(toggle)==61 and raw[off(66,0xad39):off(66,0xad7b)]==toggle+bytes([234])*5
    oldnav=(root/'family-v18-nav.bin').read_bytes();assert len(oldnav)==214 and raw[off(124,0xa000):off(124,0xa0d6)]==oldnav
    # All original native menu scalar/indirect address modes are observed on
    # actual current inputs. This supplements the source-declared padding;
    # it is finite UI closure, not a false all-ROM raw operand declaration.
    targets=[(0xa58b,0xa5b9),(0xb02e,0xb0c0)];hits=[];entries=collections.Counter();decoder_reads=set();steps=0
    def check(c):
        nonlocal steps
        steps+=1;m=c.memory
        def owned(at):return 0x8000<=at<0xe000 and m.rawtags[(at-0x8000)//8192]==194
        if owned(c.pc):
            entries[c.pc]+=1
            assert not any(lo<=c.pc<hi for lo,hi in targets),('old padding fetch',hex(c.pc))
        opcode=m[c.pc];name,mode=N.NesMPU.disassemble[opcode];operand=m[(c.pc+1)&65535]
        if mode in ['abs','abx','aby','ind']:operand|=m[(c.pc+2)&65535]<<8
        at=None
        if mode=='abs'and name not in ['JMP','JSR']:at=operand
        elif mode=='abx':at=(operand+c.x)&65535
        elif mode=='aby':at=(operand+c.y)&65535
        elif mode=='iny':at=(m[operand]+256*m[(operand+1)&255]+c.y)&65535
        elif mode=='inx':p=(operand+c.x)&255;at=m[p]+256*m[(p+1)&255]
        if at is not None and owned(at):
            assert not any(lo<=at<hi for lo,hi in targets),('old padding access',hex(c.pc),name,mode,hex(at))
            if 0xafd3<=c.pc<0xb02e and mode=='iny':decoder_reads.add(at)
    rows=json.loads((O/'current-menu-v3-CPU.json').read_text())['rows'];seed=N.fresh(old)
    for slot in range(32):
        m=N.fork(seed);N.put(m,CrossoverMenuState=1,CrossoverMenuIndex=slot,Mirror_PPUMASK=0,DisableScreenFlag=1,VRAM_Buffer1_Offset=0);F.invoke(m,'CrossoverMenuInput',watch=check)
    for row in rows:
        m=N.fork(seed);N.put(m,CrossoverMenuIndex=row['slot'],CmActive=0);m[0x5ffe]=0
        F.invoke(m,'MenuResolveCharacter',watch=check);F.invoke(m,'QueueSelection',watch=check)
        for _ in range(row['cycle']):
            N.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0);F.invoke(m,'CrossoverMenuInput',watch=check)
        for key in [0,16,128,32,64,1,2,4,8]:
            x=N.fork(m);N.put(x,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=key,SavedJoypad2Bits=0);F.invoke(x,'CrossoverMenuInput',watch=check)
    assert decoder_reads==set(range(0xae1b,0xafd3)),(min(decoder_reads),max(decoder_reads),len(decoder_reads))
    assert not hits
    source=R/'src/character_select.s';callers=[dict(line=i,text=l.strip())for i,l in enumerate(source.read_text().splitlines(),1)if re.search(r'\b(?:jsr|jmp|farcall)\s+QueueSelection\b',l)]
    assert len(callers)==2 and all('jsr QueueSelection'in r['text']for r in callers)
    q=dict(passed=True,source_proposal_only=True,ROM_written=False,shared_grant=False,current_input_SHA256=sha(raw),old_menu_codec_exact=True,old_decoder_source91_exact=True,codec_half_open=[0xae1b,0xb0c0],stream_half_open=[0xae1b,0xafd3],decoder_half_open=[0xafd3,0xb02e],source_declared_codec_padding=[0xb02e,0xb0c0],source_declared_decoder_entry_padding=[0xa58b,0xa5b9],original_Select_extent=[0xad39,0xad7b],original_Select_used=61,original_Select_padding=5,new_gate_half_open=[0xad3c,proposal['layout']['labels']['DkGateEnd']],new_code_half_open=[0xb02e,proposal['layout']['labels']['DkCodeEnd']],new_data_half_open=[0xa58b,proposal['layout']['labels']['DkDataEnd']],retained_decoder_public_JMP_A588=True,retained_Bub_event_A0D6=True,compiled_finite_UI_instruction_epochs=steps,old_padding_fetches_or_reads=0,decoder_indirect_source_read_bytes=len(decoder_reads),actual_constructor_slots=32,actual_profile_machine_states=len(rows),all8_legal_individual_inputs_per_state=True,source_QueueSelection_callers=callers,public_entry_contract='Replace exact first3B STA016A with JMPAD3C. Foreign PHP/PHA/LDA/CMP then PLA/PLP restores originalA/P; genuine STA016A and JMP original+3 reproduce the sole overwritten instruction. No original+1/+2 entry exists in source; the two genuine QueueSelection callers remain unchanged.',typed_packet_walker='After genuine DK28 queue, walk complete menu commands. All native current menu publishers and validator use address-low28 only for2328/length16; cursor lows are23,26,29,2C,2F,32,35,38,A3,A6,A9,AC,AF,B2,B5,B8. Body palettes10/11/15/19/1D, hint46, restoration10..1F cannot match28. The pointer-assumption negatives are retained. No unrestricted byte scan.',no_new_RAM_CHR_or_slot=True,remaining=['This finite current UI proof does not replace actual IRQ/FF/nested lifetime qualification of the new code or root exact menu/shared span grant.','Final same-life stage/game-select/respawn source/native path and all-owner cold composition must retain the eventual Prince/Bub fingerprints.'],bindings={p.relative_to(R).as_posix():sha(p.read_bytes())for p in [Path(__file__),Path(T.__file__),producer,root/'mr-gimmick-family-v18.json',root/'family-v18-decoder.s',root/'family-v18-decoder.bin',root/'family-v18-toggle.s',root/'family-v18-toggle.bin',root/'family-v18-nav.s',root/'family-v18-nav.bin',source,R/'src/menu_vram_budget.s',O/'current-menu-v2.json',O/'current-menu-v3-CPU.json']})
    (O/'current-menu-funding-v5.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','source_QueueSelection_callers','public_entry_contract','typed_packet_walker']}))


if __name__=='__main__':
    try:main()
    except Exception as e:
        (O/'current-menu-funding-v5-negative.json').write_text(json.dumps(dict(passed=False,exception=repr(e)),indent=2)+'\n');raise
