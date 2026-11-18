# Homeykit

Homey-app in Python die Homey aanbiedt als HomeKit-bridge, gebouwd op
[HAP-python](https://pypi.org/project/HAP-python). De gekozen Homey-apparaten
verschijnen in de Woning-app van Apple en zijn te bedienen met Siri, widgets en
HomeKit-automatiseringen. Alles draait lokaal op de Homey, zonder cloud.

## Structuur

De code staat in lagen. Een laag gebruikt alleen lagen die onder hem staan.

```
app.py                  App: bouwt de services en start en stopt de bridge
config/                 Vaste waarden: poorten, standaardnamen, limieten
domain/                 Gegevensmodellen en regels zonder I/O
storage/                Lezen en schrijven van de Homey-instellingen
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
