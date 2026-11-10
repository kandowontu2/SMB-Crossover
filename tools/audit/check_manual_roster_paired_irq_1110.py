"""Compare every ISR against74fde at identical reached70aa CPU/RAM context."""
import argparse
from collections import Counter
from hashlib import sha256
import inspect
import json
from pathlib import Path

import check_manual_roster_irq_1110 as Old
import check_manual_roster_ff_foot_1110 as F

I,P,N,R=F.I,F.P,F.N,F.R
PROOF=I.OUT/'ff-foot-proof.json'
SHA=lambda p:sha256(Path(p).read_bytes()).hexdigest()
BASELINE=None
PAIRED=Counter()
AUDIO_OFFSETS=set()
COMMIT_TRANSITIONS=Counter()
COMMIT_PUBLICATIONS=Counter()


def traced_run(c,stop,visit=None):
    def watch(q):
        q.memory.manual_last_pc=q.pc
        q.memory.manual_last_tag=P.tags(q)
        if visit:visit(q)
    return P.run(c,stop,watch)


def diagnostic(a,b):
    result=[]
    for i,(x,y) in enumerate(zip(a,b)):
        if x==y:continue
        if isinstance(x,(bytes,bytearray)):
            result.append([i,[[j,u,v] for j,(u,v) in enumerate(zip(x,y)) if u!=v][:12]])
        elif i in (6,8):
            result.append([i,[[bank,[[j,u,v] for j,(u,v) in enumerate(zip(xx,yy)) if u!=v][:12]]
                for bank,(xx,yy) in enumerate(zip(x,y)) if xx!=yy]])
        else:result.append([i,str(x)[:300],str(y)[:300]])
    return result


def native_extra(c):
    m=c.memory
    return (bytes(m[0x7382:0x73dd]),P.fields(m,P.PLAYER_FIELDS),
            bytes(m[0x658:0x674]),bytes(m[0x5c00:0x6000]))


def paired_isr(c,kind,owner,lag,regular):
    z=P.clone(c);m=z.memory
    # Replace only ROM bytes. Preserve CPU, all4 live RAM images, all cached
    # code, mapper/PPU/audio/controller state and the reached foreground PC.
    m.bundle=dict(m.bundle,raw=BASELINE)
    for window,tag in enumerate(tuple(m.rawtags)):
        if tag&128:m.raw_page(window,tag)
    m.manual_irq_probe=False
    before=P.live(z)+native_extra(z)
    entry=(z.pc,z.sp)
    m.vector_floor=0x100+z.sp;m.written_stack=set();m.manual_irq_probe=True
    if kind=='lag_FF':z.nmi()
    else:z.irq()
    hits=[0];commit_changes=[];last=[None,None,m[0x5fff]]
    def watch(q):
        commit=q.memory[0x5fff]
        if commit!=last[2]:
            commit_changes.append((last[0],last[1],last[2],commit))
        last[:]=[q.pc,P.tags(q),commit]
        if kind=='lag_FF':
            assert q.pc!=regular
            hits[0]+=q.pc==lag
    P.run(z,lambda q:(q.pc,q.sp)==entry,watch)
    m.vector_floor=None;m.manual_irq_probe=False
    assert hits[0]==int(kind=='lag_FF')
    after=P.live(z)+native_extra(z)
    offsets=tuple(i for i,(a,b) in enumerate(zip(before[8][1],after[8][1])) if a!=b)
    # Only the already-proven WWF bank1 audio capsule may legitimately advance.
    assert not offsets or owner[0]==29,(owner,kind,offsets)
    commit=None
    if before[-1][-1]!=after[-1][-1]:
        assert commit_changes==[(0xb544,191,before[-1][-1],before[-1][-1]&1)],(owner,kind,commit_changes)
        assert after[-1][-1]==before[-1][-1]&1
        commit=dict(before=before[-1][-1],after=after[-1][-1],PC=0xb544,tag=191)
        COMMIT_TRANSITIONS[(kind,commit['before'],commit['after'])]+=1
    AUDIO_OFFSETS.update(offsets);PAIRED[kind]+=1
    hardware=tuple((a,v) for a,v in m.writes if a>=0x2000)
    return after,offsets,{i:before[8][1][i] for i in offsets},hardware,commit


def restore_audio_snapshot(after,before,offsets,index):
    row=list(after);banks=list(row[index]);audio=bytearray(banks[1])
    for i in offsets:audio[i]=before[index][1][i]
    banks[1]=bytes(audio);row[index]=tuple(banks)
    return tuple(row)


def final_state(c):
    result=P.final(c)
    saved=getattr(c.memory,'manual_audio_before',{})
    if saved:
        row=list(result);banks=list(row[6]);audio=bytearray(banks[1])
        for i,value in saved.items():audio[i]=value
        banks[1]=bytes(audio);row[6]=tuple(banks);result=tuple(row)
    return result


def restore_commit_live(after,before,commit):
    if commit is None:return after
    row=list(after);exram=bytearray(row[-1])
    assert exram[-1]==commit['after'] and before[-1][-1]==commit['before']
    exram[-1]=commit['before'];row[-1]=bytes(exram)
    return tuple(row)


def final_extra(c):
    # The genuine foreign Main publisher closes the acknowledged transaction.
    # Entire final ExRAM, including5FFF, must match the no-ISR reference raw.
    return native_extra(c)


def record_commit_publication(pc,tag,old,value):
    assert (pc,tag,old,value)==(0xb428,191,0,0),('Unexpected foreground protocol write',hex(pc),tag,old,value)
    COMMIT_PUBLICATIONS[(pc,tag,old,value)]+=1


def pair_source(source):
    source=P.replace_one(source,'        z = clone(c)',
        '        paired_after,audio_offsets,audio_before,paired_hardware,commit = paired_isr(c,kind,owner,lag,regular)\n'
        '        z = clone(c)')
    source=P.replace_one(source,'        after = live(z)',
        '        after = live(z)\n'
        '        assert after == paired_after, (kind,owner,entry,"paired baseline ISR",diagnostic(after,paired_after))\n'
        '        assert tuple((a,v) for a,v in m.writes if a>=0x2000) == paired_hardware, (kind,owner,entry,"paired hardware")')
    source=P.replace_one(source,'        assert after == before, (kind, owner, entry)',
        '        after = restore_audio_snapshot(after,before,audio_offsets,8)\n'
        '        after = restore_commit_live(after,before,commit)\n'
        '        assert after == before, (kind,owner,entry,"unmodified nonaudio live state",diagnostic(after,before))\n'
        '        m.manual_audio_before=audio_before\n'
        '        m.manual_commit_before=commit["before"] if commit else None\n'
        '        m.manual_foreground_watch=bool(audio_offsets or commit)')
    source=P.replace_one(source,'or tag == 192 and (0xb378 <= pc < 0xb400 or 0xbfdd <= pc < 0xc000))',
        'or tag == 192 and (0xb378 <= pc < 0xb400 or 0xbfdd <= pc < 0xc000)\n'
        '                          or tag == 190 and 0xadc4 <= pc < 0xadde)')
    return source


def vectors(b,labels,axis,identities,scenarios):
    # Keep the established genuine IdleLoop/GameLoop/Core/SP/full-resume test.
    # Replace its equality-to-no-audio assumption with an exact paired ISR.
    source=inspect.getsource(Old.vectors).replace('def vectors(','def qualify(',1)
    source=P.replace_one(source,'    env=dict(P.__dict__)',
        '    source=pair_source(source)\n    env=dict(P.__dict__)\n'
        '    env.update(paired_isr=paired_isr,restore_audio_snapshot=restore_audio_snapshot,restore_commit_live=restore_commit_live,diagnostic=diagnostic,run=traced_run)')
    source=P.replace_one(source,'        manual_irq_probe=False',
        '        manual_irq_probe=False\n        manual_foreground_watch=False\n'
        '        def foreground_check(self,at):\n'
        '            if self.manual_foreground_watch and isinstance(at,int) and at>=0x8000:\n'
        '                tag=self.rawtags[(at-0x8000)//8192]\n'
        '                assert not (tag==1 and (at&8191) in self.manual_audio_before), ("Foreground consumes ISR-only audio byte",hex(at))\n'
        '        def __setitem__(self,at,value):\n'
        '            self.foreground_check(at)\n'
        '            if self.manual_foreground_watch and isinstance(at,int) and at==0x5fff:\n'
        '                if self.manual_commit_before is not None:\n'
        '                    record_commit_publication(self.manual_last_pc,self.manual_last_tag,self[at],value)\n'
        '            return super().__setitem__(at,value)')
    source=P.replace_one(source,'        def __getitem__(self,at):',
        '        def __getitem__(self,at):\n            self.foreground_check(at)')
    source=P.replace_one(source,'try:return (*fn(c),bytes(c.memory[0x7382:0x73dd]))',
        'try:return (*fn(c),*(final_extra(c) if fn is final_state else native_extra(c)))')
    source=P.replace_one(source,'final=lambda c:snapshot(c,P.final)',
        'final=lambda c:snapshot(c,final_state)')
    env=dict(Old.__dict__);env.update(pair_source=pair_source,paired_isr=paired_isr,
        restore_audio_snapshot=restore_audio_snapshot,diagnostic=diagnostic,
        restore_commit_live=restore_commit_live,native_extra=native_extra,final_state=final_state,final_extra=final_extra,traced_run=traced_run,
        record_commit_publication=record_commit_publication)
    exec(source,env)
    return env['qualify'](b,labels,axis,identities,scenarios)


def main():
    global BASELINE
    cli=argparse.ArgumentParser()
    cli.add_argument('--axis',type=lambda x:int(x,0),choices=(0x28,0x24),required=True)
    cli.add_argument('--identity',help='Optional owner:variant source probe.')
    cli.add_argument('--pressure',action='store_true')
    a=cli.parse_args();q=json.loads(PROOF.read_text())
    for name,digest in q['bindings'].items():assert SHA(R/name)==digest,name
    BASELINE=I.BASE.read_bytes();assert I.SHA(BASELINE)==q['parent_SHA256']==I.PIN
    raw=P.install(BASELINE,q['patches']);assert I.SHA(raw)==q['expected_memory_only_SHA256']
    b=F.bundle(raw,q['labels'])
    identities=tuple((owner,variant) for owner,count in ((22,4),(29,6)) for variant in range(count))
    if a.identity:
        identity=tuple(map(int,a.identity.split(':')));assert identity in identities
        identities=(identity,)
    result=vectors(b,q['labels'],a.axis,identities,
        ('birth','full','replacement') if a.pressure else ('birth',))
    print('Paired actual vectors',result,'baseline callbacks',dict(PAIRED),'audio offsets',sorted(AUDIO_OFFSETS),
        'native commit acknowledgments',dict(COMMIT_TRANSITIONS),flush=True)
    receipt=dict(passed=True,source_CPU_only=True,Mesen_run=False,ROM_written=False,
        expected_memory_only_SHA256=q['expected_memory_only_SHA256'],baseline_SHA256=I.PIN,
        ff_foot_proof_SHA256=SHA(PROOF),axis=a.axis,identities=identities,vectors=result,
        paired_baseline_ISR_callbacks=dict(PAIRED),audio_capsule_bank1_offsets=sorted(AUDIO_OFFSETS),
        native_commit_acknowledgments={str(k):v for k,v in COMMIT_TRANSITIONS.items()},
        native_idempotent_foreground_commit_publications={str(k):v for k,v in COMMIT_PUBLICATIONS.items()},
        exact_complete_ISR_state_and_hardware=True,
        normalization='Only actual paired-baseline bank1 audio deltas (foreground read/write trapped), plus source-typed63:B544 FamilyMainCommit AND1 ack during the immediate ISR live comparison. Resumed protocol writes admit only idempotent63:B428 0to0; final complete ExRAM including5FFF is compared raw/exact. Every other live byte and complete foreground resume remains exact.',
        source_authority='build/wwf-roster-native-1101-v1/{audio.s,native_support.s}: exclusive bank1 audio capsule scratch/context, native NMI owner; no foreground consumer admitted.',
        bindings={p.relative_to(R).as_posix():SHA(p) for p in
            (Path(__file__),PROOF,Path(F.__file__),Path(Old.__file__),R/'build/wwf-roster-native-1101-v1/audio.s',R/'build/wwf-roster-native-1101-v1/native_support.s',R/'src/rogue_dawn_audio_scheduler_hooks_v5.s',R/'tools/audit/reserve_family_main_commit_v1.py')})
    suffix=('V' if a.axis==0x28 else 'H')+('-'+a.identity.replace(':','-') if a.identity else '')+('-pressure' if a.pressure else '')
    (I.OUT/f'paired-irq-{suffix}.json').write_text(json.dumps(receipt,indent=2)+'\n')


if __name__=='__main__':main()
