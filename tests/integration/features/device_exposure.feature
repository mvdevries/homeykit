Feature: Exposing Homey devices in HomeKit
  The user chooses which Homey devices are visible in HomeKit. The bridge keeps them in sync in both directions.

  Background:
    Given the app is running

  Scenario: Nothing is exposed by default
    Then 0 devices are exposed

  Scenario: Every supported device can be exposed
    When all supported devices are exposed
    Then 9 devices are exposed

  Scenario: Unsupported devices are never exposed
    When the devices "radiator-thermostat, wall-socket" are exposed
    Then 1 device is exposed

  Scenario: Removing a device from the selection removes it from HomeKit
    Given the devices "wall-socket, plain-lamp" are exposed
    When the devices "wall-socket" are exposed
    Then 1 device is exposed
    And the log says "'Plain lamp' is no longer exposed"

  Scenario: A device deleted in Homey disappears from HomeKit
    Given the devices "wall-socket, plain-lamp" are exposed
    When "plain-lamp" is deleted in Homey
    And the devices are synchronised
    Then 1 device is exposed

  Scenario: Accessory ids stay the same after a restart
    Given the devices "wall-socket, plain-lamp" are exposed
    And the accessory ids are remembered
    When the app is restarted
    And the devices are synchronised
    Then the accessory ids are the same as before

  Scenario: The selection is restored after a restart
    Given the devices "wall-socket" are exposed
    When the app is restarted
    Then 1 device is exposed

  Scenario: A change in Homey reaches HomeKit
    Given the devices "wall-socket" are exposed
    And the characteristic "On" of "wall-socket" is on
    When "wall-socket" is switched off in Homey
    And the devices are synchronised
    Then the characteristic "On" of "wall-socket" is off

  Scenario: A change in HomeKit reaches Homey
    Given the devices "plain-lamp" are exposed
    When HomeKit sets "On" of "plain-lamp" to true
    Then Homey received the value true for "onoff" of "plain-lamp"

  Scenario: Brightness is converted to a fraction
    Given the devices "dimmable-lamp" are exposed
    When HomeKit sets "Brightness" of "dimmable-lamp" to 80
    Then Homey received the value 0.8 for "dim" of "dimmable-lamp"

  Scenario: Colour temperature switches the light mode first
    Given the devices "tunable-lamp" are exposed
    When HomeKit sets "ColorTemperature" of "tunable-lamp" to 320
    Then Homey received for "tunable-lamp" first "light_mode" with "temperature" and then "light_temperature" with 0.5

  Scenario: A failed write is logged
    Given the devices "plain-lamp" are exposed
    And Homey fails the next request with status 500
    When HomeKit sets "On" of "plain-lamp" to true
    Then the log says "Writing to 'Plain lamp' failed"

  Scenario: The HomeKit description of all supported devices does not change
    When all supported devices are exposed
    Then the HomeKit description equals the snapshot
