# Homeykit

Homey-app in Python die Homey aanbiedt als HomeKit-bridge, gebouwd op
[HAP-python](https://pypi.org/project/HAP-python). De gekozen Homey-apparaten
verschijnen in de Woning-app van Apple en zijn te bedienen met Siri, widgets en
HomeKit-automatiseringen. Alles draait lokaal op de Homey, zonder cloud.

## Structuur

De code staat in lagen. Een laag gebruikt alleen lagen die onder hem staan.

```
app.py                  App: bouwt de services en start en stopt de bridge
api.py                  Routes van de app-API, geëxporteerd voor Homey
config/                 Vaste waarden: poorten, standaardnamen, instellingssleutels
domain/                 Gegevensmodellen en regels zonder I/O
  homey_device.py         Homey-apparaat en capabilities
  device_row.py           Een regel in de apparatenlijst
  pincode.py              Regels en generatie van de pincode
storage/                Lezen en schrijven van de Homey-instellingen
gateways/               Praten met de Homey Web API
  homey_web_api.py        HTTP-client met token
  homey_devices_gateway.py  Apparaten, zones, iconen en capabilities
homekit/                HomeKit-specifiek
  service_profiles.py     Welke HomeKit-diensten een apparaat krijgt
  value_conversions.py    Omzettingen tussen Homey- en HomeKit-waarden
  homey_accessory.py      HAP-accessoire per Homey-apparaat
  setup_uri.py            Koppel-URI en QR-code
services/               De logica: één klasse per bestand
  bridge_service.py       Maakt, publiceert en stopt de HomeKit-bridge
  bridge_supervisor.py    Bepaalt wanneer de bridge start en stopt
  device_sync_service.py  Houdt de accessoires gelijk aan de gekozen apparaten
  device_overview_service.py  De apparatenlijst voor de pagina
  icon_service.py         Apparaaticonen ophalen en bewaren
  pairing_service.py      Gegevens om te koppelen: QR-code, pincode, status
  pincode_service.py      Bewaart de willekeurige pincode
  service_container.py    Stelt alle services samen
routes/                 Dunne routes die de services aanroepen
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
