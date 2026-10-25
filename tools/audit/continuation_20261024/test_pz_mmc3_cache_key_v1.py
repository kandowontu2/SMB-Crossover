from pathlib import Path
import importlib.util,hashlib,json
from py65.devices.mpu6502 import MPU
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;O=D/'ryu-head-oversized-mmc3-v8/cache-key-cpu-v1';O.mkdir(exist_ok=False)
p=R/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py';s=importlib.util.spec_from_file_location('img',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);im=m.Image(D/'ryu-head-oversized-mmc3-v8/candidate.nes')
syms={r['name']:r['val']for r in im.data['sym']if r.get('scope')==1 and 'val'in r}
mem=[0]*65536
for pc,bank in [(0x8000,254),(0xe000,255)]:mem[pc:pc+8192]=im.raw[16+bank*8192:16+(bank+1)*8192]
for name in ('M3PageExpected','M3PageStore','M3PageMatches'):
 h=im.hook(name);pc=h['address']&0xe000;bank=h['physical_bank'];mem[pc:pc+8192]=im.raw[16+bank*8192:16+(bank+1)*8192]
cpu=MPU(memory=mem);count=0;negative=0
ram=lambda n:syms[n]
def call(name):
 cpu.pc=syms[name];cpu.sp=0xfd;mem[0x1fe]=0xff;mem[0x1ff]=5
 for _ in range(100):
  cpu.step()
  if cpu.pc==0x600:return
 raise AssertionError(('call failed',name,hex(cpu.pc)))
for page in range(1024):
 mem[ram('M3RequestedLo')]=page&255;mem[ram('M3RequestedHi')]=page>>8
 call('M3PageExpected')
 assert mem[ram('M3Wanted')+8:ram('M3Wanted')+12]==[(page>>8)<<(2*i)for i in range(4)]
 for index in range(18):
  for n in ('RgAudioZp','RgAudioCpuZp'):mem[ram(n):ram(n)+24]=[(index*17+j*11)&255 for j in range(24)]
  prefix=[mem[ram(n):ram(n)+24].copy()for n in ('RgAudioZp','RgAudioCpuZp')]
  lo=ram('M3PageLo');hi=ram('M3PageHigh');mem[lo:lo+18]=[0x55]*18;mem[hi:hi+5]=[0xa5]*5
  before=mem[hi:hi+5].copy();mem[ram('M3Target')]=index
  call('M3PageStore')
  assert mem[lo:lo+18]==[page&255 if k==index else 0x55 for k in range(18)]
  expect=before.copy();k=index//4;shift=(index%4)*2;expect[k]=(expect[k]&~(3<<shift))|((page>>8)<<shift)
  assert mem[hi:hi+5]==expect
  cpu.x=index;call('M3PageMatches');assert cpu.p&1
  for delta in (1,256,512):
   other=page^delta;mem[ram('M3RequestedLo')]=other&255;mem[ram('M3RequestedHi')]=other>>8;call('M3PageExpected');cpu.x=index;call('M3PageMatches');assert not cpu.p&1;negative+=1
  mem[ram('M3RequestedLo')]=page&255;mem[ram('M3RequestedHi')]=page>>8;call('M3PageExpected')
  for n,expected in zip(('RgAudioZp','RgAudioCpuZp'),prefix):assert mem[ram(n):ram(n)+24]==expected
  count+=1
result=dict(passed=True,ROM_sha256=hashlib.sha256(im.raw).hexdigest(),page_store_and_hit_cases=count,low_and_high_page_miss_cases=negative,pages=1024,cache_slots=18,native_audio_prefix_untouched=24,all_adjacent_packed_page_entries_preserved=True,scope='Actual linked6502 pure page-directory helper instructions under py65; no hardware/PPU, whole cache upload or native integration claim.',hooks={n:im.hook(n)for n in ('M3PageExpected','M3PageStore','M3PageMatches')})
(O/'proof.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
