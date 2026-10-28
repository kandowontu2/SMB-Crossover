"""Add the three existing source-model CV3 reward rules; no native launch."""
from pathlib import Path
import difflib,json,re
import current_ee115_shared_star_life_prepare_v1 as shared
from current_shared_star_reward_model_v4 import Model,metadata
from current326_shared_powerups_retarget_v1 import actual_config
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address

R=Path(__file__).resolve().parents[2]
ROM=R/'build/zelda2_easy_glove.nes'
EXPECTED='32694243361bb1366f6fd64c054ea2451f86b2517fc020d9c2b5d66bbf07bfa0'
PARENT=R/'build/current326-shared-powerups-v1'
OLD_FIXTURE=R/'tests/current-ee115-shared-star-life-v1.lua'
FIXTURE=R/'tests/current326-cv3-star-life-v2.lua'
OUT=R/'build/current326-cv3-star-rewards-v2'
sha=shared.sha;put=shared.put
BRANCHES=""" elseif name=='RewardCvSpawn'then
  assert(family=='cv3'and phase=='contact'and counts.starContact==1 and x>=0 and x<2 and r('Cv3DropType',x)==0 and r('Cv3HitSlot')==0 and r('Enemy_ID',0)==6,'Actual protected CV3 enemy drop spawn')
  assert(r('PseudoRandomBitReg',1)&3==0 and a==(r('PseudoRandomBitReg',2)>=192 and 5 or 1),'Exact original CV3 heart drop chance/amount')
  rewardBorn[x]={kind=a,consumed=false}
  reward_emit(name,h,{slot=x,old=0,new=a,item_kind=a,award_count=0})
 elseif name=='RewardCvCredit'then
  local b=assert(rewardBorn[x])
  assert(family=='cv3'and phase=='expiry'and not b.consumed and b.kind==r('Cv3DropType',x)and r('Cv3DropAge',x)>0 and y==rewardCfg.variant-1 and r('Cv3HitSlot')==x,'Real spawned CV3 heart reaches passed native collision and owner writer')
  reward_prepare(name,'Cv3Hearts',y,math.min(r('Cv3Hearts',y)+b.kind,99),a,h,b.kind,1,b.kind)
  b.consumed=true;reward_emit('physical-CV3-collection',h,{slot=x,item_kind=b.kind,award_count=1})
 elseif name=='RewardCvKill'then
  local b=rewardBorn[x]
  if b then
   assert(b.consumed and a==0,'Only the physically collected CV3 drop reaches its native erase store')
   b.erase_issued=true;reward_emit(name,h,{slot=x,old=b.kind,new=0,award_count=0})
  end
"""

class CommittedCV3(Model):
    """Existing model plus actual source-CPU drop-type store observations."""
    def __init__(self,*a):super().__init__(*a);self.store_pending=None;self.drop_writes=[]
    def event(self,pc,bank,a,x,y,phase,hits):
        name=self.lookup.get((pc,bank));super().event(pc,bank,a,x,y,phase,hits)
        if self.expected is not None and name in ['RewardCvSpawn','RewardCvKill']and x in self.born:
            assert self.store_pending is None
            self.store_pending=dict(owner=name,writer_pc=pc,physical_bank=bank,address=self.ram['Cv3DropType']+x,slot=x,old=self.r('Cv3DropType',x),new=a)
    def write(self,at,value,pc,bank):
        super().write(at,value,pc,bank)
        if self.expected is None or not(self.ram['Cv3DropType']<=at<self.ram['Cv3DropType']+2):return
        p=self.store_pending;assert p and(p['address'],p['new'],p['writer_pc'],p['physical_bank'])==(at,value,pc,bank)
        assert self.r('Cv3DropType',p['slot'])==value
        self.drop_writes.append(p);self.store_pending=None
    def finish(self):
        z=super().finish();assert self.store_pending is None
        assert [a['owner']for a in self.drop_writes]==['RewardCvSpawn','RewardCvKill']
        assert all(self.r('Cv3DropType',x)==0 for x in self.born)
        z['actual_committed_drop_type_writes']=self.drop_writes;return z

def fixture():
    old=OLD_FIXTURE.read_text();marker=" elseif name=='RewardZ2Accepted'then"
    assert old.count(marker)==1 and "elseif name=='RewardCvSpawn'"not in old
    text=old.replace(marker,BRANCHES+marker)
    a=" for _,b in pairs(rewardBorn)do assert(b.consumed,'Spawn alone is never an earned resource credit')end"
    z=a+"\n if rewardCfg.family=='cv3'then for slot,b in pairs(rewardBorn)do assert(b.erase_issued and r('Cv3DropType',slot)==0,'Actual collected CV3 drop has completed its native erase')end end"
    assert text.count(a)==1;text=text.replace(a,z)
    assert text.replace(BRANCHES,'',1).replace(z,a,1)==old
    begin='-- All callback registration is startup-static.';end='emu.addEventCallback(function()\n if not entered'
    assert text[text.index(begin):text.index(end)]==old[old.index(begin):old.index(end)]
    assert text.count('emu.write(')==2 and 'removeMemoryCallback'not in text
    assert "else error('Unbound reward rule '..name)end"in text
    FIXTURE.write_text(text,newline='\n');return old,text

def main():
    assert sha(ROM)==EXPECTED and not OUT.exists()and not FIXTURE.exists()
    parent=PARENT/'star-life-alucard';ready=parent/'prepared-not-run.json'
    assert sha(ready)=='dff230291ca855c1d0a604f938d77cb25412350b6311384f6587c40ccb1b0a64'
    negative_log=parent/'native/zelda2_easy_glove-run.log';negative_csv=parent/'native/star-life.csv'
    assert 'Unbound reward rule RewardCvSpawn'in negative_log.read_text()and not(parent/'native/result.json').exists()
    b=scoped_load(ROM);before,text=fixture();OUT.mkdir()
    patch=OUT/'observer-only.patch';patch.write_text(''.join(difflib.unified_diff(before.splitlines(True),text.splitlines(True),fromfile=str(OLD_FIXTURE),tofile=str(FIXTURE))),newline='\n')
    ns,_=shared.namespace();ns['EXPECTED']=EXPECTED;cfgs={}
    def reward_make(bundle,identity,q):
        _,char,_,variant=ns['BASE'][identity]
        cfg=metadata(bundle,identity,shared.prior.resource_fields(identity),char,variant);cfgs[identity]=cfg
        names={p['name']for p in shared.prior.resource_fields(identity)}|{'Cv3DropType'}
        return CommittedCV3(cfg,{n:address(bundle,n)for n in names},q.get)
    ns['reward_make']=reward_make;hooks,_=ns['hooks_for'](b);readies=[]
    for who in ['alucard','grant','sypha']:
        p=PARENT/('star-life-'+who);oldready=p/'prepared-not-run.json';old=json.loads(oldready.read_text())
        for q in old['bindings']:assert sha(q['path'])==q['sha256']
        source=ns['campaign'](b,who,1,hooks);source.update(ROM_sha256=EXPECTED,fresh_current_campaign=True,Lua_VM_executed=False,
            source_scope='Existing unchanged complete Star+1Up source campaign; native successor remains Star-only because earned1Up already has separate native evidence. Actual modeled resource/drop-type committed stores observed; no real interrupts/PPU/native inference.')
        cfg=json.loads((p/'config.json').read_text());assert cfg['rewards']==cfgs[who]and cfg['rewards']['family']=='cv3'and cfg['need_life']is False
        missing=[n for n in ['Cv3DropType','Cv3DropAge','Cv3HitSlot']if n not in cfg['ram']]
        assert missing==['Cv3DropType','Cv3DropAge','Cv3HitSlot']
        for n in missing:cfg['ram'][n]=address(b,n)
        assert set(re.findall(r"\br\('([A-Za-z_0-9]+)'",text))<=set(cfg['ram'])
        fields=actual_config(b,cfg)
        sub=OUT/who;sub.mkdir();put(sub/'config.json',cfg);put(sub/'source-controls.json',source)
        run=(p/'run.lua').read_text();line=run.index('\n');suffix=run[line:]
        assert suffix.count(OLD_FIXTURE.as_posix())==1
        from observe_chip_committed_write import lua
        (sub/'run.lua').write_text('CURRENT_SHARED_STAR_LIFE='+lua(cfg)+suffix.replace(OLD_FIXTURE.as_posix(),FIXTURE.as_posix()),newline='\n')
        cmd=json.loads((p/'command.json').read_text());argv=cmd['argv'];cmd['argv']=[str(sub/'native')if x==str(p/'native')else str(sub/'run.lua')if x==str(p/'run.lua')else x for x in argv]
        assert sum(x!=y for x,y in zip(argv,cmd['argv']))==2;put(sub/'command.json',cmd)
        paths={Path(q['path'])for q in old['bindings']}|{Path(__file__),FIXTURE,OLD_FIXTURE,patch,oldready,ready,parent/'launch.json',negative_log,negative_csv,R/'src/cv3_pickups.s',R/'tools/audit/current_shared_star_reward_model_v4.py',R/'tools/audit/current326_shared_powerups_retarget_v1.py'}
        paths|={sub/n for n in ['config.json','source-controls.json','run.lua','command.json']}
        new=dict(old);new.update(status='PREPARED_DO_NOT_RUN',native_run=False,passed=False,source_calls=source['full_GameLoop_calls'],
            observer_only=True,original_Alucard_native_FALSE_preserved=True,original_Grant_Sypha_readies_unrun_unchanged=True,
            correction='Only add RewardCvSpawn/Credit/Kill rules matching existing Python source model, exact3 missing read-only RAM aliases, and require observed native erase store plus final dropType0. No credit for spawn alone; exact committed heart writer retains original strict callback.',
            current_source_qualification=dict(path=str(sub/'source-controls.json'),sha256=sha(sub/'source-controls.json')),
            source_qualification_scope=source['source_scope'],actual_current_config_fields_checked=fields,
            bindings=[dict(path=str(q.resolve()),bytes=q.stat().st_size,sha256=sha(q))for q in sorted(paths)])
        put(sub/'prepared-not-run.json',new)
        assert all(sha(q['path'])==q['sha256']for q in new['bindings'])
        readies.append(dict(identity=who,ready=str(sub/'prepared-not-run.json'),sha256=sha(sub/'prepared-not-run.json'),bindings=len(new['bindings']),source_calls=source['full_GameLoop_calls'],credits=source['reward_provenance']['credits'],drop_writes=source['reward_provenance']['actual_committed_drop_type_writes'],command=str(sub/'command.json')))
        print(json.dumps(dict(identity=who,prepared=True,native_run=False,source_calls=source['full_GameLoop_calls'])),flush=True)
    put(OUT/'handoff.json',dict(native_run=False,ROM_sha256=EXPECTED,profiles=readies,owned_files=[str(Path(__file__)),str(FIXTURE)],old24_nonCV3_inputs_unchanged=True))
    print(json.dumps(dict(handoff=str(OUT/'handoff.json'),sha256=sha(OUT/'handoff.json'),readies=readies)))

if __name__=='__main__':main()
