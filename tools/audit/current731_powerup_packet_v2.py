"""Freeze a compact read-only ledger and source/mock observer packet; no emulator."""
from pathlib import Path
import argparse,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
CURRENT='731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 ledger=D/'current731-powerup-ledger-v5';observer=D/'current731-abilities-observer-v4';checked=[]
 for folder in [ledger,observer,observer/'static-return-control']:
  m=folder/'manifest.json';z=json.loads(m.read_text())
  for b in z['bindings']:
   f=Path(b['path']);assert f.stat().st_size==b['bytes'] and sha(f)==b['sha256'],f
  checked.append(dict(manifest=str(m),sha256=sha(m),bindings=len(z['bindings']),verified=True))
 L=json.loads((ledger/'ledger.json').read_text());O=json.loads((observer/'controls.json').read_text());S=json.loads((observer/'static-return-control/controls.json').read_text())
 assert L['ROM_sha256']==O['ROM_sha256']==S['ROM_sha256']==CURRENT and len(L['rows'])==37
 assert O['Lua_runtime']==S['Lua_runtime']=='Lua 5.4'
 assert len(O['profiles'])==6 and sum(x['planned_abilities']for x in O['profiles'])==62
 assert len(S['return_core_model_cases'])==8 and len(S['genuine_compiled_call_returns'])==3 and len(O['DMA_model_cases'])==13
 assert all(x['passed']for x in S['return_core_model_cases']+S['genuine_compiled_call_returns']+O['DMA_model_cases'])
 reward_cells=sum(len(r['modes'][m]['reward_use_cells'])for r in L['rows']for m in ['easy','hard'])
 report=ROOT/'docs/qa/current731-powerup-ledger-v2-2026-10-26.txt'
 text=f'''Current731 powerup/ability completion ledger and observer preparation

Frozen ROM: {CURRENT}
Source: {L['source_root']}
Read-only work: zero native launches, no production/default/settings/Git changes.

The ledger enumerates37 identities,74 Easy/Hard cells and{reward_cells} required
reward/use entries. All74 complete-every-required-A and complete-every-required-B
cells remain false. That does not erase useful narrow components: fresh731
MarioEasy mushroom/flower/Goomba fireball/drain is linked as current. Hard,
star/1-up, all-weapon and source/waveform fidelity are not inferred.

Ledger JSON: {ledger/'ledger.json'}
Ledger SHA256: {sha(ledger/'ledger.json')}
Readable per-identity index/checklist: {ledger/'ledger.txt'}
118 evidence records retain exact historical ROM and receipt hashes. The37
ordinary routes remain3cee evidence (36Easy, BassHard), not new731 runs. Every
reward/use entry has current gap flags and exact-ID historical links where the
receipt actually declared an item/attack; scope-only links do not fill those
assertions. Ten source-owner groups are design reuse, never native coverage.

A: actual physical reveal/emergence/contact/transformation. World/resource/
target setup, controlled M3 RNG gallery and post-rise collision placement are
disclosed separately. Mature actor tests do not become reveal/rise evidence.
B: controlled fully initialized native-boundary use/graphics/contact/cost/
pool/exhaust/refusal/cleanup. Explicit resource/inventory/actor seeds are valid
for this lane and are never called genuine acquisition. Acquired-ability
prefixes keep actual collections when already finite. R: ordinary routes.

Mode correction remains additive: all18 affected220/84 runs actually observed
Easy0; nine declaredHard labels are withdrawn. Six old ability runs represent
31distinctEasy plans repeated, not62distinctplans or six mode cells. The fresh
529 numericHard replacements and all old receipts keep their own ROM hashes.
The26 historical items-v1 MODE profiles are12identities x2 plus Kirbycopy x2;
the two054d corpora together contain22identities/34modecells, not26identities.
The old054d true/false configurations and executed mode assertions were checked
again from26 frozen fixture scripts plus the10 legacy Hard fixture owners.

Finite reuse order, with per-batch hard caps rather than a new campaign:
1. Pit/Rygar/Scrooge actual acquired tiers in both modes:6profiles/62plans.
   Reuse real physical prefixes, staged valid arenas, post-rise contact setup;
   no tier/fuel/reach/pogo writes.10Pit/12Rygar/9Scrooge plans per mode.
2. Inventory galleries: at most20profiles/172plannedcases, split at16cases;
   seeded B controls with each seed logged, source passive/effect checks as well
   as firing. No acquisition credit for inventory/ammo seeds.
3. Missing physical delivery owners: at most12profiles/48cases, max4rewards
   perprofile. Actual block/head/legal-shot/reveal/fullrise/contact/transform.
4. Custom ability/restore galleries: at most24profiles/192cases, max8cases per
   profile; use explicit B seeds for rare effects instead of pretending random
   drop waiting is required. A/B stays recorded per case. Future units require
   their own source readiness and native grant; none is running or reserved.

Versioned ability observer repair

Source/mock packet: {observer/'proof.json'}
Controls SHA256: {sha(observer/'controls.json')}
Manifest SHA256: {sha(observer/'manifest.json')}
Original ability module remains byte-exact:
{S['original_module_sha256']}
The old module/84/529 receipts are unchanged. The return callback vector is
never changed during execution. One0..FFFF dispatcher is installed LAST after
all original and new static callbacks. Lua-only per-PC slots preserve original
name/return-PC pending overwrite, registration order, return SP and bank guards.
Eight Lua5.4 models pass wrongPC/SP/bank, nested, reentrant, replacement,
multiple-return and wrap cases. They test intended snapshot semantics, not the
unsafe C++ vector behavior. All6 complete generated scripts load a fixed
callback inventory, and reverse normalization restores every old mechanic and
assertion exactly. Current callback counts: {sorted(set(x['static_callback_count']for x in O['profiles']))}.

Three assembled ownership checks execute actual linked calls and returns:
ScroogeBounce atA9A4->A9C3, MM DamageEnemy atA97C->A994; both return with SP+2
to their actual adjacent continuation. Pit is reached through real
ExpandedMovement and its genuine RAM farcall JSR at016B->A13F, return016E.
Pit return code is internal RAM, not a made-up physical ROM bank. Scrooge/MM
start at the genuine compiled JSR, so these are finite CPU ownership checks,
not proof of full GameLoop reachability or native inputs.

DMA observation is reconciled to actual731 eight-byte protocol:
E005: AD7A078D0120A201, bank127. E005 EXEC is pre-DMA and explicitly rejected
as completion. E008 is after real LDA/before STA2001. Every candidate transfer
logs all256source bytes, all256physical destination bytes, per-write actual
OAMADDR/PPU/CPU stamps and differences BEFORE equality assertions. It checks
256writes, page2/source owner,0..255destinations, exactsource data, rendering
disabled during eachwrite, exacthardware and next uncontested startFrame.
Pending startFrame is labeled pending and never promoted to completed. The
old publication/endFrame assertion, CHR latch, IRQ31, fiveSMC/bank/SP and all
ability outcome guards remain intact. Additive PPUMASK records and the already
qualified scoped-enable deadline (vblank241..260 or prerender-1 dot<=274) reject
the known vertical-reload boundary. Thirteen actual-observer Lua5.4 mocks pass
positive/negative transfer and deadline controls. No PPU is emulated by these
mocks and they do not establish native timing or graphics.

No native-ready execution receipt is implied. Prepared scripts still require
fresh runtime/settings binding and ROOT review/grant before launching. There
is intentionally no native-run switch in either new preparer. Stable source
preparation command (choose a NEW absent output directory):
python -B tools/audit/final_item_abilities_current731_prepare_v1.py --output
"D:/NEW-OUTPUT" --lua-root
"{D/'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'}"
The D:/ placeholder is not this archive's actual path; replace only the output
argument with a fresh external directory. ROM source/hook target remains pinned.

Limits: current crowded body visibility and dense tiny HUD remain open; actual
old areaFALSE/natural pending-fullHUD/nonemptyBuffer2 gap is unchanged. Source
byte equality and an item counter do not establish pixel/audio fidelity. No
full current every-item, every-weapon, all-pose, campaign or no-flicker verdict.
'''
 report.write_text(text,encoding='utf-8')
 tools=['current731_powerup_ledger_v2.py','current731_powerup_packet_v2.py','final_item_abilities_static_return_v1.lua','final_item_abilities_static_prepare_v1.py','final_item_abilities_static_prepare_v2.py','final_item_abilities_dma731_v1.lua','final_item_abilities_current731_prepare_v1.py']
 checkpoint=ROOT/'docs/qa/checkpoints/2026-10-26/current731-powerup-ledger-v2'
 checkpoint.mkdir(parents=True,exist_ok=False)
 for src,name in [(ledger/'ledger.json','ledger.json'),(ledger/'ledger.txt','ledger.txt'),(ledger/'proof.json','ledger-proof.json'),(observer/'controls.json','observer-controls.json'),(observer/'proof.json','observer-proof.json'),(observer/'static-return-control/controls.json','static-return-controls.json')]:shutil.copyfile(src,checkpoint/name)
 summary=dict(passed=True,native_launches=0,ROM_sha256=CURRENT,ledger_proof=str(ledger/'proof.json'),ledger_proof_sha256=sha(ledger/'proof.json'),observer_proof=str(observer/'proof.json'),observer_proof_sha256=sha(observer/'proof.json'),verified_manifests=checked,identities=37,mode_cells=74,required_reward_use_entries=reward_cells,evidence_records=118,complete_all_required_current_A_cells=0,complete_all_required_current_B_cells=0,static_return_models=8,genuine_compiled_call_returns=3,DMA_models=13,Lua_runtime='Lua 5.4',native_worker_held=False,goal_complete=False,report=str(report),report_sha256=sha(report))
 (checkpoint/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');(a.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 (checkpoint/'README.txt').write_text('Read-only current731 completion ledger plus versioned source/mock observer preparation. No native qualification or grant. All historical receipts stay at their own ROM hashes. summary.json binds external finite packets; ledger.json enumerates37identities/74difficulty cells. No binary/capture/settings payloads included.\n',encoding='utf-8')
 bindings=[]
 for f in [report]+[ROOT/'tools/audit'/n for n in tools]+[f for f in checkpoint.iterdir()if f.is_file()]+[ledger/'manifest.json',observer/'manifest.json',observer/'static-return-control/manifest.json']:
  bindings.append(dict(path=str(f),sha256=sha(f),bytes=f.stat().st_size))
 (a.output/'manifest.json').write_text(json.dumps(dict(bindings=bindings),indent=2)+'\n')
 (checkpoint/'manifest.json').write_text(json.dumps(dict(bindings=[q for q in bindings if str(checkpoint)in q['path']]),indent=2)+'\n')
 proof=dict(passed=True,native_launches=0,ROM_sha256=CURRENT,summary_sha256=sha(a.output/'summary.json'),manifest_sha256=sha(a.output/'manifest.json'),report_sha256=sha(report),checkpoint_manifest_sha256=sha(checkpoint/'manifest.json'),verified_child_binding_entries=sum(x['bindings']for x in checked),goal_complete=False)
 (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))

if __name__=='__main__':main()
