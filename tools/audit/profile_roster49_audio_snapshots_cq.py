"""Isolated instruction profile from actual F ordinary AudioUpdate entry RAM.

No interrupt injection and no native end-state claim. This is a hotspot guide.
"""
from pathlib import Path
import collections,datetime,hashlib,importlib.util,json,statistics
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-audio-isolated-cq'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not J.exists();J.mkdir()
 native=R/'build/roster-through-2-2/root49-g-samus-Fclock-ci-2-v0-mmc3'
 assert sha(native/'manifest.json')=='d19a211c8bfac96bfa8f56330cc7e0d878e4ae54a3fd5def5a326e9ccf36e3ec'
 cp=R/'build/checkpoints/roster-audit-v49-freeze-render-fast-f/manifest.json';assert sha(cp)=='c0f31e09027aad704fc539e95adc0a53abb035fef647206b61bb10d94c8068e2'
 mp=V/'agent49-samus-bill-arsenal-a/palette_native_model_cu.py';assert sha(mp)=='213c1de880b418a19911f7af654f936bfb942c019e229bf6e871699a964bc94b'
 spec=importlib.util.spec_from_file_location('audio_CQ',mp);model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)
 im=model.q.Image(cp.parent/'smb-crossover-mmc3.nes');h=im.hook('AudioUpdate');raw=(native/'audio-starts.ram').read_bytes();starts=[json.loads(s)for s in(native/'audio-starts.jsonl').read_text().splitlines()]
 assert len(raw)==10240*len(starts)
 names=['AudioUpdate','SamusAudioUpdate','GuestMetroidStoreIndirectY','GuestNativeStatusSTA','GuestDmcStatus','GuestAudioBegin','GuestAudioFinish','RemainingAudioBegin','RemainingAudioTick','SophiaLandAudioTick']
 spans=[]
 for n in names:
  s=im.sym(n);hk=im.hook(n);spans.append((n,hk['physical_bank'],hk['address'],s.get('size',0)))
 samples=[];totals=collections.Counter();points=collections.Counter();ops={};entrycounts=collections.Counter();cpu=model.q.core.NesMPU
 for z in starts:
  initial=raw[z['ramOffset']:z['ramOffset']+10240];banks={a:z[n]for a,n in [(0x8000,'bank8'),(0xa000,'bankA'),(0xc000,'bankC'),(0xe000,'bankE')]}
  b=model.Bus(im,initial,banks,());c=cpu(memory=b);c.a,c.x,c.y,c.p,c.sp=[z[n]for n in ['A','X','Y','P','SP']];c.pc=h['address'];c.processorCycles=0
  assert b.banks[c.pc&0xe000]==h['physical_bank'] and list(b.data[c.pc:c.pc+8])==h['bytes']
  sp=c.sp;stop=(b.data[0x100+((sp+1)&255)]+256*b.data[0x100+((sp+2)&255)]+1)&65535;stopSP=(sp+2)&255
  steps=0;by=collections.Counter()
  while c.pc!=stop or c.sp!=stopSP or not steps:
   pc=c.pc;bank=b.banks[pc&0xe000]if pc>=0x8000 else-1;b.pc=pc;b.op=b.data[pc];before=c.processorCycles
   group=next((n for n,k,a,size in reversed(spans)if bank==k and a<=pc<a+size),f'bank{bank}_other')
   for n,k,a,size in spans:
    if (pc,bank)==(a,k):entrycounts[n]+=1
   key=(bank,pc);ops.setdefault(key,bytes(b.data[pc:pc+3]).hex());popped=b.data[0x100+((c.sp+1)&255)]if b.op in(0x28,0x40)else None
   c.step()
   if popped is not None:assert c.p==popped|0x30;c.p=popped&0xcf
   cost=c.processorCycles-before;by[group]+=cost;totals[group]+=cost;points[key]+=cost;steps+=1;assert steps<25000
  assert not b.hardware_i
  samples.append(dict(frame=z['frame'],world=initial[im.ram['WorldNumber']],level=initial[im.ram['LevelNumber']],cycles=c.processorCycles,steps=steps,groups=dict(by),output_ram_sha256=hashlib.sha256(b.ram()).hexdigest(),output_registers=[c.a,c.x,c.y,c.p,c.sp,c.pc]))
 report=dict(status='PASS_SCOPED_ISOLATED_AUDIO_INSTRUCTION_PROFILE',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(__file__),model_sha256=sha(mp),capture_manifest_sha256=sha(native/'manifest.json'),capture_RAM_sha256=sha(native/'audio-starts.ram'),capture_entries_sha256=sha(native/'audio-starts.jsonl'),checkpoint_sha256=sha(cp),samples=len(samples),median_cycles=statistics.median(s['cycles']for s in samples),max_cycles=max(s['cycles']for s in samples),exclusive_instruction_groups=dict(totals),entry_counts=dict(entrycounts),spans=spans,top_instruction_sites=[dict(bank=k[0],pc=k[1],bytes3=ops[k],cycles=v,exact_symbols=sorted(im.pointer(*k)))for k,v in points.most_common(40)],sample_results=samples,limits=['Actual frozen F ordinary entry RAM/registers/physical banks; current shared working ROM is G.','No IRQ/NMI injected and no native return snapshot was captured here. No exact native elapsed or ABI/end-state comparison is claimed.','No runtime or ROM patch, no performance improvement, no source/audio fidelity or arsenal coverage claimed.'])
 out=J/'report.json';out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k]for k in ['status','samples','median_cycles','max_cycles','exclusive_instruction_groups','entry_counts']}));print('RECEIPT',sha(out))
if __name__=='__main__':main()
