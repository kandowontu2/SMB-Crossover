"""Compact immutable review map for the unadmitted mixed-render component."""
from pathlib import Path
import difflib,hashlib,json,re,sys
import prepare_dragon_power_mixed_render_v3 as P
import dragon_power_mixed_render_controls_v3 as C

R=P.R;O=P.OUT
def main():
    target=O/'handoff.json';assert not target.exists()
    checks=json.loads((O/'controls-v3.json').read_text());build=json.loads((O/'build-proof.json').read_text())
    assert checks['passed']and build['passed']
    for proof in[checks,build]:assert all(P.sha(p)==h for p,h in proof['bindings'].items())
    new=C.bundle(O);old=C.bundle(P.OLD)
    deps=[]
    for line in (O/'component.dbg').read_text().splitlines():
        if line.startswith('file\t'):
            p=Path(re.search(r'name="([^"]+)"',line)[1]);p=p if p.is_absolute()else R/p
            assert p.exists();deps.append(p.resolve())
    assert len(deps)==10
    # Exact generated wrapper addresses and real parent physical owners. These
    # remain two genuine DBG files; the sparse candidate has no invented DBG.
    callbacks={}
    for n,bank in[('X5SetPhysicalChr',62),('MetaspriteRenderLoop',4),('X5PublishChr',62),('DrawMetasprite',4),('FloateyNumberRender',4)]:
        actualbank=(C.location(C.PARENT,n)-16)//8192;assert actualbank==bank
        at=C.address(C.PARENT,n);off=C.location(C.PARENT,n)
        callbacks[n]=dict(bank=bank,PC=at,first12bytes=C.BASE[off:off+12].hex())
    # One small textual patch; art recipe+complete private leaves are exact.
    patch=''.join(difflib.unified_diff((R/'src/dragon_power_render.s').read_text().splitlines(True),(O/'dragon_power_render_mixed.s').read_text().splitlines(True),fromfile='a/src/dragon_power_render.s',tofile='b/PRIVATE/dragon_power_render_mixed.s'))
    patch+='\n; NEW appended core leaf (include after original dragon_power_contact.s)\n'+(O/'dragon_power_mixed_tail.inc').read_text()
    (O/'source.patch').write_text(patch)
    report=R/'docs/qa/dragon-power-mixed-render-2026-10-28.txt'
    report.write_text('''Goku mixed body/wave source component — private, not playable

Authority: original USA Dragon Power ROM e52cc421..., original frozen
component85029e7... and audio3aafbed... remain unchanged. Parent is immutable
d52eeefe; f56a is not retagged. No shared source, menu, settings, ROM install,
new RAM/allocation, native emulator or screenshot was changed/launched.

The frozen renderer independently selected wave pages3/4 at sprite window0,
which could invalidate a simultaneously displayed body. New packing puts the
four authentic left/right wave patterns at common pair indices0..3 on EVERY
body page. All original body patterns, source palette classes, part order,
geometry and two facings are retained. Seven1KB pages use32/31/30/32/27/32/23
pairs; the eighth page is unused. ART remains1263B; original six palette bytes
36/26/04,30/36/0F remain exact. This is not a side-window allocation or a
concatenation that leaves body and wave on disjoint active pages.

Same-size LDA DpPosePage,X at86:B672 becomes JSR DpMixedPage. The new34B
helper is86:B819..<B83B. All987 old Dp symbols (PC/RAM/art) stay exact.
CORE4155/6144 leaves1989B; ART1263/4096 leaves2833B. Audio is untouched.
The helper uses existing DpRenderIndex to restore X; no borrowed RAM/stack
indexing hack. Ordinary body full-caller delta is+17CPU; wave+42..43CPU in
the measured valid-pose cases, including routing. Foreign paths are0delta.
These are CPU arenas, not a native frame cadence or performance result.

Finite executable controls on the exact private component:
-66 authentic original-executable pixel-class/geometry records; both wave
 records are decoded correctly on all seven pages.
-256 complete body/wave combinations, all32poses/bothfaces/both wave
 directions, in both draw orders, using the final published body page.
-6336 strict old/new complete draw caller comparisons with all other AXYP,
 SP, application RAM, ordered writes, mapper and whole SMC exact. Named
 pointer/page/tile representation changes are independently asserted from
 actual descriptors/patterns; they are not broad state or flag masks.
-256 all64physical-flag caller cases;8 invalid-body/live-wave cases;
224 nonplain shot states retain exact old behavior and cycles.
-594 actual native renderer whole-record capacity rejections, including
 logical sum256 and rotated physical wrap; no partial writes/advance.
-160 actual native Goomba+score caller mixes, four areas/both outlines,
 decoding actual5130/5120..2B stores: all11 nonbody windows and native glyph
 patterns stay exact. Native C12 art owner is explicit typed caller setup;
 current raw24 shared dispatch is NOT being claimed implemented.
-2040 foreign caller cases, all other255 raw IDs, state/writes/cycles exact.
-966 real parent IRQ instruction seams: sixflags/AXY/SP/PC/live stack/ZP,
 overlay/mapper/entire SMC restored. Actual IRQ2006/2005 protocol checked
 literally; MMIO is not misclassified as application RAM. No regular NMI
 or unimplemented Goku audio/publication integration is claimed.

Retained negatives: provisional inline v2 shifted old entries and added one
foreign rejection cycle; never accepted. Initial absolute/relative include
errors and two bank-metadata fixture errors are retained compactly. Initial
IRQ fixture compared actual2006=128 side effect to no-IRQ latch0; corrected
oracle requires exact native four-write protocol, not a game/guard change.
All original source/component/CHR remain byteexact.

Concrete NEXT HOST CALLER GATE (not silently fixed or waived): actual
DrawAllMetasprites::RosterShots reads SmPosePtr's header immediately after
KbDrawDispatch. Original DpDrawShots returns the wave pointer (two parts),
while body records can require12parts/48B. Host admission must preserve or
reselect the actual body pointer BEFORE that reservation consumer and before
the actual player dynamic-pointer draw; include hidden body/capacity cases.
The new wave page choice is compatible with either draw order but does not
by itself repair that unimplemented raw24 host adapter. Source body matching
does not prove scanline fairness, actual palette colors, block/enemy HP/score
integration, atomic audio, or a playable/native Goku campaign.

Phase1 hook/attack/audio proposal remains frozen at
docs/qa/dragon-power-host-integration-plan-2026-10-28.json (a542fc2e...).
No implementation of those shared hooks, enemy/block stats, or cue queue
was authorized by this render-only unit. Complete host fit is still open.
''',encoding='utf-8')
    generated=[p for p in O.iterdir()if p.is_file()]+[report]
    originals=[R/'src'/n for n in['dragon_power.s','dragon_power_state.inc','dragon_power_native.inc','dragon_power_host.s','dragon_power_render.s','dragon_power_contact.s','dragon_power_art.inc','dragon_power_audio.s','dragon_power_audio_native.inc']]+[R/'chr/characters/dragon-power.chr',P.OLD/'handoff.json',R/'build/dragon-power-audio-v1/handoff.json']
    tools=[R/'tools'/n for n in['prepare_dragon_power_mixed_render_v2.py','dragon_power_mixed_render_controls_v2.py','prepare_dragon_power_mixed_render_v3.py','dragon_power_mixed_render_controls_v3.py','prepare_dragon_power_mixed_handoff_v1.py']]
    imported=[]
    for module in list(sys.modules.values()):
        name=getattr(module,'__file__',None)
        if name and Path(name).suffix=='.py'and Path(name).exists():
            p=Path(name).resolve()
            if str(R).lower()in str(p).lower()or 'py65'in str(p).lower():imported.append(p)
    files=set(deps+generated+originals+tools+imported+[P.PARENT.with_suffix(e)for e in['.nes','.dbg','.lbl']])
    files.update(Path(p)for proof in[checks,build]for p in proof['bindings'])
    for f in['controls-v1.json','controls-v2.json','controls-v3.json','build-proof.json','prepare-first-include-negative.py','component-first-include-negative.s','art-first-include-negative.inc','build-failure.txt','controls-first-fixture-negative.py','controls-second-fixture-negative.py','controls-foreign-cycle-negative.py']:
        p=R/'build/dragon-power-mixed-render-v2'/f
        if p.exists():files.add(p)
    manifest={str(p.resolve()):P.sha(p)for p in sorted(files)}
    assert all(P.sha(p)==h for p,h in manifest.items())
    handoff=dict(status='FROZEN_PRIVATE_MIXED_RENDER_SOURCE_COMPONENT_NOT_PLAYABLE_NO_NATIVE',parent=P.binding(P.PARENT.with_suffix('.nes')),
                 phase1_plan=P.binding(R/'docs/qa/dragon-power-host-integration-plan-2026-10-28.json'),candidate=P.binding(O/'candidate.nes'),
                 core=P.binding(O/'component.bin'),art=P.binding(O/'art.bin'),CHR=P.binding(O/'chr.bin'),component_DBG=P.binding(O/'component.dbg'),parent_DBG=P.binding(P.PARENT.with_suffix('.dbg')),
                 actual_component_ASM_dependencies={str(p):P.sha(p)for p in deps},actual_parent_callback_bindings=callbacks,
                 controls=P.binding(O/'controls-v3.json'),report=P.binding(report),source_patch=P.binding(O/'source.patch'),
                 sizes=dict(CORE=4155,CORE_free=1989,ART=1263,ART_free=2833,CHR=8192,used_pages=7),
                 old_public_Dp_symbols_exact=987,old_code_change=[0xb672,0xb675],appended_genuine_helper=[0xb819,0xb83b],
                 binding_count=len(manifest),bindings=manifest,
                 review_owned_paths=[str(p.relative_to(R)).replace('\\','/')for p in tools]+[str(report.relative_to(R)).replace('\\','/')],
                 next_host_gate='Preserve/reselect actual body SmPosePtr after shot draw before RosterShots dynamic body reservation; no shared Goku admission exists yet.',
                 no_native_launch=True,no_shared_source_edits=True,frozen_originals_unchanged=True,
                 current_limits=checks['limits'])
    target.write_text(json.dumps(handoff,indent=2)+'\n');print(json.dumps(dict(handoff=P.binding(target),bindings=len(manifest),ASM_dependencies=len(deps),candidate=handoff['candidate']),indent=2))

if __name__=='__main__':main()
