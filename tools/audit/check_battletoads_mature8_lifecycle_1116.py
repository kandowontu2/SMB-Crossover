"""Actual candidate retirement/reload/player/death primitive lifecycle."""
from pathlib import Path
from unittest.mock import patch
import json
import current_battletoads_mature8_1116 as Current
import check_battletoads_mature8_components_1116 as P

C,W,N=Current.C,Current.W,Current.N

def run(parent):
    raw,composition=C.proposal(parent);rows=[]
    expected=bytearray(raw[C.CACHE:C.CACHE+8192]);expected[0x1fe0:0x1ff0]=raw[C.COOKIE:C.COOKIE+16]
    for key in('rash','zitz'):
        seed,opening=Current.cold(raw,key,True);b=seed.bundle
        # Diagnostic caller state only. These are not earned life/death or
        # two-player gameplay receipts; genuine naturalL/full routes are separate.
        m=N.fork(seed);N.put(m,InjuryTimer=0,CurrentPlayer=0,GameEngineSubroutine=8)
        m.ram[3][W.address(b,'BtSrc_Objects_Life')&8191]=3
        m.ram[3][W.address(b,'BtSrc_Objects_death_timer')&8191]=0
        death=P.public(m,slot=5)
        assert N.get(m,'GameEngineSubroutine')==11
        assert m.ram[3][W.address(b,'BtSrc_Objects_Life')&8191]==0
        assert m.ram[3][W.address(b,'BtSrc_Objects_death_timer')&8191]==0xc0
        m[W.address(b,'Enemy_State')+5]=128;assert P.public(m)['P']&1==0
        phases=[]
        for player,life,level in((0,2,0),(1,2,0),(0,3,0),(0,2,1)):
            z=N.fork(seed);N.put(z,CurrentPlayer=player,NumberofLives=life,LevelNumber=level)
            construct=P.public(z,slot=15)
            assert z.ram[3][W.address(b,'BtHostReady')&8191]==1
            assert z.ram[3][(W.address(b,'BtLife')&8191)+player]==life
            assert z.ram[3][W.address(b,'BtVariant')&8191]==(32 if key=='zitz'else 0)
            assert bytes(z.ram[3][0x45:0x48])==bytes.fromhex('4c03b6')and bytes(z.ram[3][0x1603:0x160b])==bytes.fromhex('b51f0a90fa4c3eae')
            assert bytes(z.ram[3][0x1fe0:0x1ff0])==raw[C.COOKIE:C.COOKIE+16]
            z[W.address(b,'Enemy_State')+5]=128;admit=P.public(z);assert admit['P']&1
            phases.append(dict(CurrentPlayer=player,lives=life,level=level,construct=construct,admission=admit))
        retired=N.fork(seed);before=bytes(retired.ram[3]);retire=N.invoke(retired,'BtRetire')
        assert retired.ram[3][0x1fe0]==0
        assert all(a==v for i,(a,v)in enumerate(zip(before,retired.ram[3],strict=True))if i!=0x1fe0)
        check=N.invoke(retired,'BtCheck');assert check['P']&1==0
        retired[W.address(b,'Enemy_State')+5]=128;reject=P.public(retired);assert reject['P']&1==0
        # Use the existing source loader's declared cold publication window.
        N.put(retired,SelectedCharacter=33,OperMode=1,DisableScreenFlag=1,NmiDisable=255,Mirror_PPUMASK=0,
            FamilyMainCommit=1,ReloadCHRBank=1,VRAM_Buffer_AddrCtrl=0,VRAM_Buffer1_Offset=0)
        reads=retired.ppu_reads;loaded=N.invoke(retired,'BtLoad')
        assert loaded['P']&1 and bytes(retired.ram[3])==expected
        load_reads=retired.ppu_reads-reads;assert load_reads==16400
        loaded_check=N.invoke(retired,'BtCheck');assert loaded_check['P']&1
        rows.append(dict(identity=key,actual_real_compiled_cold=opening,source_underflow_death=death,
            death_engine=11,source_death_timer=0xc0,primitive_player_area_life_constructors=phases,
            retirement=dict(result=retire,only_cookie_first_byte_cleared=True,check=check,public_rejected=reject),
            cold_reload=dict(result=loaded,PPU_reads=load_reads,entire8192_newcache_full16cookie=True,check=loaded_check)))
    q=dict(passed=True,composition=composition,actual_candidate_lifecycle=rows,
        source_components_only=True,no_seeded_gameplay_qualification=True,actual_genuine_M_L_S_full_routes_separate=True,
        preserved_food_policy=True,no_other_code_or_layout_changes=True,outputs=0,Mesen=False)
    q['receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    parent=C.ROM.read_bytes()
    def deny(*args,**kw):raise AssertionError('Lifecycle source attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Current.Previous.Cold.Runner.Native,'run',deny):q=run(parent)
    print('RESULT '+json.dumps(dict(passed=q['passed'],receipt_SHA256=q['receipt_SHA256'],
        actual_candidate_SHA256=q['composition']['candidate_SHA256'],
        identities=[dict(identity=r['identity'],death_engine=r['death_engine'],source_death_timer=r['source_death_timer'],
            constructor_cases=len(r['primitive_player_area_life_constructors']),retirement=r['retirement'],cold_reload=r['cold_reload'])
            for r in q['actual_candidate_lifecycle']],source_components_only=True,outputs=0,Mesen=False),separators=(',',':')),flush=True)
