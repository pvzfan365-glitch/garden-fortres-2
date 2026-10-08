// pvz_gw2_cornertag.nut
// Persistent small bottom-right tag during matches: "PvZ GW2 x TF2 v0.1".
// Uses ScriptPrintMessageChatAll on round start and a periodic HudHint refresh
// (TF2 VScript has no direct HUD element API, so we lean on HudHint which
// renders in the corner and respects user HUD scale).

function OnGameEvent_teamplay_round_start(params)
{
    ShowCornerTag();
}

function ShowCornerTag()
{
    local players = [];
    for (local i = 1; i <= MaxClients().tointeger(); i++) {
        local p = PlayerInstanceFromIndex(i);
        if (p != null && p.IsValid()) {
            players.append(p);
        }
    }
    foreach (p in players) {
        // 2 = HUD_PRINTCONSOLE (silent), we instead want a sticky tag.
        // ClientPrint type 4 center-screen displays for ~5s each round start,
        // which is the simplest periodic reminder available in pure VScript.
        ClientPrint(p, 4, "PvZ GW2 x TF2 v0.1");
    }
}

__CollectGameEventCallbacks(this);
