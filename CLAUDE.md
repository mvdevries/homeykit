# Homeykit

Homey-app in Python die Homey als HomeKit-bridge aanbiedt (HAP-python). Zie `README.md` voor de
structuur en de commando's.

## Afspraken

- **Code is Engels**: namen van variabelen, functies, klassen, bestanden, CSS-klassen, instellingssleutels
  en logregels. Commit-berichten, PR-teksten en docs (`README.md`, deze file) zijn Nederlands. Teksten
  voor de gebruiker staan in `locales/nl.json` en `locales/en.json`, nooit hardcoded in `settings/`.
- **Geen commentaar of docstrings in code.** Alleen Martyn schrijft commentaar. Laat de code zichzelf
  uitleggen met kleine functies en uitgebreide namen: liever te veel dan te weinig.
- Houd functies klein en laat ze één ding doen. Een naam beschrijft wat de functie doet.
- Python 3.14 en modern: type hints, dataclasses met `slots`, `match`, `Protocol`, `asyncio`.
- Wijzigingen gaan via een branch en een pull request, nooit direct naar `main`. Merge alleen als
  Martyn dat zegt. Geen `Co-Authored-By` of andere Claude-attributie in commits en PR's.
- Draai de app alleen op de Homey als Martyn dat vraagt. De app start en stop je als achtergrondtaak
  met `npx homey app run --remote`, en na elke codewijziging herstart je hem. Geen Rex-panelen.
- Het uploaden en publiceren van een build doe je alleen op uitdrukkelijk verzoek.

## Structuur

Lagen, van onder naar boven: `config` en `domain`, `repositories`, `gateways` en `homekit`, `services`,
`endpoints`, en daarboven `app.py` en `api.py`. Een laag gebruikt alleen lagen onder zich. Services staan in
`services/`, één klasse per bestand, en worden samengesteld in `services/service_container.py`.

## Dingen die je moet weten

- `self.homey.api` in de Python-SDK is **niet** de Homey Web API. Voor apparaten vraagt de app een
  token (`get_owner_api_token`) en het lokale adres (`get_local_url`) en gebruikt `httpx`. Homey beperkt
  het aantal verzoeken (429): haal iconen rustig op.
- Homey zet eigen stijlen op `label`, `button` en `input` (hoofdletters, opvulling, hoogte). Gebruik in
  `settings/` gewone elementen (`div`, `span`) en maak de opvulling van invoervelden dwingend.
  Het `hidden`-attribuut werkt alleen door de regel `[hidden] { display: none !important }`.
- Het app-icoon (`assets/icon.svg`) moet **één kleur** zijn op doorzichtig: Homey kleurt het in
  met de `brandColor`. Gevulde plaatjes of gekleurde tegels worden één effen vlak.
- Tokens in vertalingen zijn `__name__`, niet `{name}`. Fouten uit de backend zijn codes
  (`bridge_name_too_long`) die de pagina vertaalt.
- De Homey-API geeft apparaten als object met `capabilitiesObj`; het icoon van het apparaattype staat
  in `iconObj`. Gekozen iconen (`iconOverride`) zijn niet via de API op te halen.
- pyhap maakt de koppel-URI alleen met `pyqrcode`; `homekit/setup_uri.py` rekent hem zelf uit.
- HomeKit-ID's (`aid`) van accessoires worden bewaard in de Homey-instellingen zodat kamers en
  automatiseringen in de Woning-app blijven kloppen. Verwijder die niet, en houd de volgorde van
  diensten en kenmerken in een accessoire gelijk (dat bepaalt de `iid`).
- pyhap kiest het IP-adres één keer bij het starten en luistert en adverteert daarop. Verandert het
  adres later, dan klopt de mDNS-advertentie niet meer en luistert de server op het oude adres.
  `services/address_watchdog.py` controleert dit elke minuut en `BridgeSupervisor` herstart dan de
  bridge (de koppeling blijft, die staat in het state-bestand). HomeKitty verloor zo (ciao) het
  IPv4-adres en adverteerde alleen Thread-adressen.
- `homey app publish` is interactief; met `HOMEY_HEADLESS=1` is het dat niet (zie `README.md`).
- Oude instellingssleutels (`aangeboden`, `aids`, `bridge_naam`, `start_vertraging_aan`, `start_vertraging_seconden`)
  worden bij het opstarten door `repositories/legacy_settings_migration.py` overgenomen naar de Engelse sleutels en
  daarna verwijderd. Een bestaande nieuwe waarde wordt nooit overschreven.
