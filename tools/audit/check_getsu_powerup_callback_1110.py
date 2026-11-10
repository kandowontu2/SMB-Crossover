"""Fund Getsu's missing native powerup callback by factoring its own renderer."""
import argparse,hashlib,json
from pathlib import Path
from tempfile import TemporaryDirectory
import check_getsu_fuma_host_render_1110 as Render
import prepare_getsu_earned_powerups_1110 as Earned
from check_tmnt_render_oa import address

R=Render.R
BASE=R/'build/getsu-current-native-1110/candidate.nes'
PIN='095c164a574479401f284c1669264034404b83cb2e1d6cdc4a1f5ef37dcafe79'
K=16+128*8192+991*1024
ATLAS=16+128*8192+990*1024
OLD=R/'build/getsu-host-render-1110-v3/proof.json'
def sha(data):return hashlib.sha256(data).hexdigest()

def once(s,a,b):
 assert s.count(a)==1,(a,s.count(a))
 return s.replace(a,b,1)

def source():
 s=Render.SOURCE.read_text()
 stand='    lda #12\n    sta GfBodyPose\n'
 face='    lda GfFacing\n    sta GfBodyFacing\n'
 assert s.count(stand)==3 and s.count(face)==5
 s=once(s,stand+'    lda #3\n    sta UpperPose\n'+face+'    sta UpperFacing',
          '    jsr Standing\n    lda #3\n    sta UpperPose\n    lda GfFacing\n    sta UpperFacing')
 assert s.count(stand+face)==2
 s=s.replace(stand+face,'    jsr Standing\n')
 s=once(s,'Done:\n    rts\n.endproc\n\n; Donor fixed15',
          'Done:\n    rts\nStanding:\n'+stand+face+'    rts\n.endproc\n\n; Donor fixed15')
 s=once(s,'    lda GfVXLo\n    jmp Subtract\nLeft:',
          '    lda GfVXLo\n    sta SpeedLo\n    jmp Subtract\nLeft:')
 s=once(s,'    sta SpeedHi\n    lda SpeedLo\nSubtract:\n    sta SpeedLo\n',
          '    sta SpeedHi\nSubtract:\n')
 # Share the following NextWalkPose return; successful walking falls through.
 s=once(s,'    bcs Done\n    lda #0\n    sta WalkLo',
          '    bcs ::GfSharedReturn\n    lda #0\n    sta WalkLo')
 s=once(s,'    jmp NextWalkPose\nDone:\n    rts\n.endproc\n\n.proc NextWalkPose',
          '.endproc\n\n.proc NextWalkPose')
 # The early action rejection shares that same return.
 s=once(s,'    and #3\n    bne Done\n    lda GfVXHi',
          '    and #3\n    bne ::GfSharedReturn\n    lda GfVXHi')
 s=once(s,'    lda WalkIndex\n    cmp #4\n    bcc InRange\n    lda #0\n    sta WalkIndex\nInRange:\n    tay',
          '    ldy WalkIndex\n    cpy #4\n    bcc InRange\n    ldy #0\n    sty WalkIndex\nInRange:')
 s=once(s,'    sta UpperPose\n    rts\nWalkBody:',
          '    sta UpperPose\n::GfSharedReturn = *\n    rts\nWalkBody:')
 s=once(s,'    lda WalkBody,y\n    sta GfBodyPose',
          '    lda WalkUpper,y\n    sta UpperPose\n    clc\n    adc #3\n    sta GfBodyPose')
 s=once(s,'    lda WalkUpper,y\n    sta UpperPose\n::GfSharedReturn',
          '::GfSharedReturn')
 s=once(s,'WalkBody:  .byte 4,5,6,5\n','')
 return s

def compose(out):
 raw=BASE.read_bytes();assert sha(raw)==PIN;b=Render.Owner.Page.bundle()
 # Exact symbol carrier; renderer bytes themselves are checked against current.
 before,labels=Render.assemble(out,b)
 assert raw[K+0x4be:K+0x7f2]==before
 old_labels=json.loads(OLD.read_text())['labels'];assert labels==old_labels
 original=Render.SOURCE
 with TemporaryDirectory(dir=out) as folder:
  p=Path(folder)/'funded.s';p.write_text(source())
  try:Render.SOURCE=p; code,labels=Render.assemble(out,b)
  finally:Render.SOURCE=original
 # The factored renderer releases its final19 bytes, before the existing sword loop.
 assert len(code)==len(before)-20,(len(code),len(before))
 kernel=bytearray(raw[K:K+2048]);kernel[0x4be:0x7f2]=code+b'\xea'*20
 target=0xa000+0x4be+len(code)
 generic=address(b,'GuestPowerupUpdate');assert generic==0xb299
 packet=bytes.fromhex('8d6a01')+bytes((0xa9,generic&255,0x8d,0x6c,1,0xa9,generic>>8,0x8d,0x6d,1,0xa9,0x8a,0x20,0x5a,1,0x60))
 assert len(packet)==19
 kernel[target-0xa000:target-0xa000+19]=packet
 assert kernel[99:102]==bytes.fromhex('1860ea')
 kernel[99:102]=b'\x4c'+target.to_bytes(2,'little')
 kernel[78:81]=b'\x4c'+labels['GfSetColors'].to_bytes(2,'little')
 cookie=bytes((0xa7,42,1))+bytes.fromhex(sha(kernel+raw[ATLAS:ATLAS+1024]))[:13]
 rows=[];trial=bytearray(raw)
 for at,new in ((K,bytes(kernel)),(16+65*8192+0xb81,cookie)):
  old=bytes(trial[at:at+len(new)]);trial[at:at+len(new)]=new
  rows.append(dict(file_offset=at,old_hex=old.hex(),new_hex=new.hex()))
 return b,Earned.D.Current.Getsu.W.bundle(bytes(trial)),rows,labels,target,cookie

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
 a=p.parse_args();out=a.output.resolve();assert out.is_relative_to(R/'build');out.mkdir(exist_ok=True)
 before,after,rows,labels,target,cookie=compose(out)
 print('Linked',sha(after['raw']),hex(target),flush=True)
 # Actual native collection handler plus ordinary GameLoop advancement.
 episodes=Earned.ingress(after)
 for e in episodes:
  if e['kind'] in (0,1):
   assert e['final_engine']==8 and e['final_active']==0 and e['final_status']==e['initial_status']+1,e
   assert e['sampled_game_loops']==60,e
 print('Native pickup and60-frame transformation passed',flush=True)
 seed=Earned.H.prepare(after)
 # Reproduce the resident service's mapped RAM2 workspace for direct draw tests.
 seed[0x5116]=2
 Render.N.put(seed,CurrentBankC=2)
 seed[0xc030]=0
 seed[0xc021]=seed[Render.STATE['GfClock']]
 kernel=after['raw'][K:K+2048]
 gait=Render.gait(Render.Donor.ROM.read_bytes(),kernel[0x4be:0x7f2],labels)
 art=json.loads(Render.Owner.Page.ASSET.read_text())
 tiles={row['donor_tile']:row['atlas_tile'] for row in art['tiles']}
 pixels=Render.render(seed,labels,Render.Donor.DonorOam(Render.Donor.ROM.read_bytes()),tiles)
 palette=Render.palette_lifecycle(seed,labels)
 print('Original gait, native pixels and palette passed',gait,flush=True)
 Render.N.put(seed,CurrentCHRBank=0,X5ChrMode=0)
 vectors=Render.interrupt_controls(seed,labels)
 print('Original gait, pixels, palette and actual vector cuts passed',gait,flush=True)
 q=dict(passed=True,ROM_written=False,parent_SHA256=PIN,expected_memory_only_SHA256=sha(after['raw']),
        patches=rows,labels=labels,powerup_target=target,cookie=cookie.hex(),episodes=episodes,
        gait=gait,render=pixels,palette=palette,vectors=vectors,
        scope='Own renderer factor releases20 bytes;19 for missing row33 callback. Actual item handler and60 GameLoops.',
        bindings={str(p.relative_to(R)):sha(p.read_bytes()) for p in (Path(__file__).resolve(),Render.SOURCE,BASE,OLD,Path(Earned.__file__))})
 (out/'proof.json').write_text(json.dumps(q,indent=2)+'\n')

if __name__=='__main__':main()
