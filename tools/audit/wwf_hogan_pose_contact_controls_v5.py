"""Original pose records/pixels and coherent native one-life WIP contact."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import wwf_hogan_runtime_controls_v3 as V
from ff_wram_host_isr_v4 import clone
from check_tmnt_render_oa import address
from verify_native_relocation import NesMPU
H=V.H;T=V.T;J=R/'build/wwf-hogan-natural-source-v15/joint';O=R/'build/wwf-hogan-pose-contact-controls-v5'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not O.exists();O.mkdir();q=dict(passed=False,native=False,poses=[],injury=[])
 try:
  b=T.qualified(J/'candidate.nes');V.J=J;base=V.make(b)
  artpath=R/'build/wwf-roster-source-review-v1/wrestlers.json';art=json.loads(artpath.read_text());chrdata=(artpath.parent/'wrestlers-pages.chr').read_bytes()
  poses=[p for p in art['poses']if p['character']==5];pages=sorted({p['packed_page']for p in poses})
  for pose in poses:
   for face in [0,1]:
    m,_=clone(base,NesMPU(memory=base));H.put(m,Player_X_Position=80,Player_Y_Position=128,GuestOamRotationActive=0,RgOamRotation=0,CurrentOAMOffset=0)
    m.ram[2][0x32]=pose['group'];m.ram[2][0x34]=pose['frame'];m.ram[2][0x3a]=face
    H.invoke(m,'WfGraphics');H.invoke(m,'WfDrawBody');H.native_publish(m)
    off=address(b,'WfRenderBuffer')-0xc000;record=[4*len(pose['packed_8x16_cells'])]
    for cell in pose['packed_8x16_cells']:record.extend([cell['page_tile'],cell['role']|(64 if face else 0),cell['y']&255,((pose['width']-cell['x'])if face else cell['x'])&255])
    assert list(m.ram[2][off:off+len(record)])==record
    actual=list(m[512:512+H.get(m,'CurrentOAMOffset')]);assert len(actual)==4*len(pose['packed_8x16_cells'])
    sourcepage=pose['packed_page'];target=546+pages.index(sourcepage);opaque=0;colours=[]
    originx=80+(m.ram[2][0x36]if m.ram[2][0x36]<128 else m.ram[2][0x36]-256)
    originy=128+36-m.ram[2][0x42]+(m.ram[2][0x38]if m.ram[2][0x38]<128 else m.ram[2][0x38]-256)
    for i,cell in enumerate(reversed(pose['packed_8x16_cells'])):
     y,tile,attr,x=actual[4*i:4*i+4];cx=pose['width']-cell['x']if face else cell['x']
     assert[y,tile,attr,x]==[(originy+cell['y'])&255,cell['page_tile'],cell['role']|(64 if face else 0)|8,(originx+cx)&255],(pose['group'],pose['frame'],face,i,actual[4*i:4*i+4],cell)
     at=(tile&1)*4096+(tile&254)*16;physical=m.chr_latches[at//1024];assert physical==target
     data=b['raw'][1048592+physical*1024+(at&1023):1048592+physical*1024+(at&1023)+32]
     original=chrdata[sourcepage*1024+(cell['page_tile']&254)*16:sourcepage*1024+(cell['page_tile']&254)*16+32]
     assert data==original
     palette=[0,40,39,23]if cell['role']==0 else[0,22,5,15]
     for dy in range(16):
      a=(dy//8)*16+dy%8
      for dx in range(8):
       bit=dx if face else 7-dx;v=((data[a]>>bit)&1)|(((data[a+8]>>bit)&1)<<1)
       if v:opaque+=1;colours.append(palette[v])
    q['poses'].append(dict(group=pose['group'],frame=pose['frame'],face=face,parts=len(actual)//4,page=target,opaque_pixels=opaque,original_colour_digest=hashlib.sha256(bytes(colours)).hexdigest(),source_patterns_OAM_mirror_roles_exact=True))
  # Native injury uses a deliberately explicit one-life basic-WIP policy.
  # The old decline returned selected29 and poisoned PlayerStatus29; the
  # preserved negative is bound below. No source HP is silently rewritten.
  for status in [0,1,2]:
   for bits in range(64):
    m,_=clone(base,NesMPU(memory=base));H.put(m,PlayerStatus=status,GameEngineSubroutine=8,InjuryTimer=0,MmDeathFlag=0,ObjectOffset=0)
    source=bytes(m.ram[2]);p=0x30|(bits&15)|((bits&48)<<2)
    H.invoke(m,'ForceInjury',p=p)
    assert H.get(m,'GameEngineSubroutine')==11 and H.get(m,'Player_Y_Speed')==252 and H.get(m,'TimerControl')==255
    assert H.get(m,'PlayerStatus')==0 and bytes(m.ram[2])==source,(status,bits,H.get(m,'PlayerStatus'),[(hex(0xc000+i),a,v)for i,(a,v)in enumerate(zip(source,m.ram[2]))if a!=v])
    q['injury'].append([status,bits,11])
  q.update(passed=True,candidate=sha(J/'candidate.nes'),original_pose_face_cases=len(q['poses']),actual_native_injury_cases=len(q['injury']),CPU='NesMPU actual NES binary ADC/SBC with D retained',limits=['Pose/face fields are explicitly selected API units after real load and constructor. This is source pixel/OAM equality, not a native raster claim.','Native one-life contact is an explicit basic-WIP adaptation. Original WWF endurance/hurt-threshold integration is still unqualified.'])
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(V.__file__),J/'candidate.nes',J/'candidate.dbg',J.parent/'source-stage.json',R/'build/wwf-hogan-native-injury-probe-v1/controls.json',R/'build/wwf-roster-source-review-v1/wrestlers.json',R/'build/wwf-roster-source-review-v1/wrestlers-pages.chr']}
  (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q.get(k)for k in['passed','candidate','original_pose_face_cases','actual_native_injury_cases','error']}))
if __name__=='__main__':main()
