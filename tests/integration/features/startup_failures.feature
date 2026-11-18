Feature: Starting with a Homey that does not answer
  A Homey that fails the first requests must not keep the bridge from starting.

  Scenario: The first synchronisation fails
    Given the app is installed on a Homey
    And Homey fails the first 2 requests with status 500
    When the app starts
    Then the pairing details are available
    And the log says "First device synchronization failed"
