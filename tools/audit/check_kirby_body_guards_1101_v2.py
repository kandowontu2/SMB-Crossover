"""Additional actual Main release/hazard/Meta contact controls."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import check_kirby_owner_main_1101_v2 as K
import check_hogan_current_bounded_v1 as C
import ff_wram_host_controls_v7 as H
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address
O=K.O;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    q=dict(passed=False,ROM_sha256=sha(O/'candidate.nes'),source_CPU=True,native_emulator=False)
    try:
        b=qualified(O/'candidate.nes');seed,start=K.cold(b)
        m=C.fork(seed);K.scene(m);K.main_step(m,64);C.consume(m);assert H.get(m,'KbAction')==1 and H.get(m,'KbActionAge')==8
        K.actor(m,6,120);_,_,o=K.main_step(m,0);release=dict(health=H.get(m,'KbHealth'),action=H.get(m,'KbAction'),body_contacts=o.counts['KbBodyContact'],injuries=o.counts['KbInjuryStart']);assert release==dict(health=5,action=0,body_contacts=1,injuries=1),release
        hazards=[]
        for kind in[0x15,0x1b]:
            m=C.fork(seed);K.scene(m);K.actor(m,kind,120);_,low,o=K.main_step(m,64)
            row=dict(enemy_ID=kind,health=H.get(m,'KbHealth'),action=H.get(m,'KbAction'),injury_entries=o.counts['KbInjuryStart'],minimum_SP=low);hazards.append(row)
        # Explicit Meta alternate selected by real menu Select, not a variant
        # or action-state write. No active sword is staged for this contact.
        m=C.fresh(b);H.put(m,CrossoverMenuIndex=12)
        for name in['MenuResolveCharacter','QueueSelection']:C.invoke(m,name)
        H.put(m,SavedJoypad1Bits=32,SavedJoypad2Bits=0,CrossoverMenuButtons=0);C.invoke(m,'CrossoverMenuInput');assert H.get(m,'KbVariant')==1
        H.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0);C.invoke(m,'GameMenuRoutine');C.invoke(m,'PauseRoutine',a=0)
        for setup in range(600):
            if H.get(m,'OperMode_Task')==3 and H.get(m,'GameEngineSubroutine')==8:break
            K.main_step(m);C.consume(m)
        else:raise AssertionError('Meta actual menu/parser bound')
        for _ in range(40):K.main_step(m);C.consume(m)
        assert H.get(m,'KbHealth')==6 and H.get(m,'KbVariant')==1
        K.scene(m);K.actor(m,6,120);_,low,o=K.main_step(m,0);meta=dict(health=H.get(m,'KbHealth'),action=H.get(m,'KbAction'),body_contacts=o.counts['KbBodyContact'],injury_entries=o.counts['KbInjuryStart'],Meta_weapon_entries=o.counts['MkWeapons'],minimum_SP=low)
        assert meta['health']==5 and meta['action']!=1 and meta['body_contacts']and meta['injury_entries']and meta['Meta_weapon_entries'],meta
        q.update(passed=True,actual_released_B_contact=release,actual_hazard_Main=hazards,actual_Meta_Select_then_ordinary_contact=meta,no_ability_health_action_result_seeds=True,scope='Actual native Main with disclosed flat/player/NPC placement. Release B restores ordinary injury; real Select enters Meta, where ordinary unarmed contact still injures. Hazard outcomes recorded explicitly; no broad all-hazard claim.')
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),R/'tools/audit/check_kirby_owner_main_1101_v2.py',O/'candidate.nes',O/'candidate.dbg',O/'owner-link.json']}
    (O/'body-guards-CPU.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['bindings','traceback']}));assert q['passed'],q.get('error')
if __name__=='__main__':main()
