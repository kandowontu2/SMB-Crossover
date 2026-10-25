from pathlib import Path
import importlib.util,re,json
D=Path(__file__).resolve().parent;base=D/'extend_pz_mmc3_v10.py';spec=importlib.util.spec_from_file_location('v10',base);v10=importlib.util.module_from_spec(spec);spec.loader.exec_module(v10)
def once(t,a,b):
 assert t.count(a)==1,(a,t.count(a));return t.replace(a,b)
def apply(source):
 v10.apply(source)
 p=source/'src/mmc3_oversized.s';t=p.read_text()
 for a,b in [('X5ChrMode=HpRamEnd+24','X5ChrMode=ProtoVariant+3'),('X5SpecialChrUpper=HpRamEnd+25','X5SpecialChrUpper=X5ChrMode+12'),('X5HudChrUpper=HpRamEnd+26','X5HudChrUpper=X5ChrMode+13'),('X5WideChrActive=HpRamEnd+27','X5WideChrActive=X5ChrMode+14')]:t=once(t,a,b)
 t=once(t,'.assert HpRamEnd+28<=XgLzHistory,error,"MMC3 controls stay in the actual alignment gap"','''.assert HpRamEnd+24<=ProtoVariant,error,"Actual MMC3 helper state and16 variants/eight bounce/status bytes stay below native Proto state"
.assert X5ChrMode=DarkwingVariant+1,error,"Direct-body mode follows the native legacy variants"
.assert X5WideChrActive<DwHealth,error,"Direct-body publication never overlaps Darkwing gameplay"
.assert Z2Variant<XgLzHistory,error,"Legacy variant remains below the aligned audio history"''');p.write_text(t)
 p=source/'smb1base-mmc3-oversized.cfg';t=p.read_text()
 for name in ('ROLL_CHR_DW_MEM','ROLL_CHR_Z2_MEM','ROLL_CHR_MAIN_MEM'):
  a=rf'({name}:[^\n]*?)file=%O';assert len(re.findall(a,t))==1,name;t=re.sub(a,r'\1file=""',t)
 p.write_text(t)
 (source.parent/'controls-v11.json').write_text(json.dumps(dict(scope='MMC3-specific linked footprint differs from MMC5. Assert all actual neighbours rather than borrowing the larger MMC5 boundary.',helper_end_symbol='HpRamEnd',menu_and_bounce_bytes=24,next_live_state='ProtoVariant',direct_body_mode='ProtoVariant+3',publication_end='X5ChrMode+14',next_live_gameplay='DwHealth',separate_raw_chr_emission=False),indent=2))
