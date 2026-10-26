"""Authenticate proposed CV1 upper-state reuse and actual private producer inputs."""
from pathlib import Path
import argparse,hashlib,json,re
from check_tmnt_render_oa import load,address
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PARENT=D/'cv3-remaining-queue-v8/qualified-v1/source-final'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def extract(s,name):return s[s.index('.proc '+name+'\n'):s.index('.endproc',s.index('.proc '+name+'\n'))+len('.endproc')]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);rom=PARENT.parent/'candidate.nes';b=load(rom);assert sha(rom)=='7b0a2cbdd806ff057d86c1af1834ecac5d34e1bb1747852e93d6ca2ec3d2fec2'
 donor=PARENT/'src/audio/roster/castlevania.inc';text=donor.read_text();references=[]
 for line,s in enumerate(text.splitlines(),1):
  if'RgAudioRam'not in s:continue
  m=re.search(r'RgAudioRam(?:([+-])\$([0-9a-f]+))?(?:,([xy]))?',s,re.I);assert m,s;offset=int(m[2],16)*(1 if m[1]=='+'else-1)if m[2]else 0;lo,hi=(offset,offset+255)if m[3]else(offset,offset);references.append(dict(line=line,text=s.strip(),offset=offset,index=m[3],arbitrary_byte_index_min=lo,arbitrary_byte_index_max=hi))
 assert references and max(r['arbitrary_byte_index_max']for r in references)<256
 indirect_stores=[dict(line=i,text=s.strip())for i,s in enumerate(text.splitlines(),1)if re.search(r'\b(STA|STX|STY|INC|DEC|ASL|LSR|ROL|ROR)\s+\(',s,re.I)];assert not indirect_stores
 wrappers=(PARENT/'src/roster_audio.s').read_text();assert'RgAudioRam: .res $200'in wrappers and'sta RgAudioRam+$100,x'in wrappers and' jsr Cv3SaveAudioZp\n  jmp SavedPrivate\n  .res 12,$ea'in wrappers
 allrefs=[]
 for f in(PARENT/'src').rglob('*'):
  if not f.is_file()or f.suffix not in['.s','.inc']:continue
  for line,s in enumerate(f.read_text().splitlines(),1):
   if re.search(r'RgAudioRam|RgContraRam|RgZeldaRam',s):allrefs.append(dict(path=f.relative_to(PARENT).as_posix(),line=line,text=s.strip(),sha256=sha(f)))
 pna=(PARENT/'src/parodius_adapter.s').read_text();pnn=(PARENT/'src/parodius_native.s').read_text();assert'.else\nPnCapVX=RgAudioRam+252'in pna and'.if ::MAPPER_MMC5'in pnn
 combat=(PARENT/'src/cv3_combat.s').read_text();spawn=extract(combat,'Cv3Spawn');sub=extract(combat,'Cv3SpawnSub');weapons=extract(combat,'Cv3WeaponsGate');assert spawn.count('jsr Cv3FxProducer')==1
 emit=[]
 for match in re.finditer(r'lda #(\d+)\n (?:jsr|jmp) Cv3Spawn\b',combat):emit.append(dict(type=int(match[1]),prefix=combat[match.start():match.end()]))
 assert set(r['type']for r in emit)==set(range(1,7))
 calls=[s.strip()for s in combat.splitlines()if re.search(r'\b(?:jsr|jmp) Cv3Spawn\b',s)];assert len(calls)==len(emit),(len(calls),len(emit))
 callrefs=[]
 for f in(PARENT/'src').rglob('*.s'):
  for i,s in enumerate(f.read_text().splitlines(),1):
   if re.search(r'\b(?:jsr|jmp|farcall) Cv3Spawn\b',s):callrefs.append(dict(path=f.relative_to(PARENT).as_posix(),line=i,text=s.strip()))
 assert all(r['path']=='src/cv3_combat.s'for r in callrefs)
 idrefs=[]
 for f in(PARENT/'src').rglob('*'):
  if not f.is_file()or f.suffix not in['.s','.inc']:continue
  for i,s in enumerate(f.read_text().splitlines(),1):
   if'Cv3FxNoiseID'in s or'Cv3FxPulseID'in s:idrefs.append(dict(path=f.relative_to(PARENT).as_posix(),line=i,text=s.strip()))
 assert all(r['path']=='src/cv3_remaining_source_fx.s'for r in idrefs)
 game=(PARENT/'src/game.s').read_text();reset=(PARENT/'src/reset.s').read_text();assert'CatchUpOnce:'in game and'jsr GameLoop'in game and'jmp IdleLoop'in game and'KeepLagChr:'in reset and'jsr AudioUpdate'in reset
 result=dict(passed=True,accepted=False,status='SOURCE_SPACE_AND_INPUT_PLAN_ONLY_NO_IMPLEMENTATION',parent_ROM_sha256=sha(rom),source=str(PARENT),proposed_physical_range=[address(b,'RgAudioRam')+256,address(b,'RgAudioRam')+512],physical_slots=256,logical_capacity_retained=64,new_allocated_RAM=0,CV1_imported_source_sha256=sha(donor),CV1_all_direct_RAM_references=references,CV1_max_possible_direct_indexed_offset=max(r['arbitrary_byte_index_max']for r in references),CV1_indirect_stores=indirect_stores,all_shared_RAM_mentions=allrefs,Parodius_Rg_aliases_scope='Only MMC3 else branches; MMC5 uses ExRAM5C00/5E00/5F00.',wrapper_hazard='Current Kind2 cold ClearRam writes the entire proposed buffer. It MUST skip upper-half stores while retaining old spans, and a real NMI after uncommitted slot write must prove preservation.',cold_flow_plan='Three-byte upper-clear JMP to genuine8-byte INX/BNE/LDX/JMP continuation inside existing unreachable12-byte Save tail; all old Save/driver/public addresses stay exact.',private_input_constant_types=emit,all_Cv3Spawn_callrefs=callrefs,private_FAST_capacity_not_yet_authorized_by_proof=True,capacity_plan='Mute/pause consumer must drain committed requests without ticking FX; otherwise prolonged wrapper silence could accumulate requests. Then max2 GameLoops per NMI, max3 shots +1bat per loop gives8 cues. Consecutive CANCEL-run dedup bounds cancels to9, so17<64. This still needs actual mute/cold/pending/public boundary qualification.',unowned_ID_plan='Old38-byte reset may retain unowned NoiseID/PulseID, clearing Active/Owned/SourceHigh and flushing tail=head at unchanged cost. Only this audio file reads the IDs. Before any admission, the NMI consumer must zero IDs whose Owned bit is clear; all live source priorities/APU/phase remain exact. No hardware or external gameplay owner may read stale IDs.',all_ID_refs=idrefs,source_pins={str(p.relative_to(PARENT)):sha(p)for p in[PARENT/'src/roster_audio.s',PARENT/'src/game.s',PARENT/'src/reset.s',PARENT/'src/guest_audio.s',PARENT/'src/cv3_combat.s',PARENT/'src/cv3_remaining_source_fx.s',PARENT/'src/parodius_native.s',PARENT/'src/parodius_adapter.s']},scope='Exact frozen local source/storage/input authentication only. Cold wrapper, original mixed-source fidelity, all real main inputs/capacity and hardware/ordinary behavior remain to be implemented/proved. No new ROM or native launch.',tool_sha256=sha(__file__))
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in['all_shared_RAM_mentions','all_ID_refs','CV1_all_direct_RAM_references','private_input_constant_types','all_Cv3Spawn_callrefs']},indent=2))
if __name__=='__main__':main()
