"""Read-only captured OAM removal counterfactual and construction fairness bound."""
from pathlib import Path
import argparse,csv,hashlib,json
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import Memory,address
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);o=p.parse_args().output;o.mkdir(exist_ok=False)
 src=D/'root-megaman-lowbody-probe-v1/attribution.json';assert sha(src)=='83049a3ea3a60ac33e87d0b27e397a9341976763552839fa495819fc4a953d53'
 b=scoped_load(D/'root-chip-hud-composed-v1/candidate.nes');m=Memory(b);m.page(2,12)
 records={n:bytes(m[address(b,n):address(b,n)+9]).hex()for n in['MmMM_BULLET_1Right','MmMM_BULLET_1Left']}
 assert records=={'MmMM_BULLET_1Right':'080002ff000203fdfc','MmMM_BULLET_1Left':'080042fff80243fdfc'}
 csvpath=D/'root-megaman-lowbody-probe-v1/native/visibility.csv';frames={int(r['ppuFrame']):r for r in csv.DictReader(csvpath.open())}
 rows=[]
 for f in json.loads(src.read_text())['findings']:
  raw=bytes.fromhex(f['actual_physical_OAM']);assert len(raw)==256;s=[tuple(raw[i:i+4])for i in range(0,256,4)]
  actual=frames[f['actual_PPU_frame']];assert actual['hardwareOam']==f['actual_physical_OAM'];height=16 if int(actual['ctrl'])&32 else 8;assert height==16
  groups=[]
  for i,(y,t,a,x)in enumerate(s):
   j=(i+1)%64;yy,tt,aa,xx=s[j]
   if t==2 and a in[3,67]and tt==0 and aa==(a&64)|2 and yy==(y+2)&255 and xx==(x+(4 if a==3 else-4))&255:
    groups.append([i,j])
  assert len(groups)=={2475:2,2871:3}[f['actual_PPU_frame']],groups
  def visible(scan,hidden):return[i for i,(y,t,a,x)in enumerate(s)if i not in hidden and y+1<=scan<=y+height][:8]
  for w in f['body_pixel_omission_witnesses']:
   assert visible(w['scanline'],set())==w['first_eight_slots'],w
   assert w['omitted_body_slot']not in w['first_eight_slots']and w['nontransparent_source_pixels']>0
  outcomes=[]
  for retained in groups:
   hide={i for group in groups if group!=retained for i in group}
   admitted=[dict(scanline=w['scanline'],slot=w['omitted_body_slot'])for w in f['body_pixel_omission_witnesses']if w['omitted_body_slot']in visible(w['scanline'],hide)]
   outcomes.append(dict(only_normal_shot_kept=retained,other_normal_slots_hidden=sorted(hide),original_opaque_omission_witnesses=len(f['body_pixel_omission_witnesses']),previously_omitted_body_witnesses_now_admitted=len(admitted),admitted=admitted))
  rows.append(dict(actual_PPU_frame=f['actual_PPU_frame'],actual_last_DMA_FrameCounter=f['last_DMA_RAM']['FrameCounter'],PPUCTRL=int(actual['ctrl']),actual_sprite_height=height,ordinary_shot_OAM_groups=groups,counterfactual=outcomes))
 fairness=[]
 for mask in range(1,16):
  alive=[i for i in range(3,-1,-1)if mask>>i&1];sequence=[]
  for tick in range(512):
   frame=tick&255;phase=frame%3 if len(alive)==3 else frame&3;sequence.append(alive[phase%len(alive)])
  gaps={slot:max(b-a for a,b in zip([t for t,v in enumerate(sequence)if v==slot],[t for t,v in enumerate(sequence)if v==slot][1:]))for slot in alive}
  assert max(gaps.values())<=4
  if len(alive)==1:assert set(sequence)==set(alive)
  fairness.append(dict(mask=mask,live_slots=alive,max_source_constructions_between_selections=gaps))
 result=dict(passed=True,source_only=True,native_run=False,source_attribution_sha256=sha(src),source_visibility_csv_sha256=sha(csvpath),source_records=records,witnesses=rows,fairness=fairness,checker_sha256=sha(__file__),
  scope='Counterfactual removal of other ordinary shot OAM in immutable original captures, retaining every remaining byte and original slot order. It establishes scanline pressure can cause these omissions; it is NOT actual new candidate output, whose compacted/rotated OAM is separately CPU-qualified.',
  limits='Construction fairness only for constant live sets, including255-to0. Skipped DMA publication may alias phases. Offscreen live shots consume a selection turn, and a sole charged shot/player/world sprites can still exceed8. No claimed native body improvement, publication-age bound or cadence recovery.')
 (o/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in['fairness','witnesses']},indent=2));print([(r['actual_PPU_frame'],[v['previously_omitted_body_witnesses_now_admitted']for v in r['counterfactual']])for r in rows])
if __name__=='__main__':main()
