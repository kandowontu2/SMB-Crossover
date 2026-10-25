"""Compose expanded spring/stomp adapters through the live Mac outer gates."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[2];D=R/'build/verification/expanded-bounce-mu-candidate-agent';O=R/'build/verification/bounce-adoption-my'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert not O.exists()
    assert sha(D/'incremental-merge-manifest.json')=='4548750b790768af2b0502ed38f46c41ab1f781554c2dc28417300a479e96ba7'
    packet=json.loads((D/'incremental-merge-manifest.json').read_text())
    for n,f in packet['files'].items():assert sha(D/'merge-staging'/n)==f['after_sha256'],n
    parent=json.loads((R/'build/checkpoints/level-roster-mx/manifest.json').read_text())
    shared=[n for n,f in packet['files'].items() if not f['new']]
    for n in shared:assert sha(R/n)==parent['source_files'][n],n
    texts={n:(R/n).read_text() for n in shared}
    def edit(n,old,new):
        assert texts[n].count(old)==1,(n,old,texts[n].count(old));texts[n]=texts[n].replace(old,new)
    edit('smb1base-mmc5-expanded.cfg','    CD_MOTION: load=X5_NEW_51,type=ro;',
      '    CD_MOTION: load=X5_NEW_51,type=ro;\n    CD_BOUNCE_BRIDGE: load=X5_NEW_51,type=ro,optional=yes,start=$a2ec;\n    X5_BOUNCE: load=X5_NEW_56,type=ro,optional=yes;')
    edit('src/chip_dale_motion.s',' lda SavedJoypadBits\n and #A_Button\n bne Integrate',
      ' jsr X5ChipReleaseBridge ; Local release-only gate; actual input unchanged.\n nop                     ; Same4B as original zero-page LDA plus AND.\n bne Integrate')
    edit('src/cv3_core.s','  farcall MegaManMovement::Horizontal','  farcall X5BounceCv3Horizontal')
    edit('src/entrypoint.s','.include "smb3_mario_dispatch.s"','.include "smb3_mario_dispatch.s"\n.include "x5_bounce.s"')
    edit('src/game.s','farcall LmUiGate','farcall X5BounceUiDispatch')
    edit('src/player.s','farcall LmMovementGate','farcall X5BounceMovementDispatch')
    for kind,target in [('Bounce','X5StompDispatch'),('Spring','X5SpringDispatch')]:
        old='  farcall MegaMan'+kind+'VelocityModes'
        edit('src/megaman_environment.s',old,'.if ::ENABLE_MMC5_EXPANDED\n  farcall '+target+'\n.else\n'+old+'\n.endif')
    owned=(D/'merge-staging/src/x5_bounce.s').read_text()
    assert owned.count('farcall VvUiDispatch,jmp')==1 and owned.count('farcall JnMovementDispatch,jmp')==1
    owned=owned.replace('farcall VvUiDispatch,jmp','farcall LmUiGate,jmp').replace('farcall JnMovementDispatch,jmp','farcall LmMovementGate,jmp')
    assert not (R/'src/x5_bounce.s').exists();O.mkdir(parents=True)
    for n in shared:
        p=O/'before'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/n,p)
    for n,t in texts.items():(R/n).write_text(t)
    (R/'src/x5_bounce.s').write_text(owned)
    (O/'adoption.json').write_text(json.dumps(dict(parent='level-roster-mx plus outline getter',packet_sha256=sha(D/'incremental-merge-manifest.json'),before={n:sha(O/'before'/n) for n in shared},after={n:sha(R/n) for n in shared},owned={'src/x5_bounce.s':sha(R/'src/x5_bounce.s')},inactive_UI='LmUiGate',inactive_movement='LmMovementGate',resident_growth=0),indent=2)+'\n')
    print('Adopted bounded spring/stomp adapters, preserving Mac and existing low-ID gates')

if __name__=='__main__':main()
