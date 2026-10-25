from pathlib import Path
R=Path(__file__).resolve().parents[2]
s=(R/'tools/audit/check_terrain_repair_build_v.py').read_text(encoding='utf-8')
assert s.count("'build/verification/terrain-repair-build-v'")==1;s=s.replace("'build/verification/terrain-repair-build-v'","'build/verification/terrain-repair-build-ag'")
assert s.count('len(diff)==14')==1;s=s.replace('len(diff)==14','len(diff)==19')
exec(compile(s,str(R/'tools/audit/check_terrain_repair_build_v.py'),'exec'),{'__name__':'__main__','__file__':str(R/'tools/audit/check_terrain_repair_build_v.py')})
