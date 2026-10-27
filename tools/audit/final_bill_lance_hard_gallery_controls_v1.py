"""Finite compiled spatial contacts and literal prepared-finalizer controls."""
from pathlib import Path
import argparse,json,sys
from final_bill_lance_hard_gallery_source_v1 import PARENT,SHA,D,ROOT,sha,put,plans,OWNER_NAMES,EXTRA_OWNERS
from final_bill_lance_hard_gallery_source_v2 import BillArena
from link_pit_rygar_sophia_audit_cpu import scoped_load
from parodius_visibility_hud_static_startup_v1 import MOCK


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 ready=json.loads((a.ready/'proof.json').read_text());assert ready['ROM_sha256']==SHA and not ready['native_run'];b=scoped_load(PARENT/'candidate.nes')
 for n in EXTRA_OWNERS:
  if n in b['syms']and n not in OWNER_NAMES:OWNER_NAMES.append(n)
 rows=[]
 for variant in [0,1]:
  for plan in plans():
   for face in [1,2]:
    q=BillArena(b,variant);q.put(PlayerFacingDir=face,Player_MovingDir=face)
    for item in plan['grant_sequence']:q.grant(item)
    q.buttons(64);slot=None
    for tick in range(45):
     for i in range(10):
      x=q.get('RgShotX',i)+256*q.get('RgShotPage',i);y=q.get('RgShotY',i)-8
      if q.get('RgShotType',i)==plan['shot_type'] and not q.get('RgShotImpact',i) and (plan['shot_type']!=42 or not q.get('SsHidden',i))and abs(x-112)>=30 and 16<=x<232 and q.get('RgShotYHigh',i)==1 and 48<=y<192:slot=i;break
     if slot is not None:break
     q.buttons(0)
    assert slot is not None,(variant,plan['name'],face)
    x=q.get('RgShotX',slot)-6;y=q.get('RgShotY',slot)-8
    for n,v in [('Enemy_Flag',1),('Enemy_ID',6),('Enemy_State',0),('Enemy_X_Position',x),('Enemy_PageLoc',0),('Enemy_Y_Position',y),('Enemy_Y_HighPos',1),('Enemy_X_Speed',0),('Enemy_Y_Speed',0),('Enemy_X_MoveForce',0),('Enemy_Y_MoveForce',0),('Enemy_MovingDir',1),('Enemy_BoundBoxCtrl',9),('EnemyOffscrBitsMasked',0),('Enemy_CollisionBits',0),('Enemy_SprAttrib',0),('MmEnemyHealthLo',0),('MmEnemyHealthHi',0),('MmEnemyFlash',0),('RgEnemyStun',0)]:q.set(n,v)
    before=(q.get('Enemy_State'),q.get('MmEnemyHealthLo'),q.get('MmEnemyHealthHi'));history=[]
    for n in range(5):
     q.buttons(0);history.append(q.calls[-1]);after=(q.get('Enemy_State'),q.get('MmEnemyHealthLo'),q.get('MmEnemyHealthHi'))
     if after!=before:break
    assert after!=before and any(z['owner']=='MegaManWeapons::DamageEnemy'for call in history for z in call['entries']),(variant,plan['name'],face,before,after)
    rows.append(dict(variant=variant,case=plan['name'],face=face,target=dict(x=x,y=y,slot=slot,after_emission_updates=tick),before=before,after=after,calls=history,scope='Compiled full projectile gateway, actual spatial contact/damage owner; no enemy AI/PPU/NMI/native claim.'))
 put(a.output/'spatial-contacts.json',dict(passed=True,source_only=True,native_run=False,ROM_sha256=SHA,cases=len(rows),rows=rows))
 sys.path.insert(0,str(D/'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'));from lupa.lua54 import LuaRuntime
 path=Path(ready['profiles'][0]['output']);script=(path/'run.lua').read_text();cfg=json.loads((path/'config.json').read_text());anchor='local function hook(n,fn)\n';assert script.count(anchor)==1
 instrumented=script.replace(anchor,anchor+' if TEST_HOOKS then TEST_HOOKS[n]=fn end\n');assert instrumented.replace(anchor+' if TEST_HOOKS then TEST_HOOKS[n]=fn end\n',anchor)==script
 tests=[]
 variants=[('free-valid',1,'free','',True),('free-no-spawn',1,'free','current.stage.spawns={}',False),('free-no-art',1,'free','current.stage.draws=0',False),('free-no-cue',1,'free','current.stage.sourceSfx={}',False),('contact-valid',1,'contact','',True),('contact-no-hit',1,'contact','current.stage.hits=0',False),('contact-no-owner',1,'contact','current.stage.damageCalls=0',False),('ordinary-ground',1,'terrain','',True),('ordinary-missing-impact',1,'terrain','current.stage.impacts=0',False),('laser-ground-bypass',4,'terrain','current.stage.impacts=0;current.stage.groundCrossed=true',True),('laser-invented-impact',4,'terrain','current.stage.groundCrossed=true',False),('laser-no-crossing',4,'terrain','current.stage.impacts=0',False),('machine-cadence',2,'auto-cadence','',True),('machine-bad-cadence',2,'auto-cadence','current.stage.spawns[4].update=22',False),('wrong-form',1,'free',"mem[L.PlayerStatus]=0",False)]
 for name,case,kind,extra,want in variants:
  rt=LuaRuntime(unpack_returned_tuples=True)
  pre=MOCK+'''\nL={};OUTPUT='mock/';TEST_HOOKS={};mem={};emu.memType.nesPrgRom=6
emu.read=function(a,t)return mem[a]or 0 end
emu.write=function()error('Finalizer models never seed game state')end
emu.getScreenBuffer=function()local z={};for i=1,256*240 do z[i]=0xff000000 end;return z end
'''
  common=f"""
entered=true;done=false;phase='run';age=110;wall=600;updates=200;index=1;taskIndex=1
mem[L.PlayerStatus]=1
current={{q=C.cases[{case}],t={{kind='{kind}',face=1}},stages={{}},grants={{}}}}
current.stage={{kind='{kind}',face=1,spawns={{{{update=0}},{{update=7}},{{update=14}},{{update=20}},{{update=27}},{{update=33}},{{update=40}},{{update=47}},{{update=54}},{{update=61}}}},draws=1,sourceSfx={{{{kind='Square1SoundQueue',value=C.fireball_sfx}},{{kind='AvAudioRequest',value=current.q.sfx}}}},hits=1,damageCalls=1,blockCalls=1,impacts=1,target=30}}
"""
  rt.execute(pre+instrumented+common+extra+"\nMODEL_OK,MODEL_ERROR=pcall(TEST_HOOKS.finish)")
  got=bool(rt.globals().MODEL_OK);assert got==want,(name,rt.globals().MODEL_ERROR)
  tests.append(dict(case=name,accepted=got,expected=want,passed=True))
 put(a.output/'finalizer-models.json',dict(passed=True,synthetic_not_native=True,original_finalizer_body=True,instrumentation_reverse_exact=True,models=tests))
 files=[Path(__file__),path/'run.lua',path/'config.json',a.ready/'proof.json',a.ready/'manifest.json',a.output/'spatial-contacts.json',a.output/'finalizer-models.json']
 put(a.output/'proof.json',dict(passed=True,source_only=True,native_run=False,ROM_sha256=SHA,actual_spatial_cases=len(rows),synthetic_finalizer_cases=len(tests),bindings=[dict(path=str(f),sha256=sha(f),bytes=f.stat().st_size)for f in files]))
 print(json.dumps(dict(passed=True,source_only=True,spatial_cases=len(rows),finalizer_cases=len(tests),proof_sha256=sha(a.output/'proof.json'))))


if __name__=='__main__':main()
