"""Compact current source/receipts only; no ROM, DBG, assets or capture tree."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2];O=R/'build/prince-actor-1101-v1'


def main():
 frozen=O/'source-supplement-v2.zip';assert hashlib.sha256(frozen.read_bytes()).hexdigest()=='6d87bd3852b0282af330584fbf89ef4672aba61ac032cba63b2756285c671472'
 with zipfile.ZipFile(frozen)as z:
  prior=json.loads((O/'source-supplement-v2-manifest.json').read_text())['explicit_commit_files']
  for name in prior:assert(R/name).read_bytes()==z.read(name),('Frozen source changed',name)
 grant=R/'docs/qa/allocations/prince-cold-packet-1102-v19.json';proof=O/'cold-worker-CPU-v19.json';q=json.loads(proof.read_text());assert q['passed']and all(q['cold_packet_execution_checked'].values())
 g=dict(granted=True,date='2026-11-02',owner='Prince cold uninitialized exclusive RAM2',base_ROM_SHA256=q['base_ROM_SHA256'],parent='docs/qa/allocations/prince-executable-state-1102-v15.json',root_approval='Root conditionally accepted cold-only C200..C235 execution while uninitialized, forcedblank, SEI and both headers invalid; asked to document/check conditions and overwrite before live.',cold_only_additional_execution_half_open=[0xc200,0xc235],context=dict(worker_half_open=[0xc100,0xc259],decoder_half_open=[0xc000,0xc0fe],boot_half_open=[0xd25e,0xd2bf]),conditions=['Only before original actor initialization, with actual rendering disabled, SEI and both authentication commit bytes invalid.','Private boot rejects wrong rawID, live ready/actor marker, enabled rendering, enabled NMI work, clear I or either published header.','Last state decode replaces the temporary code; finalizer zeros all53 packet bytes before the original constructor and ready publication.','Both full owner headers remain unpublished until resident code has verified/copy-qualified all source images.','No new global RAM, shared loader/manager/descriptor/routing/menu or ROM mutation approval.','Final composition must carry current installed f5c and later root-approved disjoint successors after Bub stabilizes.'],proof=dict(boot_guards=len(q['cold_guard_rejections']),independent_corruption_rejections=len(q['corruption_fail_closed']),CPU=q['positive']['CPU'],actual_original_constructor_calls=1,headers_unpublished=True,all_packet_bytes_zero_before_live=True),bindings={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [proof,R/'tools/reference/prince_cold_worker_1102_v19.s',R/'tools/audit/prepare_prince_cold_worker_1102_v19.py',R/'tools/audit/check_prince_cold_worker_1102_v19.py']})
 grant.write_text(json.dumps(g,indent=2)+'\n')
 doc=R/'docs/qa/prince-native-binding-1102-v19.md';doc.write_text('''# Prince private native binding, November 2

Current: 43 physical carriers and conditional RAM2/RAM3 are granted. The exact
source-dead executable-state spans and cold-only packet interval are recorded in
`allocations/prince-executable-state-1102-v15.json` and
`allocations/prince-cold-packet-1102-v19.json`. Prince is not menu-admitted,
native-emulator qualified or installed. No helper has been placed or qualified.
Installed f5c and the eventual stable Bub successor must be retained on compose;
the component CPU proofs below bind1966 and are not a cumulative release ROM.

The actual original actor/script/control/fall/landing/ledge-climb roots now call
compiled native terrain, geometry and exports with no fixture callback stubs.
Original phases remain separate Main epochs: advance/projection, empty, controls,
then fall/contact. The native Main FrameCounter, owner identity, ready marker,
normal engine and pause state gate updates. Geometry retains original32x64 room
cells and visual+16 X origin; native position/render bindings use the proven
77-pixel vertical origin. Movement uses original programs rather than Mario
physics. Flat walking and16/32/48/64-pixel Up-climb fixtures pass; running A-only
32-pixel pipe remains a preserved negative. These are CPU rooms, not native
crossing or full1-1 proof.

All93 original programs/two facings plus controlled pipe sequences compare
4,729 actor-live continuations against actual original audio callers. The WIP
records original sound/music events quietly; it does not play original audio.
All256 music return A/X/Y/P cases match. Native scroll samples are bounded to
the parser's units while original world X remains exact. Explicit X=0 at the
public player update removes dependence on the caller's actor slot. The final
service image passes192 ingress register/flag cases,67 owner/scene/pause/ready
rejections,520 epoch advances plus520 duplicate rejects and two epoch wraps.
632 service/FarCallCommon IRQ/lag-NMI cuts supplement826 renderer cuts; no ISR
writes RAM2/3, including same-value writes. Original running then falling enters
the real native KillPlayer after104 updates, engine11/lives2. Respawn/Main life
progression is still unqualified.

Physical backing is43,918/44,032 bytes, with114 bytes remaining before additional
public callbacks. Runtime is A000..BFDF,8,159/8,160 bytes; state-code is restored
to C0B0..C60F, compact pose metadata C800..DB9A and services DB9A..DCC5. The cold
bootstrap descriptor is8 bytes for owned carriers617/619. A254-byte checked
decoder and442-byte boot/worker stage all scattered bytes, independently reread
them, decode runtime then metadata then state, and enter the actual source
constructor. It takes7,110,705 CPU cycles and24,328 buffered PPU reads. Nine
cold guard and four corruption cases fail closed. Both headers remain invalid.
The isolated fixture supplies the two common-worker bootstrap rows as declared
input; it does not claim an implemented shared cold route.

The measured third-owner manager proposal retains every existing531-byte
manager label/address and needs120 additional resident bytes, including its
16-byte cookie, plus8 descriptor bytes. Prince public row routing and warm
scene reset are not yet included. B400 in that measurement is a virtual link
address, not a lease. The current221-byte Shinobi dispatch duplicates common
transport, so a source-backed shared frame is a possible funding path; no
reclamation is granted until its full foreign/auth/ABI/interrupt proof passes.
No shared source or ROM was changed. Actual native damage/health, sword/combat,
palette, scene/respawn, native controls/first pipe and full1-1 remain open.

Active output: `build/prince-actor-1101-v1` only. The compact checkpoint contains
new sources, small aggregate receipts and a precise commit list, without ROM,
DBG, assets or captures. Frozen v2 sources/archive and the v14 grant checkpoint
remain unchanged. Reproduction uses the bounded runner and prior frozen source
inputs; no historical tree extraction is needed.
''',encoding='utf-8')
 sources=['tools/reference/prince_host_world_1102_v6.py','tools/audit/check_prince_host_world_1102_v6.py','tools/audit/recover_prince_world_coordinates_1102_v7.py','tools/audit/check_prince_world_coordinates_1102_v7.py','tools/reference/prince_host_world_1102_v8.s','tools/audit/compile_prince_host_world_1102_v8.py','tools/reference/prince_host_world_compiled_1102_v8.py','tools/audit/check_prince_host_world_compiled_1102_v8.py','tools/reference/prince_lzdict_decoder_1102_v9.s','tools/audit/measure_prince_lzdict_1102_v9.py','tools/audit/prepare_prince_geometry_codec_1102_v11.py','tools/audit/check_prince_host_render_1102_v11.py','tools/reference/prince_host_lifecycle_1102_v12.s','tools/reference/prince_host_lifecycle_model_1102_v12.py','tools/audit/compile_prince_host_lifecycle_1102_v12.py','tools/audit/check_prince_host_lifecycle_1102_v12.py','tools/audit/measure_prince_host_storage_1102_v12.py','tools/audit/check_prince_executable_state_1102_v15.py','tools/audit/persist_prince_state_amendment_1102_v15.py','tools/reference/prince_host_services_1102_v16.s','tools/audit/compile_prince_host_services_1102_v16.py','tools/audit/check_prince_host_services_1102_v16.py','tools/reference/prince_host_events_1102_v17.s','tools/audit/compile_prince_host_services_1102_v17.py','tools/audit/check_prince_host_events_1102_v17.py','tools/audit/compile_prince_host_services_1102_v18.py','tools/audit/check_prince_host_services_1102_v18.py','tools/audit/measure_prince_native_storage_1102_v18.py','tools/reference/prince_cold_worker_1102_v19.s','tools/audit/prepare_prince_cold_worker_1102_v19.py','tools/audit/check_prince_cold_worker_1102_v19.py','tools/audit/measure_prince_shared_owner_1102_v20.py',str(Path(__file__).relative_to(R)),str(grant.relative_to(R)),'docs/qa/allocations/prince-executable-state-1102-v15.json',str(doc.relative_to(R))]
 sources=[name.replace('\\','/')for name in sources]
 receipts=['world-coordinate-recovery-v7.json','world-coordinate-CPU-v7.json','host-life-layout-v12.json','host-life-CPU-v12.json','host-storage-v12.json','executable-state-proposal-v15.json','host-services-CPU-v16.json','host-events-CPU-v17.json','host-services-layout-v18.json','host-services-CPU-v18.json','host-ingress-CPU-v18.json','native-storage-v18.json','cold-worker-layout-v19.json','cold-worker-CPU-v19.json','shared-owner-measurement-v20.json']
 members={name:(R/name).read_bytes()for name in sources};members.update({'receipts/'+name:(O/name).read_bytes()for name in receipts})
 manifest=dict(passed=True,source_only=True,ROM_DBG_assets_captures_included=False,explicit_commit_files=sources,frozen_v2_SHA256_unchanged=hashlib.sha256(frozen.read_bytes()).hexdigest(),base_ROM_SHA256=q['base_ROM_SHA256'],eventual_rebase='Parent authoritative f5c plus later stable Bub, not old4395 composition.',members={name:dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())for name,data in members.items()})
 archive=O/'native-binding-source-v3.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for name,data in members.items():z.writestr(name,data)
  z.writestr('manifest.json',json.dumps(manifest,indent=2)+'\n')
 with zipfile.ZipFile(archive)as z:
  for name,data in members.items():assert z.read(name)==data
 result=dict(passed=True,ZIP=str(archive.relative_to(R)),bytes=archive.stat().st_size,SHA256=hashlib.sha256(archive.read_bytes()).hexdigest(),members=len(members)+1,explicit_commit_files=sources,ROM_DBG_assets_captures_not_included=True)
 (O/'native-binding-source-v3-manifest.json').write_text(json.dumps(result,indent=2)+'\n');files=[p for p in O.rglob('*')if p.is_file()];result.update(active_files=len(files),active_bytes=sum(p.stat().st_size for p in files));assert result['active_files']<1000 and result['active_bytes']<256000000;print(json.dumps({k:v for k,v in result.items()if k!='explicit_commit_files'}))


if __name__=='__main__':main()
