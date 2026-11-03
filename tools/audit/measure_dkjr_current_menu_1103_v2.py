"""Source-funded current32slot focused DK Jr alternate. CPU/memory only."""
from pathlib import Path
import collections,copy,itertools,json,re,subprocess,sys
import prepare_dkjr_current_menu_1103_v1 as V
R,O,N,F,D=V.R,V.O,V.N,V.F,V.D
address,location,off,sha=V.address,V.location,V.off,V.sha


def assemble(stem,source,cfg):
    p=O/stem;p.with_suffix('.s').write_text(source);p.with_suffix('.cfg').write_text(cfg)
    cc=R/'tools/Windows/cc65/bin'
    for args in [[cc/'ca65.exe',p.with_suffix('.s'),'-o',p.with_suffix('.o')],[cc/'ld65.exe','-C',p.with_suffix('.cfg'),p.with_suffix('.o'),'-o',p.with_suffix('.bin'),'-Ln',p.with_suffix('.lbl')]]:
        z=subprocess.run(list(map(str,args)),capture_output=True,text=True);assert z.returncode==0,z.stderr
    L={n:int(v,16)for v,n in re.findall(r'^al ([0-9a-fA-F]+) \.(\S+)$',p.with_suffix('.lbl').read_text(),re.M)}
    return p.with_suffix('.bin').read_bytes(),L


def image():
    old,prince,frontend=V.current();raw=old['raw'];source=R/'build/menu-family-root-candidate-1102-v1/producer-snapshot.py'
    assert 'stream+body+bytes([0xea])*(677-len(stream)-len(body))'in source.read_text()
    assert raw[off(66,0xb02e):off(66,0xb0c0)]==bytes([234])*146
    assert raw[off(66,0xa58b):off(66,0xa5b9)]==bytes([234])*46
    assert raw[off(66,0xa588)]==0x4c and raw[off(66,0xa589):off(66,0xa58b)]==bytes.fromhex('d3af')
    nav='.setcpu "6502"\n.segment "NAV"\n.export Up,Down,Hi,Resolve,UsedEnd\n'
    for name,start in [('Left',0),('Right',32),('Characters',64),('CursorLo',96)]:nav+=name+':.byte '+','.join(map(str,raw[off(124,0xa000+start):off(124,0xa020+start)]))+'\n'
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
    nb,L=assemble('current-nav-v2',nav,'MEMORY{P:start=$a000,size=$d6,file=%O;}SEGMENTS{NAV:load=P,type=ro;}')
    alt='.setcpu "6502"\n.segment "ALT"\n.export Cold\n jmp $%04x\nCold:\n lda #0\n sta $5ffe\n sta $5fe5\n sta $5fe8\n jmp $a9d0\n'%L['Resolve']
    ab,AL=assemble('current-alt-v2',alt,'MEMORY{P:start=$adee,size=$11,file=%O;}SEGMENTS{ALT:load=P,type=ro;}')
    c,frames=D.active();D.frame(c,0);sm=c.memory;original=list(sm[0x210:0x230]);rgb=list(sm.ppu[0x3f15:0x3f18]);pose=[]
    for i in range(0,32,8):
        y,t,a,x=original[i:i+4];assert original[i+4:i+8]==[y+8,t+1,a,x]
        assert 80<=t<=86 and t%2==0 and a==1
        pose += [167,t,0,112+x-original[3]]
    assert len(pose)==16 and rgb==[48,6,54],rgb
    assert (R/'build/dkjr-native-source-1102-v2/native-art-960-v38.chr').read_bytes()[256:384]==D.donor()[16400+1280:16400+1408]
    names=['SelectedCharacter','VRAM_Buffer1','VRAM_Buffer1_Offset','Sprite_Data','CurrentOAMOffset','ObjectMetasprite','SmPosePtr','SafecallA_SMC','FarcallJmpTarget_SMC','FarCallCommon']
    text='.setcpu "6502"\n.export DkQueueSelection,DkQueueOriginal,DkGateEnd,DkToggle,DkFinish,DkCodeEnd,DkMapTail,DkName,DkMenuOam,DkDataEnd\n'+''.join(n+'=$%04x\n'%address(old,n)for n in names)
    text+='''.segment "GATE"
DkQueueSelection:
 php
 pha
 lda SelectedCharacter
 cmp #40
 bne ForeignQueue
Own:
 pla
 plp
 lda #28
 sta SelectedCharacter
 jsr DkQueueOriginal
 ; Walk complete native menu packets. The current validator/publishers use
 ; low address28 only for the native2328/16 name, including unmerged queues.
 ldx #0
NameFind:
 lda VRAM_Buffer1+1,x
 cmp #$28
 beq NameFound
 ldy VRAM_Buffer1+2,x
 inx
 inx
 inx
NameSkip:
 inx
 dey
 bne NameSkip
 beq NameFind
NameFound:
 lda #<ObjectMetasprite
 sta SmPosePtr
 lda #>ObjectMetasprite
 sta SmPosePtr+1
 jmp DkFinish
ForeignQueue:
 pla
 plp
DkQueueOriginal:
 sta SafecallA_SMC+1
 jmp $%04x
DkGateEnd:
.segment "CODE"
DkToggle:
 lda $7308
 and #$20
 beq Foreign
 ldx $7309
 cpx #25
 beq Gimmick
 cpx #27
 bne Foreign
 lda $6002
 eor #$34
 sta $6002
 sec
 rts
Gimmick:
 inc $5ffe
 ldx $5ffe
 cpx #3
 bcc Keep
 ldx #0
 stx $5ffe
Keep:
 lda $5fe8
 and #$7f
 cpx #2
 bne NotBob
 ora #$80
NotBob:
 sta $5fe8
 sec
 rts
Foreign:
 lda #$8a
 sta $016c
 lda #$ba
 sta $016d
 lda #$cc
 jmp $015a
DkFinish:
 ldy #16
 sty CurrentOAMOffset
NameCopy:
 lda DkName-1,y
 sta VRAM_Buffer1+3,x
 inx
 dey
 bne NameCopy
 sty ObjectMetasprite
 lda #40
 sta SelectedCharacter
 ldx #15
OamCopy:
 lda DkMenuOam,x
 sta Sprite_Data,x
 dex
 bpl OamCopy
 lda #248
 sta Sprite_Data+16
 sta Sprite_Data+20
 ldx VRAM_Buffer1_Offset
'''%(address(old,'QueueSelection')+3)
    # NativeDK final P0 opaque30 is unchanged; swap only the two remaining
    # actual original-source colors. Native universal/background byte stays.
    for i,value in enumerate(rgb[1:],1):text+=' lda #%d\n sta VRAM_Buffer1-%d,x\n'%(value,3-i)
    text+=''' lda #$c0
 ldx #3
 iny
 sta SafecallA_SMC+1
 lda #$%02x
 sta FarcallJmpTarget_SMC+1
 jmp DkMapTail
DkCodeEnd:
.segment "DATA"
DkMapTail:
 lda #$%02x
 sta FarcallJmpTarget_SMC+2
 lda #$%02x
 jmp FarCallCommon
DkName:
 .byte '''%(address(old,'X5SetPhysicalChr')&255,address(old,'X5SetPhysicalChr')>>8,((location(old,'X5SetPhysicalChr')-16)//8192)|128)+','.join(map(str,reversed([36]+[ord(s)-55 if s!=' 'else 36 for s in 'DONKEY KONG JR']+[36])))+'\nDkMenuOam:\n .byte '+','.join(map(str,pose))+'\nDkDataEnd:\n'
    cfg='MEMORY{G:start=$ad3c,size=$3f,file=%O;C:start=$b02e,size=$92,file="'+(O/'current-menu-code-v2.bin').as_posix()+'";D:start=$a58b,size=$2e,file="'+(O/'current-menu-data-v2.bin').as_posix()+'";}SEGMENTS{GATE:load=G,type=ro;CODE:load=C,type=ro;DATA:load=D,type=ro;}'
    gate,T=assemble('current-menu-v2',text,cfg);code=(O/'current-menu-code-v2.bin').read_bytes();data=(O/'current-menu-data-v2.bin').read_bytes()
    post=bytearray(raw);patches=[]
    def put(bank,pc,new,role):
        at=off(bank,pc);before=raw[at:at+len(new)];post[at:at+len(new)]=new;patches.append(dict(physical_PRG=bank,CPU_half_open=[pc,pc+len(new)],file_offset=at,old_hex=before.hex(),new_hex=new.hex(),role=role))
    put(124,0xa000,nb,'Existing214B navigation source; factor exact Up and move14B Cold to old AltTail padding')
    put(124,0xadee,ab,'Existing17B public AltTail/sourcepadding; relocate original Cold')
    prior=json.loads((R/'build/bub-menu-navigation-1102-v1/proposal.json').read_text())
    for row in prior['patches']:
        if row['table']not in ['Up','Down','CursorHi']:continue
        name='Hi'if row['table']=='CursorHi'else row['table'];at=row['offset'];pc=0xa000+(at-16)%8192;bank=(at-16)//8192
        oldtarget={'Up':0xa080,'Down':0xa08b,'Hi':0xa096}[name];assert raw[at:at+3]==bytes([32,oldtarget&255,oldtarget>>8]);put(bank,pc,bytes([32,L[name]&255,L[name]>>8]),'Exact current '+name+' call operand')
    cold=bytes.fromhex('a9c88d6c01a9a08d6d01a9fc');assert raw.count(cold)==1;at=raw.index(cold)
    put((at-16)//8192,0xa000+(at-16)%8192,bytes([169,AL['Cold']&255])+bytes.fromhex('8d6c01a9')+bytes([AL['Cold']>>8])+bytes.fromhex('8d6d01a9fc'),'Current actual Cold farcall target only')
    put(66,0xad39,bytes([76,T['DkToggle']&255,T['DkToggle']>>8]),'Existing66B Select entry tailJMP; remainder funds exact owning wrapper')
    put(66,0xad3c,gate,'Source old Select66B extent: full foreign QueueSelection continuation and owner-only snapshot')
    put(66,0xb02e,code,'Source-declared146B codec padding: Select+post-native source name/OAM/palette')
    put(66,0xa58b,data,'Source-declared46B decoderentry padding: immutable name/sourcepose and mapper tail')
    qpc=address(old,'QueueSelection');assert raw[location(old,'QueueSelection'):location(old,'QueueSelection')+3]==bytes([0x8d,(address(old,'SafecallA_SMC')+1)&255,(address(old,'SafecallA_SMC')+1)>>8])
    put((location(old,'QueueSelection')-16)//8192,qpc,bytes([76,T['DkQueueSelection']&255,T['DkQueueSelection']>>8]),'Only exact3B first STA replaced; unchanged original +3 continuation, foreign ABI retained')
    assert len(nb)==214 and len(ab)==17 and len(gate)<=63 and len(code)<=146 and len(data)<=46
    assert post[off(124,0xa0d6):off(124,0xa0e0)]==raw[off(124,0xa0d6):off(124,0xa0e0)]
    return old,dict(old,raw=bytes(post)),dict(patches=patches,layout=dict(gate=len(gate),code=len(code),data=len(data),nav_used=L['UsedEnd']-0xa000,labels={**L,**AL,**T}),source_portrait=dict(donor_SHA256=D.SHA,credits='Nintendo original NES Donkey Kong Jr. World Rev1 pixels/idle pose and palette.',original_idle_OAM=original,original_palette1=rgb,native_8x16_OAM=pose,physical_CHR=960,physical_byte_half_open=[256,384],new_CHR_bytes=0,publisher='Actual X5SetPhysicalChr A=C0/X3/Y1',temporary_DK28_only_during_original_QueueSelection=True),source=source)


def main():
    negative=O/'current-menu-v3-negative.json';keep=O/'current-menu-v2-original-offset-negative.json'
    if negative.exists() and not keep.exists():keep.write_bytes(negative.read_bytes())
    old,new,q=image();m=V.seed(new,27);N.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0);z=F.invoke(m,'CrossoverMenuInput');name,cells=V.menu_name(m)
    assert N.get(m,'SelectedCharacter')==40 and name=='DONKEY KONG JR',(N.get(m,'SelectedCharacter'),name,cells)
    at=address(new,'Sprite_Data');assert list(m[at:at+16])==q['source_portrait']['native_8x16_OAM']
    q.update(passed=True,source_proposal_only=True,ROM_written=False,menu_admitted=False,native_qualified=False,current_input_SHA256=sha(old['raw']),expected_memory_only_SHA256=sha(new['raw']),initial_Jr_name=name,checks=dict(actual_Select_to_Jr=True,actual_source_8x16_portrait=True),bindings={str(p.relative_to(R)).replace('\\','/'):sha(p.read_bytes())for p in [Path(__file__),Path(V.__file__),q.pop('source'),R/'docs/qa/allocations/prince-current-frontend-1103-v105.json',R/'build/prince-actor-1101-v1/backdrop-manifest-v159.json']})
    (O/'current-menu-v2.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in ['passed','layout','initial_Jr_name','expected_memory_only_SHA256']}))


if __name__=='__main__':main()
