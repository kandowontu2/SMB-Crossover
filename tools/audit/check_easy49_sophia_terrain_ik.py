"""Bind the IK brick-none/coin correction and retained normal fixtures."""
from pathlib import Path
import hashlib,importlib.util,json,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
D=V/'root49-sophia-source-terrain-ik'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
parent=R/'tools/audit/check_easy49_sophia_terrain_ig.py'
assert sha(parent)=='477405b60ed26a1d42cb428e31c885d68a19a66a5c5d1a1fa989ad1f78004656'


def main():
 spec=importlib.util.spec_from_file_location('terrain_original_ig',parent)
 base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
 base.D=D
 base.main()                 # original 96 assertions, executed unchanged
 g=base.g;CPU=base.CPU
 out=D/'brick-none-ik.json';assert not out.exists()
 report=dict(status='RUNNING',script_sha256=sha(__file__),parent_checker_sha256=sha(parent),original96_sha256=sha(D/'compiled-ig.json'),maps=[],scope='Compiled seeded components only; full native callers and ordinary routes are separate.')
 try:
  for mapper in ['mmc3','mmc5']:
   im=g.Image(D/'source/build'/('smb-crossover-'+mapper+'.nes'));L=im.ram;cases=[]
   def execute(name,tile,fields):
    ram=bytearray(10240)
    def put(n,v):
     n,_,off=n.partition('+');ram[g.at(L[n]+int(off or 0))]=v&255
    for seg in im.segs.values():
     if seg['name']=='SMCCODE':ram[seg['start']:seg['start']+seg['size']]=im.raw[seg['ooffs']:seg['ooffs']+seg['size']]
    values=dict(SelectedCharacter=11,OperMode=1,GameEngineSubroutine=8,Player_State=1,Player_Y_HighPos=1,Player_PageLoc=2,Player_X_Position=228,Player_Y_Position=95,Player_Y_Speed=253,RyWallSupported=1,RyWallOldX=228,RyWallOldPage=2,RyWallOldY=98,RgDoubleJump=1)
    values.update({'MmVY+2':253,'MmYFraction+1':32,'CurrentBankC':36})
    if im.mapper==4:values['BankShadow']=0x47
    values.update(fields)
    for n,v in values.items():put(n,v)
    address=L['Block_Buffer_1']+(736//256%2)*208+(736%256//16)+((96-32)//16)*16
    ram[g.at(address)]=tile
    h=im.hook('SophiaSourceHeadProbe');bank=h['physical_bank'];put('CurrentBank',bank|(128 if im.mapper==5 else 0))
    sp=0xe9;ram[0x101+sp]=(g.RET-1)&255;ram[0x102+sp]=(g.RET-1)>>8
    got=g.execute(im,CPU,ram,[11,0,30,0x81,sp],{0x8000:62,0xa000:bank,0xc000:36,0xe000:63},h['address'],g.RET,native_status=True)
    def read(n):
     n,_,off=n.partition('+');return got['ram'][g.at(L[n]+int(off or 0))]
    assert got['regs'][4:]==[sp+2,g.RET]
    assert got['ram'][0x101+sp:0x200]==ram[0x101+sp:0x200]
    cases.append(dict(name=name,tile=tile,input=fields,cycles=got['cycles'],registers=got['regs'],canonical=[read(n)for n in ('Player_Y_Position','MmYFraction','MmYFraction+1','SmCeilingHit','R4')],writes=len(got['trace'])))
    return got,read
   for tile in [0xc2,0xc3]:
    for yf in [0,1,32,127,128]:
     got,rd=execute('coin-pickup-not-ground-%s-%s'%(tile,yf),tile,{'MmYFraction+1':yf})
     assert got['regs'][0]==tile
     assert [rd(n)for n in ['Player_Y_Position','MmYFraction','MmYFraction+1','SmCeilingHit','MmVY','MmVY+1','MmVY+2']]==[95,0,yf,0,0,0,253],('Coin changed solid geometry',tile,yf)
   for tile in [0x51,0x54,0xc0,0xc1,0x5f,0x60,0x61]:
    for water in [0,1]:
     for rise in [0,1]:
      for hover in [0,1]:
       none=hover or water and not rise
       hidden=tile in [0x5f,0x60]
       got,rd=execute('source-brick-state-%s-%s-%s-%s'%(tile,water,rise,hover),tile,dict(MmUnderwater=water,XgRise=rise,XgHoverActive=hover))
       if none and hidden:
        assert got['regs'][0]==0
        assert [rd(n)for n in ['Player_Y_Position','MmYFraction','MmYFraction+1','SmCeilingHit']]==[95,0,32,0],('Invisible brick-none collision',tile,water,rise,hover)
       else:
        assert got['regs'][0]==tile
        assert [rd(n)for n in ['Player_Y_Position','MmYFraction','MmYFraction+1','SmCeilingHit','R4']]==[95,0,128,128,0 if none else 4],('Canonical contact versus effect gate',tile,water,rise,hover)
   report['maps'].append(dict(mapper=mapper,ROM=im.metadata(),cases=cases))
  report['status']='PASS_COMPILED_SOURCE_BRICK_NONE_COINS_AND_ORIGINAL96'
 except Exception as exc:report.update(status='FAIL_RETAINED',error=str(exc));raise
 finally:out.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(dict(status=report['status'],additional_cases=sum(len(x['cases'])for x in report['maps']))))


if __name__=='__main__':main()
