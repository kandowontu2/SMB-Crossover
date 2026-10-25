"""Controller-only use of crates, wall climb, whip-safe jumps and wall arrows."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json

ROOT=Path(__file__).resolve().parents[2]

WRAPPER='''
local lastArrowPipe=0
local arrowStage='align';local arrowShot=false
local function solid(c,x,y)local t=c.block(x,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 end
local observation
if ROSTER_CONFIG.name=='darkwing'then
 observation=assert(io.open(ROSTER_CONFIG.out..'native-controls.csv','w'))
 observation:write('frame,x,y,hp,adaptor,mode,gas,hang,pipeStage,arrows\\n')
end
return function(c)
 local b=base(c)
 if observation then
  local arrows=0;for i=0,9 do if c.r('RgShotType',i)==6 then arrows=arrows+1 end end
  observation:write(table.concat({c.frame,c.x,c.y,c.r('DwHealth'),c.r('DwAdaptor'),c.r('DwMode'),c.r('DwGas'),c.r('DwHang'),arrowStage,arrows},',')..'\\n');observation:flush()
 end
 -- Actual shooter combat before attempting a ground jump into an enemy.
 if c.char==2 or c.char==3 or c.char==9 or(c.char==12 and c.r('DarkwingVariant')~=0)then
  local e=c.enemy()
  if c.grounded and e and e.dx>0 and e.dx<120 and math.abs(e.y-c.y)<42 then
   if c.r('PlayerFacingDir')~=1 then return{right=true}end
   return{b=c.r('FrameCounter')%12<2}
  end
 end
 if c.char==4 and c.r('Z2Variant')==0 and c.grounded and b.a then
  b.b=false
  if c.r('RgAttack')~=0 then b.a=false;b.right=false;b.left=false end
 end
 if c.char==10 and c.r('XgWall')~=0 then
  local face=c.r('PlayerFacingDir');local probe=c.x+(face==1 and 21 or-5)
  return{right=face==1,left=face==2,up=true,a=not c.lastA and not solid(c,probe,c.y+3)}
 end
 if c.char==14 then
  b.b=false
  local held=c.r('CdHeld');local e=c.enemy()
  local close=e and e.dx> -16 and e.dx<56 and math.abs(e.y-c.y)<46
  if held~=0 then
   if close and c.grounded then
    if c.r('PlayerFacingDir')~=1 then return{right=true}end
    if e.dx<22 then return{down=true}end
    return{b=c.r('CdThrowAge')==0 and(c.r('SavedJoypadBits')&64)==0}
   end
  else
   local nearby=false
   for i=0,5 do
    if c.r('CdBoxKind',i)~=0 and c.r('CdBoxMode',i)==0 then
     local wx=c.r('CdBoxX',i)+256*c.r('CdBoxPage',i)
     if math.abs(wx-c.x)<=20 and math.abs(c.r('CdBoxY',i)-c.y)<40 then nearby=true end
    end
   end
   local x=c.x+(c.r('PlayerFacingDir')==1 and 20 or-4)
   local t=c.block(x,c.y+20)
   if nearby or t==0x51 or t==0x52 then b.b=(c.r('SavedJoypadBits')&64)==0 end
   if close and c.grounded and not c.lastA then b.a=true;b.b=false end
  end
  if not c.grounded and c.vy>=128 then b.a=true end
 end
 -- Darkwing's real Arrow adaptor creates a native climbable wall actor.
 -- Use it for the tall pipes; no ability/equipment is granted by the script.
 if c.char==12 and c.r('DarkwingVariant')~=0 then
  local pipe
  if c.x>=660 and c.x<778 then pipe=736 elseif c.x>=836 and c.x<954 then pipe=912 end
  if pipe and c.r('DwAdaptor')==2 then
   if lastArrowPipe~=pipe then lastArrowPipe=pipe;arrowStage='align';arrowShot=false end
   if c.r('DwMode')==0 then return{select=(c.r('SavedJoypadBits')&32)==0}end
   if c.r('DwHang')>=128 then
    arrowStage='cross';return{right=true,a=not c.lastA}
   end
   if arrowStage=='align'then
    local target=pipe-34
    if c.grounded and c.x>=target and c.x<=target+2 then arrowStage='rise'
    else return{right=c.x<target,left=c.x>target+2}end
   end
   if arrowStage=='rise'then
    local shoot=not arrowShot and not c.grounded and c.y<=128
    if shoot then arrowShot=true end
    if arrowShot and c.grounded then arrowStage='rise';arrowShot=false end
    return{a=c.grounded and not c.lastA or c.vy>=128,b=shoot}
   end
   return{right=true,a=c.vy>=128}
  end
  if not pipe and c.r('DwMode')~=0 then return{select=(c.r('SavedJoypadBits')&32)==0}end
  if not c.grounded and c.vy>=128 then b.a=true end
 end
 return b
end
'''


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    path=a.rom.with_suffix('.dbg');debug=path.read_text()if path.exists()else gzip.decompress(a.rom.with_suffix('.dbg.gz').read_bytes()).decode()
    syms={}
    for line in debug.splitlines():
        if line.startswith('sym\t'):
            fields=dict(q.split('=',1)for q in line[4:].split(',')if '='in q)
            if 'val'in fields:syms[fields['name'].strip('"')]=int(fields['val'],0)
    names=['CdHeld','CdThrowAge','CdBoxKind','CdBoxMode','CdBoxX','CdBoxPage','CdBoxY',
        'DwHealth','DwAdaptor','DwMode','DwGas','DwHang','FrameCounter','RgShotType','DarkwingVariant','Z2Variant','XgWall']
    aliases={n:syms[n]for n in names}
    text='-- Metadata aliases only; no writes to emulated state.\n'+''.join('L.'+n+'='+str(v)+'\n'for n,v in aliases.items())
    base=ROOT/'tools/playthroughs/full_roster_policy_og.lua'
    text+='local base=(function()\n'+base.read_text()+'\nend)()\n'+WRAPPER
    out=a.output/'policy.lua';out.write_text(text)
    q=dict(prepared=True,ROM_sha256=hashlib.sha256(a.rom.read_bytes()).hexdigest(),memory_writes=False,game_changes=False,
        base_policy_sha256=hashlib.sha256(base.read_bytes()).hexdigest(),policy_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),metadata_aliases=aliases,
        scope='Native controller attempts: retain/reuse existing crates, grounded projectile combat, wait for Link sword lock before jumping, use Ryu wall climb and Darkwing Arrow adaptor. Equipment must actually be acquired; no native state/physics or death assertions are changed. Discovery remains unverified until an exact independent replay.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
