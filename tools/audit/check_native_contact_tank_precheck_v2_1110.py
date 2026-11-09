"""Preserve all five SMC operands across the native contact handoff."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

import check_native_contact_tank_precheck_1110 as C


SOURCE = C.R/'tools/reference/native_contact_tank_precheck_v2_1110.s'
PREDECESSOR = C.R/'build/native-contact-tank-precheck-1110/proof.json'
S2_AUDIO = C.R/'src/smb2_roster_common_audio_v9.s'
RETURN_A, S2_RETURN_A_BACKUP = 0x0179, 0x727c


def arrival(image, raw, mode, p, variant, bad_cookie):
    owned = raw in (25,39,41) or raw==0 and variant==7
    seed = C.cold(image,raw if owned else None)
    cpu = C.setup(seed,raw,mode,p,variant=variant,bad_cookie=bad_cookie,power=2,whole=True)
    C.run(cpu,lambda c:C.point(c) in (C.NATIVE,C.WORKER))
    wants_worker = raw==0 and variant==7 and bad_cookie is None
    assert C.point(cpu)==(C.WORKER if wants_worker else C.NATIVE)
    return cpu


def counterexample(before,receipt):
    earlier = C.install(before,receipt['patches'])
    assert receipt['passed'] and receipt['parent_SHA256']==C.M.sha(before)
    assert receipt['expected_memory_only_SHA256']==C.M.sha(earlier)
    images = C.Contact.L.bundles(before,earlier)
    lag,normal = C.lag_pcs(C.cold(images[0],41))
    rows = []
    for image in images:
        cpu = arrival(image,25,0,0x20,0,None)
        incoming = cpu.memory[RETURN_A]
        cpu = C.fork(cpu)
        C.IRQ.interrupt(cpu,'FF',lag,normal)
        assert cpu.memory[RETURN_A]==incoming
        rows.append((incoming,cpu.memory[S2_RETURN_A_BACKUP]))
    assert rows==[(25,25),(1,1)],rows
    source = S2_AUDIO.read_text()
    assert 'lda SafereturnA_SMC+1\n sta S2CommonSmc+4' in source
    assert 'lda S2CommonSmc+4\n sta SafereturnA_SMC+1' in source
    return dict(raw=25,scene='Easy contact at native AD52, actual lag NMI',
                SMC_operand=RETURN_A,persistent_backup=S2_RETURN_A_BACKUP,
                original=rows[0],rejected_v1=rows[1])


def first_return_publish(cpu):
    clone = C.fork(cpu)
    m = clone.memory
    m.pending_dispatch = frozenset({RETURN_A})
    writer = None

    def watch(z):
        nonlocal writer
        m.dispatch_site = C.point(z)
        if m.pending_dispatch:
            writer = m.dispatch_site

    C.run(clone,C.done,watch)
    assert not m.pending_dispatch and writer[1]==0x016e,writer
    return writer[1]


def handoff(before,after):
    old,new = C.Contact.L.bundles(before,after)
    lag,normal = C.lag_pcs(C.cold(new,41))
    cases = [(raw,0,None) for raw in (25,39,41)] + [(8,1,None),(0,0,None),(0,7,None),(0,7,15)]
    counts,writers = Counter(),Counter()
    minimum = 255

    def compare(z,w,*,arriving):
        a,b = z.memory,w.memory
        sp_delta = 2 if arriving else 0
        assert C.registers(z,0xef)[:-1]==C.registers(w,0xef)[:-1] and w.sp-z.sp==sp_delta
        assert bytes(a[0x15a:0x17b])==bytes(b[0x15a:0x17b])
        C.Contact.A.P.compare_memory(a,b)
        if not arriving:
            assert C.live_stack(z)==C.live_stack(w) and C.final(z)==C.final(w)

    for (raw,variant,bad),mode,p in product(cases,(0,1),(0x20,0x21)):
        pair = [arrival(image,raw,mode,p,variant,bad) for image in (old,new)]
        compare(*pair,arriving=True)
        for cpu in pair:
            writers[first_return_publish(cpu)] += 1
        counts['exact_native_or_Tank_entry'] += 1
        for kind in ('FF','IRQ','normal'):
            z,w = [C.fork(cpu) for cpu in pair]
            for q in (z,w):
                if kind=='normal':
                    C.N.put(q.memory,NmiDisable=0)

            def track(q):
                nonlocal minimum
                minimum = min(minimum,q.sp)

            assert C.IRQ.interrupt(z,kind,lag,normal,track)==C.IRQ.interrupt(w,kind,lag,normal,track)
            assert C.IRQ.hardware(z)==C.IRQ.hardware(w),(raw,mode,p,kind)
            compare(z,w,arriving=True)
            for q in (z,w):
                C.run(q,C.done)
            compare(z,w,arriving=False)
            assert C.IRQ.hardware(z)==C.IRQ.hardware(w),(raw,mode,p,kind,'after contact')
            counts[kind] += 1
    return dict(paired_cases=dict(counts),first_returnA_writer_PC=dict(writers),minimum_handler_SP=minimum)


foreground = C.foreground
vectors = C.vectors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    out = parser.parse_args().output.resolve()
    assert out.is_relative_to(C.R/'build') and out!=C.R/'build'
    out.mkdir(exist_ok=True)
    dest = out/'proof.json'
    assert not dest.exists()
    before = C.BASE.read_bytes()
    assert C.M.sha(before)==C.PIN
    original = C.SOURCE
    try:
        C.SOURCE = SOURCE
        after,patches = C.link(before,out)
    finally:
        C.SOURCE = original
    previous = C.read(PREDECESSOR)
    negative = counterexample(before,previous)
    exact_handoff = handoff(before,after)
    print('All five SMC operands, real native/Tank handoffs, and actual ISR resumes match.',flush=True)
    front = foreground(before,after)
    irqs = vectors(before,after)
    refs = (Path(__file__),SOURCE,original,Path(C.__file__),PREDECESSOR,S2_AUDIO)
    proof = dict(passed=True,ROM_written=False,parent_SHA256=C.PIN,expected_memory_only_SHA256=C.M.sha(after),
                 patches=patches,foreground=front,vectors=irqs,handoff=exact_handoff,rejected_v1=negative,
                 bindings=previous['bindings'] | {str(p.resolve()):C.M.sha(p.read_bytes()) for p in refs})
    dest.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    print(dest,proof['expected_memory_only_SHA256'],flush=True)


if __name__=='__main__':
    main()
