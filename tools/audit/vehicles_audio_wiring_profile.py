"""CPU-only cost attribution; no cadence changes or candidate mutation."""
from pathlib import Path
import argparse,collections,hashlib,json,statistics,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/audit'))
from check_tmnt_render_oa import load,Memory,address
from verify_native_relocation import NesMPU


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def run(path,count):
 b=load(path);m=Memory(b);m.page(1,0);m.page(2,13)
 for n,v in [('SelectedCharacter',19),('OperMode',1),('GameEngineSubroutine',8),
             ('CurrentBank',128),('CurrentBankC',141),('Player_Y_HighPos',1)]:m[address(b,n)]=v
 helper={address(b,n):n for n in b['syms']if n.startswith('TnSourceSTA')}
 calls=[];writers=collections.Counter();sites=collections.Counter()
 # The full expanded-audio wrapper reestablishes physical graphics banks and
 # saves/restores the A bank around each real native music call.
 for tick in range(count+1):
  m[address(b,'FrameCounter')]=tick&255
  m[address(b,'AreaMusicQueue')]=1 if tick==0 else 0
  m[address(b,'EventMusicQueue')]=0
  for i in range(16):m[address(b,'GuestNativeDirty')+i]=0
  c=NesMPU(memory=m,pc=address(b,'ExpandedAudioUpdate'));c.sp=0xfd;c.stPushWord(0x5aff)
  before=dict(writers);steps=0
  while c.pc!=0x5b00:
   if c.pc in helper and m.banks[(c.pc-0x8000)//8192]==123:
    name=helper[c.pc];writers[name]+=1
    ret=(m[0x100+(c.sp+1)%256]+256*m[0x100+(c.sp+2)%256]+1)&65535
    sites[(name,ret,m[ret])]+=1
   c.step();steps+=1
   assert steps<50000,('Audio wrapper timeout',tick,hex(c.pc),m.banks)
  assert c.sp==0xfd
  calls.append(dict(tick=tick,cycles=c.processorCycles,
                    writer_calls=sum(writers.values())-sum(before.values())))
 return dict(ROM_sha256=sha(path),calls=calls,writer_calls=dict(writers),
             call_sites=[dict(helper=n,return_PC=pc,next_opcode=op,calls=num)
                         for(n,pc,op),num in sites.most_common()])


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['baseline','candidate','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();assert not a.output.exists()
 old,new=run(a.baseline,600),run(a.candidate,600)
 baseline=[q['cycles']for q in old['calls'][1:]];candidate=[q['cycles']for q in new['calls'][1:]]
 deltas=[b-a for a,b in zip(baseline,candidate)]
 # Only a measured opportunity. No generic writer ABI may be weakened on the
 # basis of this local next-instruction observation alone.
 load_ops=[0xa9,0xa5,0xb5,0xad,0xbd,0xb9,0xa1,0xb1]
 direct={'TnSourceSTA00','TnSourceSTA01','TnSourceSTA04','TnSourceSTA05',
         'TnSourceSTA08','TnSourceSTA0C','TnSourceSTA00X','TnSourceSTA01X','TnSourceSTA02X','TnSourceSTA03X'}
 opportunity=[q for q in new['call_sites']if q['helper']in direct and q['next_opcode']in load_ops]
 report=dict(passed=True,checker_sha256=sha(Path(__file__)),baseline=old,candidate=new,
  summary=dict(source_play_updates=600,baseline_mean_cycles=statistics.mean(baseline),
               candidate_mean_cycles=statistics.mean(candidate),mean_added_cycles=statistics.mean(deltas),
               maximum_added_cycles=max(deltas),minimum_added_cycles=min(deltas),
               candidate_peak_cycles=max(candidate),
               candidate_peak_tick=new['calls'][1+candidate.index(max(candidate))]['tick']),
  local_writer_opportunity=dict(status='Unimplemented/unqualified optimization lead only',
      description='PHP/PLP in a direct buffered STA costs7cycles. Some observed call sites immediately reload A, making their N/Z values locally dead. A separate call-site proof and all-song equivalence would be required before a specialized writer could omit these saves. Existing generic writer ABI remains unchanged.',
      observed_eligible_calls_including_initialization=sum(q['calls']for q in opportunity),sites=opportunity),
  scope='CPU-only601 wrapper calls (one real song initialization plus600 plays), normal-area request, no SFX. Includes expanded wrapper/graphics-bank publication, excludes shared audio mixer/ISR/PPU/DMC DMA stall time. Baseline is its existing Rygar fallback; candidate is authentic TMNT song2. Cost attribution, not an equivalence/performance pass or all-song optimization proof.')
 a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['summary'],indent=2))


if __name__=='__main__':main()
