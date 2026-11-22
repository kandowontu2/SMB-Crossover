"""Compact exact59e performance handoff and bounded side-batch negative.

No ROM proposal, cache, runtime patch, producer output or Mesen launch.
--trace repeats the actual compiled-menu/1-1 ordered-call observation using
the existing standalone CPU profiler and its normal logical NMI scheduler.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import compose_sonic_original_motion_1122 as Motion
import check_sonic_sms_side_batch_1110 as Side

PIN = '59e1a591d5ea31d62dafa9332990598b74b5b0852194ef7cc7ad22788196b723'
ROWS = [0, 13, 12, 10, 35, 35, 14, 14, 14, 14, 34, 9, 1, 2]
PREDICATE = bytes.fromhex('8d6a01a96d8d6c01a9b18d6d01a9d2205a01')


def H(raw):
    return sha256(raw).hexdigest()


def source_handoff(raw):
    assert H(raw) == PIN and len(raw) == 2097168
    meta = Motion.page(raw, 328)
    scene_side = int.from_bytes(meta[0x12b:0x12d], 'little')
    assert scene_side == 0xd2f5
    imports = dict(SideAdder=0x106, PlayerY=0xbd, R0=3, SceneSide=scene_side,
                   MTileAttribute=0xef36, SideEffect=0x9cb6)
    code = Side.assemble(''.join(f'{name}=${value:04x}\n' for name,value in imports.items()) +
                         Side.SOURCE.read_text(encoding='ascii'), {'SONIC_SIDE_BATCH': (0xda40,96)})
    leaf = code['images']['SONIC_SIDE_BATCH']
    at = Side.offset(126, 0x9c6e)
    native = raw[at:Side.offset(126,0x9cb6)]
    assert len(native) == 72 and len(leaf) == 75
    assert raw[Side.offset(126,0x9c8a):Side.offset(126,0x9c9c)] == PREDICATE
    assert raw[Side.offset(82,0xb16d):Side.offset(82,0xb189)] == bytes.fromhex(
        'c91cf015c96bf011a8b936ef2902f007c025d0054c2eb19860a90060')
    allowed = {0x9c86-0x9c6e,0x9c87-0x9c6e,0x9cad-0x9c6e,0x9cae-0x9c6e,0x9cb0-0x9c6e}
    differences = {i for i,value in enumerate(native) if value != leaf[i]}
    assert differences - allowed, 'Historical leaf unexpectedly matches current side predicate'
    return dict(
        ROM_SHA256=PIN, source_SHA256=H(Path(__file__).read_bytes()),
        measured_instruction_cycles_per_Main=dict(
            Sonic_idle=49227.1875, Sonic_Right16=49313.3125,
            Super_idle=49227.1875, Super_Right16=49313.3125,
            scope='16 actual empty1-1 Main returns/phase/form; normal logicalNMI, no DMA/physicalIRQ'),
        measured_nested_costs=dict(bank65_self=16236, shared_SMC_self_about=7007,
            CoCheckCode_calls=14, CoCheckCode_inclusive=9142,
            CoCheckHeaders_inclusive=8022, native_motor_idle=6449,
            full184_byte_rollback_snapshot=1907,
            warning='Nested inclusive costs overlap; bank65 and SMC self-costs are disjoint.'),
        observed_empty_row_order=ROWS,
        current_auth=dict(native_gate=[65,0xa75e], CoCheckCode=0xaee2, CoCheckHeaders=0xaf27,
            observed_shadow_and_actual_C=3, actual_Main_return_word='5283',
            row0_epoch='Before row0: prior epoch; after row0: current FrameCounter in C11B, HaveEpoch C11A=1.',
            observed_header_and_identity_writes='None in the two traced idle/Right Main samples; not a lifetime proof.'),
        side_batch_negative=dict(passed_as_expected=True, original_source=str(Side.SOURCE),
            original_checker=str(Path(Side.__file__)), historical_leaf_bytes=75,
            current_native_half_open=[0x9c6e,0x9cb6],
            unexpected_different_PCs=[0x9c6e+i for i in sorted(differences-allowed)],
            current_upper_predicate=dict(caller_bank=126,caller_PC=0x9c8a,bank=82,PC=0xb16d,
                                         producer='compose_prince_native_flag_1111.py',
                                         contract='Retain native pipe/climb predicate and special tile25 flag/climb jump to B12E.'),
            conclusion='Old source cannot be applied unchanged. No current leaf-equivalence or patch cycle saving claimed.'),
        reusable_patterns=[
            dict(file='tools/reference/mini_mario_idle_fast.s',
                 contract='Same-frame Mini cache plus both live header prefixes; native side/constant ABI fast paths.'),
            dict(file='tools/audit/check_contra_force_fast_ingress_1122.py',
                 admission=[69,0xbf94],scope_marker='01FA:83->84->83',
                 contract='Full owner admission; owner31 + live stack marker + actual C2; retire marker and respect published C mapping.'),
            dict(file='tools/audit/check_mini_sonic_owner_irq_9826_1116.py',
                 contract='Existing actual shared owner-reload IRQ/busyNMI proof at79:B53C/B53F.')],
        required_scope_boundaries=[
            'Start only after complete authentication on the genuine ordinary native Main stack; detached/cold/retire calls retain full checks.',
            'Prove raw owner/form, both physical code/state banks and actual mapping. Current calls arrive with C3, so do not transplant the CF C2 test blindly.',
            'End before native Main unwinds. Invalidate before header clear/owner replacement/cold copy, fresh/powerup resets, scene transitions and failed admission.',
            'FrameCounter is8-bit and does not advance while paused. HaveEpoch/epoch alone is not a newly granted authentication lease.',
            'BusyNMI preserves current registers/SMC/maps but strips proposed FamilyMainCommit high bits; do not store a cache token there.',
            'Keep native head/feet/side effects, the current Prince upper-side predicate, rollback and all IRQ/NMI return cleanup.'
        ],
        projected_not_removed=dict(skip_all14_header_checks_upper_bound=8022,
            one_full_check_then_skip13_header_loops_upper_bound=7449,
            warning='Before guard/entry/exit overhead; insufficient alone to establish a physical cadence improvement.'),
        DK_Jr_relevance='Same common bank65 auth/dispatch and generic SMC work can share a future framework. Sonic-specific side filter/batch and context bytes cannot be applied to DK Jr unchanged.',
        production_patch=None, proven_current_patch_cycles_removed=0, outputs=0, Mesen=False)


def ordered_trace(raw):
    import profile_sonic_empty_cpu_1110 as B
    m=B.enter(raw)
    for _ in range(300):
        if tuple(B.N.get(m,n) for n in ('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):break
        B.main_step(m,0)
    else:raise AssertionError('Native1-1 entrance bound')
    for _ in range(4):B.main_step(m,0)
    baseline=B.N.NesMPU
    rows=[]
    for pad in (0,1):
        events=[]
        class CPU(baseline):
            def step(self):
                tag=m.rawtags[(self.pc-0x8000)//8192] if self.pc>=0x8000 else -1
                if (tag,self.pc)==(193,0xaf27):
                    target=m[0x16c]+256*m[0x16d]
                    events.append(dict(row=(target-0xb08c)//3,SP=self.sp,
                        shadow_C=B.N.get(m,'CurrentBankC'),actual_C=m.rawtags[2],
                        FrameCounter=B.N.get(m,'FrameCounter'),Ready=m.ram[2][0x119],
                        HaveEpoch=m.ram[2][0x11a],Epoch=m.ram[2][0x11b],
                        Main_return_word=bytes(m[0x1f9:0x1fb]).hex()))
                return super().step()
        with patch.object(B.N,'NesMPU',CPU):cycles,nmi=B.main_step(m,pad)
        assert [e['row'] for e in events]==ROWS
        assert all(e['shadow_C']==e['actual_C']==3 for e in events)
        assert events[0]['Epoch']!=events[0]['FrameCounter']
        assert all(e['Epoch']==e['FrameCounter'] for e in events[1:])
        assert not any(B.flags(m))
        rows.append(dict(pad=pad,Main_cycles=cycles,scheduled_NMI_cycles=nmi,events=events))
    return rows


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--trace',action='store_true');args=parser.parse_args()
    def deny(*a,**k):raise AssertionError('Scope research attempted output/process')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        raw=Motion.ROM.read_bytes();q=source_handoff(raw)
        if args.trace:q['repeated_actual_trace']=ordered_trace(raw)
    q['receipt_SHA256']=H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('SONIC SCOPE HANDOFF '+json.dumps(q,separators=(',',':')),flush=True)
