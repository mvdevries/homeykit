Feature: Choosing the devices
  The user chooses which Homey devices are visible in HomeKit.

  Scenario: Supported devices are shown by default
    When I open the devices page
    Then I see 9 devices
    And I see 0 unsupported devices

  Scenario: A filter is needed to see devices
    When I open the devices page
    And I switch the "Active" filter
    And I switch the "Inactive" filter
    Then I am asked to choose a filter

  Scenario: The unsupported filter adds the thermostat
    When I open the devices page
    And I switch the "Not supported" filter
    Then I see 10 devices
    And I see 1 unsupported device

  Scenario: Searching narrows the list
    When I open the devices page
    And I search for "lamp"
    Then I see 3 devices
    When I search for "nothing matches this"
    Then I am told that no devices were found

  Scenario: Choosing a device is saved
    When I open the devices page
    And I switch on "Wall socket"
    Then the page confirms with "Saved"
    And the app exposes 1 device
    And the summary mentions "1 of"

  Scenario: Unsupported devices cannot be switched on
    When I open the devices page
    And I switch the "Not supported" filter
    Then the switch of "Radiator thermostat" is disabled
    When I try to switch on "Radiator thermostat"
    Then the switch of "Radiator thermostat" stays off
