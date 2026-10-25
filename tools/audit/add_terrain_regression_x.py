from pathlib import Path
R=Path(__file__).resolve().parents[2]
p=R/'build/verification/terrain-coin-queue-q/new-mmc3/fixture.lua'
t=p.read_text(encoding='utf-8')
t='SelectEasyRules() -- Reproduce the ordinary Easy Bill recording.\n'+t
t=t.replace("TEST_DIR..'result.json'","OUTPUT..ROM_NAME..'-terrain-coin-publication.json'")
out=R/'tests/terrain-coin-publication.lua';assert not out.exists();out.write_text(t,encoding='utf-8')
print('PERMANENT_REGRESSION',out)
