"""Measure a source-contact/native-head adapter in the existing private gap.

No cartridge is written. This is a private source/CPU proposal against b7e2.
"""
import hashlib,json
from collections import Counter,deque
from pathlib import Path
import compose_bub_tail_gateways_1102_v66 as G
import measure_bub_landing_1102_v21 as L
from check_tmnt_render_oa import location
from prepare_selected_native_packet_v1 import R,sha

O=L.O;Q=G.G.G.Q;N=Q.N;address=Q.address
PIN='b7e2a161ea2781a8346b126b9c759f7c60f2583e2a18e58f8ca888d041c0bd53'
PAGES=[301,305,337,362,363,440,819,666]

def bundle():
    _,old,route,q=G.bundles();assert hashlib.sha256(old['raw']).hexdigest()==PIN
    image=bytearray((G.U.O/'private-image.bin').read_bytes());lab=q['labels']
    assert image[30:33]==bytes.fromhex('4c8795'),'Actual HuHead row10 is the native getter'
    start=lab['BbPowerupEnd'];assert start==0xb2b5
    assert image[start-0xa000:0x153a]==bytes([255])*(0xb53a-start)
    defs='\n'.join(f'{name}=${address(old,name):04x}' for name in [
        'Player_Y_Position','Player_Y_Speed','Player_Y_HighPos','GameEngineSubroutine',
        'AreaType','BlockBounceTimer','GuestHurtTicks','MTileAttribute','R2','R3','R6','R7'])
    source=f'''.setcpu "6502"
.export BbHeadBegin,BbHeadCapture,BbDeferredHead,BbDeferredHeadDone,BbHeadEnd
{defs}
BbNativeProxiesIn=${lab['BbNativeProxiesIn']:04x}
BbNativeCeilingContinue=${lab['BbNativeCeilingHit']+7:04x}
PlayerHeadCollision=$9ef5 ; Actual fixed126 public native head transaction.
NativeHead=$9587 ; Actual old row10 target, not an ambiguous DBG alias.
.segment "CODE"
; One genuine movement epoch owns this pending byte. C3C8 is the existing
; sweep pixel, written only by Ceiling until the next movement invocation.
BbHeadBegin:
 lda #0
 sta $c3ef
 jmp BbNativeProxiesIn
; R6 is the exact first-solid column pointer, X the actual metatile, Y row.
; Both block-buffer low bases 00/D0 have bit5 clear; OR20 is a valid flag.
; No deeper source stack frame: the original clamp is replayed then tailed.
BbHeadCapture:
 lda R6
 ora #$20
 sta $c3ef
 lda $c3c8
 and #$f0
 sta Player_Y_Position
 jmp BbNativeCeilingContinue
; HuHead is invoked after movement and its private save envelope unwind.
; Consume exactly once. An absent event uses the byte-exact old raw getter.
BbDeferredHead:
 lda $c3ef
 beq OldHead
 and #$df
 sta R6
 lda #0
 sta $c3ef
 lda GameEngineSubroutine
 cmp #8
 bne BbDeferredHeadDone
 lda Player_Y_HighPos
 cmp #1
 bne BbDeferredHeadDone
 lda AreaType
 beq BbDeferredHeadDone
 lda BlockBounceTimer
 ora GuestHurtTicks
 bne BbDeferredHeadDone
 lda $c3c8
 and #$f0
 sec
 sbc #32
 sta R2
 tay
 lda #>{address(old,'Block_Buffer_1')}
 sta R7
 lda (R6),y
 sta R3
 tax
 lda MTileAttribute,x
 and #3
 cmp #1
 bne BbDeferredHeadDone
 lda MTileAttribute,x
 and #6 ; Actual MTILE_BUMP4|MTILE_CLIMB2 exclusions.
 bne BbDeferredHeadDone
 ; The ordinary native bump writes speed0. Restore the already exported
 ; source displacement, as the existing deferred Rogue transaction does.
 lda Player_Y_Speed
 sta $c3ef
 txa
 jsr PlayerHeadCollision
 lda $c3ef
 sta Player_Y_Speed
 lda #0
 sta $c3ef
BbDeferredHeadDone:
 lda #0 ; The actual source contact was consumed; do not bump it twice.
 sec
 rts
OldHead:
 jmp NativeHead
BbHeadEnd:
'''
    labels=L.assemble('deferred-head-v54',source,
        f'MEMORY{{M:start=${start:04x},size=${0xb53a-start:x},file=%O;}}SEGMENTS{{CODE:load=M,type=ro;}}')
    code=(O/'deferred-head-v54.bin').read_bytes();assert len(code)<=645
    patches=[]
    def patch(pc,before,after,role):
        assert image[pc-0xa000:pc-0xa000+len(before)]==before,(hex(pc),role)
        assert len(before)==len(after)
        patches.append(dict(CPU=pc,old=before.hex(),new=after.hex(),role=role))
        image[pc-0xa000:pc-0xa000+len(after)]=after
    def jmp(pc):return bytes([0x4c])+pc.to_bytes(2,'little')
    patch(start,bytes([255])*len(code),code,'Source-declared reclaimed gap after the two current native gateways')
    patch(0xa01e,bytes.fromhex('4c8795'),jmp(labels['BbDeferredHead']),'Authoritative HuHead10 vector')
    hit=lab['BbNativeCeilingHit'];before=bytes.fromhex('adc8c329f085bd')
    assert before[-1]==address(old,'Player_Y_Position')
    patch(hit,before,jmp(labels['BbHeadCapture'])+bytes([234])*4,'Existing first-solid ceiling clamp, same continuation')
    needle=bytes([0x20])+lab['BbNativeProxiesIn'].to_bytes(2,'little')
    matches=[i+0xa000 for i in range(0x1540,len(image)-2)if image[i:i+3]==needle]
    assert len(matches)==1,matches
    patch(matches[0],needle,bytes([0x20])+labels['BbHeadBegin'].to_bytes(2,'little'),'Actual accepted movement boundary')
    raw=bytearray(old['raw']);art=raw[1048592+441*1024:1048592+442*1024]
    cookie=bytes([0xa7,39,1])+hashlib.sha256(image+art).digest()[:13]
    for i,page in enumerate(PAGES):raw[1048592+page*1024:1048592+(page+1)*1024]=image[i*1024:(i+1)*1024]
    raw[q['cookie_offset']:q['cookie_offset']+16]=cookie
    return old,dict(old,raw=bytes(raw)),route,q,labels,bytes(image),patches,cookie

def arena(b,route,identity,x=329):
    m=Q.Q.fresh(b,route,identity);Q.L.E.main_fields(m)
    N.put(m,NmiDisable=255,Player_X_Position=x&255,Player_PageLoc=x>>8,
        ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=x>>8,ScreenRight_PageLoc=(x>>8)+1,
        Player_Y_Position=176,Player_Y_HighPos=1,Player_State=0,Player_Y_Speed=0,
        PlayerSize=1,PlayerStatus=0,BlockBounceTimer=0,GuestHurtTicks=0,AreaType=1)
    for name in ['Block_Buffer_1','Block_Buffer_2']:
        for i in range(208):m[address(b,name)+i]=0
        for col in range(16):m[address(b,name)+0xb0+col]=0x54
    bx=(x+8)//16;cell=address(b,'Block_Buffer_2'if(bx//16)&1 else'Block_Buffer_1')+0x70+bx%16
    m[cell]=0xc1
    return m,cell

def main():
    old,b,route,q,labels,image,patches,cookie=bundle();records=[];actual=N.NesMPU
    points={(3,q['labels']['BbNativeCeilingHit']):'swept-source-ceiling',
        (3,labels['BbHeadCapture']):'capture', (3,labels['BbDeferredHead']):'deferred-head'}
    for name in ['PlayerHeadCollision','NativeRarePlayerHeadCollision','MushFlowerBlock','SetupPowerUp']:
        if name in b['syms']:points[(((location(b,name)-16)//8192)|128,address(b,name))]=name
    calls=Counter();events=[];epoch=0;recent=deque(maxlen=40)
    class Trace(actual):
        def step(self):
            bank=self.memory.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else None
            recent.append([self.pc,bank,self.sp,self.a,self.x,self.y])
            name=points.get((bank,self.pc))
            if name:
                calls[name]+=1
                if name!='deferred-head'and len(events)<20:
                    m=self.memory;events.append(dict(epoch=epoch,name=name,SP=self.sp,A=self.a,X=self.x,Y=self.y,
                        nativeY=N.get(m,'Player_Y_Position'),nativeDY=N.get(m,'Player_Y_Speed'),
                        scratch=list(m[3:11]),sweep_pixel=m.ram[2][0x3c8],pending=m.ram[2][0x3ef]))
            return actual.step(self)
    N.NesMPU=Trace
    try:
        for identity in [0,1]:
            for variant,bb in [('current-negative',old),('deferred-proposal',b)]:
                m,cell=arena(bb,route,identity);calls.clear();events.clear();minimum=224;ys=[]
                for epoch in range(55):
                    keys=128 if 1<=epoch<26 else 0
                    N.put(m,FrameCounter=epoch,SavedJoypadBits=keys,SavedJoypad1Bits=keys,VRAM_Buffer1_Offset=0)
                    try:z=N.invoke(m,'GameCoreRoutine',x=0,y=0)
                    except Exception as e:
                        (O/'deferred-head-v54-negative.json').write_text(json.dumps(dict(passed=False,variant=variant,identity=identity,epoch=epoch,exception=repr(e),events=events,calls=dict(calls),recent=list(recent),stack=list(m[0x170:0x1b0])),indent=2)+'\n');raise
                    minimum=min(minimum,z['minimum_SP']);ys.append(N.get(m,'Player_Y_Position'))
                row=dict(identity=identity,variant=variant,calls=dict(calls),events=list(events),minimum_SP=minimum,
                    minY=min(ys),finalY=ys[-1],cell=m[cell],lives=N.get(m,'NumberofLives'),
                    items=[dict(slot=i,flag=N.get(m,'Enemy_Flag',i),ID=N.get(m,'Enemy_ID',i),state=N.get(m,'Enemy_State',i)) for i in range(6) if N.get(m,'Enemy_ID',i)==46])
                records.append(row)
                assert calls['swept-source-ceiling']>0,row
                if variant=='current-negative':assert calls['PlayerHeadCollision']==0,row
                else:assert calls['PlayerHeadCollision']==1 and row['items'] and row['lives']==2,row
    finally:N.NesMPU=actual
    (O/'deferred-head-v54-image.bin').write_bytes(image)
    out=dict(passed=True,proposal_only=True,ROM_written=False,installed=False,qualified=False,
        base_ROM_SHA256=PIN,memory_ROM_SHA256=hashlib.sha256(b['raw']).hexdigest(),cookie=cookie.hex(),
        bytes=len((O/'deferred-head-v54.bin').read_bytes()),source_gap_remaining=645-len((O/'deferred-head-v54.bin').read_bytes()),
        private_patches=patches,labels=labels,scenarios=records,
        pending='C3EF stores R6|20 between the actual accepted movement and HuHead10; C3C8 retains actual first-solid sweep pixel. Native callback uses EF transiently for source-exported DY and clears it before return.',
        remaining=['Finite compiled C3EF/C3C8 reader/writer and lifecycle closure.','All native exclusion/foreign/header policies and full source/callback parity outside genuine blocks.','Actual IRQ, FF lag-NMI and nested audio stack cuts before admission.','Real native earned block emergence and collection; no emulator or fullstage claim.'],
        bindings={str(p.relative_to(R)):sha(p)for p in[Path(__file__),G.U.O/'proposal.json',G.U.O/'private-image.bin',O/'deferred-head-v54.s',O/'deferred-head-v54.bin',O/'deferred-head-v54-image.bin']})
    (O/'deferred-head-v54.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in['passed','qualified','memory_ROM_SHA256','bytes','source_gap_remaining','scenarios']}))

if __name__=='__main__':main()
