Feature: The pairing pincode
  The user can set their own pincode or ask for a new random one.

  Scenario: A pincode can be set
    When I open the pincode page
    And I enter the pincode "20481357"
    And I save the pincode
    Then the current pincode shows "204-81-357"
    And the bridge has the pincode "204-81-357"

  Scenario: A simple pincode is rejected
    When I open the pincode page
    And I enter the pincode "11111111"
    And I save the pincode
    Then I see a message containing "does not accept this code"

  Scenario: A new random pincode replaces the current one
    When I open the pincode page
    And I remember the current pincode
    And I ask for a new random pincode
    Then the current pincode is different
