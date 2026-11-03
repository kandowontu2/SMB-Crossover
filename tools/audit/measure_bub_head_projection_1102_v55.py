"""Return the actual swept source head contact to the ordinary native caller.

Unlike the retained v54 negative, this never calls a native transaction while
the private head callback's resident envelope is retained. No ROM is written.
"""
import hashlib,json
from collections import Counter,deque
from pathlib import Path
import measure_bub_deferred_head_1102_v54 as H
from check_tmnt_render_oa import location
G,L,O,Q,N,address,R,sha=H.G,H.L,H.O,H.Q,H.N,H.address,H.R,H.sha
PIN=H.PIN

def bundle():
    _,old,route,q=G.bundles();assert hashlib.sha256(old['raw']).hexdigest()==PIN
    image=bytearray((G.U.O/'private-image.bin').read_bytes());lab=q['labels']
    start=lab['BbPowerupEnd'];assert start==0xb2b5
    assert image[start-0xa000:0x153a]==bytes([255])*645
    source=(O/'deferred-head-v54.s').read_text()
    begin=source.index('BbDeferredHead:\n');end=source.index('BbHeadEnd:\n',begin)
    projection=f'''BbDeferredHead:
 lda $c3ef
 beq OldHead
 and #$df
 sta R6
 lda #0
 sta $c3ef
 lda GameEngineSubroutine
 cmp #8
 bne OldHead
 lda Player_Y_HighPos
 cmp #1
 bne OldHead
 ; Preserve the getter's incoming adder-index Y and its untouched R0/R1.
 tya
 pha
 ; C3C9 is the actual pre-clamp native anchor+15; C382 is this source
 ; epoch's native starting Y. Report that real attempted upward displacement.
 lda $c3c9
 sec
 sbc #15
 sta ${address(old,'R4'):04x}
 sec
 sbc $c382
 sta Player_Y_Speed
 lda ${address(old,'R4'):04x}
 and #15
 sta ${address(old,'R4'):04x}
 ; Native raw getter R5 is the sampled world X low; this is the actual
 ; source sweep's left or right inset, including native page-carry handling.
 lda $c3cb
 sta ${address(old,'R5'):04x}
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
 pla
 tay
 ldx #0 ; Ordinary BlockBufferPlayerCollision returns player object X0.
 lda R3 ; Z/N describe the actual returned tile, C/V the source row SBC.
BbDeferredHeadDone:
 rts
OldHead:
 jmp NativeHead
'''
    source=source[:begin]+projection+source[end:]
    source=source.replace('PlayerHeadCollision=$9ef5 ; Actual fixed126 public native head transaction.\n','')
    labels=L.assemble('head-projection-v55',source,
        f'MEMORY{{M:start=${start:04x},size=$285,file=%O;}}SEGMENTS{{CODE:load=M,type=ro;}}')
    code=(O/'head-projection-v55.bin').read_bytes();assert len(code)<=645
    patches=[]
    def patch(pc,before,after,role):
        assert image[pc-0xa000:pc-0xa000+len(before)]==before,(hex(pc),role)
        assert len(before)==len(after)
        patches.append(dict(CPU=pc,old=before.hex(),new=after.hex(),role=role))
        image[pc-0xa000:pc-0xa000+len(after)]=after
    def jmp(pc):return bytes([76])+pc.to_bytes(2,'little')
    patch(start,bytes([255])*len(code),code,'Declared reclaimed source gap')
    patch(0xa01e,bytes.fromhex('4c8795'),jmp(labels['BbDeferredHead']),'Actual HuHead row10')
    patch(lab['BbNativeCeilingHit'],bytes.fromhex('adc8c329f085bd'),jmp(labels['BbHeadCapture'])+bytes([234])*4,'Same first-solid source clamp and continuation')
    needle=bytes([32])+lab['BbNativeProxiesIn'].to_bytes(2,'little')
    hits=[i+0xa000 for i in range(0x1540,len(image)-2)if image[i:i+3]==needle];assert len(hits)==1
    patch(hits[0],needle,bytes([32])+labels['BbHeadBegin'].to_bytes(2,'little'),'Accepted movement pending clear')
    raw=bytearray(old['raw']);art=raw[1048592+441*1024:1048592+442*1024]
    cookie=bytes([167,39,1])+hashlib.sha256(image+art).digest()[:13]
    for i,p in enumerate(H.PAGES):raw[1048592+p*1024:1048592+(p+1)*1024]=image[i*1024:(i+1)*1024]
    raw[q['cookie_offset']:q['cookie_offset']+16]=cookie
    return old,dict(old,raw=bytes(raw)),route,q,labels,bytes(image),patches,cookie

def main():
    old,b,route,q,labels,image,patches,cookie=bundle();records=[];actual=N.NesMPU
    calls=Counter();events=[];epoch=0;recent=deque(maxlen=30)
    points={(3,q['labels']['BbNativeCeilingHit']):'source-hit',
        (3,labels['BbHeadCapture']):'capture',(3,labels['BbDeferredHeadDone']):'projected-return'}
    for name in ['PlayerHeadCollision','NativeRarePlayerHeadCollision','MushFlowerBlock','SetupPowerUp']:
        if name in b['syms']:points[(((location(b,name)-16)//8192)|128,address(b,name))]=name
    class Trace(actual):
        def step(self):
            m=self.memory;bank=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else None
            recent.append([self.pc,bank,self.sp]);name=points.get((bank,self.pc))
            if name:
                calls[name]+=1
                if len(events)<16:events.append(dict(epoch=epoch,name=name,SP=self.sp,A=self.a,X=self.x,Y=self.y,P=self.p,
                    nativeY=N.get(m,'Player_Y_Position'),nativeDY=N.get(m,'Player_Y_Speed'),scratch=list(m[3:11]),
                    collision_pixel=m.ram[2][0x3c8],attempt_pixel=m.ram[2][0x3c9],startY=m.ram[2][0x382],pending=m.ram[2][0x3ef]))
            return actual.step(self)
    N.NesMPU=Trace
    try:
        for identity in [0,1]:
            for variant,bb in [('current-negative',old),('shallow-projection',b)]:
                m,cell=H.arena(bb,route,identity);calls.clear();events.clear();minimum=224;ys=[]
                for epoch in range(55):
                    keys=128 if 1<=epoch<26 else 0
                    N.put(m,FrameCounter=epoch,SavedJoypadBits=keys,SavedJoypad1Bits=keys,VRAM_Buffer1_Offset=0)
                    try:z=N.invoke(m,'GameCoreRoutine',x=0,y=0)
                    except Exception as e:
                        (O/'head-projection-v55-negative.json').write_text(json.dumps(dict(passed=False,identity=identity,variant=variant,epoch=epoch,exception=repr(e),events=events,recent=list(recent)),indent=2)+'\n');raise
                    minimum=min(minimum,z['minimum_SP']);ys.append(N.get(m,'Player_Y_Position'))
                row=dict(identity=identity,variant=variant,calls=dict(calls),events=list(events),minimum_SP=minimum,
                    minY=min(ys),finalY=ys[-1],cell=m[cell],lives=N.get(m,'NumberofLives'),
                    items=[dict(slot=i,flag=N.get(m,'Enemy_Flag',i),ID=N.get(m,'Enemy_ID',i),state=N.get(m,'Enemy_State',i))for i in range(6)if N.get(m,'Enemy_ID',i)==46])
                records.append(row)
                assert calls['source-hit']>0,row
                if variant=='current-negative':assert calls['PlayerHeadCollision']==0,row
                else:
                    assert calls['PlayerHeadCollision']==1 and row['items']and row['lives']==2,row
                    event=next(x for x in events if x['name']=='projected-return')
                    assert event['A']==0xc1 and not event['P']&2 and event['X']==0 and event['Y']==14,event
                    assert event['scratch'][2:]==[0x70,0xc1,14,0x57,0xd5,3],event
                    assert event['nativeY']==144 and event['nativeDY']==254,event
    finally:N.NesMPU=actual
    (O/'head-projection-v55-image.bin').write_bytes(image)
    out=dict(passed=True,proposal_only=True,ROM_written=False,installed=False,qualified=False,
        base_ROM_SHA256=PIN,memory_ROM_SHA256=hashlib.sha256(b['raw']).hexdigest(),cookie=cookie.hex(),
        bytes=len((O/'head-projection-v55.bin').read_bytes()),source_gap_remaining=645-len((O/'head-projection-v55.bin').read_bytes()),
        private_patches=patches,labels=labels,scenarios=records,
        ABI='Actual pending source contact returns the real R2/R3/R4/R5/R6/R7 and sampled attempted source DY. R0/R1 remain untouched; X0 and original adderY14 match the native getter; final LDA tile establishes NZ. Unchanged native caller guards and calls the genuine transaction after the resident head envelope unwinds.',
        remaining=['C3EF/C3C8/C3C9/C382 reader/writer and caller/lifecycle closure.','No-contact complete source/AXYP parity and all native exclusion policies.','Actual IRQ/FF lag-NMI/nested audio stack replay.','Native earned block emergence, mature collection and source-upgrade animation.'],
        bindings={str(p.relative_to(R)):sha(p)for p in[Path(__file__),Path(H.__file__),O/'deferred-head-v54-negative.json',G.U.O/'proposal.json',G.U.O/'private-image.bin',O/'head-projection-v55.s',O/'head-projection-v55.bin',O/'head-projection-v55-image.bin']})
    (O/'head-projection-v55.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in['passed','qualified','memory_ROM_SHA256','bytes','source_gap_remaining','scenarios']}))

if __name__=='__main__':main()
