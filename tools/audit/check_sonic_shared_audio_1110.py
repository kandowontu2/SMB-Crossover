"""Source-funded relocated Sonic vanilla-audio fallback; stdout, no ROM writes."""
from collections import Counter
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

import check_wwf_native_powerups_1110 as Parent

W,N,L=Parent.W,Parent.N,Parent.L
sys.path.insert(0,str(W.R/'tools/reference'))
import sonic_sms_compact_cold_worker_1110 as Asm

SOURCE=W.R/'tools/reference/sonic_shared_audio_1110.s'
START,END=0xb53b,0xb57c
OFFSET=16+63*8192+(START&8191)
OLD=bytes.fromhex('28680848adff5f29018dff5fadda72c982d010a9ff8dda72a9008d11408d15408d15506828ad7107f014ad0260f00fc908f00bc917f007c91cf0034c6ff04cd8f0')
BUNDLE=None


def proposal(raw):
    assert len(OLD)==END-START and raw[OFFSET:OFFSET+len(OLD)]==OLD
    off=lambda pc:16+63*8192+(pc&8191)
    assert raw[off(0xb431):off(0xb448)]==bytes.fromhex('ad7107f010ad0260c902d009adee5fc901d00238601860')
    assert raw[off(0xb448):off(0xb461)]==bytes.fromhex('08ad0773c908d0034c3bb52031b4b0034c3bb528a9bf8d4501')
    source=SOURCE.read_text();p=Asm.assemble(source,{'AUDIO':(START,END-START)})
    new=p['images']['AUDIO'];assert len(new)==len(OLD)
    q=bytearray(raw);q[OFFSET:OFFSET+len(new)]=new
    return bytes(q),dict(parent_SHA256=sha256(raw).hexdigest(),image_SHA256=sha256(q).hexdigest(),
        source_SHA256=sha256(SOURCE.read_bytes()).hexdigest(),bank=63,half_open=[START,END],
        old=OLD.hex(),new=new.hex(),funding='Four-byte stack reorder factor, no padding',
        original_Vanilla_and_Guest_targets=[0xf0d8,0xf06f])


def gate(raw,owner,mode,flags,prior):
    b=dict(BUNDLE,raw=raw);m=N.fresh(b)
    m.raw_page(1,191);N.put(m,CurrentBank=191,SelectedCharacter=owner,OperMode=mode)
    m[0x5fff]=0xa5;m[0x72da]=prior
    c=N.NesMPU(memory=m,pc=START);c.a,c.x,c.y,c.p,c.sp=0xa9,71,109,flags,224
    # Actual fallback entry's two live bytes: saved original P above old A bank.
    c.stPush(197);c.stPush(flags)
    before_stack=bytes(m[0x1e1:0x200]);W.clear_logs(m)
    for _ in range(100):
        if c.pc in (0xf06f,0xf0d8):break
        assert m[c.pc],hex(c.pc);c.step()
    else:raise AssertionError('Relocated audio gate bound')
    assert c.sp==224 and bytes(m[0x1e1:0x200])==before_stack
    return c,m


def main():
    global BUNDLE
    cli=argparse.ArgumentParser();cli.add_argument('--section',choices=('unit','vectors','all'),default='unit');args=cli.parse_args()
    BUNDLE=W.Symbols.bundle()
    raw=Parent.Images.proposal(Parent.Images.Ex.proposal(Parent.Images.Route.A5.proposal(W.ROM.read_bytes())[0])[0])[0]
    image,record=proposal(raw);counts=Counter()
    # These are typed fallback-entry fixtures, not natural control routes.
    for mode in ((0,1,2) if args.section in ('unit','all') else ()):
        for owner in range(256):
            for flags in (0x20,0x21,0x61,0xe5):
                for prior in (0x82,0xff):
                    old,a=gate(raw,owner,mode,flags,prior);new,b=gate(image,owner,mode,flags,prior)
                    assert (old.a,old.x,old.y,old.sp)==(new.a,new.x,new.y,new.sp)
                    if owner!=43 or mode==0:
                        assert L.regs(old)==L.regs(new),(owner,mode,flags,'non43 flags/path')
                    else:assert old.pc==0xf06f and new.pc==0xf0d8
                    actual=lambda m:[(at,v)for at,v in m.writes if not 0x100<=at<=0x1e0]
                    assert (bytes(a[:0x100]),bytes(a[0x200:0x8000]),a.ram,a.rawtags,actual(a))==(
                        bytes(b[:0x100]),bytes(b[0x200:0x8000]),b.ram,b.rawtags,actual(b)),(owner,mode,flags,prior)
                    counts['typed_fallback_pairs']+=1
    real_vectors=native_vectors(image) if args.section in ('vectors','all') else None
    print(json.dumps(dict(passed=True,source_CPU_only=True,Mesen_run=False,ROM_written=False,
        output_files=0,record=record,cases=dict(counts),
        vectors=real_vectors,
        scope='Typed valid two-byte fallback stack. Optional vectors use real menu cold seed and actual full regular NMIs, with explicitly directed owner/queue fixtures; not a natural Sonic movement/pickup or Mesen claim.')),flush=True)


def native_vectors(image):
    b=dict(BUNDLE,raw=image);inventory=Parent.C.Starts.C.inventory(image)
    row=next(r for r in inventory['rows']if r['slot']==0 and r['cycle']==0)
    _,seed=Parent.C.cold(b,row);samples={};nmis=0
    for owner in (0,23,29,43):
        for prior in (0x82,0xff):
            m=L.clone(seed);N.put(m,SelectedCharacter=owner,OperMode=1,NmiDisable=0,FamilyMainCommit=0)
            m[0x72da]=prior
            c=N.NesMPU(memory=m,pc=0x5b00);c.sp,c.p=224,0x31;c.nmi()
            for _ in range(200000):
                if (c.pc,c.sp)==(0x5b00,224):break
                if START<=c.pc<END and m.rawtags[1]==191:
                    if c.pc==START:
                        assert not (c.p^m[0x100+((c.sp+1)&255)])&4,'Actual fallback changed saved I'
                    if c.pc not in samples:samples[c.pc]=L.clone(m,c)
                assert m[c.pc],('Actual full NMI BRK',hex(c.pc),m.rawtags);c.step()
            else:raise AssertionError('Actual full NMI bound')
            nmis+=1
    assert START in samples and samples
    rows=Counter()
    for pc,(state,cpu) in samples.items():
        m,c=L.clone(state,cpu);ref,r=L.clone(state,cpu)
        before=(L.regs(c),L.app(m),bytes(m[3:11]),bytes(m[0x15a:0x17b]),bytes(m[0x101+c.sp:0x200]))
        result=L.isr(m,c,'IRQ')
        assert before==(L.regs(c),L.app(m),bytes(m[3:11]),bytes(m[0x15a:0x17b]),bytes(m[0x101+c.sp:0x200])),hex(pc)
        L.finish(m,c,(0x5b00,224));L.finish(ref,r,(0x5b00,224))
        assert (L.regs(c),L.app(m))==(L.regs(r),L.app(ref)),('Real NMI continuation',hex(pc))
        rows[result]+=1
    return dict(full_regular_NMIs=nmis,reached_new_instruction_cuts=len(samples),actual_nested_IRQs=dict(rows),
        exact_registers_live_stack_R0_7_SMC_gameplay_private_mapper=True,
        actual_entry_saved_I_equal=True,no_private_audio_or_native_state_normalization=True)


if __name__=='__main__':main()
