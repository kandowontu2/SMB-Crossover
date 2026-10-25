from pathlib import Path
D=Path(__file__).resolve().parent;t=(D/'diagnose_kirby_wave_v1.py').read_text()
t=t.replace("out=D/'kirby-wave-diagnosis-v1'","out=D/'kirby-wave-fixed-v2'")
t=t.replace("rom=R/'build/checkpoints/native-items-px/candidate.nes'","rom=D/'wave-candidate-v1/candidate.nes'")
t=t.replace("kirby-copies-v2/easy/run.lua","kirby-copies-wave-v3/easy/run.lua")
(D/'diagnose_kirby_wave_fixed_v2.py').write_text(t)
t=t.replace("out=D/'kirby-wave-fixed-v2'","out=D/'kirby-wave-parent-v2'").replace("rom=D/'wave-candidate-v1/candidate.nes'","rom=R/'build/checkpoints/native-items-px/candidate.nes'")
(D/'diagnose_kirby_wave_parent_v2.py').write_text(t)
