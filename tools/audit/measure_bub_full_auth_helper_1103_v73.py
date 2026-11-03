"""Measure complete-header auth factoring against the canonical DK79 owner.

No cache, descriptor lease, ROM output or shared source mutation is used.
"""
import json,re
from pathlib import Path
import profile_bub_current_bridge_1103_v69 as C
import measure_bub_landing_1102_v21 as L
import prepare_dkjr_current_owner_1103_v79 as D
import check_bubble_bobble_common_cold_1102_v4 as Cold

O,R,N,Q,address,sha=C.O,C.R,C.N,C.Q,C.address,C.sha


def build():
    current,route,q,head,_,_=C.bundle();canonical,manifest=D.image()
    old=dict(current,raw=canonical['raw']);oldlabels=manifest['manager_labels']
    src=(D.O/'native-owner-v79.s').read_text()
    cfg='MEMORY{M:start=$ae00,size=$213,file=%O;X:start=$ab72,size=$62,file="'+(O/'full-auth-v73-reproduce-extra.bin').as_posix()+'";}SEGMENTS{COMMON_OWNER_PROPOSAL:load=M,type=ro;PR_EXTRA:load=X,type=ro;}'
    labels=L.assemble('full-auth-v73-reproduce',src,cfg)
    at=16+65*8192+0xe00
    assert (O/'full-auth-v73-reproduce.bin').read_bytes()==old['raw'][at:at+531]
    assert (O/'full-auth-v73-reproduce-extra.bin').read_bytes()==(D.O/'native-owner-extra-v79.bin').read_bytes()
    assert all(labels[k]==v for k,v in oldlabels.items())
    start,end=src.index('CoCheckCode:\n'),src.index('CoCheckHeaders:\n')
    before=src[start:end]
    expected='''CoCheckCode:
 ldx #3
:
 lda R3,x
 pha
 dex
 bpl :-
 jsr CoSelect
 bcc :+
 jsr CoCheckHeaders
:
 lda #0
 rol
 tay
 ldx #0
:
 pla
 sta R3,x
 inx
 cpx #4
 bne :-
 tya
 lsr
 rts

CoSelect:
 lda SelectedCharacter
 sec
 sbc #37
 cmp #4
 bcs CoSelectNo
 tax
 lda CoCookieLo,x
 sta R5
 lda CoCookieHi,x
 sta R6
 lda CoDescriptorLo,x
 sta R3
 lda CoDescriptorHi,x
 sta R4
 sec
 rts
CoSelectNo:
 clc
 rts

'''
    assert before==expected
    replacement='''; Carry-only private helper; all actual callers save AXYP externally.
; R3/R4 are cold-worker descriptors and need not be touched by hot auth.
CoCheckCode:
 lda R5
 pha
 lda R6
 pha
 jsr CoSelectCookie
 bcc :+
 jsr CoCheckHeaders
:
 pla
 sta R6
 pla
 sta R5
 rts

; Cold callers still obtain precisely the original descriptor and outputs.
CoSelect:
 jsr CoSelectCookie
 bcc CoSelectReturn
 lda CoDescriptorLo,x
 sta R3
 lda CoDescriptorHi,x
 sta R4
 sec
CoSelectReturn:
 rts
CoSelectCookie:
 lda SelectedCharacter
 sec
 sbc #37
 cmp #4
 bcs CoSelectNo
 tax
 lda CoCookieLo,x
 sta R5
 lda CoCookieHi,x
 sta R6
 sec
 rts
CoSelectNo:
 clc
 rts

'''
    src=src[:start]+replacement+src[end:]
    cfg=cfg.replace('full-auth-v73-reproduce-extra','full-auth-v73-final-extra')
    newlabels=L.assemble('full-auth-v73-final',src,cfg)
    blob=(O/'full-auth-v73-final.bin').read_bytes();extra=(O/'full-auth-v73-final-extra.bin').read_bytes()
    assert len(blob)==531 and len(extra)==manifest['extra_bytes']
    assert newlabels['CoCold']==0xae00 and newlabels['CoRetire']==0xae0b
    raw=bytearray(old['raw']);raw[at:at+531]=blob
    ext=16+65*8192+0xb72;raw[ext:ext+len(extra)]=extra
    changes=[];bank=bytearray(raw[16+65*8192:16+66*8192])
    # Canonical transport uses its own immutable ShSmc table atAA61. The two
    # CoSmc readers are now both inside the reproduced owner frame itself.
    for opcode,name,want in [(0xbc,'CoSmc',0),(0x20,'CoCheckCode',1)]:
        needle=bytes([opcode])+oldlabels[name].to_bytes(2,'little')
        sites=[i for i in range(8190)if bank[i:i+3]==needle and not 0xe00<=i<0x1013 and not 0xb72<=i<0xbd4]
        assert len(sites)==want,(name,sites)
        for i in sites:
            data=bytes([opcode])+newlabels[name].to_bytes(2,'little')
            changes.append(dict(bank_offset=i,symbol=name,old=needle.hex(),new=data.hex()))
            bank[i:i+3]=data
    raw[16+65*8192:16+66*8192]=bank
    return old,dict(old,raw=bytes(raw)),route,q,head,manifest,oldlabels,newlabels,changes


def parity(a,z,out):
    assert [out[0][k]for k in ['A','X','Y','P']]==[out[1][k]for k in ['A','X','Y','P']],out
    assert a.ram==z.ram and a.rawtags==z.rawtags
    assert bytes(a[3:11])==bytes(z[3:11])and bytes(a[0x15a:0x17b])==bytes(z[0x15a:0x17b])
    assert bytes(a[0x200:0x800])==bytes(z[0x200:0x800])


def main():
    dst=O/'full-auth-v73-measurement.json';assert not dst.exists()
    old,new,route,q,head,manifest,oldlabels,newlabels,changes=build()
    cold=[];bad=0;direct=0;foreign=0
    for owner in [37,38,39,40]:
        seeds=[];outs=[]
        for bb in [old,new]:
            m,z=D.C.cold(bb,owner)
            outs.append(dict(zip(['A','X','Y','P'],z['regs'][:4]),CPU=z['CPU']));seeds.append(m)
        parity(*seeds,outs);assert outs[0]['P']&1
        cold.append(dict(owner=owner,baseline_CPU=outs[0]['CPU'],proposal_CPU=outs[1]['CPU']))
        for y in range(32):
            pair=[N.fork(m)for m in seeds];out=[]
            for m in pair:out.append(N.invoke(m,'HuSide',a=y*7,x=9,y=y,p=0x71))
            parity(*pair,out);direct+=1
        for bank in [2,3]:
            for offset in range(16):
                pair=[N.fork(m)for m in seeds];out=[]
                for m in pair:
                    m.ram[bank][0x1fe0+offset]^=1
                    out.append(Cold.call(m,0xb0b6,flags=0x71))
                parity(*pair,out);assert not out[0]['P']&1;bad+=1
    seeds=[Q.Q.fresh(bb,route,0)for bb in [old,new]]
    for raw in range(256):
        if raw in [37,38,39,40]:continue
        pair=[N.fork(m)for m in seeds];out=[]
        for m in pair:N.put(m,SelectedCharacter=raw);out.append(Cold.call(m,0xb0b6,flags=0x71))
        parity(*pair,out);foreign+=1
    CPU=N.NesMPU;cases=[]
    for identity in [0,1]:
        for phase,keys in [('idle',0),('walk',1),('left',2),('jump',129),('bubble',64)]:
            pair=[Q.Q.fresh(bb,route,identity)for bb in [old,new]];traces=[];outputs=[];counts=[]
            for index,m in enumerate(pair):
                Q.L.E.main_fields(m);trace=[];count=0
                class Trace(CPU):
                    def step(self):
                        nonlocal count
                        mm=self.memory;pc=self.pc;bank=mm.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
                        if bank==193 and pc==(oldlabels if index==0 else newlabels)['CoCheckCode']:count+=1
                        if bank in [2,3]:trace.append((bank,pc,self.a,self.x,self.y,self.p,self.sp))
                        return super().step()
                N.NesMPU=Trace
                try:
                    out=[]
                    for epoch in range(12):
                        held=(keys&127)|(128 if keys&128 and epoch==1 else 0)
                        N.put(m,FrameCounter=epoch,SavedJoypadBits=held,SavedJoypad1Bits=held,VRAM_Buffer1_Offset=0)
                        out.append(N.invoke(m,'GameCoreRoutine',a=85,x=0,y=0,p=0x31))
                    outputs.append(out)
                finally:N.NesMPU=CPU
                traces.append(trace);counts.append(count)
            parity(*pair,[out[-1]for out in outputs]);assert traces[0]==traces[1],(identity,phase,'private AXYP/SP')
            for out in zip(*outputs):assert [out[0][k]for k in ['A','X','Y','P']]==[out[1][k]for k in ['A','X','Y','P']]
            assert counts==[156,156],counts
            before=sum(o['CPU']for o in outputs[0])/12;after=sum(o['CPU']for o in outputs[1])/12
            row=dict(identity=identity,phase=phase,Main_updates=12,baseline_CPU=before,proposal_CPU=after,
                saving_CPU=before-after,saving_percent=100*(before-after)/before,full_auth_calls=counts,
                private_instruction_AXYP_SP_exact=True,trace_entries=len(traces[0]))
            cases.append(row);print(json.dumps(row),flush=True)
    result=dict(passed=True,CPU_only=True,CPU_qualified=False,candidate_allowed=False,ROM_written=False,
        cache_used=False,new_RAM_used=False,canonical_proposal=str((D.O/'native-owner-proposal-v79.json').relative_to(R)),
        base_memory_SHA256=__import__('hashlib').sha256(old['raw']).hexdigest(),
        proposal_memory_SHA256=__import__('hashlib').sha256(new['raw']).hexdigest(),
        manager_bytes=531,extra_bytes=manifest['extra_bytes'],cold_cases=cold,public_direct_cases=direct,
        header_byte_poison_rejections=bad,foreign_raw_cases=foreign,Main_cases=cases,changed_consumers=changes,
        old_labels=oldlabels,new_labels=newlabels,
        scope='All 32 header bytes are compared on every one of the 13 Main service calls. Hot auth saves only its two actually modified cookie-pointer bytes; R3/R4 cold descriptors are left untouched. The cold CoSelect contract still initializes all four original scratch bytes. Existing carry-only private helper contract is retained; public AXYP/SMC/R0..7/maps/private traces remain exact. No cache/lifetime assumption, owner admission, ROM or native cadence claim.',
        remaining=['Source and actual external entry/SMC/cookie reference closure for every moved private symbol.',
            'Changed cold/retire fault/transition contracts and actual IRQ/FF/NMI nested cuts before candidate permission.',
            'Quantify larger combined transport/full-auth improvements before requesting any native candidate.'],
        bindings={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),Path(C.__file__),Path(D.__file__),
            D.O/'native-owner-proposal-v79.json',D.O/'native-owner-v79.s',D.O/'native-selector-v79.s',
            O/'full-auth-v73-reproduce.bin',O/'full-auth-v73-reproduce-extra.bin',
            O/'full-auth-v73-final.s',O/'full-auth-v73-final.bin',O/'full-auth-v73-final-extra.bin',O/'full-auth-v73-final.lbl']})
    dst.write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
