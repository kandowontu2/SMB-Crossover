"""Source/provenance, prefix ABI and strict fault checks; zero output files.

The direct CPU matrix stops at the real callee/gateway entry. Whole caller,
family continuations and hardware interrupts have a separate owned suite.
"""
from collections import Counter
import argparse
from hashlib import sha256
import json

import compose_smb2_postbg_mirror_1113 as C


class PrefixMemory(list):
    def __init__(self, code):
        super().__init__([0]*65536)
        list.__setitem__(self,slice(C.BRIDGE,C.BRIDGE+len(code)),code)
        self.writes=[]

    def __setitem__(self, at, value):
        assert isinstance(at,int) and at in (0x16a,0x16c,0x16d,0x1dd,0x1de,0x1df,0x1e0)
        self.writes.append((at,value))
        list.__setitem__(self,at,value)


def prefix(memory, owner, a, p, x=7, y=91):
    for at,_ in memory.writes:
        list.__setitem__(memory,at,0)
    memory.writes.clear()
    list.__setitem__(memory,0x6002,owner)
    list.__setitem__(memory,0x16c,0x5a)
    list.__setitem__(memory,0x16d,0xa5)
    cpu=C.N.NesMPU(memory=memory,pc=C.BRIDGE)
    cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp=a,x,y,p,224
    cpu.stPushWord(0x5aff)
    memory.writes.clear()
    target=0xaca4 if owner==3 else 0x15a
    for _ in range(20):
        if cpu.pc==target:
            assert cpu.x==x and cpu.y==y
            assert cpu.a==(0 if owner==3 else 194)
            assert cpu.p==((p&~0x82)|(2 if owner==3 else 0x80))
            assert memory[0x16a]==a
            if owner!=3:assert (memory[0x16c],memory[0x16d])==(0x38,0xb4)
            return ((cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,cpu.pc,cpu.processorCycles),
                    tuple(memory.writes),bytes(memory[0x100+cpu.sp+1:0x200]))
        # These actual prefix instructions cannot read or modify X/Y. The
        # exhaustive A/P matrix therefore retains arbitrary incoming X/Y.
        assert memory[cpu.pc] in (0x8d,0xad,0x49,0xd0,0x20,0xa9,0x4c)
        cpu.step()
    raise AssertionError('Bounded actual prefix')


def finite(raw):
    image,q=C.proposal(raw)
    canonical=PrefixMemory(C.CANONICAL)
    mirrors=[]
    for bank in (119,120):
        at=16+bank*8192+(C.BRIDGE&8191)
        mirrors.append(PrefixMemory(image[at:at+49]))
    counts=Counter()
    for owner in (3,25):
        for p in range(256):
            for a in range(256):
                expected=prefix(canonical,owner,a,p)
                for mirror in mirrors:
                    assert prefix(mirror,owner,a,p)==expected
                counts['selected_special'if owner==3 else 'SMB2_fallback']+=1
    # This closes the prefix's byte-owner domain without executing any
    # uninitialized foreign private actor. The selected-special continuation
    # is separately the real canonical ACA4 entry, not a source substitution.
    for owner in range(256):
        for p in (0x30,0xf1):
            expected=prefix(canonical,owner,85,p,x=255,y=0)
            for mirror in mirrors:assert prefix(mirror,owner,85,p,x=255,y=0)==expected
            counts['all_raw_owner_prefix']+=1
    old=PrefixMemory(C.OLD)
    for p in range(256):
        # The original selected-special path never reaches a changed operand.
        assert prefix(old,3,85,p)==prefix(canonical,3,85,p)
    return dict(passed=True,ROM_SHA256=q['ROM_SHA256'],counts=dict(counts),
                repaired_alias_canonical_pairs=2*sum(counts.values()),
                original_special_all_flags_pairs=256,
                AXY_P_SP_live_stack_ordered_SMC_writes_exact=True,
                explicit_prefix_only_fixture=True,whole_caller_or_native_claim=False,outputs=0)


def faults(raw):
    image,q=C.proposal(raw)
    assert C.inverse(image)==raw
    tests=[]
    for label,base,fn,at in (
        ('parent_unowned',raw,C.proposal,16),
        ('parent_operand',raw,C.proposal,C.EDITS[0][0]),
        ('parent_canonical',raw,C.proposal,16+127*8192+0x5ea),
        ('parent_sample',raw,C.proposal,q['samples'][0]['file']),
        ('candidate_unowned',image,C.inverse,16),
        ('candidate_operand',image,C.inverse,C.EDITS[0][0]),
        ('candidate_sample',image,C.inverse,q['samples'][0]['file'])):
        broken=bytearray(base);broken[at]^=1
        tests.append((label,fn,bytes(broken)))
    tests.extend((('parent_truncated',C.proposal,raw[:-1]),
                  ('candidate_truncated',C.inverse,image[:-1]),
                  ('candidate_as_parent',C.proposal,image),
                  ('parent_as_candidate',C.inverse,raw)))
    for label,fn,data in tests:
        try:fn(data)
        except AssertionError:continue
        raise AssertionError(('Unexpected corrupted image acceptance',label))
    return dict(passed=True,ROM_SHA256=C.CANDIDATE,strict_rejections=[label for label,_,_ in tests],
                inverse_exact_parent=True,outputs=0)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode',choices=('all','layout','finite','faults'),default='all')
    args=p.parse_args();raw=C.Owner.NIGHTLY.read_bytes();out={}
    if args.mode in ('all','layout'):
        image,out['layout']=C.proposal(raw);assert C.inverse(image)==raw
    if args.mode in ('all','finite'):out['finite']=finite(raw)
    if args.mode in ('all','faults'):out['faults']=faults(raw)
    print(json.dumps(out,separators=(',',':')),flush=True)
