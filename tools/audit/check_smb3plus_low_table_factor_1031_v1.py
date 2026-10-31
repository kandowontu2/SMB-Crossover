"""Exact typed low-table factor controls; transient pointers classified by actual writer only."""
from pathlib import Path
import argparse,collections,hashlib,itertools,json,re,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import smb3plus_body_host_controls_1030_v5 as G
import smb3plus_kick_host_controls_1031_v1 as K
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
O=R/'build/smb3plus-low-table-factor-host-1031-v4';J=O/'joint';P=R/'build/smb3plus-current66-source-1031-v2/joint'
M,B=G.M,G.B
sha=B.sha
BS=None
original_app=M.T.app

def typed_app(q,tr):
 b=q.b;form=q.get('M3RenderForm');f=form if form<7 else 0
 start=address(b,'M3SetFrame::Chr');seen=[];rewritten=[]
 for w in tr:
  w=dict(w)
  if w['bank']==90 and w['pc'] in[start+12,start+17]:
   index=0 if w['pc']==start+12 else 1
   assert w['opcode']==133 and w['address']==address(b,'R0')+index,w
   table='M3ChrLoTableLo' if index==0 else 'M3ChrLoTableHi'
   expected=b['raw'][location(b,table)+f]
   assert w['value']==expected,(w,expected,form)
   w['value']=('typed_low_pointer',index,f);seen.append(index)
  rewritten.append(w)
 assert len(seen)%2==0 and seen==[0,1]*(len(seen)//2),seen
 return original_app(q,rewritten)

def graphics():
 old,new=BS;rows=[];deltas=collections.Counter()
 for variant,form,frame,flags in itertools.product(range(4),range(7),range(81),[48,49,113,241]):
  results=[]
  for b in BS:
   q=G.seed(b,variant,form,frame,1);c,tr,path,info=M.T.invoke(q,'M3Graphics',a=91,x=3,y=7,p=flags)
   results.append((M.regs(c),typed_app(q,tr),q.m.banks[:],bytes(q.m[0x5c00:0x5e00]),c.processorCycles))
  assert results[0][:-1]==results[1][:-1],('exact graphics',variant,form,frame,flags)
  deltas[results[1][-1]-results[0][-1]]+=1
 return dict(pairs=4*7*81*4,AXYP_SP_final_private_RAM_maps_and_all_ordered_writes_exact=True,CPU_delta_histogram=dict(deltas),
  only_transient_pointer_exception='Exactly bank90 M3SetFrame::Chr+12/+17 STA zp R0/R1; actual compiled table value required, ordered symbolic form pointer compared. Final high-pointer stores and all other scratch/application writes exact.')

def helper():
 count=0;deltas=collections.Counter()
 for f,frame,flags in itertools.product(range(7),range(81),range(64)):
  pair=[];p=48|sum(bit for i,bit in enumerate([1,2,4,8,64,128])if flags>>i&1)
  for b in BS:
   q=G.seed(b,3,f,frame,1);q.m.page(2,91);q.set('CurrentBankC',219)
   lo=b['raw'][location(b,'M3ChrLoTableLo')+f];hi=b['raw'][location(b,'M3ChrLoTableHi')+f];q.put(R0=lo,R1=hi)
   c,tr,path,info=M.T.invoke(q,'MbFloatReadChrLow',a=91,x=f,y=frame,p=p)
   assert(c.x,c.y,c.p,c.sp)==(f,frame,p,253)
   pair.append((M.regs(c),original_app(q,tr),c.processorCycles))
  assert pair[0][:2]==pair[1][:2],(f,frame,p,pair)
  deltas[pair[1][2]-pair[0][2]]+=1;count+=1
 # The genuine caller clamps any invalid form, while old helper's form5 special case stays typed to form5.
 invalid=0
 for f,flags in itertools.product(range(7,256),[48,49,113,241]):
  pair=[]
  for b in BS:
   q=G.seed(b,3,f,14,1);q.m.page(2,91);q.set('CurrentBankC',219)
   c,tr,path,info=M.T.invoke(q,'M3SetFrame',a=91,x=14,y=7,p=flags)
   pair.append((M.regs(c),typed_app(q,tr),q.m.banks[:]))
  assert pair[0]==pair[1],('genuine invalidform clamp',f,flags);invalid+=1
 return dict(full64flags_typed_form_frame_pairs=count,invalid_form_actual_caller_pairs=invalid,CPU_delta_histogram=dict(deltas),scope='Actual helper typed X0..6,Y0..80. Arbitrary private-helper X is not an unchanged ABI claim.')

def pixels():
 b=BS[1];donor=Path('C:/NES/the stash/Super Mario Bros. 3+.nes').read_bytes()[16+524288:];chrdata=b['raw'][16+128*8192:]
 records={(q['character'],q['form'],q['frame'],q['facing']):q for q in json.loads(B.read(G.A/'draw-consumers.json'))};okay=0;unsupported=[]
 for variant,form,frame,face in itertools.product([2,3],range(7),range(81),[1,2]):
  q=G.seed(b,variant,form,frame,face);M.T.invoke(q,'M3Graphics');page=q.get('SmChrBank')+256*q.get('M3SpritePageHi');ptr=q.get('SmPosePtr')+256*q.get('SmPosePtr',1);size=q.m[ptr]
  assert 0<size<=24 and size%4==0
  parts=[list(q.m[ptr+1+i:ptr+5+i])for i in range(0,size,4)];source=records[variant,form,frame,64 if face==1 else 0];raw=bytes.fromhex(source['original_OAM']);src=[list(raw[i:i+4])for i in range(0,24,4)]
  actual=G.pixels(parts,chrdata,page);expected=G.pixels(src,donor,source['original_page'],(64,160),True)
  if actual!=expected:
   assert frame in[24,25,67,68],('unexpected original pixel mismatch',variant,form,frame,face)
   unsupported.append(dict(variant=variant,form=form,frame=frame,face=face,target_pixels=len(actual),source_pixels=len(expected)));continue
  okay+=1
 assert okay==2156 and len(unsupported)==112
 return dict(source_exact_pixel_cases=okay,retained_unsupported_disabled_Kuribo_records=unsupported,all81frames_audited=True,no_palette_or_CHR_change=True)

def regressions():
 import smb3plus_gravity_regressions_1031_v1 as T
 T.O=O;T.J=J;T.P=P;M.T.app=typed_app
 try:T.main()
 finally:M.T.app=original_app
 return json.loads((O/'regressions-v1.json').read_text())

def menu():
 p=R/'tools/audit/smb3plus_menu_controls_1031_v1.py';s=p.read_text();s=s.replace("O=R/'build/smb3plus-menu-host-1031-v4';J=O/'joint'",f"O=R/{O.relative_to(R).as_posix()!r};J=O/'joint'").replace("P=R/'build/smb3plus-peach-float-host-1031-v4/joint'",f"P=R/{P.relative_to(R).as_posix()!r}")
 s=s.replace("stage['status_names'][variant]","['MARIO3 ','LUIGI3 ',' TOAD3 ',' PEACH3'][variant]").replace("stage['limits']","stage['reason']")
 ns={'__file__':str(p),'__name__':'factored_current68_menu'};exec(compile(s,str(p),'exec'),ns);ns['main']();return json.loads((O/'menu-controls-v1.json').read_text())

def vectors():
 p=R/'tools/audit/smb3plus_gravity_vectors_1031_v1.py';s=p.read_text().replace('smb3plus-peach-gravity-consumer-1031-v1',O.name)
 ns={'__file__':str(p),'__name__':'factored_current68_vectors'};exec(compile(s,str(p),'exec'),ns);ns['main']();return json.loads((O/'vectors-v1.json').read_text())

def whole():
 p=R/'tools/audit/smb3plus_whole_controller_edges_1031_v1.py';s=p.read_text().replace('smb3plus-whole-controller-edges-1031-v1','smb3plus-low-factor-whole-controller-1031-v1').replace('smb3plus-peach-complete-controller-1031-v3',O.name)
 s=s.replace('text=prior.read_text()',"text=prior.read_text().replace('for i in range(8):bus.ram','for i in range(4):bus.ram')")
 ns={'__file__':str(p),'__name__':'factored_current68_controller'};exec(compile(s,str(p),'exec'),ns);ns['main']();return json.loads((R/'build/smb3plus-low-factor-whole-controller-1031-v1/probe.json').read_text())

def foreign():
 import cf_bt_shared_foreign_main_v1 as T
 T.J=J;T.P=P;T.O=R/'build/smb3plus-low-factor-foreign-main-1031-v1';T.main();return json.loads((T.O/'controls.json').read_text())

def main():
 global BS
 parser=argparse.ArgumentParser();parser.add_argument('--check',required=True,choices=['graphics','helper','pixels','regressions','menu','vectors','whole','foreign']);a=parser.parse_args()
 stage=json.loads(B.read(O/'source-stage.json'));B.bound(stage);assert stage['candidate']==sha(J/'candidate.nes')=='e54b91fa15b335bb17fd24fa7a0b667ef50bf31c8fad900d6c1a1ec38526116a'
 BS=[scoped_load(p/'candidate.nes')for p in[P,J]]
 out=O/(a.check+'-factor-controls-v1.json');assert not out.exists()
 result=globals()[a.check]();q=dict(passed=True,source_CPU=True,native=False,candidate=stage['candidate'],parent=sha(P/'candidate.nes'),check=a.check,result=result,bindings={str(p.resolve()):sha(p)for p in[Path(__file__),Path(G.__file__),Path(K.__file__),O/'source-stage.json',P/'candidate.nes',P/'candidate.dbg',J/'candidate.nes',J/'candidate.dbg',J/'src/smb3_mario_render.s',J/'src/smb3_mario_art.inc']});B.write(out,json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=True,check=a.check,out=str(out),sha256=sha(out))))
if __name__=='__main__':main()
