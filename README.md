# home-assistant-postcode-loterij
Customer Home Assistant Component for Postcode Loterij






Voorbeeld automatisering:

```yaml
- id: postcodeloterij
  alias: "Postcodeloterij: Prijs"
  initial_state: 'on'
  trigger:
    platform: time
    at: '14:00:00'
  condition:
    - "{{ now().day == 2 }}"
    - "{{ states('sensor.postcodeloterij_prijs') | int(0) > 0 }}"
  action:
    service: notify.all_devices
    data:
      title: "Postcodeloterij uitslag"
      message: "Deze maand heb je {{ states('sensor.postcodeloterij_prijs') }}x prijs! Namelijk {{ state_attr('sensor.postcodeloterij_prijs', 'prizes') }}. Gefelicteerd!"
      data:
        ttl: 0
        priority: high
        tag: "postcodeloterij_{{ now().strftime('%Y_%m') }}"
```