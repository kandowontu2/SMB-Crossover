"""Source-funded ninth Mario menu alternate; memory-only proposal, no ROM."""
import hashlib,json,re,subprocess
from pathlib import Path
import prepare_dkjr_current_menu_1103_v1 as V
from prepare_selected_native_packet_v1 import R,sha
N,F,address,location,off=V.N,V.F,V.address,V.location,V.off
O=R/'build/mini-mario-menu-1103-v14'
ROM=R/'build/combined-owner-auth-root-1103-v116/combined-auth-private.nes'
PIN='80d3ae95894f5ddb430c3e753dd95f3fc2eca6a87d8e1afdb4b8ce8376ec795a'
ART_PAGE=0 # Explicit placeholder only; no claim page0 is free/allocated.


def assemble(stem,source,cfg):
    p=O/stem;p.with_suffix('.s').write_text(source);p.with_suffix('.cfg').write_text(cfg)
    cc=R/'tools/Windows/cc65/bin'
    for args in[[cc/'ca65.exe',p.with_suffix('.s'),'-o',p.with_suffix('.o')],[cc/'ld65.exe','-C',p.with_suffix('.cfg'),p.with_suffix('.o'),'-o',p.with_suffix('.bin'),'-Ln',p.with_suffix('.lbl')]]:
        z=subprocess.run(list(map(str,args)),capture_output=True,text=True);assert z.returncode==0,z.stderr
    labels={n:int(v,16)for v,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',p.with_suffix('.lbl').read_text(),re.M)}
    return p.with_suffix('.bin').read_bytes(),labels


def image():
    old,_,_=V.current();old=dict(old,raw=ROM.read_bytes());raw=old['raw'];assert sha(ROM)==PIN
    for pc,size in[(0xb02e,146),(0xa58b,46)]:assert raw[off(66,pc):off(66,pc)+size]==bytes([234])*size
    funding=R/'build/menu-family-root-candidate-1102-v1/producer-snapshot.py'
    assert 'stream+body+bytes([0xea])*(677-len(stream)-len(body))'in funding.read_text()
    nav='.setcpu "6502"\n.segment "NAV"\n.export Up,Down,Hi,Resolve,UsedEnd\n'
    for name,start in[('Left',0),('Right',32),('Characters',64),('CursorLo',96)]:nav+=name+':.byte '+','.join(map(str,raw[off(124,0xa000+start):off(124,0xa020+start)]))+'\n'
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
 cpx #0
 bne Old
 lda $730a
 cmp #8
 bne Mario
 lda #41
 bne Done
Mario:
 lda #0
 beq Done
Old:
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
    nb,L=assemble('nav',nav,'MEMORY{P:start=$a000,size=$d6,file=%O;}SEGMENTS{NAV:load=P,type=ro;}')
    ab,AL=assemble('alt','.setcpu "6502"\n.segment "ALT"\n.export Cold\n jmp $%04x\nCold:\n lda #0\n sta $5ffe\n sta $5fe5\n sta $5fe8\n jmp $a9d0\n'%L['Resolve'],'MEMORY{P:start=$adee,size=$11,file=%O;}SEGMENTS{ALT:load=P,type=ro;}')
    names=['SelectedCharacter','MarioVariant','VRAM_Buffer1','VRAM_Buffer1_Offset','Sprite_Data','ObjectMetasprite','SmPosePtr','SafecallA_SMC','FarcallJmpTarget_SMC','FarCallCommon']
    code='.setcpu "6502"\n.export MiniQueue,MiniOriginal,MiniToggle,MiniFinish,MiniMapSetup,MiniGateEnd,MiniCodeEnd,MiniDataEnd\n'+''.join(n+'=$%04x\n'%address(old,n)for n in names)
    code+='''.segment "GATE"
MiniQueue:
 php
 pha
 lda SelectedCharacter
 cmp #41
 bne ForeignQueue
 pla
 plp
 lda #0
 sta MarioVariant
 sta SelectedCharacter
 jsr MiniOriginal
 ldx #0
FindName:
 lda VRAM_Buffer1+1,x
 cmp #$28
 beq Found
 txa
 clc
 adc VRAM_Buffer1+2,x
 adc #3
 tax
 bne FindName
Found:
 lda #<ObjectMetasprite
 sta SmPosePtr
 lda #>ObjectMetasprite
 sta SmPosePtr+1
 jmp MiniFinish
ForeignQueue:
 pla
 plp
MiniOriginal:
 sta SafecallA_SMC+1
 jmp $%04x
MiniGateEnd:
.segment "CODE"
MiniToggle:
 lda $7308
 and #$20
 beq Foreign
 ldx $7309
 bne Gimmick
 lda MarioVariant
 cmp #7
 bne Foreign
 inc MarioVariant
 lda #41
 sta SelectedCharacter
 ; Successful CMP#7 already supplies C; INC/LDA/STA preserve it.
 rts
Gimmick:
 cpx #25
 bne Foreign
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
MiniFinish:
 ldy #16
NameCopy:
 lda MiniName-1,y
 sta VRAM_Buffer1+3,x
 inx
 dey
 bne NameCopy
 sty ObjectMetasprite
 lda #8
 sta MarioVariant
 lda #41
 sta SelectedCharacter
 lda #64
 sta Sprite_Data+1
 lda #124
 sta Sprite_Data+3
 ldx #20
 lda #248
Hide:
 sta Sprite_Data,x
 dex
 dex
 dex
 dex
 bne Hide
 ldx VRAM_Buffer1_Offset
 jmp MiniPalette
MiniMapSetup:
 ldx #%d
 iny
 sta SafecallA_SMC+1
 lda #$%02x
 sta FarcallJmpTarget_SMC+1
 jmp MiniMapTail
MiniCodeEnd:
.segment "DATA"
MiniMapTail:
 lda #$%02x
 sta FarcallJmpTarget_SMC+2
 lda #$%02x
 jmp FarCallCommon
MiniName:
 .byte '''%(address(old,'QueueSelection')+3,ART_PAGE>>8,address(old,'X5SetPhysicalChr')&255,address(old,'X5SetPhysicalChr')>>8,((location(old,'X5SetPhysicalChr')-16)//8192)|128)
    name=[36]*3+[ord(c)-55 if c!=' 'else 36 for c in 'MINI MARIO']+[36]*3;assert len(name)==16
    code+=','.join(map(str,reversed(name)))+'''
MiniPalette:
 lda #$27
 sta VRAM_Buffer1-3,x
 lda #$16
 sta VRAM_Buffer1-2,x
 lda #$18
 sta VRAM_Buffer1-1,x
 lda #%d
 jmp MiniMapSetup
MiniDataEnd:
'''%(ART_PAGE&255)
    cfg='MEMORY{G:start=$ad3c,size=$3f,file=%O;C:start=$b02e,size=$92,file="'+(O/'code.bin').as_posix()+'";D:start=$a58b,size=$2e,file="'+(O/'data.bin').as_posix()+'";}SEGMENTS{GATE:load=G,type=ro;CODE:load=C,type=ro;DATA:load=D,type=ro;}'
    gate,T=assemble('menu',code,cfg);body=(O/'code.bin').read_bytes();data=(O/'data.bin').read_bytes();post=bytearray(raw);patches=[]
    def put(bank,pc,new,role):
        at=off(bank,pc);before=raw[at:at+len(new)];assert all(not(set(range(at,at+len(new)))&set(range(z['file_offset'],z['file_offset']+len(bytes.fromhex(z['new_hex'])))))for z in patches)
        post[at:at+len(new)]=new;patches.append(dict(physical_PRG=bank,CPU_half_open=[pc,pc+len(new)],file_offset=at,old_hex=before.hex(),new_hex=new.hex(),role=role))
    put(124,0xa000,nb,'Same214B nav; exact old32slots and Mini raw41 resolver; original Cold moves to authored AltTail padding')
    put(124,0xadee,ab,'Same17B AltTail/14B declaredpadding; old Cold relocated unchanged')
    prior=json.loads((R/'build/bub-menu-navigation-1102-v1/proposal.json').read_text())
    for row in prior['patches']:
        if row['table']not in['Up','Down','CursorHi']:continue
        name='Hi'if row['table']=='CursorHi'else row['table'];at=row['offset'];assert raw[at]==32
        put((at-16)//8192,0xa000+(at-16)%8192,bytes([32,L[name]&255,L[name]>>8]),'Exact '+name+' public operand')
    cold=bytes.fromhex('a9c88d6c01a9a08d6d01a9fc');assert raw.count(cold)==1;at=raw.index(cold)
    put((at-16)//8192,0xa000+(at-16)%8192,bytes([169,AL['Cold']&255])+bytes.fromhex('8d6c01a9')+bytes([AL['Cold']>>8])+bytes.fromhex('8d6d01a9fc'),'Exact old Cold farcall operand')
    put(66,0xad39,bytes([76,T['MiniToggle']&255,T['MiniToggle']>>8]),'Existing public Select gate; current Gimmick branch reproduced')
    put(66,0xad3c,gate,'Existing63B Select owned source; Mini/foreign queued continuation')
    put(66,0xb02e,body,'Source-declared146B codecpadding; early MiniSelect and owner-only preview finish')
    put(66,0xa58b,data,'Source-declared46B decoderpadding; name/palette/map tail')
    qpc=address(old,'QueueSelection');qat=location(old,'QueueSelection');assert raw[qat:qat+3]==bytes([141,(address(old,'SafecallA_SMC')+1)&255,(address(old,'SafecallA_SMC')+1)>>8])
    put((qat-16)//8192,qpc,bytes([76,T['MiniQueue']&255,T['MiniQueue']>>8]),'Exact3B QueueSelection prefix; full foreign original+3 continuation')
    assert len(nb)==214 and len(ab)==17 and len(gate)<=63 and len(body)<=146 and len(data)<=46
    assert post[off(124,0xa0d6):off(124,0xa0e0)]==raw[off(124,0xa0d6):off(124,0xa0e0)]
    return old,dict(old,raw=bytes(post)),dict(patches=patches,labels={**L,**AL,**T},sizes=dict(nav=len(nb),alt=len(ab),gate=len(gate),code=len(body),data=len(data)),
        art=dict(physical_page_placeholder=ART_PAGE,allocation_claim=False,source='build/mini-mario-art-1103-v12/menu-portrait.chr',
            tile64_even_bank0_window1=True,source8x16pair=True,opaque_palette=[39,22,24],right_facing=True))


def main():
    O.mkdir(exist_ok=True);old,new,q=image();m=V.seed(new,0)
    N.put(m,MarioVariant=7);F.invoke(m,'MenuResolveCharacter');F.invoke(m,'QueueSelection')
    N.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0)
    F.invoke(m,'CrossoverMenuInput');name,cells=V.menu_name(m)
    assert N.get(m,'SelectedCharacter')==41 and N.get(m,'MarioVariant')==8 and name=='MINI MARIO',(N.get(m,'SelectedCharacter'),N.get(m,'MarioVariant'),name)
    sp=address(new,'Sprite_Data');portrait=list(m[sp:sp+24]);print('PORTRAIT',portrait,flush=True)
    q.update(passed=True,source_only=True,ROM_written=False,native_qualified=False,current_input_SHA256=PIN,expected_memory_only_SHA256=hashlib.sha256(new['raw']).hexdigest(),
        initial_name=name,initial_OAM=portrait,CurrentOAMOffset=N.get(m,'CurrentOAMOffset'),
        bindings={p.relative_to(R).as_posix():sha(p)for p in[Path(__file__),ROM,R/'build/menu-family-root-candidate-1102-v1/producer-snapshot.py',R/'build/mini-mario-art-1103-v12/receipt.json']})
    (O/'proposal.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=True,sizes=q['sizes'],memory_SHA256=q['expected_memory_only_SHA256'],name=name)))


if __name__=='__main__':main()
