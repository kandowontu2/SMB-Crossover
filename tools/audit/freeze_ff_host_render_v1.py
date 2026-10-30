"""Freeze native-format full FX renderer; retain timing and hook limitations."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_host_render_controls_v4 as T
from check_tmnt_render_oa import address
C=T.C;sha=C.sha
P=T.P;O=R/'build/final-fantasy-host-render-qualified-v1'


if __name__=='__main__':
    assert not O.exists()
    paths=[P/'build-proof.json',T.O/'controls.json',
        R/'build/final-fantasy-host-render-fast-controls-v3/controls.json',
        R/'build/final-fantasy-host-render-native-budget-v1/controls.json',
        R/'build/final-fantasy-host-render-overload-v2/controls.json']
    paths += [R/f'build/final-fantasy-host-render-controls-v{i}/controls.json'for i in range(1,7)]
    paths += [R/f'build/final-fantasy-host-render-fast-controls-v{i}/controls.json'for i in [1,2]]
    paths += [R/'build/final-fantasy-host-render-overload-v1/controls.json']
    bindings={};proofs=[]
    for p in paths:
        j=json.loads(p.read_text());proofs.append(j)
        for n,d in j['bindings'].items():
            assert sha(n)==d,n
            assert bindings.get(n,d)==d,n
            bindings[n]=d
        bindings[str(p.resolve())]=sha(p)
    assert all(j['passed']for j in proofs[:5])
    assert not proofs[5]['passed']and proofs[-1]['observed_visible_parts']==33
    assert not proofs[-1]['passed']and len(proofs[-1]['never_seen_source_parts'])==11
    assert proofs[4]['source_visible_parts']==proofs[4]['observed_visible_parts']==44
    for version in [1,2,6]:
        for p in (R/f'build/final-fantasy-host-render-v{version}').iterdir():
            if p.is_file():bindings[str(p.resolve())]=sha(p)
    bindings[str(Path(__file__).resolve())]=sha(__file__)
    for p,d in bindings.items():assert sha(p)==d,p
    h=proofs[0];b=C.bundle(P)
    assert sha(P/'ram3.bin')=='c22aad37d582041d757bdde88058aad18649ce48f7f3c55f43bbc5f9f1c74e30'
    report=dict(passed=True,status='PRIVATE_FF_FULL_CHUNK_RENDER_SOURCE_CPU_PASS_MAIN_PALETTE_TIMING_PENDING',
        image=str((P/'ram3.bin').resolve()),image_sha256=sha(P/'ram3.bin'),
        native=False,full_Main=False,loader=False,shared_or_Downloads_changed=False,
        code_bytes=h['host_render_bytes'],code_span='RAM3 A300..<A6E3',
        fx_index_bytes=h['fx_index_bytes'],source_predecoded_FX_bytes=h['fx_predecoded_bytes'],
        storage='Original CORE3211/publisher20/combat492/terrain583/pickups399/ART3410/CHR32768 exact. New data occupy only proven unused FF-exclusive RAM3 holes A000,A700,A800,A874,BCEF, below BFE0 cookie; no new PRG/CHR/global-RAM lease.',
        adapter_state='Existing three FF projectile record reserved2/3 are chunk/part cursors; real allocation/area reset clears them. Part cursor advances once per complete chunk cycle. Existing RgDrawRemaining is leased only during selectedFF earlydraw as220 minus actual SmPosePtr body0 byteheader, then native owners may reuse it. Combat output scratch reused during draw; no extra game-RAM addresses.',
        entries={n:dict(virtual_PC=f'{address(b,n):04X}',raw_A=3)for n in ['FfHostDrawShots','FfHostRenderChunk','FfHostCompact']},
        API=dict(
            FfHostDrawShots='Public selected22 early native weapon-draw callback. Requires verified RAM3 cookie and actual preceding FfHostGraphics. Parent calls exactlyonce before native body/world reservation and bypasses duplicate legacyFFshots. Emits source bodychunks>=1 only when ShadowsOn, plus all live spellchunks in three1KB physical windows1/2/3; bodywindow0 restored. Source body0 descriptor regenerated after effects, callerC restored. No movement/weapon/action tick. DefaultShadowsOff+noeffects fastpath only publishes actualbody0 physicalCHR.',
            FfHostRenderChunk='Typed own internal descriptor/R4..R7 draw. Compact exact native-valid X and Y>=HUD32, apply actual remaining native OAM capacity, rotate complete source subsets on overload and call genuine physicalA4 MetaspriteRenderLoop through native FarCallCommon. Borrowed RgDrawRemaining must already contain native-compatible bound.',
            FfHostCompact='Internal native-format descriptor compactor. Accepted tile/attribute/relativeXY bytes unchanged; rejects native-offscreen X/wordY and OAMY<31 or>=240. Not a second gameplay collision engine.'),
        checks=dict(native_source_chunks=4224,genuine_native_draw_calls=1548,
                    four_class_draws=240,foreign_guards=34,predecoded_source_pairs=1056,
                    source_chunk_origin_cull_cases=11264,whole_chunks_rejected=2830,
                    optional_body_chunks=432,actual_native_reservation_blocks=1296,
                    actual_source_weapon_ticks=24,actual_full_callback_vector_cuts=528,
                    minimum_real_ISR_SP=184,overload_stress_draws=100,
                    overload_visible_parts_expected_and_seen=44),
        measured_callback_CPU=proofs[1]['checks']['full_draw']['measured_callback_CPU'],
        retained_negatives=[
            'Preassembly native-bank export size, missing original scratch exports and ld65 fixed-segment ordering failures retained with exact failed source/builders/configs. No linked images/admission claimed for these attempts.',
            'Initial OAM model forgot that native wordY includes highpage1; source/native emitter agreed, model was corrected by subtracting256 and validating all actual64records/physicalbank-qualified worker calls.',
            'Actual overload v8 starved11of44 visible Bolt parts during100one-record-pressure draws because chunk/part cursor periods shared factors. Source v9 advances part cursor once per full chunk cycle; unchangedstress fixture observes44/44. Original failure retained.',
            'Initial fixed64B body reservation was conservative but inaccurate. Actual native RosterProjectileOamReady reads SmPosePtr header;1296true native block executions prove source headers16/20/24/28/32. Final220-header budget retains32B world and252B nonwrapping end.'],
        remaining=[
            'No assembled Main/cart hook or native emulator admission for this exact image. Loader must compose new payload/cookie fingerprint; actual FF earlydraw route/native body0 pipeline and real PPU publication still need integration.',
            'Heavy spells remain expensive (see exact callbackCPU). Emptydefault149CPU is not a wholeframe or60Hz claim; three-spell pool stress is synthetic and source prepare/cast timing is not bypassed in real gameplay.',
            'Parent owns palettes/world actor color sharing, SFX/audio/music, native body/effect scanline fairness and visual review. CHR metadata/OAM source equivalence alone does not prove hardware screenshots.',
            'Body/feet/postBG, flash aging/render, NewEnemy lifecycle, all source class powerups, natural1-1/Hard/P2 and scene/admission remain goal work.'],
        bindings=bindings)
    O.mkdir();p=O/'handoff.json';p.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=True,handoff=str(p),sha256=sha(p),bindings=len(bindings),image_sha256=report['image_sha256'])))
