"""Replay deepest actual lag-handler IRQ winners from qualified79 contexts."""
import inspect,json
from pathlib import Path
import check_bub_shared_auth_interrupts_1103_v79 as P
O,R,sha=P.O,P.R,P.sha


def main():
    proof=O/'shared-auth-v79-ISR.json';q=json.loads(proof.read_text());assert q['passed']
    for rel,digest in q['bindings'].items():assert sha(R/rel)==digest,rel
    wanted={(tuple(x['scenario']),x['foreground_ordinal'],tuple(x['handler_cut']))for x in q['nested_handler_winners']}
    contexts={(a,b)for a,b,c in wanted};confirmed=set()
    source=inspect.getsource(P.main)
    source=source.replace("O/'shared-auth-v79-ISR.json'","O/'shared-auth-v80-nested.json'")
    start=source.index('            watched=tag==193')
    end=source.index('            return super().step()',start)
    source=source[:start]+'''            if (current,ordinal) in CONTEXTS:
                entry_count+=1
                probe(self,'FF')
'''+source[end:]
    anchor='            ins=bytes(m[z.pc:z.pc+3])\n'
    assert source.count(anchor)==1
    nested='''            nested_key=(current,ordinal,(z.pc,z.sp,m.rawtags[1],m.rawtags[2]))
            if kind=='FF'and nested_key in WANTED and nested_key not in CONFIRMED:
                iz,im=probe(z,'IRQ')
                # The winning handler instruction is outside every changed
                # resident span. Continue both the actual nested path and
                # unchanged native counterpart through the outer RTI.
                baseline=N.fork(im);baseline.bundle=old
                for win,t in enumerate(baseline.rawtags[:]):
                    if t&128:baseline.raw_page(win,t)
                bz=CPU(memory=baseline,pc=iz.pc);bz.a,bz.x,bz.y,bz.p,bz.sp=iz.a,iz.x,iz.y,iz.p,iz.sp
                for active,mem in [(iz,im),(bz,baseline)]:
                    for _ in range(200000):
                        if(active.pc,active.sp)==(regs[5],regs[4]):break
                        minimum=min(minimum,active.sp)
                        assert mem[active.pc]!=0,('Nested outer NMI BRK',nested_key,hex(active.pc))
                        # No changed code is admitted into the native-handler
                        # suffix used as the exact baseline continuation.
                        physical=mem.rawtags[(active.pc-0x8000)//8192]if active.pc>=0x8000 else-1
                        assert not(physical==193 and(0xa800<=active.pc<0xa849 or 0xae00<=active.pc<0xb013 or 0xab72<=active.pc<0xabce))
                        active.step()
                    else:raise AssertionError(('Nested outer NMI return bound',nested_key))
                assert (iz.a,iz.x,iz.y,iz.p&0xef,iz.sp,iz.pc)==(regs[0],regs[1],regs[2],regs[3]&0xef,regs[4],regs[5])
                assert view(im)[:7]==view(reference)[:7]and im.rawtags==reference.rawtags
                assert view(im)==view(baseline)and tuple(im[a]for a in SOUND)==tuple(reference[a]for a in SOUND)
                assert bytes(im[0x101+regs[4]:0x200])==live
                CONFIRMED.add(nested_key)
'''
    source=source.replace(anchor,nested+anchor)
    source=source.replace('        counts[kind]+=1\n','        counts[kind]+=1\n        return z,m\n')
    anchor='    result=dict(passed=True,CPU_only=True'
    assert source.count(anchor)==1
    source=source.replace(anchor,"    assert CONFIRMED==WANTED,('Nested winning contexts missed',len(CONFIRMED),len(WANTED))\n"+anchor)
    source=source.replace("        nested_handler_winners=list(winners.values()),", "        replayed_nested_IRQs=len(CONFIRMED),reconstructed_FF_contexts=len(CONTEXTS),reused_full_ISR_receipt=dict(path=proof.relative_to(R).as_posix(),SHA256=sha(proof),IRQ=PROOF['actual_ISR_counts']['IRQ'],FF=PROOF['actual_ISR_counts']['FF']),")
    begin=source.index("        scope='Genuine full native IRQ")
    end=source.index("        remaining=",begin)
    source=source[:begin]+"        scope='Every qualified79 deepest I0 lag-handler PC/A/C witness is replayed with actual native IRQ inside actual FF NMI. IRQ returns preserve architecturalCPU, live stack, private/native/scratch/SMC, owner/maps and four real audio clocks; PPU outputs equal the unchanged baseline native handler. Each nested clone then resumes the outer NMI through its real RTI, checking original foreground AXYP/SP and all source/private/native state. No changed native-handler suffix instruction is used as a baseline. All original8127IRQ/9287FF cuts are reused by exact source/hash; only winning134foreground contexts are reconstructed, no duplicate full sweep.',\n"+source[end:]
    source=source.replace("remaining=['Deepest actual lag-handler nestedIRQ replay across all retained contexts.','Complete external caller/reference closure and pending combined-owner source rebind.']", "remaining=['Complete external caller/reference closure and pending combined-owner source rebind before any candidate.']")
    source=source.replace("Path(P.__file__),Path(H.__file__),", "Path(P.__file__),Path(H.__file__),proof,")
    env=dict(P.__dict__,__file__=__file__,CONTEXTS=contexts,WANTED=wanted,CONFIRMED=confirmed,proof=proof,PROOF=q)
    exec(compile(source,__file__,'exec'),env);env['main']()


if __name__=='__main__':main()
