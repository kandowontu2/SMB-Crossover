"""Measure native-only private link funding; no stub Main or shared edits."""
import json,re,subprocess,zipfile
from pathlib import Path
import prepare_dkjr_native_carry_1102_v4 as P
R=P.R;O=P.O


def main():
 cpu=json.loads((O/'native-carry-v4-CPU.json').read_text());assert cpu['passed']
 for rel,sha in cpu['bindings'].items():assert P.P.P.sha((R/rel).read_bytes())==sha,rel
 old=(O/'native-carry-v4.s').read_text();layout=json.loads((O/'native-carry-v4-layout.json').read_text());L=layout['labels'];source=old;removed=[]
 def cut(first,last,role):
  nonlocal source
  a=source.index(first);b=source.index(last,a);removed.append(dict(role=role,source_start=first.split(':')[0],source_end=last.split(':')[0]));source=source[:a]+source[b:]
 cut('D_cd91:','D_e893:','Donor top-level phase and donor-stage enemy dispatcher; native Main must deliberately replace their phase/contact contract')
 for name,target in[('DkjrFrame','D_cd91'),('DkjrPlayerContact','D_d2fc')]:
  text='.export %s\n%s=%s\n'%(name,name,target);assert source.count(text)==1;source=source.replace(text,'')
 geometry=re.findall(r'^DGeometry_[0-9a-f]{4}:',source,re.M);assert len(geometry)==9
 cut(geometry[0],'.export DkjrUseOriginalGeometry,DkjrUseNativeGeometry','Nine donor-level immutable geometry lists; admitted native-only geometry uses C800/40/80 lists')
 source=source.replace('.export DkjrUseOriginalGeometry,DkjrUseNativeGeometry','.export DkjrUseNativeGeometry')
 cut('DkjrUseOriginalGeometry:','DkjrUseNativeGeometry:','Original geometry-pointer publisher is not a native entry')
 cut('DkjrOriginalGeometryPointers:','D_f23e:','Original four-stage geometry pointer table is not a native reader')
 cut('DkjrNativeWorldDisable:','DkjrNativeTerrainHook:','Original-geometry fallback is omitted from the proposed native-only API')
 source=source.replace('DkjrNativeWorldEnable,DkjrNativeWorldDisable,','DkjrNativeWorldEnable,')
 discarded=['cdfd','ced4','cef4','cf9d','edab']
 for name in discarded:
  text='.export DImport_%s\nDImport_%s: jmp DImport_%s ; explicit independent donor/native phase import\n'%(name,name,name)
  assert source.count(text)==1;source=source.replace(text,'')
 for name in geometry:
  assert name[:-1]not in source
 assert 'DkjrUseOriginalGeometry'not in source and'DkjrNativeWorldDisable'not in source
 # All source instructions outside these explicitly host-replaced ranges
 # remain verbatim in the assembly. No movement/jump/vine/fruit/death leaf
 # has been replaced by a hand-written approximation or default RTS.
 def original_pcs(text):return{int(x,16)for x in re.findall(r'^D_([0-9a-f]{4}):',text,re.M)}
 erased=original_pcs(old)-original_pcs(source);assert erased and all(0xcd91<=x<0xcde4 or 0xd2fc<=x<0xd405 for x in erased)
 for name in['DkjrInput','DkjrTransition','DkjrMove','DkjrJump','DkjrVineProbe','DkjrHandProbe','DkjrFruitTouch','DkjrFruitAdvance','DkjrFruitCollision','DkjrFruitHit','DkjrDamage','DkjrDefeatTick','DkjrClock']:
  assert '.export '+name+'\n'in source,name
 (O/'native-link-v5.s').write_text(source);(O/'native-link-v5.cfg').write_text('MEMORY{C:start=$a000,size=$2000,file=%O;}SEGMENTS{DKJR:load=C,type=rw;}')
 cc=R/'tools/Windows/cc65/bin'
 for cmd in[[cc/'ca65.exe',O/'native-link-v5.s','-g','-o',O/'native-link-v5.o'],[cc/'ld65.exe','-C',O/'native-link-v5.cfg',O/'native-link-v5.o','-o',O/'native-link-v5.bin','-Ln',O/'native-link-v5.lbl']]:
  p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert p.returncode==0,p.stderr
 blob=(O/'native-link-v5.bin').read_bytes();labels={n:int(a,16)for a,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(O/'native-link-v5.lbl').read_text(),re.M)}
 q=dict(passed=True,source_only=True,qualified=False,native_Main_implemented=False,native_playable=False,ROM_written=False,current_ROM_SHA256=P.P.PIN,input_component_bytes=layout['component_bytes'],native_only_component_bytes=len(blob),private_bytes_reclaimed=layout['component_bytes']-len(blob),remaining_header_reserved_bytes=8160-len(blob),native_vector_budget=114,remaining_after_vector_before_missing_ports=8160-len(blob)-114,original_instruction_labels_retained=len(original_pcs(source)),original_instruction_labels_removed=len(erased),only_removed_original_instruction_ranges=[[0xcd91,0xcde4],[0xd2fc,0xd405]],removed_source_regions=removed,removed_import_vectors=[int(x,16)for x in discarded],remaining_unbound_imports=[0xecb7,0xed44,0xed7b,0xefce,0xf1c5],required_replacements=['Native phase: preserve CD91 air-input latch, fruit-hit freeze, death branch, one originalClock and55=54; native pause/demo/scene gate owns host states.','Native original-bounds body/enemy contact and fruit priority replace donor stage-specific enemy OAM dispatch.','Native hanging-fruit world/presentation and victim/credit callbacks close the five remaining imports.','Native Main/current-carry-event/velocity/head/side/coins/scene callback vector, bounded OAM/CHR/colors/HUD and cold/owner lifecycle all require implementation and measured fit.'],scope='Actual source-only relink measurement, not a completed integration or dead padding claim. Full frozen donor reference remains intact. Removed geometry is unreachable only under the proposed native-only ABI, whose caller must initialize/use native lists and must not expose original-geometry/oldFrame entrypoints.',code_SHA256=P.P.P.sha(blob),labels=labels,bindings={p.relative_to(R).as_posix():P.P.P.sha(p.read_bytes())for p in[Path(__file__),O/'native-carry-v4-CPU.json',O/'native-carry-v4.s',O/'native-link-v5.s',O/'native-link-v5.bin']})
 checkpoint=R/'docs/qa/checkpoints/2026-11-02/dkjr-native-world-v3'
 with zipfile.ZipFile(checkpoint/'inputs.zip')as archive:baseline=json.loads(archive.read('build/dkjr-native-source-1102-v2/native-world-v3-layout.json'))
 for field in['native_bindings','native_MTileAttribute_file_offset','native_MTileAttribute_SHA256']:q[field]=baseline[field]
 q.update(component_bytes=len(blob),header_reserved_spare=8160-len(blob))
 (O/'native-link-v5-layout.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in['passed','qualified','native_Main_implemented','input_component_bytes','native_only_component_bytes','private_bytes_reclaimed','remaining_header_reserved_bytes','remaining_after_vector_before_missing_ports','code_SHA256']}))


if __name__=='__main__':main()
