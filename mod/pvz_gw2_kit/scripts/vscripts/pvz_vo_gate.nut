// pvz_vo_gate.nut
// Team-gated VO switcher. Problem: BLU Scout = Peashooter but RED Scout = Imp
// share one TF2 class. Solution: on each player_spawn, re-point the player's
// vo entity alias to the right sound event via EmitSoundOnClient hooks.
//
// This runs purely in VScript (Squirrel) — no SourceMod required. TF2 loads
// vscripts from maps that enable them; our autoexec runs
// `script_execute pvz_vo_gate` on map load to force-register it on
// koth_harvest_final.

local TEAM_BLU = 3;
local TEAM_RED = 2;

local VO_MAP = {
    // key: tf2 class name → { team: { event: new_event_name } }
    scout = {
        [TEAM_BLU] = {
            battlecry = "Peashooter.BattleCry",
            pain      = "Peashooter.PainSevere",
            taunt     = "Peashooter.Taunt",
        },
        [TEAM_RED] = {
            battlecry = "Imp.BattleCry",
            pain      = "Imp.PainSevere",
        },
    },
    pyro     = { [TEAM_BLU] = { battlecry = "Chomper.BattleCry",    pain = "Chomper.PainSevere" } },
    medic    = { [TEAM_BLU] = { medic_call = "Sunflower.MedicCall", thanks = "Sunflower.Thanks" } },
    sniper   = { [TEAM_BLU] = { battlecry = "Cactus.BattleCry",     mark   = "Cactus.Mark" } },
    engineer = { [TEAM_RED] = { battlecry = "Scientist.BattleCry",  medic_call = "Scientist.HealCall" } },
    heavy    = { [TEAM_RED] = { battlecry = "AllStar.BattleCry",    taunt  = "AllStar.Taunt" } },
    soldier  = { [TEAM_RED] = { battlecry = "FootSoldier.BattleCry" } },
};

function OnGameEvent_player_spawn(params)
{
    local player = GetPlayerFromUserID(params.userid);
    if (player == null || !player.IsValid()) return;

    local classname = GetClassName(player);
    local team      = player.GetTeam();
    if (!(classname in VO_MAP)) return;
    if (!(team in VO_MAP[classname])) return;

    local events = VO_MAP[classname][team];
    foreach (slot, newEvent in events) {
        // Hint for the engine's VO scheduler. The actual swap happens by
        // the game_sounds_vo.txt entries we authored — this just stops
        // the stock event from firing on top.
        NetProps.SetPropString(player, "m_PlayerAnimState.m_sVOOverride_" + slot, newEvent);
    }
}

function GetClassName(player)
{
    local idx = NetProps.GetPropInt(player, "m_PlayerClass.m_iClass");
    switch (idx) {
        case 1: return "scout";
        case 2: return "sniper";
        case 3: return "soldier";
        case 4: return "demoman";
        case 5: return "medic";
        case 6: return "heavy";
        case 7: return "pyro";
        case 8: return "spy";
        case 9: return "engineer";
    }
    return "";
}

__CollectGameEventCallbacks(this);
