"""Freeze the small read-only Gimmick source packet; never builds/launches/copies ROMs."""
from pathlib import Path
import hashlib,json

R=Path(__file__).resolve().parents[1]
OUT=R/'build/gimmick-source-handoff-v1.json'
SHA=lambda b:hashlib.sha256(b).hexdigest()
def bind(p):
 p=Path(p).resolve();b=p.read_bytes()
 return dict(path=str(p),bytes=len(b),sha256=SHA(b))
def rows(value):
 if isinstance(value,dict):
  if {'path','bytes','sha256'}<=value.keys():yield value
  for v in value.values():yield from rows(v)
 elif isinstance(value,list):
  for v in value:yield from rows(v)

def main():
 assert not OUT.exists(),'Preserve the frozen handoff'
 expected={
  'build/gimmick-source-audit-v1.json':'c1b24c0d8c9af52dbe371952d18300618ff3cb32800ef3660c7fad91c71bead2',
  'build/gimmick-source-details-v1.json':'6f8454492a60080e4c73add7578003c1c4e31ccf94565d8ac5b7ca2a4f8e58ab',
  'build/gimmick-original-hero-poses-v1.png':'fff5b9cdda4259db09d1e39c64630b03f30330cfce5c31f1e3eef0a5d880f6a2'}
 refs={}
 for rel,sha in expected.items():
  b=bind(R/rel);assert b['sha256']==sha,(rel,b['sha256']);refs[b['path']]=b
  if rel.endswith('.json'):
   for row in rows(json.loads((R/rel).read_text())):
    actual=bind(row['path']);assert actual==row,('Bound input changed',row,actual)
    refs[actual['path']]=actual
 owned=[R/p for p in ['tools/gimmick_source_audit_v1.py','tools/gimmick_source_details_v1.py',
  'tools/gimmick_source_freeze_v1.py','docs/qa/gimmick-source-port-plan-2026-10-29.txt',
  *expected.keys()]]
 snapshots=[R/p for p in ['smb1base-mmc5-expanded.cfg','src/roster_expansion_menu.inc',
  'src/audio/roster/contra.inc','src/roster_audio.s','tools/prepare_rogue_dawn_audio_driver_v4.py',
  'tools/audit/verify_native_relocation.py','tools/audit/link_pit_rygar_sophia_audit_cpu.py',
  'tools/audit/check_tmnt_render_oa.py']]
 for p in owned+snapshots:
  b=bind(p);refs[b['path']]=b
 payload=dict(status='FROZEN_READ_ONLY_SOURCE_AUDIT_NO_PORT_NO_ALLOCATION_NO_NATIVE',
  original_sha256='ce2f84618dfe3d5581fcdf11a10190b717853af3be0bea7988cd27cd1498c092',
  authority='Existing readable disassembly PRG+CHR payload exact; header-only offsets7/15 differ. Original source controls, not a port differential.',
  source_preview='22 actual original records, grayscale bitplane classes; not a final NES palette/native image.',
  no_change=dict(shared_source=True,canonical=True,settings=True,Downloads=True,ROM=True),
  native_runs=0,new_ROM_DBG_or_source_tree_outputs=0,
  additive_errata=[
   'Details corrects base star_frames.CHR_page: star records depend on current hero slot0 pages12/13 AND slot1 page8.',
   'Port-plan note excludes details allocator candidates91/92/99: existing Rogue upper audio views own those tails. Mechanical gap list is not an allocator or lease.',
   'All proposed24/122/75/73 spans remain unallocated and require actual consumer/private-owner proof on final current triple. No physical CHR/RAM range is claimed free.'],
  evidence_counts=dict(hero_frame_indices=22,star_frame_indices=66,original_renderer_cases=176,
   original_audio_callbacks=384,native=0,complete_original_Main=0,compiled_port=0),
  open=['Exact raw26/menu25 admission and storage leases','Complete original terrain/collision/health/world callback closure',
   'All host caller/foreign/IRQ/stack/cycle/OAM/PPU controls','Approved Mushroom/Flower and Easy-stomp crossover policy',
   'Full5B/APU/DPCM audio fit/scheduling/voice-preservation design','Root-owned actual native playability'],
  owned_files=[bind(p)for p in owned],
  current_snapshot_limits='Helper/source/CFG snapshots are the files read for this bounded investigation, not a historical full-build closure or a claim current shared source reproduces pinned737d. Existing ROM/DBG/MAP are explicitly bound. No old tests or native evidence is relabelled.',
  bindings=sorted(refs.values(),key=lambda x:x['path']))
 OUT.write_text(json.dumps(payload,indent=2)+'\n',newline='\n')
 print(json.dumps(dict(handoff=bind(OUT),bindings=len(refs),owned=len(owned),owned_bytes=sum(p.stat().st_size for p in owned))))

if __name__=='__main__':main()
