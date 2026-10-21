"""Compiled exact normal head/side fixtures; never controller route evidence."""
from pathlib import Path
import hashlib,importlib.util,json,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
D=V/'root49-sophia-source-terrain-ib';G=V/'ryu49-head-status-bridge-g'
sys.path.insert(0,str(G));s=importlib.util.spec_from_file_location('terrain_bus',G/'check.py');g=importlib.util.module_from_spec(s);s.loader.exec_module(g);CPU=g.loadcpu().NesMPU
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 out=D/'compiled-id.json';assert not out.exists();report=dict(status='RUNNING',maps=[],script_sha256=sha(__file__),scope='Explicit compiled component fixtures against source rational normal geometry, not Mesen or route evidence. Corner calcAxis/fullfootspan and rotated forms remain required.',retained_IC_negative='IC completed mapper3 fixtures but attempted nonexistent mapper5 BankShadow seed. Seed it only for mapper3; no runtime source changes.')
 try:
  for mapper in ['mmc3','mmc5']:
   im=g.Image(D/'source/build'/('smb-crossover-'+mapper+'.nes'));old=g.Image(V/'root49-sophia-source-body-hs/source/build'/im.path.name);L=im.ram
   for n in ['NonMaskableInterrupt','IrqScrollSplit','MegaManVineAnchor']:
    assert old.hook(n)==im.hook(n),('Original resident continuation/bank/eightbytes',mapper,n)
   assert all(im.ram[n]==a for n,a in old.ram.items())
   cases=[]
   def execute(name,entry,fields,tiles,y=30,prior=None):
    ram=bytearray(10240)
    def put(n,v):
     n,_,off=n.partition('+');ram[g.at(L[n]+int(off or 0))]=v&255
    for seg in im.segs.values():
     if seg['name']=='SMCCODE':ram[seg['start']:seg['start']+seg['size']]=im.raw[seg['ooffs']:seg['ooffs']+seg['size']]
    defaults=dict(SelectedCharacter=11,OperMode=1,GameEngineSubroutine=8,Player_State=1,Player_Y_HighPos=1,Player_PageLoc=2,Player_X_Position=228,Player_Y_Position=95,Player_Y_Speed=253,PlayerFacingDir=1,RyWallSupported=1,RyWallOldX=228,RyWallOldPage=2,RyWallOldY=98,RgDoubleJump=1)
    defaults.update({'MmVY+2':253,'MmYFraction+1':128,'CurrentBankC':36})
    if im.mapper==4:defaults['BankShadow']=0x47
    defaults.update(fields)
    for n,v in defaults.items():put(n,v)
    for x,yy,tile in tiles:
     # Actual native two-page column-major block-buffer layout.
     address=L['Block_Buffer_1']+(x//256%2)*208+(x%256//16)+((yy-32)//16)*16
     ram[g.at(address)]=tile
    bank=im.hook(entry)['physical_bank'];put('CurrentBank',bank|(128 if im.mapper==5 else 0))
    sp=0xe9;ram[0x101+sp]=(g.RET-1)&255;ram[0x102+sp]=(g.RET-1)>>8
    got=g.execute(im,CPU,ram,[11,0,y,0x81,sp],{0x8000:62,0xa000:bank,0xc000:36,0xe000:63},im.hook(entry)['address'],g.RET,native_status=True)
    def read(n):
     n,_,off=n.partition('+');return got['ram'][g.at(L[n]+int(off or 0))]
    assert got['regs'][4:]==[sp+2,g.RET] and got['ram'][0x101+sp:0x200]==ram[0x101+sp:0x200],('Caller stack',name)
    cases.append(dict(name=name,entry=entry,cycles=got['cycles'],A=got['regs'][0],X=got['regs'][1],Y=got['regs'][2],P=got['regs'][3],writes=len(got['trace'])))
    return got,read
   for yf in [0,1,127,128,129,255]:
    got,rd=execute('premature-ceiling-'+str(yf),'SophiaSourceHeadProbe',{'Player_Y_Position':96,'MmYFraction+1':yf},[(736,96,0x54)])
    assert got['regs'][0]==0 and rd('SmCeilingHit')==0 and rd('Player_Y_Position')==96,'Source head below ceiling must not bump'
   for xcell in [736,752]:
    for fine in [0,1,255]:
     got,rd=execute('source-real-head-%s-%s'%(xcell,fine),'SophiaSourceHeadProbe',{'MmYFraction':fine},[(xcell,96,0x54)])
     # yf=.5+epsilon, PY95 => top112+epsilon: only exact.5 is contact.
     expected=0x54 if fine==0 else 0
     assert got['regs'][0]==expected,('Exact head boundary',xcell,fine,got['regs'])
     if expected:assert [rd('Player_Y_Position'),rd('MmYFraction'),rd('MmYFraction+1'),rd('SmCeilingHit'),rd('R4')]==[95,0,128,128,4]
   for xf in [0,1,127,128,129,255]:
    for row in [33,34,35,36]:
     got,rd=execute('no-above-body-side-%s-%s'%(xf,row),'SophiaSourceSideProbe',{'Player_Y_Position':112,'MmYFraction+1':0,'MmXFraction+1':xf,'R0':2 if row<35 else 1},[(736,112,0x54),(752,112,0x54)],y=row)
     assert got['regs'][0]==0,('Old upper-side point lies above source',xf,row)
   for side in [1,2]:
    for vx in [1,255,0]:
     # Direct wall consumer uses the actual source query cell, with source
     # exact half-pixel separations on both sides and page-carry boundary.
     fields={'Player_Y_Position':112,'MmYFraction+1':0,'R0':side,'SmHeadX':240,'SmHeadPage':2,'MmVX+2':vx,'MmVX+1':64,'MmVX':1,'Player_X_Speed':vx}
     got,rd=execute('wall-halfpixel-%s-%s'%(side,vx),'SophiaSourceWall',fields,[])
     assert [rd('MmXFraction'),rd('MmXFraction+1')]==[0,128]
     assert [rd('Player_PageLoc'),rd('Player_X_Position')]==([2,222]if side==1 else[3,1])
     cancel=(side==1 and vx<128)or(side==2 and vx>=128)
     assert [rd('MmVX'),rd('MmVX+1'),rd('MmVX+2')]==([0,0,0]if cancel else[1,64,vx]),('Directional velocity',side,vx)
   for jumped in [0,1]:
    for water,hover in [(0,0),(1,0),(0,1)]:
     got,rd=execute('post-ceiling-%s-%s-%s'%(jumped,water,hover),'SophiaSourceAfterTerrain',{'SmCeilingHit':128,'SmTempY':95,'Player_Y_Position':97,'Player_Y_Speed':1,'MmYFraction+1':0,'RgDoubleJump':jumped,'MmUnderwater':water,'XgHoverActive':hover},[])
     assert [rd('Player_Y_Position'),rd('MmYFraction'),rd('MmYFraction+1'),rd('SmCeilingHit'),rd('XgRise')]==[95,0,128,0,0]
     displace=jumped and not water and not hover
     assert [rd('MmVY'),rd('MmVY+1'),rd('MmVY+2')]==([85,213,0]if displace else[0,0,253])
     assert bool(rd('Square1SoundQueue')&2)==(not water and not hover),'Dry non-hover ceiling cue'
   report['maps'].append(dict(mapper=mapper,ROM=im.metadata(),cases=cases,NMI_IRQ_Vine_literal=True,old_RAM_literal=True))
   out.write_text(json.dumps(report,indent=2)+'\n')
  report['status']='PASS_COMPILED_NORMAL_SOURCE_TERRAIN_FIXTURES'
 except Exception as exc:report.update(status='FAIL_RETAINED',error=str(exc));raise
 finally:out.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(dict(status=report['status'],cases=sum(len(x['cases'])for x in report['maps']))))


if __name__=='__main__':main()
