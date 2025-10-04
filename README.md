# 🎯 Pinball Simulator (Python + Pygame)

Et klassisk **Pinball-spil** udviklet i **Python** med **Pygame**, inklusive fysik, lyd, point, highscore-system og genkendelse af fastsiddende kugler.  
Spillet er bygget med realistisk boldfysik, flipper-kollisioner, samleobjekter og baggrundsmusik.  

---

## 🧩 Funktioner

- Realistisk **fysikmotor** med tyngdekraft og energi-tab  
- **Flipper-styring** med præcis kollision og rebound  
- **Samleobjekter (Collectibles)** der giver point  
- **Highscore-system** gemt i `highscore.txt`  
- **Baggrundsbillede** og **lyd-effekter**  
- **Ekstra kugler** for hver 500 point  
- Automatisk **detektion af fastsiddende kugle** (`R` for reset)  
- **Game Over skærm** med mulighed for nyt spil  

---

## 🕹️ Styring

| Tast | Funktion |
|------|-----------|
| `Venstre Shift / Ctrl` | Aktiver venstre flipper |
| `Højre Shift / Ctrl` | Aktiver højre flipper |
| `R` | Reset bold (hvis den sidder fast) |
| `SPACE` | Start nyt spil (efter Game Over) |
| `ESC` eller luk vinduet | Afslut spillet |

---

## 🖼️ Krav til filer

For at spillet fungerer optimalt, skal følgende filer ligge i samme mappe som `pinball.py`:

| Filnavn | Type | Beskrivelse |
|----------|------|-------------|
| `pinball.png` | Billede | Baggrundsbillede (valgfrit, ellers vises mørk baggrund) |
| `flipper_hit.mp3` | Lyd | Afspilles ved flipper-træf |
| `wall_hit.mp3` | Lyd | Afspilles ved vægkollision |
| `lost_ball_hit.mp3` | Lyd | Afspilles når kuglen tabes |
| `punch_hit.mp3` | Lyd | Afspilles ved samleobjekt |
| `background_music.mp3` | Lyd | Baggrundsmusik (loopes automatisk) |
| `highscore.txt` | Tekst | Gemmer highscore (oprettes automatisk) |

---

## 🧠 Afhængigheder

Installer **Pygame** inden du kører spillet:

```bash
pip install pygame

| System                                            | Virker?        | Bemærkning                                                               |
| ------------------------------------------------- | -------------- | ------------------------------------------------------------------------ |
| 🐧 **Linux (Debian, Arch, Ubuntu, Fedora m.fl.)** | ✅ **Ja**       | Kører direkte. Pygame findes i pip og distroens pakker.                  |
| 🪟 **Windows 10 / 11**                            | ✅ **Ja**       | Kører problemfrit via `python pinball.py` efter `pip install pygame`.    |
| 🍎 **macOS (Intel & Apple Silicon)**              | ✅ **Ja**       | Virker via Homebrew Python + pip. Nogle lyde kræver SDL2 backend.        |
| 🤖 **Android (via Pydroid3)**                     | ⚠️ **Delvist** | Grafikken kører, men lydfiler (.mp3) kan give fejl — brug .wav i stedet. |
| 💻 **Raspberry Pi (Pi OS / Debian ARM)**          | ✅ **Ja**       | Ydelsen afhænger af model, men Pygame fungerer stabilt.                  |
| 💾 **FreeBSD / OpenBSD**                          | ⚠️ **Muligt**  | Kræver SDL2 og Pygame-kompilering manuelt.                               |


