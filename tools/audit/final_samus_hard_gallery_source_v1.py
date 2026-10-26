"""Finite Samus Hard B-gallery owner/plan preparation. No native launcher."""
from pathlib import Path
import argparse, hashlib, json, sys
from link_pit_rygar_sophia_audit_cpu import scoped_load, Arena, ROOT
from check_tmnt_render_oa import address, location
from verify_native_relocation import NesMPU

D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PARENT = D/'root-current-roster-composition-v1'
SHA = '3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p, v): p.write_text(json.dumps(v, indent=2)+'\n', encoding='utf-8')

class TraceArena(Arena):
    """Execute full compiled gateways and record genuine entry/return ownership."""
    def __init__(self, b):
        super().__init__(b, 2)
        self.calls=[]
        self.put(OperMode_Task=3, PlayerStatus=1, Player_Y_Position=160,
                 Player_Rel_XPos=96, Player_CollisionBits=255)
        self.set('InvOwnedLo',129,2)
    def invoke(self, name, a=0, x=0, y=0):
        b=self.b; s=b['syms'][name]; g=b['segs'][s['seg']]
        at=address(b,name); bank=(int(g['ooffs'],0)-16)//8192; w=(at-0x8000)//8192
        self.m.page(w,bank)
        if w in [1,2]: self.set('CurrentBank' if w==1 else 'CurrentBankC',bank|128)
        c=NesMPU(memory=self.m,pc=at);c.a,c.x,c.y,c.p,c.sp=a,x,y,0x30,0xfd
        c.stPushWord(0x5aff);self.m.writes=[];trace=[];entries=[];pending=[];returns=[];seen=set()
        wanted={}
        for n in OWNER_NAMES:
            if n in b['syms']:
                wanted[(address(b,n),(location(b,n)-16)//8192)]=n
        for _ in range(200000):
            physical=self.m.banks[(c.pc-0x8000)//8192] if c.pc>=0x8000 else -1
            # Original return semantics: PC, actual bank AND SP must match.
            for q in list(pending):
                if (c.pc,physical,c.sp)==(q['return_pc'],q['return_bank'],q['return_sp']):
                    pending.remove(q);returns.append(dict(**q,returned_a=c.a,returned_x=c.x,returned_y=c.y,returned_p=c.p))
            if c.pc==0x5b00:
                assert c.sp==0xfd and not pending,(name,c.sp,pending)
                self.calls.append(dict(gateway=name,cycles=c.processorCycles,entries=entries,returns=returns,
                                       returned=dict(a=c.a,x=c.x,y=c.y,p=c.p,sp=c.sp)))
                return c,trace
            n=wanted.get((c.pc,physical))
            if n:
                ret=(self.m[0x100+((c.sp+1)&255)]+256*self.m[0x100+((c.sp+2)&255)]+1)&65535
                rb=self.m.banks[(ret-0x8000)//8192] if ret>=0x8000 else -1
                q=dict(owner=n,entry_pc=c.pc,entry_bank=physical,entry_sp=c.sp,return_pc=ret,return_bank=rb,return_sp=(c.sp+2)&255)
                entries.append(q)
                # Tail-called and nested owners may share a genuine return. All must finish.
                pending.append(q)
            at=c.pc;before=len(self.m.writes);c.step()
            trace.extend(dict(pc=at,bank=physical,address=p,value=v)for p,v in self.m.writes[before:])
        raise AssertionError(('compiled gateway timeout',name,hex(c.pc),self.m.banks))

OWNER_NAMES=[
 'ProcFireball_Bubble','Z2RemainingWeaponsGate','RemainingWeapons','RemainingWeapons::SamusInput',
 'RemainingWeapons::FireOwned','InventorySpend','RemainingWeapons::Spawn','AvSamusPrimary',
 'RemainingSamusPool','SamusBeamType','SamusWeapons','SamusWeapons::Spawn','SamusWeapons::DropBomb',
 'SamusWeapons::BombBoost','SamusWeapons::BombBlocks','SamusMovement','SamusMorphEnter',
 'PlayerMovementSubs','PlayerGfxHandler','SamusGraphics','GuestVisualStatus','RemainingPower',
 'RlUiDispatch','InventoryUiTick','InventoryCycle','InventorySelectionCommit','InventoryClearActive',
 'GuestBodyContactBridge','LmBodyGate','JnBodyDispatch','M3BodyDispatch','KbBodyDispatch','Cv3BodyGate',
 'GuestBodyContact','GuestBodyContact::SpinDamage','MegaManWeapons::Enemies','RosterEnemyHit',
 'MegaManWeapons::DamageEnemy','SamusHardEnemyAdmission','SamusShotConfirmed','SamusFrozenDecrement',
 'FirebarCollision','CacheFirebarPart','GuestInjuryStart','SamusDrawShots','RemainingDraw',
 'SamusFreezeRenderFinish','RemainingWeapons::Screw','RemainingAudioBegin','SamusAudioUpdate',
]

def expect_entries(q,*names):
    got={z['owner']for z in q.calls[-1]['entries']}
    assert set(names)<=got,(q.calls[-1]['gateway'],set(names)-got,got)

def source_controls(b):
    rows=[];observed=[]
    def done(q,kind,data):
        rows.append(dict(kind=kind,**data,calls=q.calls));observed.extend(q.calls)
    def fresh(q,buttons=64):
        q.put(A_B_Buttons=buttons&0xc0,PreviousA_B_Buttons=0,SavedJoypadBits=buttons,
              SavedJoypad1Bits=buttons,InvPrevious=0)
        q.invoke('RlUiDispatch')
        assert q.get('InvFresh')==buttons
        expect_entries(q,'InventoryUiTick')
        return q.invoke('ProcFireball_Bubble')
    # Full foreground update gateways retain BOTH additional and primary paths.
    for owned,word,typ in [(0,'short',1),(129,'long',2),(137,'ice',46),(145,'wave',3)]:
        for face in [1,2]:
            q=TraceArena(b);q.set('InvOwnedLo',owned,2)
            q.put(PlayerStatus=0 if not owned else 1,PlayerFacingDir=face)
            fresh(q)
            expect_entries(q,'Z2RemainingWeaponsGate','RemainingWeapons','SamusWeapons','AvSamusPrimary')
            native=[q.get('SmShotType',i)for i in range(3)];shared=[q.get('RgShotType',i)for i in range(10)]
            assert (typ in native) if typ<4 else (typ in shared),(word,native,shared)
            if typ<4:expect_entries(q,'SamusWeapons::Spawn','SamusBeamType')
            else:expect_entries(q,'RemainingWeapons::Spawn')
            for _ in range(12):
                q.put(A_B_Buttons=0,PreviousA_B_Buttons=0,InvFresh=0);q.invoke('ProcFireball_Bubble')
            assert (not any(q.get('SmShotType',i)for i in range(3))) if word=='short' else True
            if word=='long': assert any(q.get('SmShotType',i)==2 for i in range(3))
            done(q,'complete-primary-gateways',dict(weapon=word,face=face,spawn_type=typ,short_expires_by13=True if word=='short' else None,ownership_seed=owned))
    # A real Select edge is modern Hard Special fire, not Bass's cycle command.
    for stock,owned,ball,count in [(2,133,0,0),(0,133,0,0),(2,129,0,0),(2,133,1,0),(2,133,0,3)]:
        q=TraceArena(b);q.set('InvOwnedLo',owned,2);q.set('InvAmmo',stock,34);q.put(SmBall=ball)
        for i in range(count):q.set('SmShotType',2,i);q.set('SmShotX',140+i*4,i);q.set('SmShotPage',1,i);q.set('SmShotY',90,i);q.set('SmShotDir',1,i)
        fresh(q,32)
        paid=bool(stock and owned&4 and not ball and count<3)
        assert q.get('InvAmmo',34)==stock-int(paid)
        assert any(q.get('RgShotType',i)==41 for i in range(10))==paid
        assert q.get('InvSelected',2)==0 # It fires even with default HUD selection.
        if paid:expect_entries(q,'RemainingWeapons::SamusInput','RemainingWeapons::FireOwned','InventorySpend','RemainingWeapons::Spawn')
        done(q,'complete-modern-Special-source-admission',dict(stock=stock,owned=owned,ball=ball,shared_count=count,paid=paid))
    q=TraceArena(b);q.set('InvOwnedLo',133,2);q.put(GamePauseStatus=1,SavedJoypad1Bits=1,InvPrevious=0)
    q.invoke('RlUiDispatch');assert q.get('InvSelected',2)==2
    expect_entries(q,'InventoryUiTick','InventoryCycle','InventorySelectionCommit','InventoryClearActive')
    done(q,'actual-paused-controller-selection',dict(selected=2,mode=1))
    # Three-slot beam/missile/Ice accounting is shared; bombs are a separate pool.
    for types in [(2,2,2),(41,46,2)]:
        q=TraceArena(b);q.set('InvOwnedLo',145,2)
        for i,t in enumerate(types):
            if t<4:
                q.set('SmShotType',t,i);q.set('SmShotX',100+i*5,i);q.set('SmShotPage',1,i);q.set('SmShotY',80,i);q.set('SmShotDir',1,i)
            else:
                q.set('RgShotType',t,i);q.set('RgShotX',100+i*5,i);q.set('RgShotPage',1,i);q.set('RgShotY',80,i);q.set('RgShotYHigh',1,i)
        fresh(q);assert sum(q.get('SmShotType',i)>0 for i in range(3))+sum(q.get('RgShotType',i)in[41,46]for i in range(10))==3
        assert not any(z['owner']=='SamusWeapons::Spawn'for z in q.calls[-1]['entries'])
        done(q,'complete-shared-three-pool-refusal',dict(types=types))
    for morph in [0,1]:
        q=TraceArena(b);q.set('InvOwnedLo',129|(2 if morph else 0),2)
        for buttons in [4,0,4]:
            q.put(SavedJoypadBits=buttons);q.invoke('PlayerMovementSubs')
            expect_entries(q,'SamusMovement')
        assert q.get('SmBall')==morph
        if morph:
            fresh(q);assert any(q.get('SmBombAge',i)>0 for i in range(3))
            expect_entries(q,'SamusWeapons::DropBomb')
            for _ in range(85):q.put(A_B_Buttons=0,InvFresh=0);q.invoke('ProcFireball_Bubble')
            assert not any(q.get('SmBombAge',i)for i in range(3))
            # The actual explosion/boost owners must have run in complete gateways.
            assert {'SamusWeapons::BombBoost','SamusWeapons::BombBlocks'}<={z['owner']for c in q.calls for z in c['entries']}
        done(q,'complete-movement-Morph-bomb-owners',dict(Morph_owned=morph,ball=q.get('SmBall'),bombs_expired=True if morph else None))
    # Real full FirebarCollision intersects the complete native player geometry.
    for varia in [0,1]:
        q=TraceArena(b);q.set('InvOwnedLo',129|(32 if varia else 0),2)
        q.put(Player_Rel_XPos=96,R6=100,R7=160,ObjectOffset=0,PlayerSize=0)
        q.invoke('FirebarCollision',y=0)
        entered={x['owner']for x in q.calls[-1]['entries']}
        assert ('GuestInjuryStart'in entered)==(not varia),(varia,entered)
        if varia:assert q.get('PlayerStatus')==1 and q.get('GuestHurtTicks')==0
        done(q,'complete-firebar-contact-protection',dict(Varia_owned=varia,injury_owner_entered='GuestInjuryStart'in entered,after_status=q.get('PlayerStatus')))
    # Screw body damage is actually downstream of the complete body bridge.
    for owned,spin,state,enemy in [(193,1,1,6),(129,1,1,6),(193,0,1,6),(193,1,0,6),(193,1,1,45)]:
        q=TraceArena(b);q.set('InvOwnedLo',owned,2);q.put(SmFlip=spin,Player_State=state,ObjectOffset=0)
        for n,v in [('Enemy_Flag',1),('Enemy_ID',enemy),('Enemy_State',0),('Enemy_Y_HighPos',1),('Enemy_X_Position',110),('Enemy_PageLoc',1),('Enemy_Y_Position',160)]:q.set(n,v)
        c,t=q.invoke('GuestBodyContactBridge',x=0)
        protect=owned==193 and spin==state==1 and enemy!=45
        assert bool(c.p&1)==protect,(owned,spin,state,enemy,c.p)
        expect_entries(q,'LmBodyGate','GuestBodyContact')
        if protect:expect_entries(q,'GuestBodyContact::SpinDamage','MegaManWeapons::DamageEnemy')
        done(q,'complete-body-bridge-Screw-admission',dict(owned=owned,spin=spin,state=state,enemy=enemy,protected=protect))
    # Actual compiled selected-form/art owner. Source presentation policy differs
    # from the pinned2.02 Varia palette rows; we authenticate current records only.
    for varia in [0,1]:
        q=TraceArena(b);q.set('InvOwnedLo',129|(32 if varia else 0),2)
        q.invoke('PlayerGfxHandler');expect_entries(q,'SamusGraphics','GuestVisualStatus','RemainingPower')
        ptr=q.get('SmPosePtr')+256*q.get('SmPosePtr',1);assert ptr>=0xc000
        done(q,'complete-body-art-dispatch',dict(Varia_owned=varia,pose=q.get('SmPose'),pointer=ptr,logical_chr=q.get('SmChrBank')))
    return rows, observed

def plans():
    common=['numeric Hard1 cold Samus2 readback','explicit complete GameLoop-boundary arena/actor/resources, B-only; no acquisition claim',
            'both facings as bounded subphases; idle/release edges before each attempt',
            'full raw PPU, physical256DMA E008, safe enable, IRQ31, actual CHR latch/body/effect record ownership, A/C/5SMC/SP guards',
            'source-specific queued SFX and actual APU writes; no listening/waveform/source-audio-fidelity claim',
            'natural cleanup/exhaustion predicate per source; future seed reset never counted as source cleanup']
    return [
      dict(case=1,name='starting-short',owned=0,status=0,stock=None,checks=['actual B edge → native SmShotType1','age12 expiration; no imaginary ammo debit','normal terrain impact and real Goomba hit','shared-three-slot refusal, both horizontal facings and Up'],common=common),
      dict(case=2,name='long-beam',owned=129,status=1,stock=None,checks=['actual B edge → SmShotType2','survives short12-update range; moves until actual impact/offscreen','normal terrain collision, real target contact, shared-three refusal','actual suit/body/muzzle/shoot pose and effect pixels'],common=common),
      dict(case=3,name='Morph-bombs',owned=131,status=1,stock=None,checks=['first Down crouches; release+fresh second Down enters Morph','without Morph control refuses second Down; Up/A exit only with actual clearance','actual B drops three-bomb-independent-pool, fourth refused','age58 explosion/boost/terrain/enemy hit; age82 expiry; actual ball/explosion art/SFX'],common=common),
      dict(case=4,name='missile-Special',owned=133,status=1,stock=2,checks=['paused real directional selection commits MISSILE2; nonpaused Select is Special fire, not cycle','B remains Long beam even with missiles selected','real Select edges spend exactly1 after pool admission; actual debit-to0 witness and clean0 refusal','three shared beam/missile/Ice refusal without debit; Morph/climb rules source-bound','missile real target hit/terrain/expiry/HUD0/2/readable digits and art; native restoration2/cap20 CPU separate'],common=common),
      dict(case=5,name='Ice',owned=137,status=1,stock=None,checks=['B routes through AvSamusPrimary and RemainingWeapons::Spawn → RgShot46','actual accepted ordinary-enemy contact freezes360 source updates without initial HP damage; shot consumes','actual frozen blue palette/OAM/CHR publication, AI STOP and eventual unfreeze','subsequent hit removes freeze before native damage; Lakitu/Bowser resistance control','shared-three pool/terrain impact/natural effect cleanup'],common=common),
      dict(case=6,name='Wave',owned=145,status=1,stock=None,checks=['B native SmShot3 and mutually exclusive Ice/Wave source expectation','actual upward sinusoid crosses world-page edge in both directions; full world position not low-byte only','passes genuine question-block terrain while Long control impacts; real target consumption','actual both-facing/up effect pixels and offscreen expiry'],common=common),
      dict(case=7,name='Varia',owned=161,status=1,stock=None,checks=['actual RemainingPower2/current third-form body+palette records','real source-aligned firebar intersections preserve status/owned/hurt state, noVaria control injures','ordinary enemy contact still hurts; no invented universal invulnerability','existing third-form/suitless art is an explicit pinned2.02 presentation difference, not silently fixed'],common=common),
      dict(case=8,name='Screw',owned=193,status=1,stock=None,checks=['real A+direction jump establishes airborne SmFlip; actual body contact damages/protects','source NewContact prevents repeated contact credit; landing/nonspin/noownership refuses protection','Bowser/hostile projectile excluded; no invented ammunition cost','actual source flip/body art/queued Screw SFX; landing clears one-shot sound latch'],common=common),
    ]

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT);a.output.mkdir(parents=True,exist_ok=False)
    rom=PARENT/'candidate.nes';assert sha(rom)==SHA;b=scoped_load(rom)
    ready=PARENT/'ROOT-source-readiness.json';assert sha(ready)=='a332aec91cb2b16f8064c2423b2e0f3d5bbc9603325c0e06e4f0965d0386c220'
    rows,calls=source_controls(b)
    put(a.output/'assembled-gateway-controls.json',dict(passed=True,ROM_sha256=SHA,cases=len(rows),rows=rows,scope='Actual assembled complete foreground gateways in declared isolated states. No PPU/controller/interrupt/native proof; no emulator launch. No mechanics stubs.'))
    put(a.output/'plans.json',dict(profile='samus-hard',actual_mode_required=1,character=2,maximum_cases=8,lane='B controlled real-engine ability use',acquisition=False,plans=plans()))
    hooks={n:dict(address=address(b,n),physical_bank=(location(b,n)-16)//8192,bytes=list(b['raw'][location(b,n):location(b,n)+min(8,int(b['syms'][n].get('size','8'),0))]))for n in OWNER_NAMES if n in b['syms']}
    put(a.output/'compiled-owner-hooks.json',hooks)
    put(a.output/'actual-owner-returns.json',dict(passed=True,scope='Observed compiled CPU calls; exact return PC/SP/bank, including real wrapper/leaf route. Future native startup dispatcher only; NO runtime callback registration.',calls=calls))
    refs=[ROOT/'reference/crossover2/extracted/scripts/com/smbc/characters/Samus.as',ROOT/'reference/crossover2/source.swf',ROOT/'docs/qa/samus-contra-source-2026-10-25.txt',ROOT/'docs/reference/samus-upgrade-pool.json',D/'native-probes-qa-v2/legacy-native-items-batch-v2/samus/build/verification/native-legacy-items.json',D/'samus-contra-source-v1/native-candidate-v2/native-proof.json']
    history=[]
    for f in refs:
        assert f.is_file(),f;history.append(dict(path=str(f),bytes=f.stat().st_size,sha256=sha(f)))
    put(a.output/'historical-evidence.json',dict(bindings=history,retagged=False,observations=['054d mature8actor grants declare missile/Ice attacks only; no full reveal/rise or passive effect closure.','Samus55→84 Wave16native components are historical on their own hashes, not current3b coverage.','Easy classic short/Long/Wave is separate from modernHard inventory; no Easy result inferred.','No HighJump/missile-capacity random pickup is expected from pinned2.02 obtainable arrays.']))
    files=[Path(__file__),rom,rom.with_suffix('.dbg'),rom.with_suffix('.lbl'),ready]+refs
    for n in ['samus.s','samus_weapons.s','samus_ice_hit.s','samus_freeze_render.s','remaining_weapons.s','remaining_audio.s','samus_audio.s','inventory.s','inventory_data.inc','guest_body_contact.s','object.s','player.s','zelda2_inventory_glue.s','little_mac_core.s','mike_jones_dispatch.s','smb3_mario_core.s','kirby_dispatch.s','cv3_combat.s']:
        f=PARENT/'source/src'/n
        if f.exists():files.append(f)
    for n in ['final_item_abilities_static_return_v1.lua','final_item_abilities_dma731_v1.lua','final_item_matrix_progressive.lua','final_item_abilities_pit731_ppu_v1.lua','samus_contra_source_chr.lua']:
        files.append(ROOT/'tools/audit'/n)
    files.extend(q for q in a.output.iterdir()if q.is_file())
    put(a.output/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),bytes=f.stat().st_size,sha256=sha(f))for f in sorted(set(files),key=str)]))
    put(a.output/'proof.json',dict(passed=True,source_only=True,native_run=False,ROM_sha256=SHA,mode=1,plans=8,assembled_full_gateway_cases=len(rows),observed_compiled_calls=len(calls),manifest_sha256=sha(a.output/'manifest.json'),scope='Finite owner/plan source packet. Not native launch readiness: the 8-case Lua mechanics still require implementation and static controls before any grant. Reuses qualified observers, not an additional generic framework.',goal_complete=False))
    print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),cases=len(rows),plans=8),indent=2))

if __name__=='__main__':main()
