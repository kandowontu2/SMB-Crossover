from pathlib import Path
import shutil
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;out=D/'wave-candidate-v1/source';(out/'src').mkdir(parents=True,exist_ok=False)
for name in ['kirby.s','kirby_weapons.s']:shutil.copy2(R/'src'/name,out/'src'/name)
shutil.copy2(R/'smb1base-mmc5-expanded.cfg',out/'smb1base-mmc5-expanded.cfg')
p=out/'src/kirby_weapons.s';text=p.read_text();old='''  lda KbShotAge,x
  and #8
  jeq WaveDown
  lda #$ff
  jne Wave
WaveDown:
  lda #1
Wave:
''';assert text.count(old)==1
new='''  lda KbShotAge,x
  and #8
  jeq WaveDown
  lda #1
  jne Wave
WaveDown:
  ; Start upward from the mouth. The opposite phase drove this16px effect
  ; into the floor within five updates. These same8-update half waves now
  ; stay above the ground without changing their speed, range or CPU cost.
  lda #$ff
Wave:
'''
p.write_text(text.replace(old,new))
