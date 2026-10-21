-- Regression for the reported falling-Goomba-contact crash. Source Bill has
-- canStomp=false: genuine contact must injure/kill normally without granting
-- Mario's stomp or corrupting enemy health. The old stomp-success oracle was
-- incorrect and is preserved in historical v24 evidence.
ORDINARY_CHARACTER=3
dofile(TEST_DIR..'guest-ordinary-contact.lua')
