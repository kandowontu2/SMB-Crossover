"""Read actual source body bounds and trace native body policy without patches."""
import collections,json
import prepare_shinobi_draw_reservation_1101_v26 as P
import check_shinobi_draw_reservation_1101_v26 as D
import check_hogan_current_bounded_v1 as M
from check_tmnt_render_oa import address
from link_pit_rygar_sophia_audit_cpu import scoped_load

O=P.R/'build/shinobi-pipe-clearance-1101-v27'


def main():
 b=scoped_load(P.O/'candidate.nes');lab=P.S.labels(P.R/'build/shinobi-hurt-layout-1101-v5/component.lbl')
 poses=json.loads((P.R/'build/shinobi-hurt-layout-1101-v5/pose-packets.json').read_text())['poses'];rows=[]
 for pose in sorted(set(z['pose']for z in poses)):
  m=D.preload(b);m[0xc300]=pose;m[0xc379]=128;m[0xc38f]=224
  c=D.run(m,lab['ShSourceBounds'],x=0)
  # Player native origin120/192 -> donor anchor128/224.
  box=[m[0xc000+i]+256*m[0xc001+i]for i in [8,10,12,14]]if c.p&1 else None
  rows.append(dict(pose=pose,supported=bool(c.p&1),source_box=box,native_relative=[box[0]-120,box[1]-120,box[2]-192,box[3]-192]if box else None))
 assert next(z for z in rows if z['pose']==0)['native_relative']==[0,16,-8,32]
 b['segs']['shinobi_rom']={'start':str(0xa800),'ooffs':str(16+65*8192+0x800)}
 for n,a in P.S.labels(P.R/'build/shinobi-scene-1101-v7/resident.lbl').items():
  if n.startswith('Sh')and 0xa800<=a<0xae00:b['syms'][n]={'val':str(a),'seg':'shinobi_rom'}
 m=M.fresh(b)
 M.put(m,SelectedCharacter=36,OperMode=1,OperMode_Task=3,FamilyMainCommit=1,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,Mirror_PPUCTRL=160,Player_X_Position=120,Player_Y_Position=176,Player_Y_HighPos=1,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,PlayerFacingDir=1,AreaType=1)
 M.invoke(m,'ShScene');M.put(m,GameEngineSubroutine=8,DisableScreenFlag=0,FrameCounter=1,SavedJoypadBits=0)
 for buffer in ['Block_Buffer_1','Block_Buffer_2']:
  at=address(b,buffer)
  for row in range(13):
   for col in range(16):m[at+row*16+col]=0x54 if row>=11 else 0
 names=['HuPlayerSubs','HuBody','HuBox','HuAdder','HuFullBox','HuMovement','MegaManCollisionBox','MegaManCollisionAdder','HotCollisionBox','HotCollisionAdder','LmBoundingBoxGate','BoundingBoxCore']
 points={address(b,n):n for n in names if n in b['syms']};points[0xd682]='ShBody';points[lab['ShHostMovement']]='ShHostMovement'
 events=[];cpu=M.NesMPU
 class Trace(cpu):
  def step(self):
   if self.pc in points:events.append(dict(name=points[self.pc],bank=m.rawtags[(self.pc-0x8000)//8192],size=M.get(m,'PlayerSize'),box=M.get(m,'Player_BoundBoxCtrl'),A=self.a,X=self.x,Y=self.y))
   if self.pc==address(b,'FarCallCommon')+3:events.append(dict(far_bank=self.a,target=M.get(m,'FarcallJmpTarget_SMC',1)+256*M.get(m,'FarcallJmpTarget_SMC',2)))
   if m[self.pc]in [0x8d,0x9d,0x99]and m[self.pc+1]+256*m[self.pc+2]==address(b,'PlayerSize'):events.append(dict(write_size=self.a,pc=self.pc,bank=m.rawtags[(self.pc-0x8000)//8192]))
   return super().step()
 M.NesMPU=Trace
 try:M.invoke(m,'PlayerCtrlRoutine')
 finally:M.NesMPU=cpu
 native=dict(size=M.get(m,'PlayerSize'),box=M.get(m,'Player_BoundBoxCtrl'),bbox=list(m[address(b,'BoundingBox_UL_Corner'):address(b,'BoundingBox_UL_Corner')+4]))
 # Explicit callback demonstrates its current independent fixed policy.
 r=M.invoke(m,'HuBody');explicit=dict(size=M.get(m,'PlayerSize'),box=M.get(m,'Player_BoundBoxCtrl'),return_C=bool(r['P']&1))
 q=dict(passed=True,ROM_sha256=P.S.sha(P.O/'candidate.nes'),source_bounds=rows,native_idle=native,explicit_HuBody=explicit,events=events,findings=['Import offset32 aligns donor feet to SMB surface; it is not a declaration that every donor body is32px tall.','Original stand pose0 bounds are40px tall: donorY-40..Y, native-relativeY-8..+32. Other pose bounds vary.','Native fixed body/probe policy must be assessed separately from original source terrain queries; no code changed.'],scope='Actual cached ShSourceBounds and a complete PlayerCtrlRoutine on explicit flat terrain; one native idle CPU trace, not native video/Main/ISR or natural enemy-contact proof.')
 (O/'body-policy-CPU.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
