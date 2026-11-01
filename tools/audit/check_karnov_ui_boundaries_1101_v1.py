"""Ensure exposed raw34 never reaches the legacy12-owner inventory leaves."""
from pathlib import Path
import hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import check_hogan_current_bounded_v1 as C
import ff_wram_host_controls_v7 as H
from check_tmnt_render_oa import address,location
O=R/'build/karnov-host-resource-base-1101-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    q=dict(passed=False,source_CPU=True,native=False,installed=False,progress_only=True)
    paths=[Path(__file__),O/'terrain-assembly.json',O/'candidate.nes',O/'candidate.dbg']
    try:
        stage=json.loads(paths[1].read_text());assert stage['passed']and stage['menu']
        for p,h in stage['bindings'].items():assert sha(p)==h,p
        b=H.C.qualified(O/'candidate.nes')
        names=['InventorySupported','InventoryUiTick','InventoryHud','NrFullPower','NrUi']
        dangerous=['CheatsInventoryMax','InventoryGrant','InventoryHasRaw','InventoryIndex','InventoryMaximum','InventoryCycle']
        markers={(address(b,n),((location(b,n)-16)//8192)|128):n for n in dangerous}
        owners={n:(address(b,n),size)for n,size in [('InvOwnedLo',12),('InvOwnedHi',12),('InvSelected',12),('InvAmmo',192)]}
        rows=[]
        for loaded,mode,name in itertools.product([False,True],[0,1],names):
            m=C.fresh(b);H.put(m,SelectedCharacter=34,FmAlts=1,CrossoverMenuIndex=7,CrossoverBehaviorVersion=mode)
            if loaded:
                H.put(m,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,NumberofLives=2)
                C.invoke(m,'InitScreen')
                assert m.ram[2][address(b,'KrReady')&8191]==167
                H.put(m,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,DisableScreenFlag=0,Mirror_PPUMASK=30,NmiDisable=0)
            before={n:bytes(m[a:a+size])for n,(a,size)in owners.items()}
            events=[];c=H.start(m,name,a=89,x=0,y=0,p=0x70)
            def watch(mem,c,i):
                if c.pc>=32768:
                    n=markers.get((c.pc,mem.rawtags[(c.pc-32768)//8192]));assert not n,('raw34 entered legacy indexed leaf',name,n,loaded,mode)
                if not loaded:assert not(0xa000<=c.pc<0xc000 and mem.rawtags[1]==3),('Cold UI ran RAM code',name)
            c,low=H.finish(m,c,watch)
            assert all(bytes(m[a:a+size])==before[n]for n,(a,size)in owners.items()),('Legacy ownership/ammo changed',loaded,mode,name)
            if name=='InventorySupported':assert not c.p&1,'Karnov must decline legacy2.02 inventory'
            rows.append(dict(entry=name,loaded=loaded,hard=bool(mode),returned=[c.a,c.x,c.y,c.p,c.sp],minimum_SP=low))
        q.update(passed=True,ROM_sha256=stage['ROM_sha256'],entry_cases=len(rows),legacy_inventory_declined=True,no_legacy_raw34_index_leaf=True,no_legacy_owner_ammo_mutation=True,no_cold_RAM_opcode=True,rows=rows,scope='Actual exposed inventory support/UI/HUD and NrFullPower/NrUi entrypoints in Easy/Hard, cold and initialized. Proves these paths avoid legacy12-owner index leaves and do not change their ownership/ammo. Full-power is currently an unsupported no-op for Karnov, not an implemented upgrade. Does not close every pickup/collision/direct-ID leaf or admit gameplay.')
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['bindings']={str(p.resolve()):sha(p)for p in paths}
    (O/'ui-boundary-controls.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','rows','traceback']}));assert q['passed'],q.get('error')


if __name__=='__main__':main()
