"""Freeze the true CF lifecycle/presentation payload and bounded source delta."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2]
P=R/'build/contra-force-lifecycle-cart-v4';K=R/'build/contra-force-lifecycle-kernel-v6'
O=R/'build/contra-force-lifecycle-qualified-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not O.exists();O.mkdir();bindings={}
 inputs=[P/'source-stage.json',K/'build-proof.json',R/'build/contra-force-lifecycle-controls-v4/controls.json',R/'build/contra-force-lifecycle-isr-controls-v2/controls.json']
 for p in inputs:
  d=json.loads(p.read_text());assert d['passed'],p
  for f,h in d['bindings'].items():assert sha(f)==h,f;bindings[f]=h
  bindings[str(p.resolve())]=sha(p)
 producers=[P/'joint'/n for n in ['cf-loader.s','cf-guard.s','cf-carrier.s','cf-retire.s','cf-stream.bin','cf-cookie.bin']]
 api=dict(status='AUTHENTICATED_SOURCE_SCENE_LIFE_PLAYER_RESET_AND_PRESENTATION_ONLY',native=False,ready=False,
  parent='f5231061660c6b898554a86c429db8357bd80da71b8aa38525b09636a6eb8e5e',candidate=sha(P/'joint/candidate.nes'),joint=str((P/'joint').resolve()),source_stage=str(P/'source-stage.json'),
  cart_producer='tools/audit/prepare_contra_force_lifecycle_cart_v4.py',kernel_producer='tools/audit/prepare_contra_force_lifecycle_kernel_v6.py',kernel=str(K),
  actual_six_cart_producers={str(p.resolve()):sha(p)for p in producers},
  cart_objects=['cf-loader.o','cf-guard.o','cf-carrier.o','cf-retire.o'],
  rebase='Recompile the four true own cartridge producers with the exact current cf-stream.bin and cf-cookie.bin from this joint. Preserve current common/main/BW/BT/scene/menu producers. No wholesale cfg or main replacement. Existing f523 own CF MEMORY splits remain unchanged; no additional PRG/CHR lease.',
  native_imports='Real current f523 DBG imports; CfNativeResetBank derived from genuine JnResetDispatch location. Current all79609 nonCF native/public symbols exact. Source Input/Body use the genuine existing C2 CfHostCallInput/Body bank gates, never near-call A1 while A3 is mapped.',
  service_rows={'0':'CfHostMovement: general Ensure then original source input/body through authentic C2 bank gates',
   '1/3':'CfHostGraphics source body suppression/zero reservation; exact original descriptor renderer remains',
   '2':'CfHostDraw genuine EARLY nativeDrawAll callback; source body/shots plus nativeworld once',
   '9':'CfHostVisible native death/injury C result','17':'CfHostPortrait source idle frames25/75/117/159; genuine lives offset and source/nativeY restored',
   '15':'CfHostSceneEnsure: no CmFresh. Full internal AXYP except C; genuine SFC sets NZ from A as usual. Reject unless selected31, mode1, busy odd, forcedblank mask, DisableFlag nonzero, NmiDisable<0, unpaused. Valid cold initializes; valid warm retains all original gear/HP.',
   '19':'CfHostReset: actual native JnReset exactly once through genuine SFC, then general Ensure and area motion reset, restores native AXYP. NOT forcedblank-only; valid current-owner InitializeArea can reset motion before screen phase.'},
  warm_life_policy={'own_new_byte':'CfHostLastLife DDB8, appended after exact prior callback gates/body metadata; no old C2 metadata PCs moved','ready':'CFReady02E1 = CurrentPlayer+1','same_player_life':'Preserve source state/HP/gear; exact A2 transport output02EC..EE intentionally changes per service.','extra_life':'Actual native deferred1up raises lives; only update last-life marker, preserve source gear/HP.','life_decrease_or_player_change':'Reconstruct from actual native PlayerStatus clamped0..2; native PlayerLoseLife/ContinueGame clears status0. Native TransposePlayers does NOT swap PlayerStatus.','native_injury_limit':'One native life; genuine native KillPlayer. No CF persistent multi-hit HP claim or extra lease.','scene_reset':'Clear original actor/projectile/motion/action pages300/400, import native position, mark bodypalette dirty; preserve class and all four original7F..82 gear/HP bytes.'},
  pre_load='Unready15 MUST call actual native CmFresh once in ROM fallback; unready19 actual JnReset once. Never enter first A2 opcode before real ROM full-cookie check. Shared sibling owns natural cold wrapper and readiness; these are not installed here.',
  pending=['Natural menu→Start→InitScreen load/Ensure hook and warm shared policy (sibling-owned)','BodyP0 palette26/29, names18/status30/world32 still unimplemented','Exact yellow-shot P1 policy: whole loan-requiring shots remain hidden; unadopted measured proposal only','Ready31 preview must explicitly use authentic ROM FmDrawCfPreview before loading; generic raw>=28 preview is wrong','No native emulator or real natural Main admission claim'],
  boundaries={'own_ROM':'Exact existing A115147/C78302/A69118+36 preserved','own_CHR':'935..<969; stream935..<959 body959..<968 shots968','new_state':'One own C2 DDB8 byte. Future UNGRANTED P1 transient workspace must startDDB9, notDDB8.'})
 (O/'api-and-scope.json').write_text(json.dumps(api,indent=2)+'\n')
 neg=[R/'build/contra-force-lifecycle-controls-v1/controls.json',R/'build/contra-force-lifecycle-controls-v2/controls.json',R/'build/contra-force-lifecycle-controls-v3/controls.json',R/'build/contra-force-lifecycle-isr-controls-v1/controls.json',R/'build/contra-force-lifecycle-kernel-v1/negative.json',R/'build/contra-force-lifecycle-kernel-v2/negative.json']
 files={Path(__file__),*inputs,*neg,O/'api-and-scope.json',*producers}
 for root in [P,K]:
  files|={p for p in root.rglob('*')if p.is_file()and p.suffix in ['.s','.inc','.cfg','.dep','.json']}
 for n in ['contra_force_host_runtime_v9.s','contra_force_a2_router_v5.s','contra_force_host_render_v3.s']:files.add(R/'tools/reference'/n)
 for n in ['prepare_contra_force_lifecycle_kernel_v6.py','prepare_contra_force_lifecycle_cart_v4.py','contra_force_lifecycle_controls_v4.py','contra_force_lifecycle_isr_controls_v2.py']:files.add(R/'tools/audit'/n)
 # Original CHR input assets are immutable source bytes, not carrier-ROM copies.
 for p in [R/'build/contra-force-body-pack-v3/atlas.chr',R/'build/contra-force-shot-pack-v1/atlas.chr']:files.add(p)
 z=O/'source-delta-only.zip'
 with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as a:
  for p in sorted(files):a.write(p,p.relative_to(R).as_posix())
 for p in files|{z}:bindings[str(p.resolve())]=sha(p)
 for f,h in bindings.items():assert sha(f)==h,f
 out=dict(passed=True,native=False,ready=False,candidate=api['candidate'],source_stage=str(P/'source-stage.json'),API=api,retained_negatives=[str(p)for p in neg],source_delta_zip_sha256=sha(z),source_delta_zip_members=len(files),source_delta_zip_bytes=z.stat().st_size,bindings=bindings)
 p=O/'handoff.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(path=str(p),sha256=sha(p),candidate=api['candidate'],bindings=len(bindings),members=len(files),bytes=z.stat().st_size)),flush=True)
if __name__=='__main__':main()
