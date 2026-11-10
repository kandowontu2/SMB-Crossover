"""Merge immutable source, numeric, real-vector and floor qualifications."""
from hashlib import sha256
import json
from pathlib import Path

import check_manual_wide_horizontal_1110 as W
import check_manual_wide_final_vectors_1110 as V

R,OUT,P=W.R,W.OUT,W.P


def sha(path):return sha256(path.read_bytes()).hexdigest()


def main():
    names=('proof.json','qualification-foreground.json','irq.json','floor-proof.json','supplement-irq.json')
    paths=[OUT/n for n in names]
    initial,foreground,owned,floor,supplement=[json.loads(p.read_text()) for p in paths]
    assert all(q['passed'] for q in (initial,foreground,owned,floor,supplement))
    assert foreground['preliminary_proof_SHA256']==owned['preliminary_proof_SHA256']==sha(paths[0])
    assert foreground['expected_memory_only_SHA256']==owned['expected_memory_only_SHA256']==initial['expected_memory_only_SHA256']
    assert floor['predecessor_proof_SHA256']==sha(paths[0])
    assert floor['predecessor_SHA256']==initial['expected_memory_only_SHA256']
    assert supplement['floor_proof_SHA256']==sha(paths[3])
    assert supplement['expected_memory_only_SHA256']==floor['expected_memory_only_SHA256']
    assert supplement['full_helper_SRAM_preserved']
    assert set(supplement['vectors'])=={'late-no-manual','authored-inside','manual-bypass',
        'generic-sine-0','generic-sine-16','generic-sine-64','generic-sine-160'}
    bindings={}
    for q in (initial,foreground,owned,floor,supplement):
        for path,digest in q.get('bindings',{}).items():
            assert sha(R/path)==digest,path
            if path in bindings:assert bindings[path]==digest,path
            bindings[path]=digest
    base=W.BASE.read_bytes();assert W.sha(base)==floor['parent_SHA256']==W.PIN
    old=P.install(base,initial['patches']);new=P.install(base,floor['patches'])
    assert W.sha(old)==initial['expected_memory_only_SHA256'] and W.sha(new)==floor['expected_memory_only_SHA256']
    allowed=set(range(P.L.CODE,P.L.CODE+5120))|set(range(P.L.COOKIE+3,P.L.COOKIE+16))
    changed={i for i,(a,b) in enumerate(zip(old,new)) if a!=b}
    assert changed<=allowed
    for key in ('MiniHostMain','MiniStep','MiniAnimate','MiniHostDraw','MiniHostGraphics','MiniNativeDraw',
                'MiniHostBox','MiniHostHead','MiniHostInjury','ManualPlatform','ManualPlatformCreated',
                'ManualMotionGate','ManualWideHorizontal','ManualSineDecode','KrManualOptions'):
        assert initial['labels'][key]==floor['labels'][key],key
    refs=paths+[Path(__file__).resolve(),Path(V.__file__).resolve(),Path(V.G.__file__).resolve(),
                OUT/'kernel.bin',OUT/'floor-kernel.bin']
    bindings.update({p.relative_to(R).as_posix():sha(p) for p in refs})
    result=floor|dict(interrupt_pending=False,fully_source_qualified=True,Mesen_run=False,
        bindings=bindings,
        qualification=dict(numeric_foreign=names[1],owned_constructor_motion_vectors=names[2],
            final_floor_and_generic_decoder_vectors=names[4],
            exact_sine_states=foreground['sine']['states'],foreign_native_cases=foreground['foreign']['cases'],
            old_owned_vector_reuse='Only Mini body/floor scope plus authenticcookie changed after ownedFF/IRQ qualification; same constructor/gate/motion/decoder bytes and public entry PCs. Final floor/mapping/HP scratch paths exercised by supplemental actualGameLoop vectors.',
            final_kernel_changed_bytes=len(changed),
            generic_H_sine_added_CPU=foreground['sine']['additional_CPU_cycles'],
            ISR_decoder_state_reads_forbidden=supplement['ISR_decoder_state_read_trap'],
            native_acceptance='Root-owned exact74fde Mini/Karnov6birth fullright-left-right112pixel carry, Mini3494/3494zero-lag andGetsu earnedmushroom/flower; native/delivery receipts remain separate.'))
    (OUT/'qualified-proof.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,interrupt_pending=False,expected_memory_only_SHA256=result['expected_memory_only_SHA256'],
        proof_SHA256=sha(OUT/'qualified-proof.json'),files=len([p for p in OUT.rglob('*') if p.is_file()]))),flush=True)


if __name__=='__main__':main()
