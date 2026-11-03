"""Private focused DK/Jr menu wrapper with genuine DK family preview.

Uses the v17 declared source padding. No ROM/admission/shared mutation. The
initial functional policy deliberately shares DK's static family portrait.
"""
import copy,json,re
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
import audit_current_menu_indicators_1102_v1 as MENU
import check_hogan_current_bounded_v1 as N
from inventory_playable_menu_1101_v3 import menu_name
R=A.R;O=A.O;W=A.W


def main():
    raw=A.BASE.read_bytes();assert A.sha(raw)==A.PIN
    prior=json.loads((O/'menu-proposal-v17.json').read_text());assert prior['passed'];image=bytearray(raw)
    for p in prior['patches']:
        at=p['offset'];assert image[at:at+len(bytes.fromhex(p['old']))]==bytes.fromhex(p['old']);image[at:at+len(bytes.fromhex(p['new']))]=bytes.fromhex(p['new'])
    b=MENU.bundle();b['raw']=bytes(image)
    current=W.scoped_load(R/'build/menu-family-root-candidate-1102-v1/mr-gimmick-family.nes')
    for key,value in current['segs'].items():b['segs']['DK_MENU_'+str(key)]=value
    for key,value in current['syms'].items():
        row=dict(value)
        if 'seg'in row:row['seg']='DK_MENU_'+str(row['seg'])
        b['syms'][key]=row
    off=lambda bank,pc:16+bank*8192+pc-0xa000
    qp=W.address(b,'QueueSelection');at=W.location(b,'QueueSelection');prefix=raw[at:at+18]
    assert prefix==bytes.fromhex('8d6a01a9998d6c01a9b58d6d01a99d205a01')
    names=['SelectedCharacter','VRAM_Buffer1','VRAM_Buffer1_Offset','R0']
    glyphs=[ord(c)-55 if c!=' 'else 36 for c in 'DONKEY KONG JR'];assert len(glyphs)==14
    src='.setcpu "6502"\n.segment "GATE"\n.export DkQueueSelection,DkQueueOriginal,DkQueueEnd,DkNameFix,DkNameEnd\n'+''.join(n+'=$%04x\n'%W.address(b,n)for n in names)
    src+='''DkQueueSelection:
 php
 pha
 lda SelectedCharacter
 cmp #40
 beq DkQueueOwn
 pla
 plp
 jmp DkQueueOriginal
DkQueueOwn:
 pla
 plp
 lda #28
 sta SelectedCharacter
 jsr DkQueueOriginal
 lda #40
 sta SelectedCharacter
 jmp DkNameFix
DkQueueOriginal:
 .byte '''+','.join('$%02x'%v for v in prefix)+'''
 jmp $%04x
DkQueueEnd:
.segment "NAME"
DkNameFix:
 ldx #0
DkNameScan:
 cpx VRAM_Buffer1_Offset
 bcs DkNameDone
 lda VRAM_Buffer1,x
 cmp #$23
 bne DkNameNext
 lda VRAM_Buffer1+1,x
 cmp #$28
 bne DkNameNext
 lda VRAM_Buffer1+2,x
 cmp #16
 beq DkNameFound
DkNameNext:
 ; This owned branch sees only genuine DK28 QueueSelection's direct commands.
 ldy VRAM_Buffer1+2,x
 inx
 inx
 inx
DkNameSkip:
 inx
 dey
 bne DkNameSkip
 beq DkNameScan
DkNameDone:
 rts
DkNameFound:
 ldy #15
DkNameCopy:
 lda DkName,y
 sta VRAM_Buffer1+3,x
 inx
 dey
 bpl DkNameCopy
 rts
DkName:
 .byte '''%(qp+18)+','.join(str(v)for v in reversed([36]+glyphs+[36]))+'''
DkNameEnd:
'''
    cfg='MEMORY{G:start=$ad3c,size=$3f,file=%O;N:start=$b079,size=$47,file="'+(O/'menu-name-extra-v19.bin').as_posix()+'";}SEGMENTS{GATE:load=G,type=ro;NAME:load=N,type=ro;}'
    gate,L=A.assemble('menu-name-v19',src,cfg);namebin=(O/'menu-name-extra-v19.bin').read_bytes();assert len(gate)<=63 and len(namebin)<=71
    patches=[]
    def patch(at,data,role):
        old=bytes(image[at:at+len(data)]);image[at:at+len(data)]=data;patches.append(dict(offset=at,old=old.hex(),new=data.hex(),role=role))
    patch(off(66,0xad3c),gate,'Source-declared old-toggle tail: focused40 full native DK queue wrapper and exact prefix')
    patch(off(66,0xb079),namebin,'Remaining declared codec tail: replace existing16tile menu name in-place')
    patch(at,bytes([0x4c,L['DkQueueSelection']&255,L['DkQueueSelection']>>8]),'Actual QueueSelection owning gate, original18B prefix retained in funded helper')
    new=copy.deepcopy(b);new['raw']=bytes(image)
    tests=0;examples=[]
    for flags in [0x30,0x31,0x70,0xf1]:
        m=N.fresh(new);N.put(m,CrossoverMenuIndex=27,SelectedCharacter=28,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0,VRAM_Buffer1_Offset=0)
        N.invoke(m,'CrossoverMenuInput',p=flags);name,cells=menu_name(m)
        assert N.get(m,'SelectedCharacter')==40 and name=='DONKEY KONG JR',(flags,N.get(m,'SelectedCharacter'),name,cells)
        assert N.get(m,'VRAM_Buffer1_Offset')<=83
        # Public confirmation already returns ready for the legacy slot27.
        # This fixture tests source menu retention only; its image is not live.
        for key in [16,128]:
            n=N.fork(m);N.put(n,CrossoverMenuButtons=0,SavedJoypad1Bits=key,SavedJoypad2Bits=0,VRAM_Buffer1_Offset=0)
            N.invoke(n,'CrossoverMenuInput',p=flags)
            assert N.get(n,'CrossoverMenuState')==0 and N.get(n,'SelectedCharacter')==40
            tests+=1
        examples.append(dict(P=flags,name=name,raw40=True,Start_A_retains40=True,existing_native_DK_family_portrait=True,VRAM_offset=N.get(m,'VRAM_Buffer1_Offset')))
    # Foreign actual QueueSelection enters the unchanged native continuation
    # with exact AXYP; all legal old profiles retain their actual name/palettes.
    profiles=json.loads((O/'resource-menu-v13.json').read_text())['rows'];foreign=0
    seed=N.fresh(b)
    for row in profiles:
        if row['slot']==27:continue
        m=N.fork(seed);N.put(m,CrossoverMenuIndex=row['slot']);N.invoke(m,'MenuResolveCharacter');N.invoke(m,'QueueSelection')
        for _ in range(row['cycle']):
            N.put(m,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0,VRAM_Buffer1_Offset=0);N.invoke(m,'CrossoverMenuInput')
        n=N.fork(m);n.bundle=new
        for win,tag in enumerate(list(n.rawtags)):
            if tag&128:n.raw_page(win,tag)
        for mm in [m,n]:N.put(mm,VRAM_Buffer1_Offset=0)
        za=N.invoke(m,'QueueSelection',p=0xf1);zn=N.invoke(n,'QueueSelection',p=0xf1)
        assert all(za[k]==zn[k]for k in ['A','X','Y','P'])and menu_name(m)==menu_name(n)
        assert bytes(m[:256])+bytes(m[0x1e0:0x800])+bytes(m[0x5000:0x8000])==bytes(n[:256])+bytes(n[0x1e0:0x800])+bytes(n[0x5000:0x8000]),row['name']
        foreign+=1
    out=dict(passed=True,proposal_only=True,ROM_written=False,menu_admitted=False,native_owner_admitted=False,base_SHA256=A.PIN,gate_bytes=len(gate),gate_span=[0xad3c,L['DkQueueEnd']],name_bytes=len(namebin),name_span=[0xb079,L['DkNameEnd']],remaining_source_frontend_bytes=134-len(gate)-len(namebin),exact_foreign_QueueSelection_AXYP_state_profiles=foreign,actual_DK_Jr_Start_A_cases=tests,examples=examples,patches=patches,
        source_policy='Focused40 temporarily uses genuine DK28 only inside the complete native menu QueueSelection callback, then restores40 and replaces its existing2328/16 buffered name payload in-place. No extra mutable byte or VRAM command. Initial static portrait remains the existing DK family portrait; native Jr body is separate. Both Select directions and leaving-focus reset inherit exact v17 proposal.',
        remaining=['Full current source reader/indirect entry closure for the replaced QueueSelection prefix and all menu paths/cold/preview async proof.','All physical/conditional RAM/header/cookie/raw40/native-owner/public lifecycle grants and native qualification remain pending.'],
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in [Path(__file__),A.BASE,O/'resource-menu-v13.json',O/'menu-proposal-v17.json',R/'src/character_select.s',O/'menu-name-v19.s',O/'menu-name-v19.bin',O/'menu-name-extra-v19.bin']})
    (O/'menu-name-proposal-v19.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in ['passed','gate_bytes','name_bytes','remaining_source_frontend_bytes','exact_foreign_QueueSelection_AXYP_state_profiles','actual_DK_Jr_Start_A_cases']}))


if __name__=='__main__':main()
