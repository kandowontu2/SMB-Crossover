"""Retain I and prepare its narrow controller handoff correction; no execution."""
from pathlib import Path
import ast,hashlib,json

ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    source=ROOT/'tools/playthroughs/scrooge_castle_phase_i.lua'
    driver=ROOT/'tools/audit/run_current49p_scrooge_phase_i.py'
    assert sha(source)=='ecac90b9c1573ff52902c315b37e89ac008b01e1225c50ee1169d7ac90cc88c0'
    assert sha(driver)=='da1b734ff5496ff85cc2b2fd4e875691a21d112e229c6a8d012f6d21f47fd39d'
    destination=source.with_name('scrooge_castle_phase_i2.lua')
    nextdriver=driver.with_name('run_current49p_scrooge_phase_i2.py')
    assert not destination.exists()and not nextdriver.exists()
    text=source.read_text();assert text.count('c.x>=1144')==1
    text=text.replace('c.x>=1144','c.x>=1128')
    destination.write_text(text)
    code=driver.read_text().replace('root49p-scrooge-phase-i','root49p-scrooge-phase-i2')
    code=code.replace('scrooge_castle_phase_i.lua','scrooge_castle_phase_i2.lua').replace('PHASE_I','PHASE_I2')
    ast.parse(code);nextdriver.write_text(code)
    print(json.dumps(dict(status='PREPARED_CONTROLLER_HANDOFF_ONLY_NOT_EXECUTED',policy_sha256=sha(destination),
                          driver_sha256=sha(nextdriver),retained_I_source_sha256=sha(source),retained_I_driver_sha256=sha(driver))))

if __name__=='__main__':main()
