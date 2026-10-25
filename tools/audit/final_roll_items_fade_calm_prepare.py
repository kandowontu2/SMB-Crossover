"""Add a separate natural single-orb visual control to frozen fade-v5 helpers."""
from pathlib import Path
import argparse,hashlib,json,shutil,sys
from final_roll_items_prepare import lua
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);p.add_argument('--parser-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);z=json.loads((a.packet/'preparation.json').read_text(encoding='utf-8'))
    text=(a.packet/'fixture.lua').read_text(encoding='utf-8');assert sha(a.packet/'fixture.lua')==z['fixture_sha256']
    def replace(old,new):
        nonlocal text
        assert text.count(old)==1,old;text=text.replace(old,new)
    replace('local births,alive,coverage,artSeen={},{},{},{}','local births,alive,coverage,artSeen={},{},{},{}\nlocal calmSerial,calmBorn,calmGood,calmDone=nil,nil,false,false\nlocal calmAges,calmMaxScanline,calmAdmitted,calmHidden={},0,0,0')
    replace("phase=='pickup-birth'and drops()==0)","phase=='pickup-birth'and drops()==0 or phase=='calm-birth'and drops()==0)")
    replace("if phase=='pickup-birth'then pickupSlot=i;phase='pickup';age=0 end","if phase=='pickup-birth'then pickupSlot=i;phase='pickup';age=0\n   elseif phase=='calm-birth'then calmSerial=q.serial;calmBorn=updates;calmGood=q.kind==1 and q.meter==128;phase='calm-expiry';age=0 end")
    replace("onReturn('fade-complete-render',function()","drawEpoch.calm={serial=calmSerial,desired=calmGood,player_y=r('Player_Y_Position'),shots=shots(),enemies=0}\n for i=0,5 do if r('Enemy_Flag',i)~=0 then drawEpoch.calm.enemies=drawEpoch.calm.enemies+1 end end\n onReturn('fade-complete-render',function()")
    replace("elseif phase=='empty-before'and age>=120 then initialEmptyEnd=updates;phase='pool';age=0","elseif phase=='empty-before'and age>=120 then initialEmptyEnd=updates;phase='calm-birth';age=0\n elseif phase=='calm-expiry'and drops()==0 and shots()==0 and r('RlAttack')==0 then\n  if calmGood then assert(count(calmAges)==12 and calmAdmitted>0 and calmHidden>0,'Calm source-age236..247 committed window contains admitted and hidden controls');calmDone=true;phase='pickup-birth'else phase='calm-birth'end;age=0")
    replace("elseif targetActive then b.b=(updates-fireAt)%12<2","elseif targetActive then b.b=(updates-fireAt)%12<2\n elseif phase=='calm-expiry'and calmGood then b.a=updates-calmBorn>=225 and updates-calmBorn<255")
    replace("coverage[coverKey(a.age,a.frame&1)]=true;sample=true","coverage[coverKey(a.age,a.frame&1)]=true;sample=true\n      if epoch.calm.desired and a.birth==epoch.calm.serial then\n       assert(a.kind==1 and a.meter==128 and epoch.calm.shots==0 and epoch.calm.enemies==0,'Calm genuine small health orb with no active shot/enemy')\n       assert(epoch.calm.player_y+32<200,'Actual controller jump places body clear of orb scanlines')\n       local o=epoch.visible_start.oam;local maximum=0\n       for scan=201,216 do local n=0;for at=1,256,4 do local y=o[at];if y<240 and scan>=y+1 and scan<y+17 then n=n+1 end end;maximum=math.max(maximum,n)end\n       assert(maximum<=8,'Calm source orb is uncontested by hardware scanline capacity')\n       calmMaxScanline=math.max(calmMaxScanline,maximum);calmAges[a.age]=true\n       if a.expected_visible then calmAdmitted=calmAdmitted+1 else calmHidden=calmHidden+1 end\n      end")
    replace("assert(poolSeen and poolFinished and fourRenders>0 and emptyRenders>=120 and expiryCount>=4 and pickups==1 and count(coverage)==24,'Natural four-slot/empty/fade parity/pickup/expiry completed')","assert(calmDone and count(calmAges)==12 and calmAdmitted>0 and calmHidden>0 and emptyRenders>=120 and expiryCount>=1 and pickups==1,'Separate calm natural-orb window/expiry/real-pickup completed')")
    replace("local q={mechanics_passed=true,fade_policy_passed=firstWrong==nil","local q={component='calm-actual-small-health-orb',calm_serial=calmSerial,calm_complete=calmDone,calm_committed_ages=calmAges,calm_admitted=calmAdmitted,calm_hidden=calmHidden,calm_max_scanline_sprites=calmMaxScanline,mechanics_passed=true,fade_policy_passed=firstWrong==nil")
    # The numeric serial is retained after the final real pickup; the desired
    # calm actor was fully earned and expired before the pickup-birth phase.
    sys.path.insert(0,str(a.parser_root));from luaparser import ast;ast.parse(text)
    (a.output/'fixture.lua').write_text(text,encoding='utf-8')
    profiles=[]
    for role in ['baseline','candidate']:shutil.copytree(a.packet/role,a.output/role)
    for old in z['profiles']:
        role=old['role'];mode=old['mode_value'];folder=a.output/(role+'-'+('hard'if mode else'easy'));folder.mkdir()
        c=json.loads((Path(old['script']).parent/'config.json').read_text(encoding='utf-8'));c['component']='calm-actual-small-health-orb'
        script=folder/'run.lua';script.write_text('OUTPUT=assert(OUTPUT)\nFINAL_ROLL_ITEMS='+lua(c)+'\n'+text,encoding='utf-8');ast.parse(script.read_text(encoding='utf-8'))
        (folder/'config.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
        profiles.append(dict(old,script=str(script),script_sha256=sha(script),config_sha256=sha(folder/'config.json')))
    dependencies={str(q.relative_to(ROOT)).replace('\\','/'):sha(q)for q in [Path(__file__),ROOT/'tools/audit/final_roll_items_prepare.py',ROOT/'tools/run_mesen.py',ROOT/'tools/audit/run_mesen_isolated.py',ROOT/'tools/audit/final_roll_items_fade_native_run.py']}
    result=dict(z,component='separate-calm-single-orb',fixture_sha256=sha(a.output/'fixture.lua'),parent_preparation_sha256=sha(a.packet/'preparation.json'),profiles=profiles,dependencies=dependencies,scope='Separate calm visual component, not a replacement for full-pool controls: cold mode, actual free-buster default Goomba defeats and untouched RNG, wrong-kind natural420 expiry, genuine small health orb birth/expiry, actual controller jump at ages225..254 to move body vertically clear, no shots/enemies during236..247, exact8-sprite admission guard, actual PPU/publication/DMA binding; subsequent genuine full-cap pickup. No actor/resource/RNG/counter/outcome writes.')
    (a.output/'preparation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(preparation_sha256=sha(a.output/'preparation.json'),fixture_sha256=result['fixture_sha256'])))
if __name__=='__main__':main()
