Feature: Naming the bridge
  The user can give the bridge a name or return to the name of the Homey.

  Scenario: The name can be changed and restored
    When I open the name page
    And I enter the bridge name "Hall bridge"
    And I save the name
    Then the page confirms with "Saved"
    And the bridge is named "Hall bridge"
    When I restore the default name
    Then the name field shows "Test Homey"

  Scenario: A name that is too long is rejected
    When I open the name page
    And I enter a bridge name of 70 characters
    And I save the name
    Then the page confirms with "The name can be at most 64 characters"
