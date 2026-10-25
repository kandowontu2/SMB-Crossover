from pathlib import Path
import shutil
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;out=D/'food-candidate-v3/source';shutil.copytree(D/'food-candidate-v2/source',out)
p=out/'src/kirby_draw.s';shutil.copy2(R/'src/kirby_draw.s',p);t=p.read_text();old='''  lda #108
  sta R4
  lda #0
  sta R5
  lda #12
  sta R6
  jsr Draw
Done:
''';assert t.count(old)==1
new='''  ; Keep even32px native enemy portraits in the empty left HUD margin.
  ; The old position covered the coin counter with tall copied enemies.
  lda #4
  sta R4
  lda #0
  sta R5
  lda #0
  sta R6
  jsr Draw
Done:
''';p.write_text(t.replace(old,new))
t=(D/'packet_food_v2.py').read_text().replace('food-candidate-v2','food-candidate-v3').replace('food-packet-v2','food-packet-v3')
t=t.replace("'src/chip_dale_dispatch.s']","'src/chip_dale_dispatch.s','src/kirby_draw.s']")
(D/'packet_food_v3.py').write_text(t)
t=(D/'run_kirby_copies_combined_v2.py').read_text().replace('food-candidate-v2','food-candidate-v3').replace('kirby-copies-combined-v2','kirby-copies-final-v3')
(D/'run_kirby_copies_final_v3.py').write_text(t)
t=(D/'run_health_food_combined_v2.py').read_text().replace('food-candidate-v2','food-candidate-v3').replace('health-food-combined-v2','health-food-final-v3')
(D/'run_health_food_final_v3.py').write_text(t)
t=(D/'capture_food_v2.py').read_text().replace('food-candidate-v2','food-candidate-v3').replace('food-v2-direct-v1','food-v3-direct-v1').replace('health-food-combined-v2','health-food-final-v3').replace('kirby-copies-combined-v2','kirby-copies-final-v3')
(D/'capture_food_v3.py').write_text(t)
