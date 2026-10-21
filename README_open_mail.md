# Optionales 4. Mockup: Geöffnete E-Mail

Dieser Patch ergänzt die bestehende App um ein optionales viertes Smartphone-Mockup, ohne die drei bestehenden Mockups intern zu verändern.

Enthalten im Dummy:
- Zähler `1 von 5` (entsprechend der aktuellen Mailliste mit 5 Mails)
- Newsletter-Pille plus `Newsletter abbestellen` und Icon
- identischer Marken-/Avatar aus dem tD Preview Builder
- Markenname + trustedDialog-Siegel mit Ellipsis-Logik
- `Heute um [Zeit der ersten Mail]` über dieselbe `data-off=-3`-Logik
- fixer Dummy-Betreff `[PREVIEW] tD Preview_Microdata Bilder & Gutscheincode`
- Platzhalterfläche für den späteren interaktiven E-Mail-Inhalt

Anwendung: `python add_open_mail_mockup.py` im selben Verzeichnis wie die aktuelle `app.py`.
