from pathlib import Path
D=Path(__file__).resolve().parent
t=(D/'run_health_food_v1.py').read_text().replace("rom=R/'build/checkpoints/native-items-px/candidate.nes'","rom=D/'food-candidate-v2/candidate.nes'").replace("out=D/'health-food-v1'","out=D/'health-food-combined-v2'")
old="dict(kind=0,health=2),dict(kind=0,health=3),dict(kind=0,health=3),dict(kind=1,health=3,sceneStatus=True,seed=[['PlayerStatus',1],['CdHealth',1]])"
new="dict(kind=0,health=2),dict(kind=1,health=3),dict(kind=0,health=3),dict(kind=1,health=3,seed=[['CdHealth',1]])"
assert t.count(old)==1;t=t.replace(old,new)
(D/'run_health_food_combined_v2.py').write_text(t)
t=(D/'run_kirby_copies_wave_v3.py').read_text().replace('wave-candidate-v1','food-candidate-v2').replace('kirby-copies-wave-v3','kirby-copies-combined-v2')
(D/'run_kirby_copies_combined_v2.py').write_text(t)
t=(D/'packet_wave_v1.py').read_text().replace('wave-candidate-v1','food-candidate-v2').replace('wave-packet-v1','food-packet-v2')
old="name='src/kirby_weapons.s';p=candidate/'source'/name;q=source/name;changes[name]=dict(before=sha(q),after=sha(p));shutil.copy2(p,q)"
new="for name in ['src/kirby_weapons.s','src/chip_dale_health.s','src/chip_dale_dispatch.s']:\n p=candidate/'source'/name;q=source/name;changes[name]=dict(before=sha(q),after=sha(p));shutil.copy2(p,q)"
assert t.count(old)==1;t=t.replace(old,new)
(D/'packet_food_v2.py').write_text(t)
