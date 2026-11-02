"""Enumerate real compiled Select cycles and confirmation, without gameplay claims."""
import json
import argparse
from pathlib import Path
import check_hogan_current_bounded_v1 as M
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/playable-menu-1101-v3';ROM=R/'build/roster-combined-1101-v3/candidate.nes'

def menu_name(m):
 a=address(m.bundle,'VRAM_Buffer1');data=bytes(m[a:a+256]);p=0
 while p+3<=len(data)and data[p]:
  hi,lo,n=data[p:p+3];n&=63
  if (hi,lo)==(0x23,0x28):
   cells=list(data[p+3:p+3+n]);return ''.join(str(x)if x<10 else chr(x+55)if x<36 else ' 'if x==36 else f'<{x:02X}>'for x in cells).strip(),cells
  p+=3+n
 return '',[]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--rom',type=Path,default=ROM);ap.add_argument('--output',type=Path,default=O);a=ap.parse_args();rom=a.rom;out=a.output
 out.mkdir(exist_ok=True);b=scoped_load(rom);rows=[]
 fields=[n for n,q in b['syms'].items()if 'Variant'in n and not '::'in n and int(q['val'],0)<0x8000 and not n.startswith('.')]
 fields+=['FmAlts']
 for slot in range(32):
  m=M.fresh(b);M.put(m,CrossoverMenuIndex=slot);M.invoke(m,'MenuResolveCharacter');M.invoke(m,'QueueSelection')
  seen=set()
  for cycle in range(33):
   name,cells=menu_name(m);raw=M.get(m,'SelectedCharacter');sig=(raw,tuple(cells),tuple((n,M.get(m,n))for n in fields))
   if sig in seen:break
   seen.add(sig);confirm=[]
   for key in [16,128]:
    n=M.fork(m);M.put(n,CrossoverMenuButtons=0,SavedJoypad1Bits=key,SavedJoypad2Bits=0,VRAM_Buffer1_Offset=0)
    M.invoke(n,'CrossoverMenuInput');confirm.append(M.get(n,'CrossoverMenuState')==0)
   assert confirm[0]==confirm[1],(slot,cycle,name,confirm)
   rows.append(dict(slot=slot,cycle=cycle,raw=raw,name=name,tiles=cells,confirm_starts=confirm[0],variants={n:M.get(m,n)for n in fields if M.get(m,n)},portrait_pending=bool(M.invoke(m,'FmPending')['P']&1)))
   M.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0);M.invoke(m,'CrossoverMenuInput')
  else:raise AssertionError(('Select cycle did not repeat within32',slot))
 unique={(r['slot'],r['raw'],tuple(r['tiles'])):r for r in rows}
 names=[r['name']for r in rows]
 requested={'Bub':['BUB'],'Bob':['BOB'],'Sonic (Sonic3 reference)':['SONIC'],'Donkey Kong Jr.':['DONKEY KONG JR','DK JR'],'Getsu Fuma':['GETSU FUMA'],'Mega Giant Mario':['GIANT MARIO'],'Jay McCray':['JAY MCCRAY'],'Steve Hermann':['STEVE HERMANN']}
 missing=[label for label,aliases in requested.items()if not any(alias in name for name in names for alias in aliases)]
 q=dict(ROM_sha256=sha(rom),installed_bytes_identical=rom.read_bytes()==Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes(),select_states=len(rows),distinct_named_entries=len(unique),confirmable_named_entries=sum(r['confirm_starts']for r in unique.values()),requested_names_absent=missing,rows=rows,scope='Actual compiled menu resolution/Select cycle/Start and A confirmation; fresh native initialization in CPU model. Names decoded from emitted VRAM commands; duplicates caused by cached active-variant state are counted once for named entries. Requested absences checked against the full emitted-name list, not a proof no dormant component exists. No emulator/gameplay/fullstage/powerup proof.')
 (out/'inventory.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='rows'}));print(json.dumps([r for r in rows if not r['confirm_starts']]))
if __name__=='__main__':main()
