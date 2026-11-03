"""Source-funded focused DK/Jr selector and current finite menu reader proof.

Private in-memory image only. Names/portraits and native admission are not
silently implemented by selecting raw40; the receipt states those boundaries.
"""
import collections,copy,json,re
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
import audit_current_menu_indicators_1102_v1 as MENU
import audit_bub_menu_frontend_1102_v1 as F
import check_hogan_current_bounded_v1 as N
from inventory_playable_menu_1101_v3 import menu_name
R=A.R;O=A.O;W=A.W


def main():
    raw=A.BASE.read_bytes();assert A.sha(raw)==A.PIN
    b=MENU.bundle();b['raw']=raw
    current=W.scoped_load(R/'build/menu-family-root-candidate-1102-v1/mr-gimmick-family.nes')
    for key,value in current['segs'].items():b['segs']['DK_MENU_'+str(key)]=value
    for key,value in current['syms'].items():
        row=dict(value)
        if 'seg'in row:row['seg']='DK_MENU_'+str(row['seg'])
        b['syms'][key]=row
    source=R/'build/menu-family-root-candidate-1102-v1/producer-snapshot.py';authority=source.read_text()
    assert 'stream+body+bytes([0xea])*(677-len(stream)-len(body))'in authority
    off=lambda bank,pc:16+bank*8192+pc-0xa000
    assert raw[off(66,0xb02e):off(66,0xb0c0)]==bytes([234])*146
    assert raw[off(124,0xadee):off(124,0xadff)]==bytes.fromhex('4ca6a0')+bytes([234])*14
    nav='.setcpu "6502"\n.segment "NAV"\n.export Up,Down,Hi,Resolve,UsedEnd\n'
    for name,start in [('Left',0),('Right',32),('Characters',64),('CursorLo',96)]:
        nav+=name+':.byte '+','.join(map(str,raw[off(124,0xa000+start):off(124,0xa020+start)]))+'\n'
    nav+='''Up:
 jsr Down
 eor #16
 rts
Down:
 php
 txa
 clc
 adc #8
 and #31
 plp
 ora #0
 rts
Hi:
 php
 tya
 lsr
 lsr
 lsr
 clc
 adc #1
 lsr
 clc
 adc #$20
 plp
 ora #0
 rts
Resolve:
 lda Characters,x
 php
 cpx #27
 bne OldFamilies
 lda $6002
 cmp #40
 beq Done
 lda #28
 bne Done
OldFamilies:
 cpx #25
 bne Arthur
 lda $5ffe
 beq Gimmick
 lda #39
 bne Done
Gimmick:
 lda #26
 bne Done
Arthur:
 cpx #31
 bne Done
 bit $5fe5
 bpl Done
 lda #24
Done:
 plp
 rts
UsedEnd:
 .res $d6-(*-Left),$ea
'''
    navbin,L=A.assemble('menu-nav-v17',nav,'MEMORY{P:start=$a000,size=$d6,file=%O;}SEGMENTS{NAV:load=P,type=ro;}')
    assert len(navbin)==214 and L['UsedEnd']==0xa0d2
    alt='.setcpu "6502"\n.segment "ALT"\n.export Cold\n jmp $%04x\nCold:\n lda #0\n sta $5ffe\n sta $5fe5\n sta $5fe8\n jmp $a9d0\n'%L['Resolve']
    altbin,AL=A.assemble('menu-alt-v17',alt,'MEMORY{P:start=$adee,size=$11,file=%O;}SEGMENTS{ALT:load=P,type=ro;}')
    assert len(altbin)==17
    oldtoggle=(R/'build/menu-family-root-candidate-1102-v1/family-v18-toggle.s').read_text()
    assert oldtoggle.count(' cpx #25\n bne Foreign\n')==1
    toggle=oldtoggle.replace(' cpx #25\n bne Foreign\n',''' cpx #25
 beq Gimmick
 cpx #27
 bne Foreign
 lda $6002
 eor #$34
 sta $6002
 sec
 rts
Gimmick:
''')
    togglebin,TL=A.assemble('menu-toggle-v17',toggle,'MEMORY{P:start=$b02e,size=$92,file=%O;}SEGMENTS{CODE:load=P,type=ro;}')
    assert len(togglebin)==75
    image=bytearray(raw);patches=[]
    def patch(at,new,role):
        old=raw[at:at+len(new)];assert len(old)==len(new)
        assert not any(max(at,p['offset'])<min(at+len(new),p['offset']+len(bytes.fromhex(p['new'])))for p in patches)
        image[at:at+len(new)]=new;patches.append(dict(offset=at,old=old.hex(),new=new.hex(),role=role))
    patch(off(124,0xa000),navbin,'Existing214B nav: exact flag-preserving Up factor and DK focus resolver')
    patch(off(124,0xadee),altbin,'Existing17B public AltTail: JMP plus relocated14B Cold in declared tail')
    prior=json.loads((R/'build/bub-menu-navigation-1102-v1/proposal.json').read_text())
    for row in prior['patches']:
        if row['table']not in ['Up','Down','CursorHi']:continue
        name='Hi'if row['table']=='CursorHi'else row['table'];at=row['offset'];oldtarget={'Up':0xa080,'Down':0xa08b,'Hi':0xa096}[name]
        assert raw[at:at+3]==bytes([32,oldtarget&255,oldtarget>>8])
        patch(at,bytes([32,L[name]&255,L[name]>>8]),'Current actual '+row['table']+' operand')
    cold=bytes.fromhex('a9c88d6c01a9a08d6d01a9fc');assert raw.count(cold)==1
    patch(raw.index(cold),bytes([169,AL['Cold']&255])+bytes.fromhex('8d6c01a9')+bytes([AL['Cold']>>8])+bytes.fromhex('8d6d01a9fc'),'Unique current real cold FarCallCommon target')
    patch(off(66,0xad39),bytes.fromhex('4c2eb0')+bytes([234])*63,'Same66B old toggle entry: tail JMP and declared source padding')
    patch(off(66,0xb02e),togglebin,'75B expanded Select in source-declared146B codec tail')
    new=copy.deepcopy(b);new['raw']=bytes(image)
    assert image[off(124,0xa0d6):off(124,0xa0e0)]==raw[off(124,0xa0d6):off(124,0xa0e0)]
    # Exact native navigation/QueueCursor ABI across every old position and
    # flag combination; no Python imitation of input/cursor implementation.
    seeds=[N.fresh(x)for x in [b,new]];tests=collections.Counter()
    def state(m):return bytes(m[:256])+bytes(m[0x1e0:0x800])+bytes(m[0x5000:0x8000])
    for slot,flags,mask in __import__('itertools').product(range(32),[0x30,0x31,0x70,0xf1],[0,1,2,4,8,15]):
        pair=[]
        for seed in seeds:
            m=N.fork(seed);N.put(m,CrossoverMenuIndex=slot,CrossoverMenuPressed=mask,VRAM_Buffer1_Offset=0)
            z=N.invoke(m,'NrMenuNavigate',p=flags);pair.append((m,z))
        assert state(pair[0][0])==state(pair[1][0])
        assert all(pair[0][1][k]==pair[1][1][k]for k in ['A','X','Y','P']);tests['actual_navigation_foreign_AXYP_state_exact']+=1
    for slot,flags,offset in __import__('itertools').product(range(32),[0x30,0x31,0x70,0xf1],[0,32,76]):
        pair=[]
        for seed in seeds:
            m=N.fork(seed);N.put(m,CrossoverMenuIndex=slot,VRAM_Buffer1_Offset=offset);pair.append((m,N.invoke(m,'QueueCursor',a=253,p=flags)))
        assert state(pair[0][0])==state(pair[1][0])and all(pair[0][1][k]==pair[1][1][k]for k in ['A','X','Y','P']);tests['actual_public_cursor_AXYP_state_exact']+=1
    # Complete current finite source profiles. Record every actual pending
    # name/portrait index, including later QueueSelection/cold callbacks.
    points={(W.address(b,'FmQueueName')+3,((W.location(b,'FmQueueName')-16)//8192)|128):'name',
            (W.address(b,'FmDrawPreviewSelected'),((W.location(b,'FmDrawPreviewSelected')-16)//8192)|128):'portrait'}
    readers=collections.Counter();trace=N.NesMPU
    class Trace(trace):
        def step(self):
            if self.pc>=0x8000:
                kind=points.get((self.pc,self.memory.rawtags[(self.pc-0x8000)//8192]))
                if kind:readers[kind,self.a]+=1
            return super().step()
    N.NesMPU=Trace;profiles=[]
    variant_fields=[n for n,s in b['syms'].items()if 'Variant'in n and '::'not in n and int(s['val'],0)<0x8000 and not n.startswith('.')]+['FmAlts']
    try:
        for slot in range(32):
            m=N.fork(seeds[0]);N.put(m,CrossoverMenuIndex=slot,CmActive=0);m[0x5ffe]=0;N.invoke(m,'MenuResolveCharacter');N.invoke(m,'QueueSelection');seen=set()
            n=N.fork(seeds[1]);N.put(n,CrossoverMenuIndex=slot,CmActive=0);n[0x5ffe]=0;N.invoke(n,'MenuResolveCharacter');N.invoke(n,'QueueSelection')
            for cycle in range(32):
                name,cells=menu_name(m);sig=(name,N.get(m,'SelectedCharacter'),m[0x5ffe],tuple((n,N.get(m,n))for n in variant_fields))
                if sig in seen:break
                seen.add(sig);profiles.append(dict(slot=slot,cycle=cycle,name=name,raw=N.get(m,'SelectedCharacter')))
                if slot!=27:
                    assert menu_name(n)==(name,cells)and N.get(n,'SelectedCharacter')==N.get(m,'SelectedCharacter'),(slot,cycle,name,menu_name(n))
                    tests['all_current_foreign_Select_names_raw_exact']+=1
                for hook in ['FmPending']:
                    z=N.invoke(m,hook);tests['actual_current_pending_profiles']+=1
                N.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0);N.invoke(m,'CrossoverMenuInput')
                if slot!=27:
                    N.put(n,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0);N.invoke(n,'CrossoverMenuInput')
        assert len(profiles)==94,len(profiles)
    finally:N.NesMPU=trace
    # DK focus retains40 through ordinary resolution; leaving focus replaces
    # SelectedCharacter through the genuine menu resolver, returning defaults28.
    dk=[]
    for flags in [0x30,0x31,0x70,0xf1]:
        m=N.fork(seeds[1]);N.put(m,CrossoverMenuIndex=27,SelectedCharacter=28,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0,VRAM_Buffer1_Offset=0)
        N.invoke(m,'CrossoverMenuInput',p=flags)
        assert N.get(m,'SelectedCharacter')==40
        N.invoke(m,'MenuResolveCharacter',p=flags);assert N.get(m,'SelectedCharacter')==40
        # Name/portrait for raw40 are deliberately not claimed by this slice.
        N.put(m,CrossoverMenuButtons=0,VRAM_Buffer1_Offset=0);N.invoke(m,'CrossoverMenuInput',p=flags);assert N.get(m,'SelectedCharacter')==28
        N.put(m,CrossoverMenuIndex=27,SelectedCharacter=40);N.invoke(m,'MenuResolveCharacter');assert N.get(m,'SelectedCharacter')==40
        N.put(m,CrossoverMenuIndex=26);N.invoke(m,'MenuResolveCharacter');assert N.get(m,'SelectedCharacter')!=40
        N.put(m,CrossoverMenuIndex=27);N.invoke(m,'MenuResolveCharacter');assert N.get(m,'SelectedCharacter')==28
        dk.append(dict(P=flags,toggle_both_directions=True,focused_resolution_retains40=True,leaving_focus_reset28=True));tests['actual_DK_Jr_focus_Select_resolution']+=1
    out=dict(passed=True,proposal_only=True,ROM_written=False,menu_admitted=False,native_owner_admitted=False,base_SHA256=A.PIN,nav_used=210,nav_extent=214,nav_event_gate_unchanged=True,toggle_bytes=75,toggle_PC_half_open=[0xb02e,0xb079],old_toggle_entry_extent=66,source_declared_codec_tail=[0xb02e,0xb0c0],remaining_frontend_source_bytes=134,
        checks=dict(tests),focused_DK_cases=dk,current_profile_count=len(profiles),actual_pending_readers=[dict(kind=k,index=i,calls=n)for(k,i),n in sorted(readers.items())],current_DK_profiles=[x for x in profiles if x['slot']==27],
        pending_row17_observed=any(i==17 for(k,i)in readers),patches=patches,
        policy='Temporary focused-only DK/Jr selector uses existing SelectedCharacter. Select28<->40, repeated resolver while focused retains40; leaving roster focus may resetDK. Gameplay identity must be separately retained by owner lifecycle. No new persistent selector RAM.',
        remaining=['Static Jr name/portrait/pending/readiness and real Start/A launch remain gated until complete source caller/resource proof.','Actual native owner raw40 namespace, code/art/RAM lease/public routes and lifecycle/IRQ qualification are not granted by this menu measurement.'],
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),A.BASE,source,R/'build/menu-family-root-candidate-1102-v1/family-v18-toggle.s',O/'menu-nav-v17.s',O/'menu-nav-v17.bin',O/'menu-alt-v17.bin',O/'menu-toggle-v17.bin']})
    (O/'menu-proposal-v17.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in ['passed','nav_used','toggle_bytes','remaining_frontend_source_bytes','checks','current_profile_count','actual_pending_readers','pending_row17_observed']}))


if __name__=='__main__':main()
