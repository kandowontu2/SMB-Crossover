"""Re-execute every complete captured H audio call, including actual IRQs."""
from pathlib import Path
import collections,csv,hashlib,importlib.util,json,struct,traceback
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-samus-audio-scan-h';J=H/'native-irq-cz'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 out=J/'cpu-native-review-da.json';assert not out.exists()
 z=json.loads((J/'native-result.json').read_text());assert z['expected_partial']and z['result']['failure']=='frame limit'and z['result']['frames']==1100
 assert sha(J/'preparation.json')=='f3e13de8d4dde43bbb080d82833406c341a96593f62b7d20668e46847fb7aa3a'
 D=R/z['native_directory'];m=json.loads((D/'manifest.json').read_text());assert sha(D/'manifest.json')==z['manifest_sha256'] and m['controller_only']and not m['memory_or_register_writes']and m['full_frame_audit']and not m['config']['record']
 mp=V/'agent49-samus-bill-arsenal-a/palette_native_model_cu.py';assert sha(mp)=='213c1de880b418a19911f7af654f936bfb942c019e229bf6e871699a964bc94b';sp=importlib.util.spec_from_file_location('H_audio_actual_DA',mp);model=importlib.util.module_from_spec(sp);sp.loader.exec_module(model)
 image=model.q.Image(H/'source/build/smb-crossover-mmc3.nes');assert sha(image.path)==m['rom_sha256']
 for ext in ['nes','dbg','lbl']:assert sha(D/f'smb-crossover-mmc3.{ext}')==sha(image.path.with_suffix('.'+ext))
 ev=[json.loads(s)for s in(D/'audio-native.jsonl').read_text().splitlines()];raw=(D/'audio-native.ram').read_bytes();fmt=struct.Struct('<HB');wr=(D/'audio-writes.bin').read_bytes();assert len(wr)%fmt.size==0;writes=list(fmt.iter_unpack(wr));hardware=[json.loads(s)for s in(D/'audio-hardware.jsonl').read_text().splitlines()]
 assert len(raw)==len(ev)*10240 and [q['ramOffset']for q in ev]==list(range(0,len(raw),10240))
 by={}
 for q in ev:
  if q['event']in['audio-entry','audio-return']:by.setdefault(q['call'],{})[q['event']]=q
 assert set(by)==set(range(1,len(by)+1))and len(by)==560
 results=[];irqs=0;cycles=0
 for serial,pair in by.items():
  assert set(pair)=={'audio-entry','audio-return'},('No incomplete call silently dropped',serial)
  a=pair['audio-entry'];b=pair['audio-return'];initial=model.snapshot(raw,a);expected=model.snapshot(raw,b);bs={ad:a[n]for ad,n in[(0x8000,'bank8'),(0xa000,'bankA'),(0xc000,'bankC'),(0xe000,'bankE')]}
  interrupts=model.irq_records(ev,raw,a,b);assert all(q['name']=='IRQ'for q in interrupts)
  ports=[q for q in hardware if q['call']==serial];subject=model.execute(image,initial,[a[n]for n in['A','X','Y','P','SP']],bs,a['PC'],b['PC'],b['SP'],interrupts=interrupts,hardware=ports)
  assert subject['regs']==[b[n]for n in['A','X','Y','P','SP','PC']],('Every native return register',serial)
  assert subject['ram']==expected,('All10240 native RAM bytes including live/dead stack and IRQ effects',serial)
  actual=writes[a['writeCount']:b['writeCount']];computed=[(q[2],q[4])for q in subject['trace']]
  assert actual==computed,('Every ordered physical native RAM/mapper/APU/PPU write',serial)
  assert subject['banks']=={ad:b[n]for ad,n in[(0x8000,'bank8'),(0xa000,'bankA'),(0xc000,'bankC'),(0xe000,'bankE')]}
  elapsed=b['cycle']-a['cycle'];assert elapsed==subject['cycles'],('Exact native no-DMA instruction elapsed cycles',serial,elapsed,subject['cycles'])
  irqs+=len(interrupts);cycles+=elapsed;results.append(dict(call=serial,frame=a['frame'],elapsed_cycles=elapsed,writes=len(actual),actual_child_IRQs=len(interrupts),RAM_sha256=hashlib.sha256(expected).hexdigest()))
 assert irqs==258 and len(writes)==233997 and not hardware
 t=list(csv.DictReader((D/'trace.csv').open()));assert len(t)==1100 and (t[-1]['mode'],t[-1]['task'],t[-1]['engine'],t[-1]['x'],t[-1]['y'])==('1','3','8','40','176')
 identity=json.loads((D/'current-c-identity.json').read_text());assert identity==dict(character=2,behavior=0,marioVariant=0,billVariant=0,outlinesOff=1)
 inp=list(csv.DictReader((D/'inputs.csv').open()));assert len(inp)==1099
 for q in inp[540:]:assert int(q['mask'])==(64 if int(q['poll'])%8<4 else 0)
 # Decode the actual entry snapshots, rather than infer shots from controller B.
 at=lambda ad:ad if ad<2048 else ad-0x6000+2048
 shot_entries=sum(any(model.snapshot(raw,pair['audio-entry'])[at(image.ram['SmShotType']+i)]for i in range(3))for pair in by.values());assert shot_entries>0
 report=dict(status='PASS_ACTUAL_PRIVATE_H_AUDIO_AND_IRQ_COMPOSED_NATIVE_EXECUTION',script_sha256=sha(__file__),preparation_sha256=sha(J/'preparation.json'),native_result_sha256=sha(J/'native-result.json'),native_manifest_sha256=sha(D/'manifest.json'),ROM_sha256=sha(image.path),model_sha256=sha(mp),capture_files={n:dict(bytes=(D/n).stat().st_size,sha256=sha(D/n))for n in['audio-native.jsonl','audio-native.ram','audio-writes.bin','audio-hardware.jsonl']},ordinary_smoke=dict(identity=identity,physical_frames=1100,input_polls=1099,stationary_B_only_after_actual_menu_prefix=True,actual_active_shot_entries=shot_entries,endpoint=t[-1]),complete_audio_calls=len(results),exact_nested_IRQs=irqs,complete_ordered_native_writes=len(writes),external_hardware_reads=len(hardware),native_elapsed_cycles=cycles,per_call=results,main_changed=False,limits=['Ordinary stationary short-beam firing smoke, no item grants/state/ROM/RAM/register/mapper writes. Not a traversal, all-weapon acquisition or final-media proof.','Exact captured H native registers/all10240RAM/ordered writes/cycles include258 actual nested IRQs. No unobserved nested NMI case is claimed.','Matched-state H/G optimization semantics separately checked in CT; physical H/G frame/AI schedules need not match.'],goal_complete=False)
 out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],calls=len(results),IRQs=irqs,writes=len(writes),sha256=sha(out))))
if __name__=='__main__':
 try:main()
 except Exception:
  p=J/'cpu-native-negative-da.txt';assert not p.exists();p.write_text(traceback.format_exc());raise
