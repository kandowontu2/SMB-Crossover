"""Exact full Mike AudioUpdate ABI of faithful v5 versus fast candidate.

Original source pointer fields are asserted against the independent NSF
state before canonically comparing those precise private bytes. All other
RAM, ordered hardware APU stores, A/X/Y/P/SP and banks are compared literally.
"""
from pathlib import Path
import argparse,gzip,hashlib,itertools,json
from mike_native_music_cpu import Run,state,translated
from check_tmnt_render_oa import load,address
from mike_native_music_dispatch_cpu import golds

def result(r,want,components):
 b=r.b;got=state(r,False);expected=translated(b,want,components);assert got==expected,('Full Mike private source state differs from original',r.get('RgAudioSong'),want['step'])
 mem=bytearray(r.m[:0x8000])
 for name,key in [('StNativeRam','ram'),('StNativeZp','zp')]:
  at=address(b,name);mem[at:at+len(want[key])]=bytes(want[key])
 return(r.c.a,r.c.x,r.c.y,r.c.p&0xcf,r.c.sp,bytes(mem[:256])+bytes(mem[512:]),list(r.m.banks),[(at,v)for at,v in r.m.writes if 0x4000<=at<=0x4017 or 0x5000<=at<=0x5015])

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in['rom','faithful','gold','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old,new=load(a.faithful),load(a.rom);q=json.loads((a.gold/'coverage.json').read_text());components={}
 for lo,hi,at,target in q['pointer_components']:components[lo]=('<',target);components[hi]=('>',target)
 flags=sorted({0x20|c|(z<<1)|(v<<6)|(n<<7)for c,z,v,n in itertools.product([0,1],repeat=4)}|{0xee,0xff});roles=[('area',i,s)for i,s in enumerate([1,2,4,5,14,11,22])]+[('event',i,s)for i,s in enumerate([13,15,9,17,15,9,5])];rows=[]
 for role,bit,song in roles:
  source=golds(a.gold,song,16);count=0;costs=[]
  for mode,P in itertools.product([0,1],flags):
   qs=[Run(b)for b in[old,new]]
   for r in qs:
    for n,v in dict(SelectedCharacter=16,OperMode=1,CrossoverBehaviorVersion=mode,PlayerStatus=1,DisableScreenFlag=1,CurrentBank=215,CurrentBankC=166).items():r.set(n,v)
    r.set('AreaMusicQueue'if role=='area'else'EventMusicQueue',1<<bit)
   cursor=0
   for tick in range(8):
    paused=tick in[2,3]
    for r in qs:r.set('GamePauseStatus',int(paused));r.set('AvAudioRequest',21 if tick==1 else 0)
    cs=[r.call('AudioUpdate',a=0x55,x=3,y=7,p=P)for r in qs]
    if tick and not paused:cursor+=1
    assert result(qs[0],source[cursor],components)==result(qs[1],source[cursor],components),('Whole fast Mike ABI differs',role,bit,mode,hex(P),tick,cursor)
    costs.append(cs[1]-cs[0]);count+=1
  row=dict(role=role,bit=bit,song=song,cases=count,cycle_delta=[min(costs),max(costs)]);rows.append(row);print(row,flush=True)
 proof=dict(passed=True,accepted=False,faithful_v5_ROM_sha256=hashlib.sha256(a.faithful.read_bytes()).hexdigest(),candidate_ROM_sha256=hashlib.sha256(a.rom.read_bytes()).hexdigest(),tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),whole_Mike_AudioUpdate_calls=sum(r['cases']for r in rows),CPU_modes=[0,1],all_N_V_Z_C_combinations_plus_DI=flags,rows=rows,scope=__doc__,native_emulator_launched=False)
 (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
if __name__=='__main__':main()
