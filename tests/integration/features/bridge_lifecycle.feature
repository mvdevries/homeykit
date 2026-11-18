Feature: Bridge lifecycle
  The HomeKit bridge is published on the local network and follows the settings of the user.

  Background:
    Given the app is installed on a Homey

  Scenario: The bridge is published on the local address
    When the app starts
    Then the bridge is reachable on its port
    And the bridge runs on the local address
    And the log says the bridge is published

  Scenario: The bridge takes the name of the Homey
    Given the app is running
    Then the pairing details show the bridge name "Test Homey"
    And the bridge is not paired yet

  Scenario: The pairing details can be used to pair
    Given the app is running
    Then the pairing details contain an eight digit pincode and a QR code

  Scenario: Stopping the app closes the port
    Given the app is running
    When the app stops
    Then the bridge is no longer reachable

  Scenario: The pincode survives a restart
    Given the app is running
    And the current pincode is remembered
    When the app is restarted
    Then the pincode is the same as before

  Scenario: The app waits for a network address
    Given the Homey has no network address yet
    When the app starts
    Then the pairing details are not available yet
    When the Homey gets a network address
    Then the bridge becomes reachable on its port

  Scenario: A startup delay postpones the bridge
    Given a startup delay of 2 seconds
    When the app starts
    Then the pairing details are not available yet
    And the pairing details count down to the start
    And the bridge is not reachable
    When the startup delay has passed
    Then the bridge becomes reachable on its port

  Scenario: Stopping during the startup delay cancels the start
    Given a startup delay of 30 seconds
    When the app starts
    And the app stops
    Then the bridge is no longer reachable

  Scenario: A new IP address restarts the bridge
    Given the app is running
    When the Homey gets a new IP address
    And the IP address is checked
    Then the bridge runs on the new address
    And the log says the IP address changed

  Scenario: A new pincode applies to the running bridge
    Given the app is running
    When the pincode is set to "20481357"
    Then the pairing details show the pincode "204-81-357"

  Scenario: A new name restarts the bridge
    Given the app is running
    When the bridge name is set to "Custom name"
    Then the pairing details show the bridge name "Custom name"
    And the bridge is reachable on its port
