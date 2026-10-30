"""Freeze exact read-only epoch model and unlinked source sizing, no adoption."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_ff_joint_source_v1 as B
O=R/'build/ff-fx-epoch-model-qualified-v1'

def main():
    O.mkdir(exist_ok=False);files={Path(__file__)}
    receipts=[R/'build/ff-fx-epoch-oracle-v3/controls.json',
        R/'build/ff-fx-epoch-alias-proposal-v1/proposal.json',
        R/'build/ff-fx-epoch-workers-sizing-v3/sizing.json']
    for p in receipts:
        d=json.loads(p.read_text());assert d['passed'];files.add(p)
        for f,h in d['bindings'].items():assert B.sha(f)==h,f;files.add(Path(f))
    negatives=[R/'build/ff-fx-epoch-oracle-v1/negative-controls.json',
               R/'build/ff-fx-epoch-oracle-v2/negative-controls.json']
    for p in negatives:
        d=json.loads(p.read_text());assert not d['passed'];files.add(p)
        for f,h in d['bindings'].items():assert B.sha(f)==h,f;files.add(Path(f))
    for stem in ['ff-fx-epoch-workers-sizing-v1','ff-fx-epoch-workers-sizing-v2']:
        p=R/'build'/stem/'sizing.json';files.add(p)
        for f,h in json.loads(p.read_text())['bindings'].items():assert B.sha(f)==h,f;files.add(Path(f))
    files|={R/'tools/audit/prepare_ff_fx_epoch_cart_v1.py'}
    B.write(O/'README.md','''FF palette epoch model and unlinked source preparation only.

Frozen marker predecessor5c225bb9 and its actual source RAM3v6 remain unchanged.
No scheduler or new palette state has been installed, linked, or executed.

480 actual DrawAll plus normal-NMI fixtures produce native OAM/CHR/palettes.
The independent Python model chooses exact complete color families and verifies
every admitted opaque source index; it does not write emulated OAM/palette.
It preserves body0, native mixed Fireflower whole-object grouping, nativeP2/P3,
part order and maximum scanline load. Four areas, both facings, both optional
outline settings, mushroom/Koopa/mixed-flower scenes and ten fixed-class legal
render scenarios are covered. This is renderer setup, not controller-earned
combat or a native campaign. Existing64OAM/eight-sprite losses are not repaired.

Retained oracle negatives: v1 used an inappropriate deliberately poisoned API
seed with a non-four-aligned rotation; v2 incorrectly expected nativeP1 colors
for a mixed flower's actualP0 head. Corrected v3 keeps genuine Main seed and
each original mixed object's per-part palette. No product assertion weakened.

Actual current DBG-source references enumerate Packet07E0..07E6/Pending07EA,
Turn7FF8/Last7FFA/State7FF7/Control7FF9/bodyAck5FC8 and emitted instruction
spans. Alias reuse is proposed, not approved by this packet: existingTurn0..5,
Last80|family0..5, existing7B packet and80/C0 pending. BodyAck stays body-only;
RenderState stays0 under acquired FF. No new persistent or transient RAM.
The real InventoryInit clears mailbox aliases. Four actual TransposePlayers
cases preserve globalSelected22 and aliases; actual nextInitScreen resets the
display context. Frozen retirement/acquisition remains a prerequisite.

Unlinked corrected code actually assembles:98B ROM glue within explicit104B
retired-gate grant;480B RAM3 worker/data within exact593B granted holes.
Main208+heartbeat49 fitsBECF..<BFE0; classifier74 atA289; packet107 atB68B;
exact color vectors27 atA6E5; lookup tables15 atBFF0. Every compiler output
was checked by private_build_outputs_v1 before invocation.

Two earlier unlinked designs remain distinct negatives: v1 would have restored
the pre-native C bank through FwCallEnter; corrected ROM invokes nativeDrawAll
before entering RAM3 so its intentional C result survives. V2 declared actual
absoluteSmPosePtr6B06 as ZP; v3 copies that pair into borrowedR0/R1. Neither
faulty design was linked/executed. Genuine returnedAXYP andR0..7 are saved on
the CPU stack, with no source combat/target/rectangle/bodybuffer mutation.

The guarded source-cart builder is prepared but NOT run. It requires an exact
root alias receipt before installation. It will preserve every original
occupied source span/publicPC, replace only explicitly retired own104B gates,
existing18B native tail and ownrow29, and source-rebuild the existing8KB carrier
with a new full payload hash/cookie version7. No shared hook/lease/native run,
ready flag, Downloads update, simultaneous full-frame color parity or cadence
claim is made. Full queue/heartbeat/pause/skip/Main/foreign/ISR and loader proof
are still required on that eventual actual source cartridge.
''')
    files.add(O/'README.md')
    out=dict(passed=True,read_only_model_qualified=True,source_workers_unlinked=True,
        aliases_installed=False,source_scheduler_installed=False,native=False,admitted=False,
        oracle_cases=480,actual_alternating_player_cases=4,unlinked_ROM_bytes=98,unlinked_RAM3_bytes=480,
        parent_sha256=B.sha(R/'build/ff-fx-world-marker-proposal-v2/joint/candidate.nes'),
        receipts={str(p.resolve()):B.sha(p)for p in receipts},
        retained_oracle_negatives={str(p.resolve()):B.sha(p)for p in negatives},
        limits=['No actual scheduler execution/alias adoption; root exact alias grant needed.',
                'No new sourcecart qualification, native/campaign/readiness/timing proof.'],
        bindings={str(f.resolve()):B.sha(f)for f in sorted(files)})
    B.save(O/'handoff.json',out)
    print(json.dumps(dict(path=str(O/'handoff.json'),sha256=B.sha(O/'handoff.json'),bindings=len(files))),flush=True)

if __name__=='__main__':main()
