Feature: The startup delay
  The user can make the bridge wait after the app starts.

  Scenario: The startup delay can be enabled and changed
    When I open the startup page
    And I switch on the startup delay
    Then the startup menu item says "Waits 10 s after startup"
    When I enter a delay of 25 seconds
    Then the startup menu item says "Waits 25 s after startup"
    And the app stores a startup delay of 25 seconds
