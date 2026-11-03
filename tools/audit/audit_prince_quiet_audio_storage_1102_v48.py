"""Finite source-dead audio state proposal, no RAM or code grant inferred."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prepare_prince_successor_manifest_1102_v26 as M
O=M.O


def main():
 graph={k:v for name in ['contact-recovery.json','world-coordinate-recovery-v7.json','combat-tail-recovery-v34.json']for k,v in json.loads((O/name).read_text())['instructions'].items()};assert len(graph)==2485
 broad={};direct=[];other=[];index={'abx','aby','zpx','zpy'}
 for key,v in graph.items():
  mn,mode,value=v['mn'],v['mode'],v['value']
  if mn in ['JSR','JMP']or mode not in index|{'abs','zpg'}or value>=2048:continue
  end=value+(256 if mode in index else 1)
  if value<0x800 and end>0x780:
   assert mode=='abx',(key,v);broad[key]=v
  if mode in ['abs','zpg']and 0x780<=value<0x800:direct.append(key)
 assert not direct
 expected={'5:871D':('LDA',0x6cf),'5:8725':('STA',0x6cf),'4:AD50':('STA',0x6dd),'4:B8DB':('LDA',0x710),'7:E991':('LDA',0x711),'7:E996':('STA',0x711)}
 assert set(broad)==set(expected)
 for key,(mn,value)in expected.items():assert(broad[key]['mn'],broad[key]['value'])==(mn,value)
 # LoseHP's exact selector producesX0forplayerY0, X1forguardY14. The
 # terminal4:AD50 retains thatX through the X-preserving landing leaf.
 for key,mn,val in [('5:8715','LDX',1),('5:8717','CPY',0),('5:871B','LDX',0),('4:AD4B','JSR',0xd487),('4:AD50','STA',0x6dd)]:
  assert graph[key]['mn']==mn,(key,graph[key]);assert val is None or graph[key]['value']==val,(key,graph[key])
 prior=json.loads((O/'battle-lifetime-proposal-v46.json').read_text());assert prior['passed']and prior['all256_indices_expanded_except_source_unreachable_ledger']==['4:B8DB','7:E991','7:E996']
 services=(O/'native-services-v42.s').read_text();quiet=services[services.index('PpNativeQuietSfx:'):services.index('PpNativeMotionExport:')];assert '$c780'not in quiet and '$c7ff'not in quiet
 layout=json.loads((O/'cold-link-storage-v44.json').read_text());assert layout['physical_spare']==802
 q=dict(passed=True,proposal_only=True,resource_granted=False,ROM_written=False,base_SHA256=M.A.PIN,requested_existing_exclusive_RAM2_half_open=[0xc780,0xc800],bytes=128,source_instruction_boundaries=len(graph),original_direct_readers_writers=[],conservative_index_overlaps=broad,finite_index_contract='Original5:8715..871B derivesX0or1 from defenderY0or14, touchingHP6CF/D0 only. Terminal4:AD50 retains thatX through X-preserving source/world landing leaf, touchingdeath6DD/DE only. Remaining three guardledger sites are source-unreachable for native guardHP1 and playerY0 as formally bound in v46. Original actor scripts/controls/renderer have no other direct/indexed/indirect route into780..7FF.',quiet_audio_contract='Current source-event leaves only retain eventA/X atC0AD/AE, savedY atC041, originalbank6 atC6D1, musicA atC0AF and sourceactor-visible musicX arithmetic. Actual donor6:AA13/AA19 audio state is absent from this quietWIP. Original6DC backdrop flash is not an audio RAM ownership exception and remains untouched.',new_constructor_requirements=['Extend final state stream by128B audio-code backing atC65F..C6DF while uninitialized.','A measured typed cold prefix must copy/readbackC65F..C6DF→C780..C800 before the existing source-code finalizer zeros source state.','Change cold/fresh C700 zero loop to stop atC780, preserving only newly source-dead executable interval; all genuine source-live bytes still zero before NativeInit/Ready.','Source snapshot/current phase/IRQ and full state/code/cold readback/foreign retirement must be requalified before root native queue.'],intended_source_funding='128B source-dead original audio-state interval for native full-box/pickup/cold prefix and constants. Existing46metadata+13deadrenderer bytes fund typed public/native query routes; no arbitrary FF/page or shared RAM allocation.',scope='Concrete source-consumer proposal only. No new code or ROM has been placed atC780, no constructor patch made, no new grant assumed.',bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),O/'contact-recovery.json',O/'world-coordinate-recovery-v7.json',O/'combat-tail-recovery-v34.json',O/'battle-lifetime-proposal-v46.json',O/'native-services-v42.s',O/'host-events-CPU-v17.json',O/'native-link-CPU-v43.json',O/'cold-link-CPU-v45.json',O/'cold-link-storage-v44.json',R/'docs/qa/allocations/prince-battle-lifetime-1102-v46.json']})
 (O/'quiet-audio-code-proposal-v48.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','conservative_index_overlaps']}))


if __name__=='__main__':main()
