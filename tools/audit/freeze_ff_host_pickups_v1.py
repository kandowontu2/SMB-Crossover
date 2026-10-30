"""Freeze source pickup/freeze/body consumers with retained negative fixtures."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_host_pickups_edges_v3 as T
from check_tmnt_render_oa import address
C=T.C;sha=C.sha
P=T.P;O=R/'build/final-fantasy-host-pickups-qualified-v1'


if __name__=='__main__':
    assert not O.exists()
    packets=[P/'build-proof.json',T.T.P/'build-proof.json',
             T.T.O/'controls.json',T.O/'controls.json',
             R/'build/final-fantasy-host-impulse-air-v1/controls.json',
             R/'build/final-fantasy-host-pickups-controls-v1/controls.json']
    bindings={};proofs=[]
    for p in packets:
        j=json.loads(p.read_text());proofs.append(j)
        for n,d in j['bindings'].items():
            assert sha(n)==d,n
            assert bindings.get(n,d)==d,n
            bindings[n]=d
        bindings[str(p.resolve())]=sha(p)
    assert all(j['passed']for j in proofs[:5])
    assert not proofs[5]['passed']and list(proofs[5]['failures'])==['vectors']
    diagnostic=R/'build/final-fantasy-host-pickups-controls-v1/ISR-diagnostic.json'
    d=json.loads(diagnostic.read_text())
    assert d['PC']=='0xb3ca'and d['opcode']==[169,221,141,22,81]
    assert d['rawtags'][2]==216 and d['CurrentBankC']=='0xdd'
    extras=[Path(__file__).resolve(),diagnostic,
            R/'tools/audit/ff_host_pickups_controls_v1.py',
            R/'tools/audit/ff_host_pickups_vectors_v2.py',
            R/'tools/audit/ff_host_impulse_air_v1.py',
            R/'tools/reference/final_fantasy_host_pickups_v1.s',
            R/'tools/reference/final_fantasy_host_pickups_v2.s',
            R/'tools/audit/prepare_ff_host_pickups_v1.py',
            R/'tools/audit/prepare_ff_host_pickups_v2.py']
    extras+=list((R/'build/final-fantasy-host-pickups-v1').iterdir())
    for p in extras:
        if p.is_file():bindings[str(p.resolve())]=sha(p)
    for p,d in bindings.items():assert sha(p)==d,p
    assert sha(P/'ram3.bin')=='2ef76f0b00d94f5ecf10ed0bdc5745b0ac9e90394ddc1f0a0dc2abd5a26ec0ed'
    b=C.bundle(P)
    API=dict(
        FfHostCollect='Public selected22/engine8/unpaused/Timer0/notdead item callback, Xnative0..5. Requires live PowerUpObject and mature negative Enemy_State, PowerUpType0..3. No head-hit auto-collection. Genuine erase+world-projected popup and source FfPickup. Mushroom/flower advances actual class tier/charges and starts hosted60tickfreeze; star/1UP keep FFgear. Cset accepted/Cclear rejected; actual X/ObjectOffset preserved. Actual collision admission remains parent-owned.',
        FfHostBeginFreeze='Byte-exact genuine native MarioSourceBeginFreeze clone in owned RAM3; internal selected callback only. Captures existing ObjectMetasprite, resets native freeze counters and shot pose, activates TimerFF/engine9.',
        FfHostPowerupTick='Public selected22/engine9/unpaused/GuestPowerupActive callback. Exactly60 logicalupdates; displayed tier alternates using native6tick pattern without revoking acquired gear. Final PlayerStatus/source target, engine8, clears native freeze flags, marks FfPaletteAckFF. Actual main hook and palette compositor still required.',
        FfHostGraphics='Typed own22 graphics wrapper. Ensure genuine lifecycle; temporarily substitutes GuestPowerupDisplay only while building actual source descriptor, then restores acquired FfPower. No movement. CallerC left as genuine ART93 output; ROM bridge must restore caller mapping.',
        FfHostBody='Typed selected22 enemy-body callback, service11. Preserves original enemy-ID A/X/Y and V/D/I; genuine Easy+notunderwater policy writes GuestBodyStompAllowed/NoStomp. Cclear continues genuine native enemy contact; this is not terrain foot service.',
        FfHostImpulseAccepted='Typed selected22 callback AFTER actual native X5StompDispatch or X5SpringDispatch populated MmVY. Preserves complete A/X/Y/P, including all64flag combinations, and native fractional impulse. Sets FfJump1/FfGPhase0; subsequent actual source dry-air integrator retains fraction. Parent ROM bridge must genuinely farcall native X5, never nearcall foreign A.')
    report=dict(passed=True,status='PRIVATE_FF_ITEM_FREEZE_BODY_SOURCE_CPU_PASS_CART_HOOKS_PENDING',
        native=False,full_Main=False,loader=False,shared_or_Downloads_changed=False,
        image=str((P/'ram3.bin').resolve()),image_sha256=sha(P/'ram3.bin'),
        host_pickups_bytes=399,source_span='rawRAM3 BB60..<BCEF; original CORE/publisher/ART/CHR/combat/terrain unchanged',
        added_state_bytes=0,entries={n:dict(virtual_PC=f'{address(b,n):04X}',raw_A=3)for n in API},API=API,
        counts=dict(source_progression=432,inactive_emerging=60,invalid_slots=3,
                    stock_star_life=288,hosted_freeze_ticks=720,source_display_descriptors=288,
                    original_real_vector_cuts=2229,body_policy=256,real_native_X5_impulse_pairs=256,
                    real_deferred_score_life=96,new_helper_real_vector_cuts=153,
                    native_to_source_fractional_air_ticks=12),
        retained_negatives=[
            'Initial preassembly import-size failure: PowerUpType incorrectly declared absolute, real native ABI is zeropage0034. Exact bad source/builder/failure preserved; source import fixed before successful assembly.',
            'Original source/item controls passed5groups but vector observer rejected actual FfGraphicsBank PC B3CA normalNMI seam. Genuine11-byte macro is LDA DD/STA CurrentBankC/LDA DD/STA5116/RTS. Old observer recognized only pendingSTA; new observer additionally recognizes this exact original secondLDA site/rawRAM3/shadowDD. Cartridge unchanged, actualNMI map restoration and all143FF/33SMC/livepage1/R0R1/R6R7/RAMbanks assertions retained.'],
        remaining=[
            'No cart hooks, full Main, native emulator playback or new character admission. Router/forcedblank loader version+fingerprint must compose this exact image and genuinely route each callback.',
            'Typed graphics/body/impulse services require parent selected-active admission. Collect guards eligibility but actual native body/item collision must invoke it once; natural emerging-item collection remains untested.',
            'One owner must age/render native enemy flash2. Main source terrain afterhook, fullbody/effects/OAM fair admission, palette composition/music, climb/water/scroll/exit/death/P2 integration and CPU cadence remain open.',
            '60 logical freeze updates and current source-progression rules are verified hosted adaptations. This unused FFprototype was not a completed Crossover2.02 playable character; no invented authenticity claim.'],
        bindings=bindings)
    O.mkdir();out=O/'handoff.json';out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=True,handoff=str(out),sha256=sha(out),bindings=len(bindings),image_sha256=report['image_sha256'])))
