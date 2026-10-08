// pvz_gw2_kit scoreboard override
// Minimal cosmetic edit: swaps the "Class" column header text and widens it slightly
// so "Foot Soldier" / "Peashooter" don't truncate.
// Everything else inherits from stock scoreboard.res.

"Resource/UI/Scoreboard.res"
{
    "BluePlayerList"
    {
        "ControlName"   "SectionedListPanel"
        "fieldName"     "BluePlayerList"
        "wide"          "f0"
    }
    "RedPlayerList"
    {
        "ControlName"   "SectionedListPanel"
        "fieldName"     "RedPlayerList"
        "wide"          "f0"
    }

    "BlueTeamLabel"
    {
        "ControlName"   "CExLabel"
        "fieldName"     "BlueTeamLabel"
        "labelText"     "Plants"
        "textAlignment" "west"
    }
    "RedTeamLabel"
    {
        "ControlName"   "CExLabel"
        "fieldName"     "RedTeamLabel"
        "labelText"     "Zombies"
        "textAlignment" "west"
    }

    "ServerLabel"
    {
        "ControlName"   "CExLabel"
        "fieldName"     "ServerLabel"
        "labelText"     "PvZ GW2 x TF2 - KOTH Harvest"
        "textAlignment" "center"
    }
}
