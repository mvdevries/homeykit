Feature: The start page of the settings
  The first page shows how to pair the bridge and a summary of every setting.

  Scenario: The pairing details are shown
    When I open the settings page
    Then I see the pairing section with a QR code
    And I see a pincode in the form 123-45-678

  Scenario: The menu shows a summary per setting
    When I open the settings page
    Then the name menu item says "Test Homey"
    And the startup menu item says "Starts immediately"

  Scenario: The page is translated to Dutch
    When I open the settings page in Dutch
    Then the first menu item is "Apparaten"
    And the startup menu item says "Direct starten"
