"""Current-hash shared audio and relocated Metroid differential components."""
from pathlib import Path
import argparse,hashlib,itertools,json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/audit'))
from check_tmnt_render_oa import load,Memory,address
from check_tmnt_audio_fallback_oc import execute,result,qualified
from verify_native_relocation import NesMPU


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['baseline','candidate','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old,new=load(a.baseline),load(a.candidate)
 oq,nq=qualified(a.baseline),qualified(a.candidate)
 moved={str(n):[v,nq.get(n)]for n,v in oq.items()if nq.get(n)!=v}
 assert all(len(n)>1 and n[0]=='SamusAudioUpdate'for n,v in oq.items()if nq.get(n)!=v)
 checks={};count=0
 for char,area,event,paused,variant in itertools.product([6,7,9,10,11,12,13,14,15,16,17,18],
                 [1,2,4,8,16,32,64,128],[0,4,64],[0,1],[0,1]):
  seed=dict(SelectedCharacter=char,OperMode=1,AreaMusicQueue=area,EventMusicQueue=event,
            GamePauseStatus=paused,VvVariant=variant,KbVariant=variant,RlVariant=variant,CurrentBank=0xd7)
  c,m=execute(old,'VgAudioDispatch',seed);d,n=execute(new,'VgAudioDispatch',seed)
  assert result(c,m)==result(d,n),(char,area,event,paused,variant)
  count+=1
 checks['non_TMNT_dispatch_exact_register_RAM_bank_hardware']=count
 # Every legal active source marker retains the original global AudioUpdate
 # first-instruction ABI when TMNT does not own the DMC/history overlay.
 count=0
 for char,mode,marker,flags in itertools.product(range(21),[0,1],[0,2,6,14,254,255],[0x30,0x71,0x39,0xee]):
  seed=dict(SelectedCharacter=char,OperMode=mode,XgAudioCharacter=marker)
  m=Memory(new)
  for n,v in seed.items():m[address(new,n)]=v
  m[0x1fe],m[0x1ff]=0xff,0x7e;c=NesMPU(memory=m,pc=address(new,'TnAudioGlobalGate'))
  c.a,c.x,c.y,c.p,c.sp=0x55,3,7,flags,0xfd
  for _ in range(100):
   if c.pc==0x7f00:break
   c.step()
  else:raise AssertionError('Global gate timeout')
  expected=(flags&0x7d)|(2 if mode==0 else 0)
  assert(c.a,c.x,c.y,c.p&0xcf,c.sp)==(mode,3,7,expected&0xcf,0xff)
  assert m[address(new,'TnDmcDrain')]==0
  count+=1
 checks['non_owner_global_entry_ABI']=count
 count=0;deltas={}
 for stream in range(8):
  contexts=[]
  for b in [old,new]:
   m=Memory(b);m.page(1,0);m.page(2,13)
   for n,v in [('SelectedCharacter',2),('OperMode',1),('CurrentBank',128),('CurrentBankC',141),('BankShadow',0x47)]:
    if n in b['syms']:m[address(b,n)]=v
   for i in range(12):m[0xe0+i]=(stream*53+i*17)&255
   contexts.append((b,m,NesMPU(memory=m)))
  def call(name,number):
   nonlocal count
   rows=[];cycles=[]
   for b,m,c in contexts:
    m[0x1fe],m[0x1ff]=0xff,0x7e;m.writes=[]
    c.a,c.x,c.y,c.p,c.sp=number&255,(number*17)&255,(number*31)&255,(number*59)&255,0xfd
    c.pc=address(b,name);start=c.processorCycles
    for _ in range(20000):
     if c.pc==0x7f00:break
     c.step()
    else:raise AssertionError((name,stream,number,hex(c.pc),m.banks))
    hardware=[(at,v)for at,v in m.writes if 0x4000<=at<=0x4017 or 0x5000<=at<=0x5015]
    rows.append((c.a,c.x,c.y,c.p,c.sp,bytes(m[:0x1a0])+bytes(m[0x200:0x8000]),hardware,m.banks[:]))
    cycles.append(c.processorCycles-start)
   assert rows[0]==rows[1],(name,stream,number,rows[0][:5],rows[1][:5])
   delta=cycles[1]-cycles[0];deltas[delta]=deltas.get(delta,0)+1;count+=1
  call('SamusAudioInit',stream)
  for tick in range(512):
   for b,m,c in contexts:
    seed=dict(FrameCounter=tick,PlayerStatus=stream%3,AreaMusicQueue=(1<<stream)if tick in [0,256,448]else 0,
              EventMusicQueue=(1<<stream)if tick in [160,320]else 0,
              Square1SoundQueue=(1<<((tick+stream)%8))if (tick//64)&1 and tick%5==0 else 0,
              SmSfx=(1<<((tick//3+stream)%7))if (tick//64)&1 and tick%3==0 else 0,
              GamePauseStatus=int(400<=tick<404),OperMode=0 if tick==480 else 1)
    for n,v in seed.items():m[address(b,n)]=v&255
   call('SamusAudioUpdate',stream*512+tick)
 checks['Metroid_eight_streams_exact_all_registers_RAM_banks_ordered_APU']=count
 q=dict(passed=True,ROM_sha256=sha(a.candidate),baseline_ROM_sha256=sha(a.baseline),
        checker_sha256=sha(Path(__file__)),qualified_existing_symbols_checked=len(oq),
        intentionally_relocated_Samus_private_labels=moved,cases=checks,Samus_cycle_deltas=deltas,
        scope='Actual linked CPU components. Only discarded stack1A0..1FF excluded from RAM equivalence; all five SMC fields, mapper shadows, banks and ordered hardware writes compared. No interrupts/physical sample clock/gameplay performance claim.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n')
 print(json.dumps({k:v for k,v in q.items()if k!='intentionally_relocated_Samus_private_labels'},indent=2))


if __name__=='__main__':main()
