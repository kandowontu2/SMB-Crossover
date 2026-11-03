"""Preserve v32 incomplete contact-policy episode; never a gameplay pass."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import measure_prince_palette_contact_1102_v32 as Q
import prepare_prince_successor_manifest_1102_v26 as M
H,O=Q.H,Q.O


def main():
 base,_,_,_=M.bundle();H.W.PIN=M.A.PIN;episodes=[]
 for hp in [1,2]:
  h=H.host(base);h.lab.update(H.P.T.labels(O/'player-policies-v32.lbl'));meta=(O/'policy-metadata-v32.bin').read_bytes();h.s[0x800:0x800+len(meta)]=meta;h.m.ram[3][:0x1fdf]=(O/'policy-runtime-v32.bin').read_bytes();h.s[0x6cf]=hp
  for frame in range(8):h.source('PpHostUpdate')
  Q.call(h,'PpNativeContact');rows=[]
  for frame in range(100):
   H.N.put(h.m,FrameCounter=frame,SavedJoypad1Bits=0);h.source('PpNativeTick')
   if frame<32 and frame%4==0 or frame==99:rows.append(dict(Main=frame,action=h.s[0x616],pose=h.s[0x617],mode=h.s[0x618],HP=h.s[0x6cf],dead=h.s[0xac],native_engine=H.N.get(h.m,'GameEngineSubroutine')))
  if hp==2:assert(h.s[0x616],h.s[0x617],h.s[0x618],h.s[0x6cf],h.s[0xac])==(74,171,1,1,0)
  else:assert(h.s[0x616],h.s[0x617],h.s[0xac],H.N.get(h.m,'GameEngineSubroutine'))==(85,185,1,11)
  episodes.append(dict(explicit_CPU_fixture_HP=hp,trace=rows))
 # Exact original omitted tail restores the hurt action at source pose170.
 donor=H.P.machine();ram=bytearray((O/'state-899.bin').read_bytes());ram[0x6cf]=2;ram[0x6ee]=2;ram[0x6e0]=1;ram[0x401]=0;ram[0x615]=255;ram[0x623]=0;ram[0x61d:0x61f]=(224).to_bytes(2,'little');ram[0x61f]=ram[0x611];ram[0x624]=0
 list.__setitem__(donor.memory,slice(0,2048),ram);donor.memory.switch(5);H.P.call(donor,0xe95a,y=0,limit=20000);source=[]
 for tick in range(12):
  donor.memory[0x69]=0;donor.memory[0x2c]=0
  donor.memory.switch(5);donor.a,donor.x,donor.y,donor.p=0,0,0,0x21;donor.sp=253;donor.stPushWord(0x5ffe);donor.pc=0xf158
  H.P.until(donor,0xf1a2,limit=10000);donor.pc=(donor.stPopWord()+1)&65535
  donor.memory[0x2c]=3;donor.memory[0x40a]=0;H.P.call(donor,0xeff2,y=0,limit=20000)
  source.append(dict(source_advance=tick,action=donor.memory[0x616],pose=donor.memory[0x617],mode=donor.memory[0x618],sword=donor.memory[0x6ee]))
 assert any(r['pose']==170 and r['action']==0 for r in source),source
 q=dict(passed=True,negative_reproduced=True,v32_native_ready=False,ROM_written=False,base_SHA256=M.A.PIN,episodes=episodes,actual_original_full_control_continuation=source,cause='Frozen motion/control core intentionally ends atF090 before combat selector. OriginalF09D callsDBB9 and clears hurt74 at pose170; existing native core misses this recovery. Applying oneHP combat hurt to unarmed body contact is additionally incomplete: original4:AD06..AD19 selects fiveHP pathE9A4 unless source swordmode2. Preserve original modes instead of a host cooldown/unfreeze.',next='Recover F090..F110 and its real original combat call closure; original armed/native proxy contract and incoming/outgoing source predicates remain required.',bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),Path(Q.__file__),O/'player-policies-measurement-v32.json',O/'player-policies-v32.bin',O/'policy-runtime-v32.bin',O/'policy-metadata-v32.bin']})
 (O/'contact-continuation-negative-v33.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
