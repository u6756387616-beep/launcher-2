def recommend(hw):
    total = hw["ram_total"]
    free = hw["ram_available"]
    cores = hw["cores"]

    if total <= 4 or free < 1.5:
        profile = "LIGHT"
        suggested = 1
        render = 6
        note = "Mało pamięci: ogranicz dystans renderowania i liczbę modów."
    elif total <= 8 or cores <= 2:
        profile = "BALANCED"
        suggested = 2
        render = 8
        note = "Ustawienia zrównoważone dla starszego lub średniego komputera."
    else:
        profile = "PERFORMANCE"
        suggested = min(6, max(3, int(min(total * 0.5, free * 0.65))))
        render = 12
        note = "Więcej zapasu pamięci. Nie przydzielaj całego RAM-u Minecraftowi."

    # Nigdy nie przydzielamy więcej niż połowę całej pamięci ani prawie całej wolnej.
    safe_max = max(1, int(min(total * 0.5, max(1.0, free - 1.0))))
    suggested = max(1, min(suggested, safe_max))
    return {
        "profile": profile,
        "ram_gb": suggested,
        "render_distance": render,
        "note": note
    }
