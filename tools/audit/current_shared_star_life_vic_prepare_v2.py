"""Vic-only immutable scene-coordinate correction; never launches Mesen.

Original v1 remains intact. Actor placement follows genuine VvExportPosition
after the scene changes camera, without writing the private ship coordinates.
"""
from pathlib import Path
import csv
import hashlib
import json
import sys

R=Path(__file__).resolve().parents[2]
OLD=R/'tools/audit/current_shared_star_life_prepare_v1.py'
FIXTURE=R/'tests/current-shared-star-life.lua'
NEW=R/'tests/current-shared-star-life-vic-v2.lua'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')
OLD_TOOL='3be0314a1c8411abde5baa4fcc12de05b1f3305d72bb6d5e577efe35f95acc56'
OLD_FIXTURE='4aa2eadfff142cb1848bb3b338bfaad85912bb06ffa899ee0cd3a1694ea53d1d'
LUA_PAIRS=[
 (" local y=r('Player_Y_Position')-8;assert(y>=24 and y<=200,'Legal native contact band')",
  " local y=r('Player_Y_Position')-8;assert(y>=24 and y<=200,'Legal native contact band')\n local x,page=r('Player_X_Position'),r('Player_PageLoc')\n if C.character==18 then local world=r('VvObjX')-8+r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc');x,page=world&255,(world>>8)&255 end"),
 ("{'Enemy_X_Position',r('Player_X_Position')},{'Enemy_PageLoc',r('Player_PageLoc')}",
  "{'Enemy_X_Position',x},{'Enemy_PageLoc',page}")]
PY_PAIRS=[
 ("fixture=R/'tests/current-shared-star-life.lua'", "fixture=R/'tests/current-shared-star-life-vic-v2.lua'"),
 ("    y=q.get('Player_Y_Position')-8;assert 24<=y<=200",
  "    y=q.get('Player_Y_Position')-8;assert 24<=y<=200\n    world=q.get('VvObjX')-8+q.get('ScreenLeft_X_Pos')+256*q.get('ScreenLeft_PageLoc') if character==18 else q.get('Player_X_Position')+256*q.get('Player_PageLoc')"),
 ("Enemy_BoundBoxCtrl=3 if kind==46 else 9,Enemy_X_Position=q.get('Player_X_Position'),\n        Enemy_PageLoc=q.get('Player_PageLoc')",
  "Enemy_BoundBoxCtrl=3 if kind==46 else 9,Enemy_X_Position=world&255,\n        Enemy_PageLoc=(world>>8)&255"),
 ("    print(json.dumps(dict(prepared=True", "    if False:print(json.dumps(dict(prepared=True")]


def change(text,pairs):
    for old,new in pairs:
        assert text.count(old)==1,old;text=text.replace(old,new)
    return text


def counterexample(old,new):
    b=new['scoped_load'](R/'build/mega_proto_body_palette_9ea.nes')
    result=[]
    for label,ns in [('original-export-stale',old),('native-coordinate-actor',new)]:
        q=ns['Arena'](b,18)
        q.put(VvVariant=0,CrossoverBehaviorVersion=1,OperMode_Task=3,AreaType=1,PlayerStatus=0,
              Player_X_Position=112,Player_PageLoc=0,Player_Y_Position=176,Player_State=0,
              ScreenLeft_PageLoc=0,ScreenLeft_X_Pos=0,ScreenRight_PageLoc=0,ScreenRight_X_Pos=255,
              ScrollLock=1,Player_CollisionBits=255,Player_MovingDir=1)
        q.array('GameTimerDisplay',[3,9,9]);q.invoke('InventoryInit');q.invoke('CrossoverGraphicsBank')
        for n in ['Block_Buffer_1','MmSolidTerrain','MmBrickHealth']:q.array(n,[0]*416)
        for page in range(2):
            for row in [11,12]:
                for col in range(16):q.set('Block_Buffer_1',84,page*208+row*16+col)
        for _ in range(30):q.set('SavedJoypadBits',0);q.invoke('GameLoop')
        # Legal coordinate-only source context, not historical unlogged RAM.
        q.put(ScreenLeft_X_Pos=29,Player_X_Position=69,VvObjX=48)
        assert q.get('VvObjX')-8+q.get('ScreenLeft_X_Pos')==q.get('Player_X_Position')
        q.set('ScreenLeft_X_Pos',0);ns['actor'](q,46,5,2,18)
        before=dict(player=q.get('Player_X_Position'),actor=q.get('Enemy_X_Position',5),native_x=q.get('VvObjX'),camera=q.get('ScreenLeft_X_Pos'))
        snapshots=[]
        for i in range(40):
            q.set('SavedJoypadBits',0);q.invoke('GameLoop')
            if i<2 or q.get('StarInvincibleTimer')>0:snapshots.append(dict(call=i+1,player=q.get('Player_X_Position'),actor=q.get('Enemy_X_Position',5),timer=q.get('StarInvincibleTimer'),live=q.get('Enemy_Flag',5)))
            if label=='native-coordinate-actor'and q.get('StarInvincibleTimer')>0:break
        assert q.get('StarInvincibleTimer')>0 if label=='native-coordinate-actor'else q.get('StarInvincibleTimer')==0
        result.append(dict(label=label,before=before,calls=i+1,observations=snapshots,final_timer=q.get('StarInvincibleTimer')))
    return dict(passed=True,native_run=False,scope='Real compiled source CPU legal nonzero-camera coordinate context. Does not invent or backfill historical native ObjX/camera values.',cases=result)


def main():
    assert sha(OLD)==OLD_TOOL and sha(FIXTURE)==OLD_FIXTURE
    assert '--identity'in sys.argv and sys.argv[sys.argv.index('--identity')+1]=='vic','Only Vic successor authorized'
    expected=change(FIXTURE.read_text(),LUA_PAIRS);assert NEW.read_text()==expected
    for a,b in reversed(LUA_PAIRS):expected=expected.replace(b,a)
    assert expected==FIXTURE.read_text(),'Exact reverse delta, all guard/cap/phase assertions retained'
    old={'__file__':str(OLD),'__name__':'_original_star_life'};exec(compile(OLD.read_text(),str(OLD),'exec'),old)
    source=change(OLD.read_text(),PY_PAIRS)
    new={'__file__':str(Path(__file__).resolve()),'__name__':'_vic_star_life_v2'};exec(compile(source,str(OLD),'exec'),new)
    proof=counterexample(old,new)
    new['main']()
    out=Path(sys.argv[sys.argv.index('--output')+1]).resolve()
    negative=R/'build/current-ab221-vic-hard-star-life-v1/native/star-life.csv'
    rows=list(csv.DictReader(negative.open(newline='')))
    assert len([x for x in rows if x['event']=='update'])==1000
    assert rows[0]['event']=='disclosed-scene-setup'and rows[0]['x']=='69'and all(x['x']=='40'and x['star']=='0'and x['phase']=='star'for x in rows if x['event']=='update')
    proof.update(original_native_negative=dict(path=str(negative),sha256=sha(negative),update_rows=1000,setup_x=69,all_update_x=40,all_update_star=0,physical_pickup_events=0),
                 exact_fixture_reverse=True,unchanged_engine_writes=True,unchanged_caps_guards_and_controller=True)
    pp=out/'coordinate-controls.json';put(pp,proof)
    ready=out/'prepared-not-run.json';z=json.loads(ready.read_text())
    paths={Path(x['path'])for x in z['bindings']}|{OLD,FIXTURE,NEW,Path(__file__).resolve(),negative,pp}
    z.update(successor='Vic-only actor world-coordinate translation after camera setup',original_native_v1='FALSE: finite component age, zero Star contacts; retained unchanged',native_run=False)
    z['bindings']=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))for p in sorted(paths)]
    put(ready,z)
    print(json.dumps(dict(prepared=True,native_run=False,ready=str(ready),ready_sha256=sha(ready),bindings=len(z['bindings']),counterexample=str(pp))))


if __name__=='__main__':main()
