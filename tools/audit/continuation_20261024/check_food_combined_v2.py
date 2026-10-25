from pathlib import Path
import hashlib,itertools,json,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/audit'))
from check_tmnt_render_oa import load,Memory,address,location
from check_tmnt_audio_fallback_oc import qualified
from verify_native_relocation import NesMPU
A=R/'build/checkpoints/native-items-px/candidate.nes';B=D/'food-candidate-v2/candidate.nes';a,b=load(A),load(B);qa,qb=qualified(A),qualified(B)
assert all(qb.get(k)==v for k,v in qa.items())and len(qb)==len(qa)+1
wave=(D/'wave-candidate-v1/candidate.nes').read_bytes();assert b['raw'][16+74*8192:16+75*8192]==wave[16+74*8192:16+75*8192]
status=address(a,'PlayerStatus');begin=location(a,'CdCollectPickup');size=int(a['syms']['CdCollectPickup']['size'],0)
pat=bytes([0xa9,0,0x8d,status&255,status>>8]);span=a['raw'][begin:begin+size];assert span.count(pat)==1;pos=begin+span.index(pat)
entry=address(b,'CdNextFoodStatus');tail=location(b,'CdNextFoodStatus');length=int(b['syms']['CdNextFoodStatus']['size'],0)
assert length==10 and a['raw'][tail:tail+length]==bytes([255])*length
assert b['raw'][pos:pos+5]==bytes([0x20,entry&255,entry>>8,0xea,0xea])
allowed=set(range(pos,pos+5))|set(range(tail,tail+length))|{607961,607968}
diff=[i for i,(x,y)in enumerate(zip(a['raw'],b['raw']))if x!=y];assert set(diff)<=allowed
assert a['raw'][16+1048576:]==b['raw'][16+1048576:]
cases=0;extra=set()
def run(bundle,char,kind,hp,scene,x,flags):
 bank=(location(bundle,'CdCollectPickup')-16)//8192
 m=Memory(bundle);m.page(1,bank);m[address(bundle,'CurrentBank')]=bank|128
 for n,v in {'SelectedCharacter':char,'CdHealth':hp,'PlayerStatus':scene}.items():m[address(bundle,n)]=v
 m[address(bundle,'PowerUpType')+x]=kind;m[0x1fe]=0xff;m[0x1ff]=0x7e
 c=NesMPU(memory=m,pc=address(bundle,'CdCollectPickup'));c.a=85;c.x=x;c.y=71;c.p=flags;c.sp=0xfd
 for _ in range(500):
  if c.pc==0x7f00:return c,m
  c.step()
 raise AssertionError(('Food timeout',char,kind,hp,scene,x,flags,hex(c.pc),m.banks))
for char,kind,hp,scene,x,flags in itertools.product(range(21),range(4),[0,1,2,3,6],range(3),[0,5],[0x30,0x71]):
 c,m=run(a,char,kind,hp,scene,x,flags);d,n=run(b,char,kind,hp,scene,x,flags)
 assert(c.a,c.x,c.y,c.p&0xcf,c.sp)==(d.a,d.x,d.y,d.p&0xcf,d.sp)
 if char==14 and kind<2:
  assert n[status]==1-kind;m[status]=1-kind;extra.add(d.processorCycles-c.processorCycles)
 else:assert c.processorCycles==d.processorCycles
 assert bytes(m[:0x100])+bytes(m[0x200:0x8000])==bytes(n[:0x100])+bytes(n[0x200:0x8000])and m.banks==n.banks
 cases+=1
assert extra=={22},extra
q=dict(passed=True,ROM_sha256=hashlib.sha256(B.read_bytes()).hexdigest(),parent_ROM_sha256=hashlib.sha256(A.read_bytes()).hexdigest(),previous_qualified_symbols_exact=len(qa),new_labels=1,changed_ROM_bytes=len(diff),changed_PRG_banks=sorted({(i-16)//8192 for i in diff}),CHR_changes=0,collection_cases=cases,collection_health_sound_flags_and_other_RAM_exact=True,only_intended_scene_food_status_changes=True,collection_extra_CPU_cycles=sorted(extra),wave_bank_byte_exact_to_verified_wave_candidate=True,scope='Native Chip/Dale heal/cap logic and return contract retained. Only real0/1food receipts advance next block appearance. New helper occupies10unused bytes; 22extraCPUcycles occur once per health pickup, never walking/attacking. Native emergence/availability and visual proof remain separate gates.')
(D/'food-static-v2.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))
