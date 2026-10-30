"""Freeze the real terrain consumer and its explicit uninstalled-route limits."""
from pathlib import Path
import json
from checkpoint_roster_progress_1030_v2 import R,sha

O=R/'build/final-fantasy-host-terrain-qualified-v1'


if __name__=='__main__':
    assert not O.exists()
    paths=[R/'build/final-fantasy-host-terrain-v3/build-proof.json',
           R/'build/final-fantasy-host-terrain-controls-v2/controls.json',
           R/'build/final-fantasy-host-terrain-nativebg-v2/controls.json',
           R/'build/final-fantasy-host-terrain-vectors-v1/controls.json',
           R/'build/final-fantasy-host-terrain-controls-v1/controls.json',
           R/'build/final-fantasy-host-terrain-nativebg-v1/controls.json']
    bindings={};proofs=[]
    for p in paths:
        j=json.loads(p.read_text());proofs.append(j)
        for name,digest in j['bindings'].items():
            assert sha(name)==digest,name
            assert name not in bindings or bindings[name]==digest,name
            bindings[name]=digest
        bindings[str(p)]=sha(p)
    assert all(j['passed']for j in proofs[:4])
    assert proofs[4]['passed'] and not proofs[5]['passed']
    assert 'native BG ceiling displaced X' in proofs[5]['failure']['error']
    extra=[Path(__file__).resolve(),R/'tools/audit/ff_host_terrain_controls_v1.py',
           R/'tools/reference/final_fantasy_host_terrain_v2.patch']
    extra+=list((R/'build/final-fantasy-host-terrain-v1').iterdir())
    for p in extra:
        if p.is_file():bindings[str(p.resolve())]=sha(p)
    for p,d in bindings.items():assert sha(p)==d,p
    image=R/'build/final-fantasy-host-terrain-v3/ram3.bin'
    assert sha(image)=='ce492733d0931f8991eb13e36339b00eb4166b7f0e493d4f1b4b2c80fe9bf27e'
    report=dict(passed=True,status='PRIVATE_FF_TERRAIN_SOURCE_CPU_PASS_ACTUAL_CART_HOOKS_PENDING',
        native=False,full_Main=False,loader=False,shared_or_Downloads_changed=False,
        image=str(image),image_sha256=sha(image),host_terrain_bytes=583,
        source_span='rawRAM3 B900..<BB47; combat B700..<B8EC and original CORE/publisher/ART/CHR unchanged',
        added_state_bytes=0,temporal_scratch='First8 pre-existing FfRenderBuffer bytes are owned only from Movement through AfterTerrain. Complete genuine RenderChunk must overwrite the descriptor before drawing; no NMI consumer may read it as a descriptor during terrain.',
        API=dict(
            FfHostMovement='Actual selected22 logical movement wrapper. Ensure actual lifecycle, retain pre-moveY in temporary render scratch, clear terrainflags, run genuine FfMovement; C remains source move/climb handoff. Parent must retain real climb path on Cclear. Foreign path is genuine FfMovement only.',
            FfHostAdder='Typed ordinary FF BG profile; Y0/Cset. Actual local indices head0,feet1/2,sides3..6.',
            FfHostHeadWithin='Typed native head cutoff; A/Y input irrelevant, actual RgCrouch selects source top6or17. Carry admits source head>=32 without wrap. Native BG caller has already validated Yhigh1.',
            FfHostHead='Typed actual head query,Yprofile0. Center then source left/right sample as necessary. Returns Ametatile,X0,Yoriginal, actualR2/R3/R6/R7 cell. R0/R1 and Local_eb preserved. Only actual upward solid-cell crossing commits resolvedY before native side probes; sets R4=4 to retain native effects. Post adapter restores same resolution after native effects.',
            FfHostFeet='Typed first/second native foot call Y0/1; returns Y1/2 with source X+1/+14,Y+32 cell, R4 genuine penetration. R0/R1 and Local_eb preserved.',
            FfHostSide='Typed native queryY3..6 and R0left2/right1. Real source width1..<15 and top6or17/bottom32, actual page carry, R4native origin nibble. Player coordinates never used as temporary query proxies.',
            FfHostWall='Typed actual native wall response for previously returned cell tuple and FfTerrainPage; R0left2/right1. Resolves exact world edge, clears source/native horizontal velocity/fractions/scroll, native collisionbits and SideCollisionTimer16; Cset.',
            FfHostAfterTerrain='Must run after genuine PlayerBGCollision/effects and before enemy-contact/rendering. Applies saved source ceilingY after native effects or imports genuine ground state, clears vertical residuals, resets scratch flag, refreshes exact source body box. R0/R1 unchanged.',
            FfHostBox='Typed selected FF body box; native inclusive representation of actual source half-open [1,15)x[6or17,32). Real16bit camera projection/clips, no wrapped screen edge. A/X/Y/flags volatile, X/Y0 on return. Stomp policy/any genuine Easy-foot overlay remain parent-owned.'),
        counts=dict(queries=4752,source_bound_boxes=720,ceiling_crossings=378,
                    wall_world_pages=16,real_native_block_item_writers=24,
                    actual_native_BG_driver_cases=24,real_vector_cuts=1941,
                    source_bytes_preserved_per_ISR=143),
        retained_failure='First581B version passed point/response leaves but complete actual BG staged-route fixture displaced X112to127: ceiling correction was deferred until after the native upper-side check. Source successor adds exactly one2B STA Player_Y_Position after the real queried-cell crossing; native block and emerging-item origins remain exact. Local_eb import-address-size negative is also retained.',
        remaining=['Entries except Movement are typed own-active services, not foreign/pause dispatch gates. Parent router must admit only selected22/engine8/unpaused/TimerControl0/notdead. Native automatic4/5 and other engine handoffs remain native.',
                   'Complete native BG executed through explicitly staged selector substitutions using genuine FarCallCommon; no assembled cart hook, full Main, natural item pickup or native emulator claim.',
                   'Parent still owns actual hook routes, final loader image/fingerprint, climb/water/scroll/end-sequence integration, stomp/body contact, palettes/full body/effects/music, pickup/death/lifecycle and P2 semantics.',
                   'Cycle budget/per-frame cadence not qualified. Original API calls and source render descriptor must be sequenced correctly; no new RAM lease was made.'],
        bindings=bindings)
    O.mkdir();(O/'handoff.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(handoff=str(O/'handoff.json'),sha256=sha(O/'handoff.json'),bindings=len(bindings))))
