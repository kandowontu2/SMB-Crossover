"""Record the admitted GO source changes and current route evidence without promotion."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())


def main():
    cp=R/'build/checkpoints/weapons-source-go/manifest.json';j=read(cp)
    assert all(sha(R/f'build/smb-crossover-{m}.nes')==h for m,h in j['ROMs'].items())
    for n,h in j['source_overlay'].items():assert sha(R/n)==h
    routes=V/'roster-current-gu/summary.json';assert read(routes)['failed']==12
    proofs={}
    for tag,base in [('bass-1-2-overhang-gq','winning'),('bass-1-2-ledge-gs','winning'),('bass-1-2-gaps-gv','best'),('bass-1-2-pipe-entry-gw','best')]:
        p=R/'build/roster-through-2-2/search'/tag/'manifest.json';z=read(p)
        assert z[base+'_reusable_root']['verified_coldboot']
        proofs[tag]=dict(manifest_sha256=sha(p),basename=base,root=z[base+'_reusable_root'])
    sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
    used=workspace_bytes(R);assert used<100000000000
    out=V/'root-current49-progress-gx.json';assert not out.exists()
    report=dict(status='ARM_RUSH_LAND_SOURCE_REPAIRS_AND_MMC3_AUDIO_OPTIMIZATION_ADMITTED_ROSTER_RETIMING_ACTIVE',utc=datetime.now(timezone.utc).isoformat(),previous_progress='build/verification/root-current49-progress-gd.json',previous_progress_sha256=sha(V/'root-current49-progress-gd.json'),checkpoint=cp.relative_to(R).as_posix(),checkpoint_sha256=sha(cp),ROMs=j['ROMs'],report='docs/qa/arm-rush-source-2026-10-22.md',report_sha256=sha(R/'docs/qa/arm-rush-source-2026-10-22.md'),verification=j['verification'],additional_route_matrix_sha256=sha(routes),branch_proofs=proofs,workspace_bytes=used,workspace_cap=100000000000,all_lossless_and_negatives_retained=True,root_native_handles=[],goal_status='active',goal_complete=False,
        previous_goal_turn_classification='progress: latest Cheats request verified on both GA ROMs with four fresh native checks and documented controls; feature already installed',
        current_goal_turn_classification='progress: admitted seven-file additive source repair on both mappers with four builds/literal baselines, source rules/250 exact foreground callers, twelve Land groups/516 exact audio callers/462 attained IRQs,48 matched quiet audio profiles,26 scoped native regressions; current Rygar full clear reconfirmed; twelve other old tapes rejected by fresh transfer matrix; Bass new controller prefix independently advances through1-2 to exitpipe',
        next=[
            'Main is GO, byte-identical reviewed private GF. Do not reapply old L wholesale. New helpers megaman_super_arm/rush/rush_land and megaman_audio/guest_audio/special_weapons/entrypoint only. All GA/HUD/Water/terrain/cannon/firebar/score/cheats/Sophia fixes retained. Old global nonempty PCs and RAM unchanged; zero-length DPCM marker shifts samebank12. SPECIAL_ROSTER spare76/82; SRAM total unchanged52 aliases use old audio slab padding.',
            'Source rules: free Arm lift/carry/cancel, pay8 actualthrow, stock/Star guards. Rush4-unit/free summon, activeRush ordinaryBuster/sharedlimit,12-unitclamped bounce+sourcejumpflags and nativeLand. Main broad Bass fixture has exactly two independently source-backed payment expectation edits. Original fixture remains in GF source/tests and prior packet.',
            'Quiet AudioUpdate matched48 calls: MMC3 saves474 MM3 /322 MM2 cycles; MMC5 adds42 Land-hook cycles. Registers/ports/mapper/liveRAM equal,24 popped-stack differences individually traced. No universal lag-solved claim. Land512? actual516 calls and462 attainedIRQs,250 mechanics callers; authored setups/source semantics, not natural full arsenal.',
            'Rygar GO fresh replay root-rygar-weapon-gm-7-v0-mmc3 clears all6 through2-2 withzero deaths/control2-3; no new recording. Corrected GA QA/lossless video retained as GA, do not relabel GO without actual current recording.',
            'Current GO legacy transfer audit roster-current-gu completed12/12 failures: eleven1-1 deaths andLuigi1-2 life loss. PlusBass oldtape fails2251 onbothGA/GF withallcapturedCSVs literal. These are tape transfer failures, not claims of inability/crash. README now ties older fullgreen/14film claims to oldcheckpoint. Need new routes, current final recordings and complete weapon/Hard/allitem/shortcut obligations.',
            'Bass Easy new guide retime-movie-dg-9-0 clears1-1, then GQ winning6378 X1025/Y176, GS winning7487 X1825/Y176, GV best8599 X2673/Y96 power1; all independently coldboot/all10240RAM verified. GV root andbestinputs are best current start. GP stuck849, GR stuck1626 tilltimerdeath, GT gapdeath8503 retained. GS/GQ resolve these earlier segments.',
            'Bass exitpipe screenshot GV best.png showsplayer atop horizontalpipe lip (Y96) beside tall pipe. GW reusedGVroot8599 and attemptedgoalX2660/Y128 withlanding score; failed360trials, best8615 X2658/Y96 independentlyverified. Need native sidepipe height/approach audit, retreatfar enough to drop beneath lip; do not repeat same incompatible goal blindly. Use opaque verifiedroot reuse (basenamebest) and source physical entry condition, not RAM patches.',
            'Remaining actual code work still includes private RyuF climb/overlap repair and shared face/worldpalette conflict Bass/Link/Simon/Samus/MM. Restore only provenunused palettes; no blind global palette3. Check original source obtainable arrays: MagmaBazooka/RushJet/Marine appear insharedcode/icons but absentMM/Bass2.02OBTAINABLE arrays, so not automatically missing obtainable upgrades.',
            'All root sessions terminal. No agents restarted (old specialists quota-failed). Goal active; no blocker. Current README/doc edits after GO checkpoint are intentional factual scope corrections; code still matches GO overlay hashes. Continue from actual source and proofs, preserve all media under100GB.'
        ])
    # Correct prose typo before writing the sole authoritative successor.
    report['next']=[s.replace('Land512? actual516','Land actual516')for s in report['next']]
    out.write_text(json.dumps(report,indent=2)+'\n');print(out);print('workspace',used,flush=True)


if __name__=='__main__':main()
