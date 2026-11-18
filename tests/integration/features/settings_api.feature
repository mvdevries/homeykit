Feature: The settings page API
  The settings page talks to the app through the endpoints of the app API.

  Background:
    Given the app is running

  Scenario: The device list shows all devices
    When the device list is requested
    Then 10 devices are listed
    And every listed device has an id, a name, a zone and its support and exposure

  Scenario: Choosing devices updates the list and the bridge
    When the devices "wall-socket" are chosen through the API
    Then only "wall-socket" is marked as exposed in the list
    And 1 device is exposed

  Scenario: The icons of the devices are available
    When the icons are requested
    Then no icons are missing
    And icons are returned

  Scenario: The pairing details are available
    When the pairing details are requested
    Then the pairing details are available

  Scenario: The settings can be changed
    When the bridge name is changed to "Hall" through the API
    And the pincode is changed to "20481357" through the API
    And the startup delay is changed to 15 seconds through the API
    Then the settings overview shows the bridge name "Hall"
    And the settings overview shows the pincode "204-81-357"
    And the settings overview shows a startup delay of 15 seconds
    And the settings overview says the bridge is running
    And requesting the settings gives the same overview

  Scenario Outline: Invalid settings are rejected with an error code
    When <change> is attempted through the API
    Then the API answers with the error code "<code>"

    Examples:
      | change                          | code                        |
      | a pincode of "11111111"         | pincode_too_simple          |
      | a pincode of "1234"             | pincode_invalid_format      |
      | a startup delay of 0 seconds    | startup_delay_out_of_range  |
      | a bridge name of 65 characters  | bridge_name_too_long        |
