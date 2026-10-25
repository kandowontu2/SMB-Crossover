from pathlib import Path
R=Path(__file__).resolve().parents[2]
s=(R/'tools/audit/check_showcase_pixels_ah.py').read_text(encoding='utf-8')
s=s.replace('Showcases/Verified/','Showcases/Ready/').replace('showcase-pixels-ah','showcase-pixels-aj')
exec(compile(s,str(R/'tools/audit/check_showcase_pixels_ah.py'),'exec'),{'__name__':'__main__','__file__':str(R/'tools/audit/check_showcase_pixels_ah.py')})
