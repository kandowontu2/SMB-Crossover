"""Paired IRQ/FF cuts during actual neutral supported horizontal carrying."""
import argparse
from hashlib import sha256
import inspect
import json
from pathlib import Path

import check_manual_roster_paired_irq_1110 as V
import check_manual_roster_carry_1110 as Carry

F,I,P,N,R=V.F,V.I,V.P,V.N,V.R
SHA=lambda p:sha256(Path(p).read_bytes()).hexdigest()
TYPED_AUDIO=set()


def main():
    cli=argparse.ArgumentParser();cli.add_argument('--identity',default='22:0');a=cli.parse_args()
    identity=tuple(map(int,a.identity.split(':')))
    assert identity in tuple((o,v) for o,c in ((22,4),(29,6)) for v in range(c))
    proof=I.OUT/'ff-foot-proof.json';q=json.loads(proof.read_text())
    for name,digest in q['bindings'].items():assert SHA(R/name)==digest,name
    V.BASELINE=I.BASE.read_bytes();raw=P.install(V.BASELINE,q['patches'])
    assert I.SHA(raw)==q['expected_memory_only_SHA256']
    b=F.bundle(raw,q['labels'])
    original_scene=V.Old.Motion.scene
    def scene(bundle,owner,variant):
        m=original_scene(bundle,owner,variant)
        boarding=Carry.horizontal(m,owner)
        assert boarding['native_carry_samples']==60
        print('Reached real supported neutral scene',owner,variant,boarding,flush=True)
        return m
    V.Old.Motion.scene=scene
    original_pair=V.pair_source
    original_isr=V.paired_isr
    original_restore=V.restore_audio_snapshot
    original_final=V.final_state
    def supported_isr(c,kind,owner,lag,regular):
        before=tuple(bytes(row) for row in c.memory.ram)
        after,offsets,saved,hardware,commit=original_isr(c,kind,owner,lag,regular)
        typed={(1,at):value for at,value in saved.items()}
        # The warmed WWF source music image has its real channel counters in
        # WfState+$500..$57f (C500..C57F in RAM C2), as well as A1 scratch.
        # Admit only bytes that the complete paired baseline ISR actually
        # changed; every foreground access to any such byte is trapped below.
        for at,(old,new) in enumerate(zip(before[2],after[8][2])):
            if old!=new:
                assert owner[0]==29 and 0x500<=at<0x580,(owner,hex(at),old,new)
                typed[2,at]=old
        TYPED_AUDIO.update(typed)
        return after,tuple(typed),typed,hardware,commit
    def restore_typed(after,before,offsets,index):
        row=list(after);banks=list(row[index])
        for bank in {bank for bank,at in offsets}:
            image=bytearray(banks[bank])
            for b,at in offsets:
                if b==bank:image[at]=before[index][bank][at]
            banks[bank]=bytes(image)
        row[index]=tuple(banks)
        return tuple(row)
    def final_typed(c):
        result=P.final(c);saved=getattr(c.memory,'manual_audio_before',{})
        if saved:
            row=list(result);banks=list(row[6])
            for bank in {bank for bank,at in saved}:
                image=bytearray(banks[bank])
                for (b,at),value in saved.items():
                    if b==bank:image[at]=value
                banks[bank]=bytes(image)
            row[6]=tuple(banks);result=tuple(row)
        return result
    V.paired_isr=supported_isr;V.restore_audio_snapshot=restore_typed;V.final_state=final_typed
    def native_carry_source(source):
        source=original_pair(source)
        return P.replace_one(source,'or tag == 190 and 0xadc4 <= pc < 0xadde)',
            'or tag == 190 and 0xadc4 <= pc < 0xadde\n'
            '                          or tag == 128 and (0xb453 <= pc < 0xb490 or 0xb683 <= pc < 0xb6b5)\n'
            '                          or tag == 254 and (0x9512 <= pc < 0x9570 or 0x9a2c <= pc < 0x9a72))')
    V.pair_source=native_carry_source
    try:
        # Neutral actual pad, while the real preexisting H actor remains active.
        source=inspect.getsource(V.vectors).replace('def vectors(','def carry_vectors(',1)
        source=P.replace_one(source,'tag==1 and (at&8191) in self.manual_audio_before',
            '(tag,at&8191) in self.manual_audio_before')
        env=dict(V.__dict__);exec(source,env)
        result=env['carry_vectors'](b,q['labels'],0,(identity,),('carry',))
    finally:
        V.Old.Motion.scene=original_scene;V.pair_source=original_pair
        V.paired_isr=original_isr;V.restore_audio_snapshot=original_restore;V.final_state=original_final
    print('Paired supported carrying vectors',result,flush=True)
    receipt=dict(passed=True,source_CPU_only=True,Mesen_run=False,ROM_written=False,
        expected_memory_only_SHA256=q['expected_memory_only_SHA256'],identity=identity,
        vectors=result,paired_baseline_callbacks=dict(V.PAIRED),
        audio_capsule_bank1_offsets=sorted(V.AUDIO_OFFSETS),
        paired_audio_bank_and_offset=sorted(TYPED_AUDIO),
        native_commit_acknowledgments={str(k):v for k,v in V.COMMIT_TRANSITIONS.items()},
        scope='Actual controller boards and60neutralcarry updates before genuine IdleLoop/GameLoop/Core IRQ cuts, including native PlayerCollisionCore/ProcLPlatCollisions/PositionPlayerOnHPlat plus new FF temporary-foot gate. Exact paired baseline ISR effects; complete foreground resumes.',
        bindings={p.relative_to(R).as_posix():SHA(p) for p in
            (Path(__file__),Path(V.__file__),Path(Carry.__file__),proof,
             R/'build/wwf-roster-native-1101-v1/audio.s',
             R/'build/wwf-roster-native-1101-v1/native_support.s')})
    (I.OUT/('carry-irq-'+a.identity.replace(':','-')+'.json')).write_text(json.dumps(receipt,indent=2)+'\n')


if __name__=='__main__':main()
