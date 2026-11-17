EN = {
    1: "Heavy rain expected. Be ready: charge your phone and stay away from steep slopes and streams.",
    2: "Landslide warning. Keep away from slopes and river banks. Be ready to leave.",
    3: "Danger! Leave now and go to the nearest relief camp. Follow the green line on the map.",
}
ML = {
    1: "ശക്തമായ മഴയ്ക്ക് സാധ്യത. തയ്യാറായിരിക്കുക. ഫോൺ ചാർജ് ചെയ്തു വയ്ക്കുക. ചരിവുകളിലും തോടുകളുടെ അരികിലും പോകരുത്.",
    2: "ഉരുൾപൊട്ടൽ മുന്നറിയിപ്പ്. ചരിവുകളിൽ നിന്നും പുഴയോരത്തുനിന്നും മാറി നിൽക്കുക. ഒഴിഞ്ഞുപോകാൻ തയ്യാറായിരിക്കുക.",
    3: "അപകടം! ഉടൻ ഒഴിഞ്ഞുപോകുക. അടുത്തുള്ള ക്യാമ്പിലേക്ക് പോകുക.",
}

def alert_text(level):
    return f"XAI-RiskNet DEMO (sample data, not an official alert)\n{EN[level]}\n\n{ML[level]}"