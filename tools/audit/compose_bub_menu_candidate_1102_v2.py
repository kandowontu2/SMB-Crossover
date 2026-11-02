"""Compose the formally granted, blocked static frontend over exact1cd8."""
from pathlib import Path
import sys,json,hashlib,copy
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import audit_bub_menu_frontend_1102_v1 as F
M=F.M;address=F.address;location=F.location
O=R/'build/bub-menu-candidate-1102-v2';P=F.O
BASE=R/'build/metal-reservation-1102-v42/candidate.nes'
PIN='1cd8e192ee4bee33dfe0d9c737bec097e1cf2339e0b9f77353fd5194f2530f55'
sha=F.sha
NAMES=['SafecallA_SMC','FarcallJmpTarget_SMC','FarCallCommon','PrimaryGameSetup',
       'OperMode','OperMode_Task','DisableScreenFlag','Mirror_PPUMASK','Mirror_PPUCTRL','NmiDisable','FamilyMainCommit','VRAM_Buffer1_Offset','VRAM_Buffer_AddrCtrl','VRAM_Buffer1',
       'SelectedCharacter','CrossoverMenuState','CrossoverMenuButtons','CrossoverContinue','CrossoverMenuIndex','CrossoverMenuPressed','CrossoverOptionsFocus','CrossoverTitleDrawn','MarioVariant','SavedJoypad1Bits','SavedJoypad2Bits',
       'CurrentBank','CurrentBankC','CurrentCHRBank','CHRBankInitValues','ChrPhysicalMap','X5ChrMode','X5WideChrActive','X5PublishChr','ReloadCHRBank','CurrentOAMOffset','Sprite_Data','FmAlts','FmGroups',
       'MenuResolveCharacter','QueueSelection','CrossoverMenuInput','DrawSelectionPreview','FmPending','FmQueueName','FmDrawPreviewSelected','FmNames','FmPreviewTiles','FmPreviewColors','FmCfRestoreP1','FmStartRetireFlags','FmStartFlags','GroundPaletteData',
       'R0','R1','R2','R3','R4','R5','R6','R7','GameEngineSubroutine','Player_X_Position','Player_PageLoc','Player_Y_Position','WorldNumber','LevelNumber','NumberofLives','GameLoop','NonMaskableInterrupt','IrqScrollSplit','NmiSkipped']

def main():
    assert sha(BASE)==PIN;O.mkdir(exist_ok=True)
    freeze=json.loads((P/'frontend-source-freeze.json').read_text())
    for name,digest in freeze['bindings'].items():assert sha(R/name)==digest,name
    grant_paths=[R/'docs/qa/allocations'/n for n in['bub-menu-1102-v1.json','bub-menu-flags-1102-v2.json','bub-menu-static-1102-v3.json','roster-rebase-1102-v3.json']]
    grants=[json.loads(p.read_text())for p in grant_paths];assert all(g['granted']for g in grants)
    static=grants[2];assert static['base_ROM_SHA256']==PIN and not static['menu_admitted']
    proposal=json.loads((P/'controls-proposal.json').read_text());patches=proposal['all_patches']
    # The formal static lease includes all15 art/init/data and6hook patches;
    # navigation,66B glue and flags stay inside their separate prior grants.
    authorized={(p['offset'],p['old'],p['new'])for p in static['exact_static_patches']}
    art=json.loads((P/'art-proposal.json').read_text())['requested_patches']
    assert {(p['offset'],p['old'],p['new'])for p in art+proposal['required_operand_patches']}==authorized
    raw=BASE.read_bytes();out=bytearray(raw);legal=set();applied=[]
    for z in patches:
        at=z['offset'];old=bytes.fromhex(z['old']);new=bytes.fromhex(z['new'])
        assert len(old)==len(new)and out[at:at+len(old)]==old,z.get('role',z)
        out[at:at+len(new)]=new;legal.update(range(at,at+len(new)));applied.append(z)
    assert out[16+66*8192+0xd64]==0x38,'New owner must remain confirmation blocked'
    changed=[i for i,(a,b)in enumerate(zip(raw,out))if a!=b]
    assert all(i in legal for i in changed)and bytes(out[:16])==raw[:16]and len(out)==len(raw)
    candidate=O/'candidate.nes';candidate.write_bytes(out)
    # Keep minimal exact globals/segments for the controller and small CPU
    # binder; read the existing debug source without copying its12MB tree.
    b=F.scoped_load(BASE);minimal=dict(raw=bytes(out),syms={},segs={})
    keep=set(NAMES)
    for name in keep:
        assert name in b['syms'],name;minimal['syms'][name]=copy.deepcopy(b['syms'][name])
        if 'seg'in b['syms'][name]:
            seg=b['syms'][name]['seg'];minimal['segs'][seg]=copy.deepcopy(b['segs'][seg])
    # Re-encode valid ca65 debug records, retaining original segment IDs.
    def fields(d):return ','.join(k+'='+str(v)for k,v in d.items())
    lines=['version\tmajor=2,minor=0']
    for seg,z in minimal['segs'].items():lines.append('seg\t'+fields(dict(z,id=seg)))
    for number,(name,z)in enumerate(sorted(minimal['syms'].items())):
        lines.append('sym\t'+fields(dict(z,id=number,name='"'+name+'"')))
    # New typed entries get explicit physical bank segments.
    for i,(name,pc,bank)in enumerate([('BubColdPending',0xbced,76),('BubMenuToggle',0xad39,66),('BubMenuConfirmGate',0xad5d,66),('BubMenuStreamDecoder',0xafb5,66)]):
        seg=str(900000+i);lines.append('seg\t'+fields(dict(id=seg,name='"'+name+'_SEG"',start=hex(0xa000),size=8192,ooffs=16+bank*8192,type='ro')))
        lines.append('sym\t'+fields(dict(id=900000+i,name='"'+name+'"',val=hex(pc),seg=seg,type='lab')))
    (O/'candidate.dbg').write_text('\n'.join(lines)+'\n')
    labels=['al %06X .%s'%(address(b,n),n)for n in sorted(keep)]
    labels+=['al %06X .%s'%(pc,n)for n,pc in [('BubColdPending',0xbced),('BubMenuToggle',0xad39),('BubMenuConfirmGate',0xad5d),('BubMenuStreamDecoder',0xafb5)]]
    (O/'candidate.lbl').write_text('\n'.join(labels)+'\n')
    cb=F.scoped_load(candidate);cases=[]
    for bob in [False,True]:
        m=M.fresh(cb);M.put(m,CrossoverMenuIndex=32,FmGroups=128 if bob else 0)
        F.invoke(m,'MenuResolveCharacter');F.invoke(m,'QueueSelection')
        assert M.get(m,'SelectedCharacter')==39
        name=[p['bytes']for p in F.commands(m)if p['address']==0x2328][-1]
        expected=[36]*16;expected[6:9]=[11,24 if bob else 30,11];assert name==expected
        for key in[16,128,48,160,176]:
            n=M.fork(m);M.put(n,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=key,SavedJoypad2Bits=0)
            F.invoke(n,'CrossoverMenuInput');assert M.get(n,'CrossoverMenuState')==2
        cases.append(dict(Bob=bob,raw=39,name=name,blocked_confirm_inputs=5))
    # Real public screen construction includes the new forced-blank wrapper.
    m=M.fresh(cb);M.put(m,CrossoverMenuState=1,Mirror_PPUMASK=0,DisableScreenFlag=1)
    F.invoke(m,'CrossoverMenuInput');assert M.get(m,'CrossoverMenuState')==2
    for pos,v in[(676,245),(677,246),(708,247),(709,248)]:assert m.vram[0x2000+pos]==v
    for name,digest in freeze['bindings'].items():assert sha(R/name)==digest,name
    q=dict(passed=True,private_menu_only=True,native=False,installed=False,menu_admitted=False,confirmation_blocked=True,
        base_ROM_SHA256=PIN,candidate=candidate.relative_to(R).as_posix(),ROM_SHA256=sha(candidate),changed_bytes=len(changed),
        all_changes_exact_granted_owned_diffs=True,all_other_current_Metal_Ex_Arthur_bytes_and_cookies_exact=True,
        patches=applied,new_static_UI_cases=cases,actual_public_screen_constructed=True,
        frozen_proposal_sources_unchanged=True,original_debug_input_read_only=True,minimal_debug_globals=len(keep)+4,
        bindings={p.relative_to(R).as_posix():sha(p)for p in[Path(__file__),BASE,P/'frontend-source-freeze.json',P/'controls-proposal.json',*grant_paths,candidate,O/'candidate.dbg',O/'candidate.lbl']})
    (O/'candidate.json').write_text(json.dumps(q,indent=2)+'\n')
    files=[p for p in O.rglob('*')if p.is_file()];assert sum(p.stat().st_size for p in files)<32000000 and len(files)<=128
    print(json.dumps({k:v for k,v in q.items()if k not in['bindings','patches']}))
if __name__=='__main__':main()
