"""Keep source point publication, flush native score after original phase returns.

Private local stack repair; no resident/post-return/shared hook change.
"""
import json
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
R, O = A.R, A.O


def main():
    prior = json.loads((O/'native-registers-v48-layout.json').read_text())
    negative = json.loads((O/'native-service-v53-nested-negative.json').read_text())
    assert not negative['passed'] and 'nested IRQ state' in negative['error']
    source = (O/'native-registers-v48.s').read_text()
    stage = '''DkjrNativeAwardSourcePoints:
 php
 pha
 cpx #7
 bcs DkScoreStageReturn
 lda DNativeData_c61b,x
 sta ScoreAmount
DkScoreStageReturn:
 pla
 plp
 rts
; Exact native score/HUD work runs after the original phase returns. Source
; popup/point choice stays at the original EC3F site; no native effect is
; delayed beyond this owning Main call. ScoreAmount is consumed once.
DkScoreFlush:
'''
    assert source.count('DkjrNativeAwardSourcePoints:\n') == 1
    source = source.replace('DkjrNativeAwardSourcePoints:\n', stage)
    old = ''' cpx #7
DkShortCandidate195:
 bcs AwardReturn
 lda DNativeData_c61b,x
 sta ScoreAmount'''
    new = ''' lda ScoreAmount
DkShortCandidate195:
 beq AwardReturn'''
    assert source.count(old) == 1
    source = source.replace(old, new)
    old = ' sta DigitModifier+3\n jsr DkjrNativeAddScore'
    assert source.count(old) == 1
    source = source.replace(old, ' sta DigitModifier+3\n lda #0\n sta ScoreAmount\n jsr DkjrNativeAddScore')
    old = 'DkjrNativeLifeReset:\n lda #0\n sta LifeCommitted\n rts'
    assert source.count(old) == 1
    source = source.replace(old, 'DkjrNativeLifeReset:\n lda #0\n sta LifeCommitted\n sta ScoreAmount\n rts')
    old = ' jsr DkPauseMain\n bcc DkMainNo'
    assert source.count(old) == 1
    source = source.replace(old, ' jsr DkPauseMain\n jsr DkScoreFlush\n bcc DkMainNo')
    source += '\n.export DkScoreFlush,DkScoreStageReturn\n'
    cfg = ('MEMORY{C:start=$a000,size=$1fe0,file=%O;P:start=$d540,size=$11e,file="'+(O/'native-scoretail-pause-v54.bin').as_posix()+'";'
           'M:start=$d65e,size=$49,file="'+(O/'native-scoretail-main-v54.bin').as_posix()+'";'
           'N:start=$d6a7,size=$159,file="'+(O/'native-scoretail-ports-v54.bin').as_posix()+'";}'
           'SEGMENTS{DKJR:load=C,type=rw;DK_PAUSE:load=P,type=ro;DK_MAIN:load=M,type=ro;DK_PORTS:load=N,type=ro;}')
    blob, L = A.assemble('native-scoretail-v54', source, cfg)
    assert L['DkPauseThaw'] == 0xd60c and len(blob) <= 8160
    q = dict(prior)
    q.update(labels=L, body_bytes=len(blob), body_end=L['DkjrComponentEnd'], header_spare=8160-len(blob),
        score_publication=dict(original_site='EC3F', immediate_source_point_kind_and_popup=True,
            pending_packed_amount=0xc8f9, existing_private_byte=True,
            native_flush='DkNativeMain immediately after DkPauseMain before movement return/nativeAI',
            genuine_native_service='AddToScore', constructor_clears_pending=True,
            source_call_multiplicity_and_lifetime_proof_pending=True),
        metadata_end=L['DkNativePortsEnd'] if 'DkNativePortsEnd' in L else 0xd77b,
        scope='Compiled local score-stack proposal only. Original donor point-kind/EC3F popup timing and public source AXYP remain immediate. Genuine native score/HUD executes within the same Main after original phase returns. Full actual boundary/source/lifetime/IRQ proof still required; no ROM or shared write.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes()) for p in [Path(__file__), O/'native-registers-v48.s', O/'native-service-v53-nested-negative.json', O/'native-scoretail-v54.s', O/'native-scoretail-v54.bin']})
    (O/'native-scoretail-v54-layout.json').write_text(json.dumps(q, indent=2)+'\n')
    print(json.dumps({k:q[k] for k in ['passed','body_bytes','header_spare','metadata_end']}))


if __name__ == '__main__':
    main()
