"""Extend exact compiled Bill/Ryu/Rogue readers to Tank's35/81 proposals."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_mario_tank_visible_1101_v5 import O,P,PIN
sha=lambda b:hashlib.sha256(b).hexdigest()
def adapted(source,replacements):
 text=source.read_text()
 for before,after in replacements:
  assert before in text,(source,before);text=text.replace(before,after)
 ns=dict(__file__=str(Path(__file__)),__name__='tank_v5_derived_reader');exec(compile(text,str(source),'exec'),ns);ns['main']()
 return dict(path=str(source.relative_to(R)),sha256=sha(source.read_bytes()),exact_replacements=[dict(before=a,after=b)for a,b in replacements])
def main():
 common=[('from prepare_mario_tank_loader_1101_v4 import P,PIN,O','from prepare_mario_tank_visible_1101_v5 import P,PIN,O')]
 a=adapted(R/'tools/audit/audit_mario_tank_bill_tails_1101_v4.py',common+[
  ('banks=[21,31,32,33]','banks=[21,31,32,33,35]'),
  ("(33,'BILL_ORBIT_5',(0xdea2,0xdf00))]","(33,'BILL_ORBIT_5',(0xdea2,0xdf00)),(35,'BILL_ORBIT_3',(0xdeb6,0xdf00))]")])
 b=adapted(R/'tools/audit/audit_mario_tank_orbit_gap_owners_1101_v4.py',common+[
  ("('SCROOGE','Scrooge',33,11)]","('SCROOGE','Scrooge',33,11),('RYU','Ryu',35,6)]"),
  ("segment='XG_RYGAR_GFX'if bank==32 else'XG_LUIGI_GFX'","segment='XG_RYU_GFX'if bank==35 else'XG_RYGAR_GFX'if bank==32 else'XG_LUIGI_GFX'"),
  ('tag in [160,161]','tag in [160,161,163,209]'),
  ("assert hi==0xbf,(mode,index,tag,hi)","assert hi==(0xb1 if tag==209 else 0xbf),(mode,index,tag,hi)"),
  ('assert 0xbf00<=(hi<<8)+offset<0xc000','assert (0xb100 if tag==209 else 0xbf00)<=(hi<<8)+offset<(0xb200 if tag==209 else 0xc000)'),
  ('physical_bounds={32:[0x1f00,0x2000],33:[0x1f00,0x2000]}','physical_bounds={32:[0x1f00,0x2000],33:[0x1f00,0x2000],35:[0x1f00,0x2000],81:[0x1100,0x1200]}'),
  ("dict(bank=33,named_owners=['XG_LUIGI_GFX','BILL_ORBIT_5','ROGUE_RELOC_PAGE_6'],proposed_physical_gap=[0x1ea2,0x1f00],typed_data_readers_closed=True)]","dict(bank=33,named_owners=['XG_LUIGI_GFX','BILL_ORBIT_5','ROGUE_RELOC_PAGE_6'],proposed_physical_gap=[0x1ea2,0x1f00],typed_data_readers_closed=True),dict(bank=35,named_owners=['XG_RYU_GFX','BILL_ORBIT_3','ROGUE_RELOC_PAGE_8'],proposed_physical_gap=[0x1eb6,0x1f00],typed_data_readers_closed=True)]"),
  ("'scrooge_metasprites.inc'","'scrooge_metasprites.inc','ryu_metasprites.inc'"),
  ("dict(passed=True,body_cases=1512,weapon_cases=27","dict(passed=True,body_cases=2016,weapon_cases=36")])
 # Original derived receipt's prose is historical; this manifest explicitly
 # binds the transformations and exact newly executed finite domains.
 q=json.loads((O/'orbit-gap-owners.json').read_text());q['scope_correction']='Current367 compiled Ryu/Rygar/Luigi/Scrooge +Bill35 +Rogue35/81 source. All current logical reader pages checked, full256 offsets for32/33/35/81. Bank81 mapping isB100..B1FF, never proposedB0D0..B0FF. Existing historical32/33 prose is retained only inside explicit derivation.'
 q['derived_source_provenance']=[a,b];q['bindings'][str(Path(__file__).relative_to(R))]=sha(Path(__file__).read_bytes());(O/'orbit-gap-owners.json').write_text(json.dumps(q,indent=2)+'\n')
 print(json.dumps(dict(passed=True,current_ROM_sha256=PIN,new_Ryu_body_cases=504,new_Ryu_weapon_cases=9,Rogue_native_read_calls=q['Rogue_source_reader']['actual_native_read_calls'],new_Bill_bank35=True)))
if __name__=='__main__':main()
