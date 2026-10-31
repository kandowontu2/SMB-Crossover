"""Own-cache row32 genuine native query and isolated row ABI controls."""
from pathlib import Path
import itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import bt_jmp_row_cold_controls_v3 as A
L,H=A.L,A.H;J=R/'build/bt-native-world-source-v2/joint';P=R/'build/bt-jmp-row-cold-source-v1/joint';O=R/'build/bt-native-world-controls-v1'

def state(m,c):
 at=A.address(m.bundle,'VRAM_Buffer1');queue=[(a,v)for a,v in m.writes if at<=a<at+128]
 return[c.a,c.x,c.y,c.p,c.sp],bytes(m[:256]),H.get(m,'VRAM_Buffer1_Offset'),queue

def main():
 O.mkdir(exist_ok=False);q=dict(passed=False,native=False,CF_BT_pending=True,checks={})
 try:
  bundles=[H.C.qualified(x/'candidate.nes')for x in[P,J]];seeds=[]
  for b in bundles:
   m=L.make(b);c,_=L.call(m,'BtLoad');assert c.p&1;H.put(m,OperMode=0,FamilyMainCommit=1,VRAM_Buffer1_Offset=0);seeds.append(m)
  # Selected20 takes the genuine native inline branch of the same actual
  # QueueMegaManFacePalette caller; selected33 now reaches that genuine
  # query through authenticated row32. Compare complete ZP/output/VRAM order.
  native=0
  for area,bg,flag in itertools.product(range(4),range(8),range(64)):
   pair=[]
   for raw in[20,33]:
    m=A.fork(seeds[1]);H.put(m,SelectedCharacter=raw,AreaType=area,BackgroundColorCtrl=bg,VRAM_Buffer1_Offset=12);before=[bytes(x)for x in m.ram];m.writes.clear();m.ram_writes.clear()
    c=A.direct(m,'QueueMegaManFacePalette',L.flags(flag));c,lo,_=A.finish(m,c);assert not m.ram_writes and [bytes(x)for x in m.ram]==before
    pair.append(state(m,c))
   assert pair[0]==pair[1],('native caller exact query/VRAM/flags',area,bg,flag,pair[0][0],pair[1][0]);native+=1
  q['checks']['native_caller']=dict(pairs=native,actual_QueueMegaManFacePalette=True,all4_area_all8_background_all64_flags=True,full_AXYP_SP_ZP_queue_offset_and_ordered_VRAM_exact=True)
  print('actual native palette caller PASS',native,flush=True)
  # Every other row must retain real callback behavior. The only known image
  # differences are the new row32 operand/helper/fingerprint. Compare exact
  # per-bank mutations and ordered writes, rather than erasing code bytes.
  rows=0
  for slot,flag in itertools.product([i for i in range(37)if i!=32],range(64)):
   pair=[]
   for seed in seeds:
    m=A.fork(seed);before=[bytes(x)for x in m.ram];m.writes.clear();m.ram_writes.clear();c,lo,out=A.finish(m,A.start(m,slot,L.flags(flag)))
    delta=[[(i,x,y)for i,(x,y)in enumerate(zip(before[bank],m.ram[bank]))if x!=y]for bank in range(4)]
    pair.append((out[0],delta,m.ram_writes,out[3],out[4],out[5]))
   assert pair[0]==pair[1],('isolated row32 preserves real other callbacks',slot,flag);rows+=1
  q['checks']['isolated_rows']=dict(pairs=rows,all_other36_entries_including_reject_all64flags=True,AXYP_SP_each_bank_mutation_orderedwrites_maps_page1_exact=True)
  poison=0
  for byte,flag in itertools.product([-1]+list(range(16)),range(64)):
   m=A.fork(seeds[1]);m.ram[3][0x1fe0+(0 if byte<0 else byte)]^=1;before=[bytes(x)for x in m.ram];seen=[]
   def watch(mm,c,i):
    if 0xa000<=c.pc<0xc000 and mm.rawtags[1]==3:seen.append((i,c.pc))
   c,lo,out=A.finish(m,A.start(m,32,L.flags(flag)),watch)
   assert not seen and not c.p&1 and [bytes(x)for x in m.ram]==before and not m.ram_writes;poison+=1
  q['checks']['unready_poison']=dict(pairs=poison,unready_and_all16bytes_all64flags=True,no_first_guest_opcode_or_payload_write=True)
  q.update(passed=True,scope='Actual native QueueMegaManFacePalette output/VRAM/flags across all area/background contexts; other rows isolated. Raw33 stillpending; full parser ordering and native admission remain separate.')
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 files=[Path(__file__),Path(A.__file__),Path(L.__file__),Path(H.__file__),J/'source-stage.json',J/'candidate.nes',J/'candidate.dbg',J/'bt/api.s',J/'bt/cache.bin',J/'bt/cookie.bin',P/'candidate.nes',P/'candidate.dbg',P/'bt/cache.bin',P/'bt/cookie.bin']
 q['bindings']={str(p.resolve()):L.sha(p)for p in files};(O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q['checks']),flush=True);assert q['passed'],q.get('error')
if __name__=='__main__':main()
