# home-assistant-postcode-loterij
Customer Home Assistant Component for Postcode Loterij






Voorbeeld automatisering:  (vervang 1234AA door je eigen postcode)

```yaml
alias: Postcode Loterij - Prijzen
description: ""
triggers:
  - trigger: state
    entity_id:
      - sensor.postcodeloterij_periode_1234AA
conditions:
  - condition: numeric_state
    entity_id: sensor.postcodeloterij_prijs_1234AA
    above: 0
actions:
  - action: notify.all_devices
    metadata: {}
    data:
      title: Je hebt prijs in de Postcode Loterij!
      message: >-
        Deze maand heb je {{ states('sensor.postcodeloterij_prijs_1234AA') }}x
        prijs! Namelijk {{ states('sensor.postcodeloterij_prijzen_1234AA') }}.
        Gefelicteerd!
mode: single
```