"""Freeze final CF-menu/P2/BT7 source composition with exact finite receipts."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2]
J=R/'build/bt-cf-coherent-source-1031-v1/joint';S=J.parent
C=R/'build/bt-cf-coherent-controls-1031-v1';B=R/'build/bt-lives-body-source-v7';BC=R/'build/bt-lives-body-controls-v3'
P=R/'build/bt-p2-cf-menu-source-1031-v2'
O=R/'docs/qa/checkpoints/2026-10-31/bt-cf-coherent-source-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,q):p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8',newline='\n')
def main():
 assert not O.exists();O.mkdir(parents=True);bindings={}
 inputs=[S/'source-stage.json',P/'source-stage.json',B/'source-stage.json',
  *[C/(n+'-controls.json')for n in['helper','callers','vectors']],
  *[C/(n+'-final-controls.json')for n in['bt','cf','menu']],C/'cf-parser/controls.json',
  *[BC/(n+'-controls.json')for n in['natural','pixels','vectors','callers','packet-timing']],
  R/'docs/qa/checkpoints/2026-10-31/contra-force-menu-admission-v2/handoff.json',
  R/'docs/qa/checkpoints/2026-10-31/contra-force-p1-linked-source-v1/handoff.json',
  R/'docs/qa/checkpoints/2026-10-31/bt-lives-body-source-v1/handoff.json']
 for p in inputs:
  q=json.loads(p.read_text());assert q.get('passed',q.get('source')),p
  for n,h in q['bindings'].items():assert sha(n)==h,(p,n);bindings[str(Path(n).resolve())]=h
  bindings[str(p.resolve())]=sha(p)
 assert sha(J/'candidate.nes')=='e538d2b809b1dac9b70a0a1b23a1b33b3d361297b25fac0b556d8eae5c7721ed'
 assert (J/'bt/cache.bin').read_bytes()==(B/'joint/bt/cache.bin').read_bytes()
 tools=['prepare_bt_cf_final_join_1031_v1.py','check_bt_p2_coherent_1031_v1.py','check_bt_cf_final_consumers_1031_v1.py',
  'prepare_bt_lives_body_1031_v6.py','prepare_bt_lives_body_1031_v7.py','check_bt_lives_body_1031_v3.py',
  'check_bt_lives_packet_timing_1031_v1.py','check_bt_lives_packet_timing_1031_v2.py','freeze_bt_cf_coherent_1031_v1.py']
 members=set(inputs+[R/'tools/audit'/n for n in tools]+[J/'candidate.cfg',P/'main-build.json',P/'candidate-link.json',P/'joint/src/characters.s',P/'joint/src/screen_render.s'])
 for base in [S,B]:members.update(base.glob('*.json'))
 members.update(p for p in (J/'bt').rglob('*')if p.suffix in['.s','.inc','.bin'])
 # Authoritative parent archives are dependencies, not duplicated payloads.
 members={p for p in members if p.suffix.lower()not in['.zip','.nes','.o','.exe']}
 entries={};archive=O/'source-and-controls.zip'
 with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for p in sorted(members):
   data=p.read_bytes();name=p.relative_to(R).as_posix();z.writestr(name,data);entries[name]=dict(sha256=hashlib.sha256(data).hexdigest(),bytes=len(data));bindings[str(p.resolve())]=sha(p)
 save(O/'archive-members.json',entries)
 (O/'owned-files.txt').write_text('\n'.join(sorted(p.relative_to(R).as_posix()for p in members if '/bt-cf-'in p.as_posix()or '/bt-lives-'in p.as_posix()or p.name in tools))+'\n',encoding='utf-8',newline='\n')
 (O/'README.md').write_text('''# Coherent CF/BT source candidate

Candidate `e538d2b809b1dac9b70a0a1b23a1b33b3d361297b25fac0b556d8eae5c7721ed` source-composes the genuine terminal CF-ready/P2 main producer with the exact BT7 cache and authenticated loader. The full source output equals the disjoint source-delta verification oracle; no binary patch produced the cart. Actual current main/CF/67/header/common bytes stay exact to the P2 parent, and BT code/cache/cookie stay exact to the independently native-tested b356 leaf. This packet makes no native or installation claim for the combined cart.

BT repairs retained: source graphics preparation at the real early DrawAll entry; own C3 empty descriptor for native post-shot reservation; authentic two-role body colors on the real lives-text continuation. The A1/Y30 black-lives-only packet now writes3F11 length7, including unchanged native3F14=0F between the two original body roles. Actual InitScreen selects UndergroundPaletteData, and all four native area tables also contain0F at3F04/14. The resulting full32 PPU palette bytes equal the earlier two-header packet, and actual normal-NMI screen-enable work saves88 CPU cycles. Normal BtColors remains unchanged. No3F00/10 late writes or sprite-coordinate edits were added.

The genuine21-byte P2 helper occupies the old status wrapper's48-byte padding. It preserves the native LDA behavior for every foreign raw/flag case and every non-header X, while only selected33/headerXFF bypasses the later LUIGI overwrite. Both source hunks are compiled by the terminal current main producer; no old main object was substituted.

Finite final controls:32768 helper ABI cases,640 actual BT P2 text calls,480 actual foreign text pairs,36 helper interrupt cuts,86 menu profiles/688 Start-A boundaries and74 source-ready profiles, four genuine BT cold/parser cohorts with160 visible Main updates, four genuine CF cold/parser cohorts with128 Main updates. BT7 additionally binds2560 actual text caller pairs,96 original source-pose pixel pairs,410 real graphics/lives vector seams, and exact normal-NMI timing/palette comparisons. No readiness, cache, support or HP was preloaded in the natural cohorts.

Root owns all native evidence and the eventual install decision. Its b356 leaf tests visually corrected the initial lives scroll glitch; earlier f0b7 color/invisible-body and9987 first-life deadline negatives remain immutable. The local v6 packet draft placed LDY after AND and would always choose Rash; it was rejected in source review before qualification, replaced by v7, and never used for native. The timing-v1 fixture left the screen disabled and therefore had no enable event; v2 executes genuine DisplayIntermediate before measuring. Earlier diagnostics remain in the preceding frozen packet.

Functional WIP exclusions remain: no full BT campaign or complete original special moves/music claim, no perfect donor-fidelity or60Hz claim, and no CF native qualification inferred from CPU-only cohorts. Installed current68 remains root-controlled.

Actual final recipe: `build/bt-cf-coherent-source-1031-v1/final-link.json`, config `joint/candidate.cfg`. Actual current main recipe: `build/bt-p2-cf-menu-source-1031-v2/main-build.json`; BT own source recipes are beside the final cart. Parent source archives are bound dependencies. The ZIP contains source/recipes/receipts/generated cache source assets, with no NES, EXE or object files.
''',encoding='utf-8',newline='\n')
 for p in[archive,O/'archive-members.json',O/'README.md',O/'owned-files.txt']:bindings[str(p.resolve())]=sha(p)
 save(O/'handoff.json',dict(passed=True,source=True,native=False,installed=False,candidate=sha(J/'candidate.nes'),
  true_main_parent='f428406a89b5d5d8fcf07db6bafe9955e0ba4059dfbd4267480484ce57f5d779',
  exact_BT_leaf='b356ae88e13ff319dc863ddc59df02edca879aeafc923e0d815c641830b3de91',
  actual_source_delta_oracle_equal=True,BT_cache_cookie_exact=True,current_CF67_common_main_preserved=True,
  source_ready=74,menu_profiles=86,combined_native_pending=True,
  finite_counts=dict(helper_ABI=32768,BT_P2_text=640,foreign_text=480,helper_vectors=36,Start_A=688,BT_cold=4,BT_visible_Main=160,CF_cold=4,CF_Main=128),
  BT_leaf_counts=dict(text=2560,source_pixels=96,vectors=410,normal_NMI_enable_CPU_saved=88),
  archive_members=len(entries),archive_bytes=archive.stat().st_size,bindings=bindings))
 print(json.dumps(dict(passed=True,handoff=str(O/'handoff.json'),sha256=sha(O/'handoff.json'),bindings=len(bindings),members=len(entries),archive_bytes=archive.stat().st_size)))
if __name__=='__main__':main()
