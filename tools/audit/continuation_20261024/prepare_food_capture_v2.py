from pathlib import Path
D=Path(__file__).resolve().parent;t=(D/'capture_powers_v1.py').read_text()
t=t.replace("out=BASE/(name+'-direct-v1')","out=BASE/(name+'-food-v2-direct-v1')").replace("rom=BASE/'wave-candidate-v1/candidate.nes'","rom=BASE/'food-candidate-v2/candidate.nes'")
t=t.replace("BASE/'health-food-v1'","BASE/'health-food-combined-v2'").replace("BASE/'kirby-copies-wave-v3'","BASE/'kirby-copies-combined-v2'")
(D/'capture_food_v2.py').write_text(t)
