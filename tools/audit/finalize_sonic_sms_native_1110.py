"""Close a Sonic component against a separately qualified shared name carrier."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import check_sonic_sms_native_prototype_1110 as S
import check_sonic_sms_native_irq_1110 as IRQ


def sha(path):return sha256(path.read_bytes()).hexdigest()


def startup(raw,button,pad):
    I,N=S.Current.I,S.N
    b=S.Current.W.bundle(raw)
    previous=N.Bus;N.Bus=I.C.C.C.C.V.ControllerBus
    try:
        m=I.UI.seed(b,0)
        for _ in range(10):I.UI.key(m,32,pad=pad)
        assert S.Current.menu_name(m)[0]=='SONIC'
        assert N.get(m,'SelectedCharacter')==0 and N.get(m,'MarioVariant')==10
        answer=I.UI.key(m,button,pad=pad)
        I.F.invoke(m,'ChkContinue',a=answer['A'],x=answer['X'],y=answer['Y'],p=answer['P'])
        N.invoke(m,'PauseRoutine',a=0)
    finally:N.Bus=previous
    def frame(keys=0):
        N.put(m,SavedJoypadBits=keys,SavedJoypad1Bits=keys,SavedJoypad2Bits=0,
              A_B_Buttons=keys&192,Left_Right_Buttons=keys&3,Up_Down_Buttons=keys&12,NmiDisable=255)
        S.Roster.invoke_game(m,'GameLoop')
        N.consume(m);S.Roster.Cold.clear(m)
    for entrance in range(600):
        if (N.get(m,'OperMode_Task'),N.get(m,'GameEngineSubroutine'))==(3,8):break
        frame()
    else:raise AssertionError(('Sonic actual menu/newgame bound',button,pad))
    rows=[]
    for age in range(130):
        keys=0 if age<20 else 65 if age<60 else 129 if age<82 else 0
        frame(keys)
        row=dict(age=age,x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
                 y=N.get(m,'Player_Y_Position'),state=N.get(m,'Player_State'),chr=m.chr_latches[0])
        assert N.get(m,'SelectedCharacter')==0 and N.get(m,'MarioVariant')==10
        assert N.get(m,'NumberofLives')==2 and N.get(m,'GameEngineSubroutine')==8,row
        assert N.get(m,'X5ChrMode')==0x85 and row['chr'] in S.Render.S.PAGES,row
        rows.append(row)
    assert rows[59]['x']>rows[19]['x']+16
    assert min(r['y']for r in rows[60:])<rows[19]['y']-8
    return dict(button=button,pad=pad,entrance_updates=entrance,gameplay_updates=130,
                idle=[rows[0],rows[19]],right=rows[59],jump_min_y=min(r['y']for r in rows[60:]),
                final=rows[-1],lives=2,actual_native_owner_zero=True,
                new_readiness_or_cookie_bypass=False)


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    cli.add_argument('--name-recipe',type=Path,required=True)
    cli.add_argument('--shared-proof',type=Path,required=True)
    args=cli.parse_args();assert args.output.resolve()==S.OUT
    shared=json.loads(args.shared_proof.read_text())
    assert shared['passed']
    S.NAME_RECIPE=args.name_recipe.resolve()
    before,after,patches,labels,funding,art,records=S.compose(args.output)
    assert shared['expected_memory_only_SHA256']==S.digest(before)
    menu=S.frontend(before,after);print('Final menu',json.dumps(menu),flush=True)
    colors=S.colors(before,after)
    body=S.body(after);print('Final body',json.dumps(body),flush=True)
    leaves=S.Render.leaves(before,after,labels);print('All skin modes',json.dumps(leaves),flush=True)
    starts=[startup(after,button,pad)for button in (16,128)for pad in (1,2)]
    print('Four actual Sonic starts passed',flush=True)
    vectors=IRQ.vectors(before,after,funding['required_name_endpoint']['PC'])
    print('Final vectors',json.dumps(vectors),flush=True)
    proof=dict(passed=True,prototype=True,source_CPU_only=True,ROM_written=False,
        native_pending=True,interrupt_pending=False,parent_SHA256=S.digest(before),
        expected_memory_only_SHA256=S.digest(after),patches=patches,labels=labels,
        native_config=dict(menu_slot=0,MarioVariant=10,raw=0,Select_presses=10,menu_name='SONIC',
                           physics='Existing Mario host',physical_CHR=list(S.Render.S.PAGES),palette=[22,18,48]),
        required_shared_recipe=str(S.NAME_RECIPE.relative_to(S.R)),
        required_shared_proof=str(args.shared_proof.resolve().relative_to(S.R)),
        CPU=dict(menu=menu,palette=colors,body=body,all_skin_modes=leaves,startup=starts,vectors=vectors),
        source_funding=funding,
        retired_metadata_aliases=dict(MarioHint=0xaca5,QueueVariantHint_Hint=0xaca5),
        unchanged_public_PCs=dict(KmGraphics=0xb690,KmSelect=0xb6cb,KmNmiSlot0=0xa9c0,BmColors=0xbaa4),
        limitations=['Native Mario host movement/collision/powerups and sound are temporary.',
                     'SMS pose pixels use a16px native canvas and3color adaptation.',
                     'Original SMS physics, rolling, rings and full source lifecycle remain incomplete.',
                     'Root native Mesen/Downloads replay required; no1-1/fullpowerup claim.'],
        scope='Legitimate native owner0 alternate10, real menu/newgame/control startup, '
              'source-derived SMS art and exact old skin/menu/palette/interrupt contracts. '
              'This is an explicitly incomplete Sonic SMS prototype, not the completed port.',
        bindings={p.resolve().relative_to(S.R).as_posix():sha(p) for p in
            (Path(__file__),Path(S.__file__),Path(IRQ.__file__),Path(S.Render.__file__),
             Path(S.Render.S.__file__),S.SOURCE,S.Render.S.SOURCE,S.Render.S.BASE,S.Render.S.SMS,
             S.NAME_RECIPE,args.shared_proof,Path(S.Roster.__file__),
             S.R/'build/mini-mario-owner-1103-v15/carrier-audit-v16.json',
             S.R/'build/prince-actor-1101-v1/smb3-pages.json',
             S.R/'build/mega-giant-chr-lease-1110/proof.json')})
    (args.output/'qualified-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    (args.output/'sonic-native.chr').write_bytes(art)
    print(json.dumps(dict(passed=True,expected_memory_only_SHA256=S.digest(after),patches=len(patches))),flush=True)


if __name__=='__main__':main()
