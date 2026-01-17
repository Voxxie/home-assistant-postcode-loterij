# Postcode Loterij Integration
Custom Home Assistant Component for Postcode Loterij


- Add the repository to HACS.
- Install the integration via HACS.
- Configure the integration via Home Assistant Configuration > Integrations.
- Restart Home Assistant.

It will generate sensors for your postal code, such as:
- sensor.postcodeloterij_prijs_<your_postcode>
- sensor.postcodeloterij_prijzen_<your_postcode>
- sensor.postcodeloterij_periode_<your_postcode>
##




Example automation (replace 1234AA with your own postalcode)

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