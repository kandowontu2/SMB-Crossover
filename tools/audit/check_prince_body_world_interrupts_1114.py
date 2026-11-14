"""Real reached first-pipe changed-code cuts, native IRQ and busy NMI.

ISR execution runs on temporary copies of genuine foreground CPU contexts.
The actual control replay is untouched; no arbitrary gameplay fixtures.
"""
from collections import Counter
from hashlib import sha256
import json
from unittest.mock import patch
import check_prince_body_world_1114 as Game

C,P,N=Game.C,Game.P,Game.N


def run(parent):
    raw,info=C.proposal(parent);model,opening=Game.cold(raw)
    actual_cpu=N.NesMPU;actual_bus=type(model);seen={};counts=Counter();minimum=255
    fields=Counter();audio=Counter();cuts=[]
    code=bytes(model[0xe000:0x10000]);needle=bytes.fromhex('ad390110')
    hits=[i for i in range(len(code)-8)if code[i:i+4]==needle and code[i+5:i+8]==bytes.fromhex('ee3a01')]
    assert len(hits)==1;at=hits[0];rel=code[at+4];lag=0xe000+at+5;regular=lag+rel-(256 if rel&128 else 0)
    def target(cpu):
        m=cpu.memory
        return m is model and((m.rawtags[1]==3 and 0xbde2<=cpu.pc<0xbfa3)or(m.rawtags[2]==2 and 0xc552<=cpu.pc<0xc606))
    def snapshot(m):
        return([bytes(b)for b in m.ram],bytes(m[3:11]),bytes(m[0x15a:0x17b]),m.rawtags[:],bytes(m[0x200:0x800]),m.chr_latches[:])
    def check(cpu,kind):
        nonlocal minimum
        m=N.fork(model);m.__class__=actual_bus
        clone=actual_cpu(memory=m,pc=cpu.pc)
        clone.a,clone.x,clone.y,clone.p,clone.sp=cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp
        before=snapshot(m);regs=(clone.a,clone.x,clone.y,clone.p,clone.sp,clone.pc)
        skip=N.get(m,'NmiSkipped');duration=m[0x7da];lag_hits=regular_hits=0;writes=len(m.ram_writes)
        clone.irq()if kind=='IRQ'else clone.nmi()
        for _ in range(100000):
            minimum=min(minimum,clone.sp)
            if(clone.pc,clone.sp)==(regs[5],regs[4]):break
            assert clone.sp<=regs[4],('ISR stack wrapped',kind,hex(cpu.pc),clone.sp,regs[4])
            lag_hits+=clone.pc==lag;regular_hits+=clone.pc==regular
            assert m[clone.pc],('ISR BRK',kind,hex(clone.pc))
            clone.step()
        else:raise AssertionError(('ISR return bound',kind,hex(cpu.pc)))
        assert(clone.a,clone.x,clone.y,clone.p&0xef,clone.sp,clone.pc)==(*regs[:3],regs[3]&0xef,*regs[4:])
        after=snapshot(m)
        assert all(before[i]==after[i]for i in(0,1,2,3,5)),('ISR private/scratch/mapper/CHR change',kind,hex(cpu.pc))
        assert not m.ram_writes[writes:],('ISR private writes',kind,hex(cpu.pc),m.ram_writes[writes:][:4])
        native0,native1=bytearray(before[4]),bytearray(after[4])
        if kind=='IRQ':
            assert lag_hits==regular_hits==0 and duration==m[0x7da]
        else:
            assert N.get(model,'NmiDisable')==255
            assert lag_hits==1 and regular_hits==0
            assert N.get(m,'NmiSkipped')==(skip+1)&255
            audio[str((duration,m[0x7da]))]+=1
            native0[0x7da-0x200]=native1[0x7da-0x200]=0
        assert native0==native1,('Unexpected native RAM change',kind,hex(cpu.pc),[(hex(i+0x200),a,b)for i,(a,b)in enumerate(zip(native0,native1))if a!=b][:8])
        counts[kind]+=1
    class Trace(actual_cpu):
        def step(self):
            if target(self):
                fields[N.get(model,'NmiDisable')]+=1
                key=(self.pc,model.rawtags[1],model.rawtags[2])
                if key not in seen or self.sp<seen[key]:
                    seen[key]=self.sp
                    if not self.p&4:
                        check(self,'IRQ')
                        if N.get(model,'NmiDisable')==255:check(self,'busyNMI')
                        cuts.append([hex(self.pc),self.sp,*model.rawtags[1:3]])
                    else:counts['reached_masked_cuts']+=1
            return super().step()
    with patch.object(N,'NesMPU',Trace):route=Game.route(raw,model,mode='contact',pad=8)
    assert route['passed']and route['observed_pipe_climb'],route
    assert counts['IRQ']>0 and counts['busyNMI']==counts['IRQ']
    q=dict(passed=True,composition=info,opening=opening,route=route,
        cuts=dict(counts),unique_changed_PC_map_pairs=len(seen),minimum_ISR_SP=minimum,
        reached_NmiDisable_values=dict(fields),actual_busy_path=hex(lag),forbidden_regular_path=hex(regular),
        audio_duration_transitions=dict(audio),cut_examples=cuts[:8]+cuts[-8:],
        all_AXYP_SP_private_RAM_R0_R7_SMC_mapper_CHR_exact=True,
        native_RAM_exact_except_declared_busy_audio_duration=True,
        actual_reached_context_copies_only=True,outputs=0,Mesen=False)
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':print(json.dumps(run(Game.Factory.ROM.read_bytes()),separators=(',',':')),flush=True)
