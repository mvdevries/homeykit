# Homeykit

Homey-app in Python die Homey aanbiedt als HomeKit-bridge, gebouwd op
[HAP-python](https://pypi.org/project/HAP-python). De gekozen Homey-apparaten
verschijnen in de Woning-app van Apple en zijn te bedienen met Siri, widgets en
HomeKit-automatiseringen. Alles draait lokaal op de Homey, zonder cloud.

## Wat de app doet

- Publiceert een HomeKit-bridge (poort 51827) en toont een QR-code en pincode om te koppelen.
- Biedt gekozen Homey-apparaten (lampen, stopcontacten, schakelaars en sensoren) aan in HomeKit en synchroniseert in twee richtingen.
- Instellingen voor de naam, de pincode en een optionele opstartvertraging, tweetalig (Engels en Nederlands).
- Bewaakt het IP-adres: verandert het, dan herstart de bridge kort op het nieuwe adres (de koppeling blijft behouden). Zonder netwerkadres bij het opstarten wacht de app tot er een is.

## Structuur

De code staat in lagen. Een laag gebruikt alleen lagen die onder hem staan.

```
app.py                  App: bouwt de services en start en stopt de bridge
api.py                  Endpoints van de app-API, geëxporteerd voor Homey
config/                 Vaste waarden: poorten, standaardnamen, instellingssleutels
domain/                 Gegevensmodellen en regels zonder I/O
  homey_device.py         Homey-apparaat en capabilities
  device_row.py           Een regel in de apparatenlijst
  pincode.py              Regels en generatie van de pincode
  bridge_name.py          Regels voor de naam van de bridge
  startup_delay.py        De opstartvertraging en de grenzen ervan
repositories/           Lezen en schrijven van de Homey-instellingen
  legacy_settings_migration.py  Neemt instellingen van de oude (Nederlandse) sleutels over
gateways/               Praten met de Homey Web API
  homey_web_api.py        HTTP-client met token
  homey_devices_gateway.py  Apparaten, zones, iconen en capabilities
network/                Het lokale IP-adres van de Homey bepalen
homekit/                HomeKit-specifiek
  service_profiles.py     Welke HomeKit-diensten een apparaat krijgt
  value_conversions.py    Omzettingen tussen Homey- en HomeKit-waarden
  homey_accessory.py      HAP-accessoire per Homey-apparaat
  setup_uri.py            Koppel-URI en QR-code
services/               De logica: één klasse per bestand
  bridge_service.py       Maakt, publiceert en stopt de HomeKit-bridge
  bridge_supervisor.py    Bepaalt wanneer de bridge start, herstart en stopt
  device_sync_service.py  Houdt de accessoires gelijk aan de gekozen apparaten
  device_overview_service.py  De apparatenlijst voor de pagina
  address_watchdog.py     Controleert elke minuut het IP-adres en herstart de bridge bij een wijziging
  bridge_name_service.py  De naam van de bridge: eigen naam of die van de Homey
  startup_delay_service.py  Bewaart de opstartvertraging
  settings_service.py     De instellingen voor de pagina en hun gevolgen
  icon_service.py         Apparaaticonen ophalen en bewaren
  pairing_service.py      Gegevens om te koppelen: QR-code, pincode, status
  pincode_service.py      De willekeurige of zelfgekozen pincode
  service_container.py    Stelt alle services samen
endpoints/              Dunne endpoints die de services aanroepen
settings/               Instellingenpagina (HTML, css/ en js/ per onderdeel)
locales/                Vertalingen (en.json, nl.json)
assets/                 Icoon en winkelafbeeldingen
```

## Ontwikkelen

Vereist Node.js, de Homey CLI (`npx homey`) en een draaiende Docker. Eenmalig inloggen met
`npx homey login` en een Homey kiezen met `npx homey select`.

```
npx homey app dependencies install      # Python-pakketten voorbereiden
npx homey app validate                  # valideren
npx homey app run --remote              # draaien op de Homey met live logs
npx homey app install                   # blijvend installeren
```

`run` laadt gewijzigde code niet zelf: stop en start opnieuw na een wijziging.

### Testversie publiceren

```
HOMEY_HEADLESS=1 npx homey app publish
```

Zonder vragen: dit vereist een changelog voor de huidige versie in `.homeychangelog.json` en een
`README.txt`. Het publiceren als testversie doe je daarna in
[tools.developer.homey.app](https://tools.developer.homey.app).

## Bronnen

- Icoon en merkkleur zijn overgenomen van HomeKitty (`name.klep.homekitty`) voor privégebruik.
  Die repo heeft geen licentie; vraag de maker om toestemming voordat je dit publiek maakt.
- De winkelafbeeldingen gebruiken de foto
  ["Living room (Unsplash)"](https://commons.wikimedia.org/wiki/File:Living_room_(Unsplash).jpg)
  van Jarosław Ceborski, CC0.
