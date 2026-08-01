import random
from typing import Dict, Any, Tuple

GENRE_THEMES = {
    "Synthwave": {
        "topics": ["Neon highway drive at midnight", "Retro arcade memories", "Cyberpunk skyline glow", "Electric romance"],
        "verses": [
            "Tires hum on the wet asphalt\nReflections cut through the endless night\nDigital clocks that never stop\nRunning under the crimson light",
            "Speedometer climbing past eighty-four\nSynth bass pulsing right through the floor\nCassette tape winding back in time\nEvery beat in rhythm, every line in rhyme"
        ],
        "choruses": [
            "We are ghosts in the neon haze\nLiving forever in an eighties phase\nFollow the highway into the dawn\nBefore the morning, before we're gone",
            "Hold on tight to the violet glow\nFeel the frequencies as they flow\nSynthetic dreams that never fade\nIn the city the electric made"
        ],
        "bridges": [
            "And when the grid begins to bend\nWe know this ride will never end\nAnalog heart, digital soul\nTaking back complete control"
        ],
        "outros": [
            "Driving into the sun...\nJust you and me and the horizon.\nFade out on the synth arpeggio."
        ],
        "default_bpm": 124,
        "default_key": "A Minor"
    },
    "Lo-Fi": {
        "topics": ["Late night study session", "Raindrops on the window pane", "Quiet cafe moments", "Dreaming while coding"],
        "verses": [
            "Rain tapping softly on the window sill\nCup of warm coffee keeping away the chill\nCursor is blinking on the empty screen\nSomewhere between what is and what has been",
            "Lofi vinyl crackle on the turntable spin\nLetting the calm and the quiet in\nFootsteps outside on the damp sidewalk\nNothing left to prove, no need to talk"
        ],
        "choruses": [
            "Just another late night reverie\nFloating through the calm melody\nTake your time, let the world pass by\nUnderneath the quiet indigo sky",
            "Soft piano chords in the afternoon\nChasing the glow of a lazy moon\nBreathe in deep and release the weight\nEverything will find its place in time"
        ],
        "bridges": [
            "Sometimes the quiet speaks the loudest sound\nWhen peace is the only thing around\nGentle tape wobble, mellow tone\nIn this room, never feel alone"
        ],
        "outros": [
            "Tape slows down...\nRain keeps falling...\nWarm static fades into the night."
        ],
        "default_bpm": 80,
        "default_key": "C Major"
    },
    "Cyberpunk": {
        "topics": ["Android awakenings", "Megacity underground", "Neural interface glitch", "Neon rain revolution"],
        "verses": [
            "Wires in my veins, circuits in my head\nCounting down the seconds while the city bled\nHolographic billboards flickering high\nNo stars left in this synthetic sky",
            "Underground alleys where the rebels meet\nHeavy sub-bass rattling the street\nEncrypted signals flying through the air\nWe live on the edge and we don't care"
        ],
        "choruses": [
            "Break the protocol, sever the line\nThis revolution is yours and mine\nThrough the chromium mist and the laser rain\nWe will rise above the digital pain",
            "System overload, sirens screaming loud\nLost in the digital neon crowd\nThey can track the code, but they can't break free\nThe future belongs to you and me"
        ],
        "bridges": [
            "Download the fire, ignite the grid\nEverything they thought that we hid\nZeroes and ones ignite the spark\nA sudden flash in the techno dark"
        ],
        "outros": [
            "Disconnect.\nGlitch in the matrix.\nReboot complete."
        ],
        "default_bpm": 135,
        "default_key": "D Minor"
    },
    "Cinematic Epic": {
        "topics": ["Warrior's journey", "Rise of empires", "Beyond the stars", "Echoes of eternity"],
        "verses": [
            "Across the mountains where the thunder calls\nShadows fall against ancient walls\nA distant horn begins to sound\nShaking the stones beneath the ground",
            "The banners rise against the gale\nEvery spirit ready to prevail\nInto the storm we take our stand\nFor honor, truth, and the fatherland"
        ],
        "choruses": [
            "Rise up, let the drums resound\nLift your eyes from the battleground\nThrough fire, through ash, through endless skies\nThe legend wakes and never dies",
            "Hear the symphony of the brave\nCarried on the crest of the tidal wave\nNo retreat and no defeat\nWhen fate and courage finally meet"
        ],
        "bridges": [
            "From the darkest night to the golden crest\nThe greatest trial, the final test\nWith one last breath we take the heights\nUnderneath eternal lights"
        ],
        "outros": [
            "The storm subsides.\nThe kingdom stands.\nFinal crescendo."
        ],
        "default_bpm": 100,
        "default_key": "D Minor"
    },
    "Deep House": {
        "topics": ["Sunset beach party", "Club trance ecstasy", "Hypnotic rhythm", "Bassline groove"],
        "verses": [
            "Sun dipping down beneath the ocean line\nGlass of cool tonic, everything is fine\nFeel the four-on-the-floor start to groove\nNothing left to do but let your body move",
            "Lights getting dim, the bass gets low\nMoving with the current, let the rhythm flow\nSmiles all around, the beat takes hold\nA golden energy worth more than gold"
        ],
        "choruses": [
            "Lose your mind in the deep sound\nFeet off the earth, feet off the ground\nKeep moving until the break of day\nLet the heavy bassline wash you away",
            "Can you feel it? The rhythm in your chest\nPut every doubt and every fear to rest\nJust groove, just dance, just be\nIn this pure sonic ecstasy"
        ],
        "bridges": [
            "Filter sweeps up to the high frequency\nTotal surrender to the energy\nOne two three four, here comes the drop\nThis groove is never gonna stop"
        ],
        "outros": [
            "Drop the kick...\nKeep the hi-hat...\nFade into the sunrise."
        ],
        "default_bpm": 126,
        "default_key": "F Minor"
    },
    "Rock": {
        "topics": ["Rebel road", "Electric energy", "Breaking the chains", "Live stage adrenaline"],
        "verses": [
            "Marshall amps cranked up to ten\nHere we go around the bend again\nPounding drums like a heart on fire\nTaking the volume higher and higher",
            "Strap on the guitar, strike the chord\nNothing here that we can't afford\nCrowd is roaring, ready to ignite\nWe're owning the stage tonight"
        ],
        "choruses": [
            "Rock until the morning light\nNothing can stop this power tonight\nScreaming leads and driving beat\nFeel the thunder in your feet",
            "We were born to break the mold\nStories waiting to be told\nTurn it up, rip off the roof\nOur sound is all the living proof"
        ],
        "bridges": [
            "Solo rips through the smoke and haze\nLost in an overdrive distortion craze\nOne two three, kick into overdrive\nThis is what it means to be alive"
        ],
        "outros": [
            "Smash the final cymbal!\nGuitar feedback rings...\nSilence."
        ],
        "default_bpm": 138,
        "default_key": "E Minor"
    }
}

def generate_lyrics_and_style(prompt: str, custom_genre: str = None) -> Dict[str, Any]:
    # Determine best matching genre
    prompt_lower = prompt.lower()
    selected_genre = "Synthwave"

    if any(k in prompt_lower for k in ["lofi", "lo-fi", "chill", "study", "relax", "sleep", "coffee"]):
        selected_genre = "Lo-Fi"
    elif any(k in prompt_lower for k in ["cyber", "future", "techno", "android", "matrix", "dark"]):
        selected_genre = "Cyberpunk"
    elif any(k in prompt_lower for k in ["epic", "orchestra", "cinematic", "battle", "hero", "movie"]):
        selected_genre = "Cinematic Epic"
    elif any(k in prompt_lower for k in ["house", "dance", "club", "edm", "party", "rave"]):
        selected_genre = "Deep House"
    elif any(k in prompt_lower for k in ["rock", "metal", "guitar", "punk", "band"]):
        selected_genre = "Rock"
    elif custom_genre and custom_genre in GENRE_THEMES:
        selected_genre = custom_genre

    template = GENRE_THEMES.get(selected_genre, GENRE_THEMES["Synthwave"])

    v1 = random.choice(template["verses"])
    ch = random.choice(template["choruses"])
    v2 = [v for v in template["verses"] if v != v1]
    v2_text = v2[0] if v2 else v1
    br = random.choice(template["bridges"])
    ou = random.choice(template["outros"])

    title = prompt.strip().title() if prompt.strip() else f"{selected_genre} Odyssey"
    if len(title) > 40:
        title = title[:37] + "..."

    lyrics = (
        f"[Intro]\n"
        f"({selected_genre} atmospheric intro)\n\n"
        f"[Verse 1]\n{v1}\n\n"
        f"[Chorus]\n{ch}\n\n"
        f"[Verse 2]\n{v2_text}\n\n"
        f"[Guitar Solo / Synthesizer Lead]\n\n"
        f"[Bridge]\n{br}\n\n"
        f"[Chorus]\n{ch}\n\n"
        f"[Outro]\n{ou}"
    )

    style_tags = f"{selected_genre}, {template['default_bpm']} BPM, {template['default_key']}, Rich Harmony, Mastered Audio"

    return {
        "title": title,
        "genre": selected_genre,
        "bpm": template["default_bpm"],
        "key": template["default_key"],
        "lyrics": lyrics,
        "style_tags": style_tags
    }
