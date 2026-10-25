from pathlib import Path
D=Path(__file__).resolve().parent;P=D.parent/'2026-10-24-native-items-px'
t=(P/'capture_native_components_v1.py').read_text()
t=t.replace("out=BASE/(name+'-direct-v1')","out=BASE/(name+'-direct-v1')")
t=t.replace("rom=ROOT/'build/checkpoints/powerup-icon-pw/candidate.nes'","rom=BASE/'wave-candidate-v1/candidate.nes'")
t=t.replace("'NativeTail','NativeStatue'","'NativeTail','NativeStatue','KbHealth','KbCopy','KbMouth','KbAction','KbActionAge','KbFloat','KbDropKind','KbDropAge','KbMouthCopy','CdHealth','CdHeld','CdHide'")
t=t.replace("cpuCycle,case,age,","cpuCycle,case,age,phase,")
t=t.replace("ITEM_CASE or -1,ITEM_AGE or -1}","COPY_CASE or HEALTH_CASE or -1,COPY_TICK or HEALTH_AGE or -1,COPY_PHASE or 'food'}")
old="source=BASE/(name+'-native-v'+a.version)"
new="source=(BASE/'kirby-copies-wave-v3'/name.removeprefix('copies-')) if name.startswith('copies-')else BASE/'health-food-v1'/name.removeprefix('health-')"
assert t.count(old)==1;t=t.replace(old,new)
(D/'capture_powers_v1.py').write_text(t)
