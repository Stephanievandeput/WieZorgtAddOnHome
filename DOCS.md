# WieZorgt Addon

Welcome to the comprehensive documentation for the WieZorgt addon. This guide provides step-by-step instructions on how to seamlessly install and execute this module. Please note, prior to initiating this module, you will need to install some addons and integrate certain YAML code into your home assistant. This is a crucial step as it enables the module to effectively run the provided scenarios.

## Installing Dependencies

First of all its wise to enable advanced mode for your current admin user, which can be found under the profile button (left bottom of your screen).

### Installing the File Browser addon

In order to be able to edit files on your home assistant installation you can use the file browser addon.

Follow these steps to get the add-on installed on your system:

1. Navigate in your Home Assistant frontend to **Settings** -> **Add-ons** -> **Add-on store**.
2. Find the "file browser" add-on and click it.
3. Click on the "INSTALL" button.
4. Follow the instructions given with the addon.

### Installing the Terminal & SSH addon

Another way to edit files on your home assistant installation is to use SSH/SFTP, this can be done with the Terminal & SSH addon. Note: Our documentation covers the official "Terminal & SSH" addon, which is only visible in advanced mode.

Follow these steps to get the Terminal & SSH add-on installed on your system:

1. Navigate in your Home Assistant frontend to **Settings** -> **Add-ons** -> **Add-on store**.
2. Find the "Terminal & SSH" add-on and click it.
3. Click on the "INSTALL" button.
4. After installing go to the addon configuration tab and add a public key or password. Also under network click "show disabled ports" and change the port number to 22222 (which u need to use in your ssh/sftp client), click save at each section and start the addon.

### Installing the Hass.io Access Point addon

For illi-tv or esp32's to be able to network with the Home Assistant there needs to be a either a Wi-Fi router, or cabled network etc. If this is not the case you can set up a Wi-Fi access point on HomeAssistant by installing the "Hass.io Access Point" addon.

Follow these steps to get the Hass.io Access Point add-on installed on your system:

1. Navigate in your Home Assistant frontend to **Settings** -> **Add-ons** -> **Add-on store**, click **⋮** (right top of the screen) -> **Repositories**, fill in</br> `https://github.com/mattlongman/hassio-access-point` and click **Add → Close** or click the **Add repository** button below, click **Add → Close** (You might need to enter the **internal IP address** of your Home Assistant instance first).
   [![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fmattlongman%2Fhassio-access-point)
2. Navigate in your Home Assistant frontend to **Settings** -> **Add-ons** -> **Add-on store**.
3. Find the "Hass.io Access Point" add-on and click it.
4. Click on the "INSTALL" button.
5. After installing go to the addon configuration tab and add a SSID (for example WieZorgt), add a wpa_passphrase (password), and set DHCP to 1. When done configuring click save and start the addon.

### Installing the Mosquitto (MQTT) broker and Zigbee2MQTT addon

Home Assistant has 2 popular integrations for Zigbee support, we prefer the use of Follow these steps so install the Mosquitto broker: over the official ZHA (Zigbee Home Automation) integration because it supports more Zigbee devices, gives more control and allows for easy OTA updates on Zigbee devices. Also, using Zigbee2MQTT allows external hardware to also read out the Zigbee devices by using the same MQTT broker.

Follow these steps so install the Mosquitto broker addon:

1. Navigate in your Home Assistant frontend to **Settings** -> **Add-ons** -> **Add-on store**.
2. Find the "Mosquitto broker" add-on and click it.
3. Click on the "INSTALL" button.
4. Follow the instructions given with the addon.

Follow these steps so install the Zigbee2MQTT addon (note, if you have the Sonoff ZigBee **E** model, please use the Zigbee2MQTT-Edge addon instead, instructions below still apply but search for the Edge version in the addon store after adding the repository):

1. Navigate in your Home Assistant frontend to **Settings** -> **Add-ons** -> **Add-on store**, click **⋮** (right top of the screen) -> **Repositories**, fill in</br> `https://github.com/zigbee2mqtt/hassio-zigbee2mqtt` and click **Add → Close** or click the **Add repository** button below, click **Add → Close** (You might need to enter the **internal IP address** of your Home Assistant instance first).
   [![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fzigbee2mqtt%2Fhassio-zigbee2mqtt)
2. Navigate in your Home Assistant frontend to **Settings** -> **Add-ons** -> **Add-on store**.
3. Find the "Zigbee2MQTT" add-on and click it.
4. Click on the "INSTALL" button.
5. Follow the instructions given with the addon.

Optionally you can also install the MQTT Explorer addon (for testing purposes) by the following steps:

1. Navigate in your Home Assistant frontend to **Settings** -> **Add-ons** -> **Add-on store**, click **⋮** (right top of the screen) -> **Repositories**, fill in</br> `https://github.com/adamoutler/Addons` and click **Add → Close** or click the **Add repository** button below, click **Add → Close** (You might need to enter the **internal IP address** of your Home Assistant instance first).
   [![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fadamoutler%2FAddons)
2. Navigate in your Home Assistant frontend to **Settings** -> **Add-ons** -> **Add-on store**.
3. Find the "MQTT Explorer" add-on and click it.
4. Click on the "INSTALL" button.
5. Follow the instructions given with the addon.

## Adding configuration scripts

You can use the file browser addon to put the following files into Home Assistant.

### scripts.yaml

Use the left top folder button to navigate to config / scripts.yaml and add the following code:

```yaml
##############################
## WieZorgt helper services ##
##############################


## illi notify script
  mqtt_illi_notify:
    alias: "Illi-tv mqtt notify script"
    sequence:
      - service: mqtt.publish
        data:
          payload: "{{ message }}"
          topic: "illi-tv/{{ target }}"
          retain: true


################################
## WieZorgt scenario services ##
################################


## run food scenario script
  wz_food_scenario:
    alias: "Food scenario main script"
    fields:
      scenario:
        description: "Name of the scenario to run"
        example: "breakfast"
    sequence:
    - repeat:
        for_each: 
          "{{ state_attr('scenario.' ~ scenario, 'stages') }}"
        sequence:
          - choose:
            - conditions: 
                - condition: or
                  conditions:
                    - "{{ is_state('binary_sensor.person_eating', 'on') }}"
                    - "{{ is_state('binary_sensor.person_needs_a_break', 'on') }}"
              sequence: 
                - stop: "Scenario ended by person eating or stop button pressed"
          - service: "script.wz_food_stage"
            data:
              stage: "{{repeat.item}}"


## run food stage script
  wz_food_stage:
    alias: "Food stage"
    sequence:
    - repeat:
        for_each: 
          "{{stage['stimuli_scripts']}}"
        sequence:
          - service: "script.{{repeat.item['module']}}"
            data:
              device_id: "{{repeat.item['device_id']}}"
              parameters: "{{repeat.item['parameters']}}"
    - wait_template: >
        {{ is_state('binary_sensor.person_eating', 'on') or
           is_state('binary_sensor.person_needs_a_break', 'on') }}
      timeout: '{{stage["duration"]}}'
      continue_on_timeout: 'true'
    - repeat:
        for_each: 
          "{{stage['stimuli_scripts']}}"
        sequence:
          - service: "script.{{repeat.item['module']}}_end"
            data:
              device_id: "{{repeat.item['device_id']}}"
              parameters: "{{repeat.item['parameters']}}"


######################################
## WieZorgt stimuli module services ##
######################################


  wz_st_light:
    alias: "WieZorgt Light module"
    sequence:
      - service: "light.turn_on"
        target:
          entity_id: "light.{{device_id}}"
        data:
          brightness: "{{parameters['brightness']}}"

  wz_st_light_end:
    alias: "WieZorgt Light module end"
    sequence:
      - service: "light.turn_off"
        target:
          entity_id: "light.{{device_id}}"

  wz_st_switch:
    alias: "WieZorgt switch module"
    sequence:
      - service: "switch.turn_on"
        target:
          entity_id: "switch.{{device_id}}"

  wz_st_switch_end:
    alias: "WieZorgt Light module end"
    sequence:
      - service: "switch.turn_off"
        target:
          entity_id: "switch.{{device_id}}"

  wz_st_illi_video:
    alias: "Illi-TV video stimuli"
    sequence:
      - service: script.mqtt_illi_notify
        data:
            target: "{{device_id}}"
            message: '{ "command": "playVideo", "files":"{{parameters["files"]}}", "play_times":{{parameters["play_times"]}} }'

  wz_st_illi_video_end:
    alias: "Illi-TV video stimuli end"
    sequence:
      - service: script.mqtt_illi_notify
        data:
            target: "{{device_id}}"
            message: '{ "command": "stopVideo" }'

  wz_st_sound:
    alias: "Wie Zorgt sound module"
    sequence:
      - service: "tts.google_translate_say"
        data:
            target: "media_player.{{device_id}}"
            message: "Hallo, dit is het Wie Zorgt systeem dat je eraan herinnert dat het tijd is om te gaan eten"

  wz_st_sound_end:
    alias: "Wie Zorgt sound module end"
    sequence:
      - service: "tts.google_translate_say"
        data:
            target: "media_player.{{device_id}}"
            message: '{ "command": "stop" }'
```

### automations.yaml

Use the left top folder button to navigate to config / automations.yaml and add the following code:

```yaml
- id: wz_breakfast
  alias: breakfast time
  description: ''
  trigger:
  - platform: time
    at: 08:00:00
  condition: []
  action:
  - service: script.wz_food_scenario
    data:
      scenario: breakfast
  mode: single
- id: wz_lunch
  alias: lunch time
  description: ''
  trigger:
  - platform: time
    at: '12:00:00'
  condition: []
  action:
  - service: script.wz_food_scenario
    data:
      scenario: lunch
  mode: single
- id: wz_dinner
  alias: dinner time
  description: ''
  trigger:
  - platform: time
    at: '18:00:00'
  condition: []
  action:
  - service: script.wz_food_scenario
    data:
      scenario: dinner
  mode: single
```

### configuration.yaml

Use the left top folder button to navigate to config / configuration.yaml and add the following code:

```yaml
sensor:
  - platform: history_stats
    name: "person_has_pressed_yes_button"
    entity_id: sensor.yes_button_action
    state: "on"
    type: count
    end: "{{ now() }}"
    duration:
       minutes: 5
  - platform: history_stats
    name: "person_has_pressed_stop_button"
    entity_id: sensor.stop_button_action
    state: "on"
    type: count
    end: "{{ now() }}"
    duration:
       minutes: 5
       
binary_sensor:
    # determine the likelyhood a person was eating
  - platform: "bayesian"
    name: "person_eating"
    prior: 0.2
    probability_threshold: 0.8
    observations:
        # user pressed the yes button the last 5 minutes
      - platform: "numeric_state"
        entity_id: "sensor.person_has_pressed_yes_button"
        prob_given_true: 1.00
        prob_given_false: 0.00
        above: 0
  - platform: "bayesian"
    name: "person_needs_a_break"
    prior: 0.2
    probability_threshold: 0.8
    observations:
      # user pressed the stop button the last 5 minutes
      - platform: "numeric_state"
        entity_id: "sensor.person_has_pressed_stop_button"
        prob_given_true: 1.00
        prob_given_false: 0.00
        above: 0
```

### Bayesian sensor examples

Home Assistant has bayesian sensors that can be used to determine the likelihood of a person eating. The following examples can be used to determine the likelihood of a person eating. By using different history stats parameters and sensors, the likelihood can be determined, but when the users pressed the yes button, the likelihood is 100%, stopping the scenario directly.

```yaml 
sensor:
  - platform: history_stats
    name: "person_has_pressed_yes_button"
    entity_id: sensor.yes_button_action
    state: "on"
    type: count
    end: "{{ now() }}"
    duration:
       minutes: 30
  - platform: history_stats
    name: "person_has_pressed_stop_button"
    entity_id: sensor.stop_button_action
    state: "on"
    type: count
    end: "{{ now() }}"
    duration:
       minutes: 30
  - platform: history_stats
    name: "cabinet_door_opened"
    entity_id: sensor.cabinet_door_opened
    state: "on"
    type: count
    end: "{{ now() }}"
    duration:
       minutes: 20
  - platform: history_stats
    name: "fridge_door_opened"
    entity_id: sensor.fridge_door_opened
    state: "on"
    type: count
    end: "{{ now() }}"
    duration:
       minutes: 20


binary_sensor:
    # determine the likelyhood a person was eating
  - platform: "bayesian"
    name: "person_eating"
    prior: 0.2
    probability_threshold: 0.8
    observations:
        # user has pressed the yes button in the previous 30 minutes
      - platform: "numeric_state"
        entity_id: "sensor.person_has_pressed_yes_button"
        prob_given_true: 1.00
        prob_given_false: 0.00
        above: 0
        # user has opened the cabinet door in the previous 20 minutes for more than 2 times
      - platform: "numeric_state"
        entity_id: "binary_sensor.cabinet_door_opened"
        prob_given_true: 0.80
        prob_given_false: 0.20
        above: 2
          # user has opened the fridge door in the previous 20 minutes
      - platform: "numeric_state"
        entity_id: "sensor.fridge_door_opened"
        prob_given_true: 0.80
        prob_given_false: 0.20
        above: 0
  - platform: "bayesian"
    name: "person_needs_a_break"
    prior: 0.2
    probability_threshold: 0.8
    observations:
      # user pressed the stop button the last 5 minutes
      - platform: "numeric_state"
        entity_id: "sensor.person_has_pressed_stop_button"
        prob_given_true: 1.00
        prob_given_false: 0.00
        above: 0
```
The following example also uses espresense to determine the likelihood of a person eating. When the person has been in the kitchen for more than 10 minutes in the past 40 minutes to 10 minutes ago), and the person has been at the dinner table for more than 10 minutes in the past 30 minutes, it is likely the person was eating. For information on how to configure espresense see https://espresense.com/

```yaml
sensor:
    # tracking person
  - platform: mqtt_room
    device_id: "c8fd1910a008"
    name: "person_location"
    state_topic: "espresense/devices/c8fd1910a008"
    timeout: 10
    away_timeout: 10
    # see how many much time of the past 30 minutes a person was at the dinnertable
  - platform: history_stats
    name: "person_was_at_dinnertable"
    entity_id: sensor.person_location
    state: "dinnertable"
    type: ratio
    end: "{{ now() }}"
    duration:
       minutes: 30
  - platform: history_stats
    name: "person_was_at_kitchen"
    entity_id: sensor.person_location
    state: "kitchen"
    type: ratio
    end: "{{ now() - timedelta(minutes=10) }}"
    duration:
       minutes: 30
  - platform: history_stats
    name: "person_has_pressed_yes_button"
    entity_id: sensor.yes_button_action
    state: "on"
    type: count
    end: "{{ now() }}"
    duration:
       minutes: 5
  - platform: history_stats
    name: "person_has_pressed_stop_button"
    entity_id: sensor.stop_button_action
    state: "on"
    type: count
    end: "{{ now() }}"
    duration:
       minutes: 5

       
binary_sensor:
    # determine the likelyhood a person was eating
  - platform: "bayesian"
    name: "person_eating"
    prior: 0.2
    probability_threshold: 0.8
    observations:
        # user was at dinnertable for more than 20 minutes the last 30 minutes
      - platform: "numeric_state"
        entity_id: "sensor.person_was_at_dinnertable"
        prob_given_true: 0.95
        prob_given_false: 0.05
        above: 33
        # user was at kitchen for more than 5 minutes from 10 to 40 minutes ago
      - platform: "numeric_state"
        entity_id: "sensor.person_was_at_kitchen"
        prob_given_true: 0.95
        prob_given_false: 0.05
        above: 16
        # user was at kitchen for more than 5 minutes from 10 to 40 minutes ago
      - platform: "numeric_state"
        entity_id: "sensor.person_has_pressed_yes_button"
        prob_given_true: 1.00
        prob_given_false: 0.00
        above: 0
  - platform: "bayesian"
    name: "person_needs_a_break"
    prior: 0.2
    probability_threshold: 0.8
    observations:
      # user pressed the stop button the last 5 minutes
      - platform: "numeric_state"
        entity_id: "sensor.person_has_pressed_stop_button"
        prob_given_true: 1.00
        prob_given_false: 0.00
        above: 0
```


## Naming conventions

The AI system uses the "person_eating" output and probability to determine the effectiveness of a scenario. This output is generated in the examples above and can be extended with different sensor combinations. The AI system programmer that creates the scenario's should communicate the naming conventions with the Home Assistant maintainer. The device_id's in the mapping should match the entities in the Home Assistant. Instead of single devices one can also create a group in Home Assistant and use the group as device_id.
