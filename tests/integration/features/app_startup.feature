Feature: Starting and stopping the Homey app
  The app builds its services, moves old settings to the current ones and starts the bridge.

  Scenario: Old settings are moved when the app starts
    Given a Homey with the old settings:
      | key         | value             |
      | aangeboden  | ["wall-socket"]   |
      | bridge_naam | Old name          |
    When the Homey app starts
    Then the old keys are gone
    And the setting "bridge_name" is "Old name"
    And 1 device is exposed

  Scenario: Stopping the Homey app twice is harmless
    Given a Homey with the old settings:
      | key         | value |
      | bridge_naam | Name  |
    And the Homey app has started
    When the Homey app stops
    And the Homey app stops again
    Then the services are gone
