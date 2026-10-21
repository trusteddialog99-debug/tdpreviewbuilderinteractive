"""Adds an optional fourth 'Geöffnete E-Mail' mockup to the current trustedDialog Preview Builder.
Run once next to the current app.py: python add_open_mail_mockup.py
The existing 3 mockups are not edited internally; only the board/template gets an optional fourth column.
"""
from pathlib import Path
import py_compile

ROOT=Path(__file__).resolve().parent
APP=ROOT/'app.py'
BACKUP=ROOT/'app.before_open_mail_mockup.py'
if not APP.exists(): raise SystemExit('app.py muss neben add_open_mail_mockup.py liegen.')
s=APP.read_text(encoding='utf-8'); original=s

def rep(old,new,label):
 global s
 if old not in s: raise SystemExit(f'Erwarteter Codeblock fehlt: {label}. app.py wurde nicht geändert.')
 s=s.replace(old,new,1)

# Session toggle: optional fourth mockup.
rep("'motif_options': [], 'motif_notice': '', 'auto_texts': {}, 'headline_source': '', 'motif_hint': ''}.items():",
    "'motif_options': [], 'motif_notice': '', 'auto_texts': {}, 'headline_source': '', 'motif_hint': '',\n"
    "             'show_open_mail': False}.items():", 'session state')

# Small usability control, placed after the existing preview-graphic editor. No other controls changed.
needle="        st.markdown('**Promo-Code unter der Grafik**')"
insert="        st.markdown('**4. Mockup – geöffnete E-Mail**')\n        st.checkbox('Geöffnete E-Mail zusätzlich anzeigen', key='show_open_mail',\n                    help='Ergänzt rechts ein viertes Mockup. Die drei bestehenden Mockups bleiben unverändert.')\n        st.markdown('**Promo-Code unter der Grafik**')"
rep(needle,insert,'open-mail checkbox')

# Dynamic board width: existing 1144 stays exactly as-is for three mockups.
rep("BOARD_W, BOARD_H = 1144, 785", "BOARD_W, BOARD_H = 1144, 785\nBOARD_W_OPEN = 1524", 'board width')

# New CSS only for the fourth opened-mail view.
css_marker=".downloadbtn:disabled{opacity:.6;cursor:wait}\n"
open_css=r'''.om-top{position:absolute;left:0;top:43px;width:297.5px;height:54px;border-bottom:1px solid #e8e8e8;background:#fff}
.om-back{position:absolute;left:13px;top:17px;width:16px;height:16px}
.om-count{position:absolute;left:48px;top:19px;font:500 11px/1 Roboto,Arial,sans-serif;color:#5f6368}
.om-actions{position:absolute;right:15px;top:15px;display:flex;gap:13px;color:#2a68ae}
.om-news{position:absolute;left:13px;top:108px;right:13px;height:34px;display:flex;align-items:center;border-bottom:1px solid #ececec}
.om-pill{height:23px;padding:0 10px;border:1px solid #d9e0e7;border-radius:12px;background:#fff;color:#4285c5;font:500 10px/21px Roboto,Arial,sans-serif;box-shadow:0 1px 3px rgba(0,0,0,.05)}
.om-unsub{margin-left:auto;display:flex;align-items:center;gap:6px;color:#3979b9;font:500 10.5px/1 Roboto,Arial,sans-serif;white-space:nowrap}
.om-message{position:absolute;left:0;top:151px;width:297.5px;padding:0 14px}
.om-avatar{position:absolute;left:15px;top:0;width:36px;height:36px;border-radius:50%;object-fit:cover;background:#fff;overflow:hidden}
.om-senderline{position:absolute;left:61px;top:1px;right:14px;height:18px;display:flex;align-items:center;white-space:nowrap}
.om-sender{font:700 13.5px/18px Roboto,Arial,sans-serif;max-width:178px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#111}
.om-date{position:absolute;left:61px;top:23px;font:400 10px/1 Roboto,Arial,sans-serif;color:#8c8c8c}
.om-subject{position:absolute;left:15px;right:15px;top:54px;font:700 14px/18px Roboto,Arial,sans-serif;color:#111}
.om-rule{position:absolute;left:15px;right:15px;top:102px;height:1px;background:#ededed}
.om-body{position:absolute;left:15px;right:15px;top:121px;height:300px;background:#fafafa;border:1px dashed #d6d6d6;border-radius:8px;display:flex;align-items:center;justify-content:center;text-align:center;color:#9b9b9b;font:500 11px/1.4 Roboto,Arial,sans-serif;padding:18px}
'''
rep(css_marker,open_css+css_marker,'open-mail CSS')

# Reuse the exact phone shell/status bar; open mail has no inbox search/footer because the mail is open.
phone_close_marker="PHONE_CLOSE = '</div></div></div>'"
open_template="""OPEN_MAIL_BODY = r'''<div class="om-top"><span class="om-back"><svg width="16" height="16" viewBox="0 0 16 16"><path d="M11 1.6 4.6 8l6.4 6.4" fill="none" stroke="#111" stroke-width="1.8" stroke-linecap="round"/></svg></span><span class="om-count">1 von 5</span><span class="om-actions"><svg width="17" height="17" viewBox="0 0 18 18"><path d="M4 2.5h10M6 5v9.5M12 5v9.5M3.5 5h11l-.8 11H4.3z" fill="none" stroke="currentColor" stroke-width="1.4"/></svg><svg width="17" height="17" viewBox="0 0 18 18"><path d="M3 6.5h12v9H3zM5 6.5V4.3C5 3 6 2 7.3 2h3.4C12 2 13 3 13 4.3v2.2" fill="none" stroke="currentColor" stroke-width="1.4"/></svg></span></div>
<div class="om-news"><span class="om-pill">Newsletter</span><span class="om-unsub">Newsletter abbestellen <svg width="19" height="19" viewBox="0 0 20 20"><circle cx="8" cy="10" r="4.2" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M11 7l5-5m-2 0h2v2M13 8.5l3 3v5H9.5l-2-2" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></span></div>
<div class="om-message">__OPENAV__<div class="om-senderline"><span class="om-sender fit">__OPENSENDER__</span>__OPENSEAL__</div><div class="om-date">Heute um <span data-off="-3"></span></div><div class="om-subject">[PREVIEW] tD Preview_Microdata Bilder &amp; Gutscheincode</div><div class="om-rule"></div><div class="om-body">Platzhalter für den interaktiven E-Mail-Inhalt</div></div>'''

def open_mail_html(avatar, sender):
    seal = f'<img class="seal" src="{SEAL}" alt="trustedDialog Siegel">'
    body = (OPEN_MAIL_BODY.replace('__OPENAV__', avatar).replace('__OPENSENDER__', display_text(sender) or 'Marke')
            .replace('__OPENSEAL__', seal))
    # Existing phone frame and status bar are reused. Only a minimal open-mail header replaces inbox-specific content.
    status = PHONE_HEAD.split('<span class="abs round" style="left:3px">', 1)[0]
    return PHONE_OPEN + status + body + PHONE_CLOSE
'''
"""
rep(phone_close_marker,phone_close_marker+'\n'+open_template,'open-mail template')

# Board template: fourth column is injected only when enabled. Existing first 3 columns remain byte-for-byte unchanged.
rep('<div class="col" id="col3"><div class="ptitle">Mit trustedDialog Preview</div>__PHONE3__</div>\n</div></div></div>',
    '<div class="col" id="col3"><div class="ptitle">Mit trustedDialog Preview</div>__PHONE3__</div>\n__PHONE4COL__\n</div></div></div>', 'board fourth slot')

# Export labels become dynamic but preserve original wording when mockup 4 is off.
rep('Alle 3 Mockups als eine PNG-Grafik herunterladen', '__ALLDL__', 'download caption')

# fitBoard uses actual dynamic board width token that is already replaced by build function.
# Add fourth phone to build function signature.
rep("promo_label='', promo_code='', show_promo=False):",
    "promo_label='', promo_code='', show_promo=False, show_open_mail=False):", 'build signature')

# Create the 4th phone from the exact same logo/avatar and sender. Keep original three tuple untouched.
needle="    )\n    # Kontrastregel auch für die Beispiel-Mails (OH, FF, SW): Initialen auf #B8DDFD in gut lesbarer Schrift\n    out = BOARD_TEMPLATE.replace"
replacement="    )\n    open_phone = open_mail_html(logo, sender_name) if show_open_mail else ''\n    # Kontrastregel auch für die Beispiel-Mails (OH, FF, SW): Initialen auf #B8DDFD in gut lesbarer Schrift\n    out = BOARD_TEMPLATE.replace"
rep(needle,replacement,'open phone build')

# Replace dynamic values and add fourth column. Three-device board remains 1144px if disabled.
old="for token, value in {'__PHONE1__': phones[0], '__PHONE2__': phones[1], '__PHONE3__': phones[2],\n                         '__BW__': str(BOARD_W), '__BH__': str(BOARD_H), '__DLSENDER__': download_sender}.items():"
new="board_w = BOARD_W_OPEN if show_open_mail else BOARD_W\n    fourth = '<div class=\"col\" id=\"col4\"><div class=\"ptitle\">Geöffnete E-Mail</div>'+open_phone+'</div>' if show_open_mail else ''\n    for token, value in {'__PHONE1__': phones[0], '__PHONE2__': phones[1], '__PHONE3__': phones[2], '__PHONE4COL__': fourth,\n                         '__BW__': str(board_w), '__BH__': str(BOARD_H), '__DLSENDER__': download_sender,\n                         '__ALLDL__': ('Alle 4 Mockups als eine PNG-Grafik herunterladen' if show_open_mail else 'Alle 3 Mockups als eine PNG-Grafik herunterladen')}.items():"
rep(old,new,'dynamic board replacement')

# Pass the optional flag; existing args untouched.
rep("st.session_state.promo_label, st.session_state.promo_code, bool(st.session_state.promo_show))",
    "st.session_state.promo_label, st.session_state.promo_code, bool(st.session_state.promo_show),\n                     bool(st.session_state.show_open_mail))", 'show_open_mail argument')

# Caption reflects optional fourth panel.
rep("'Maße nach GMX-App-Vorlage (je Gerät 344 × 701 px) · Export: eine Grafik mit allen 3 Mockups')",
    "'Maße nach GMX-App-Vorlage (je Gerät 344 × 701 px) · optional: geöffnetes E-Mail-Dummy als 4. Mockup')", 'footer caption')

BACKUP.write_text(original,encoding='utf-8'); APP.write_text(s,encoding='utf-8')
py_compile.compile(str(APP),doraise=True)
print('OK: optionales 4. Mockup ergänzt; Syntaxprüfung erfolgreich.')
