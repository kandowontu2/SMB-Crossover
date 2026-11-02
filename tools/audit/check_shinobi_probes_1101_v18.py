"""Native terrain ABI regression and compact continuation for Shinobi admission."""
import itertools,json
import prepare_shinobi_chr_owner_1101_v18 as P
import check_hogan_current_bounded_v1 as M
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from prepare_selected_native_packet_v1 import sha

def main():
 b=scoped_load(P.O/'candidate.nes');seed=M.fresh(b);cases=0
 for head,x,y,probe in itertools.product([True,False],[0,15,40,127,240,255],[32,80,144,176],[30,33,34,35,36]):
  if (head and probe!=30) or (not head and probe==30):continue
  a=M.fork(seed);M.put(a,SelectedCharacter=36,Player_X_Position=x,Player_PageLoc=1,Player_Y_Position=y,Player_Y_HighPos=1)
  start=address(b,'Block_Buffer_1')
  for i in range(416):a[start+i]=0x61 if i%3==0 else 0
  z=M.fork(a)
  left=M.invoke(a,'HuHead' if head else 'HuSide',a=176,y=probe)
  right=M.invoke(z,'BlockBufferColli_Head' if head else 'BlockBufferColli_Side',a=176,y=probe)
  assert tuple(left[n] for n in ['A','X','Y','P'])==tuple(right[n] for n in ['A','X','Y','P'])
  assert bytes(a[:11])==bytes(z[:11]) and a.ram==z.ram
  cases+=1
 native=json.loads((P.O/'native-smoke/capture/result.json').read_text())
 assert native['passed'] and native['world_x']>40
 q=dict(passed=True,ROM_sha256=sha(P.O/'candidate.nes'),terrain_contract_cases=cases,native=native,installed=False,
  remaining='Full1-1, palette/name, original audio, enemy melee and magic callbacks, contacts and severe-lag assessment remain incomplete. No publication or all-roster completion claim.')
 (P.O/'checks.json').write_text(json.dumps(q,indent=2)+'\n')
 path=P.R/'docs/qa/continuation-current.json';c=json.loads(path.read_text())
 c={'shinobi_native_followup':dict(candidate=str(P.O.relative_to(P.R)/'candidate.nes'),**q,
  fixed='Private menu Start works. Generic reject head/side callbacks returned character ID as solid tiles and shoved X16/update. Direct native queries fix idle/walk. GmOnlyHigh now admits36. Legacy MegaManFullShotBank no longer overwrites Shinobi sprite window4.',
  next='Continue Shinobi1-1 gameplay and contacts; sprite now coherent but colors dark, HUD still MARIO. Resident ADD4..ADF4 owns32-byte exact-ID shot-bank gate;12bytes remain. Preserve v15 cookie, v16 direct probe veneers, v17 range admission and v18 gate when rebuilding.'),**c}
 path.write_text(json.dumps(c,indent=2)+'\n')
 print(json.dumps(q))
if __name__=='__main__':main()
