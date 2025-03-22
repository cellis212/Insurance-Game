# Manual Testing Guide for Insurance Simulation Game

This guide provides steps for manual testing of the Insurance Simulation Game running in a web browser.

## Prerequisites

1. Ensure the game is running at http://localhost:8000 (or your deployment URL)
2. Have a modern browser with developer tools available (Chrome, Firefox, Edge, etc.)
3. Clear browser cache/cookies if needed for a fresh test

## Test Cases

### Test 1: Game Loading & Startup Screen

1. Open the game URL in your browser
2. Verify the game loads and displays the startup screen
3. Check that the company name input field and state selection work correctly
4. Enter a company name (e.g., "Test Insurance Co")
5. Select a state (California or Florida)
6. Click the "Start Game" button
7. Verify the game initializes correctly and shows the main game interface

**Expected result**: Game should load properly and transition from startup to the main game view.

### Test 2: Navigation Between Screens

1. From the main game screen, click on "Investments" button
2. Verify the investments screen appears with proper content
3. Click on "Financial Reports" button
4. Verify the reports screen appears with proper content
5. Click on "Premium Rates" button 
6. Verify you return to the premium setting screen

**Expected result**: All navigation buttons work and display the correct screens.

### Test 3: Setting Premium Rates

1. On the Premium Rates screen, ensure rate sliders are visible
2. Adjust premium rates for home and auto insurance
3. Verify that the UI updates to show the new rates
4. Change to a different state (if unlocked)
5. Verify each state has independent premium settings

**Expected result**: Premium rate adjustments work correctly in the UI.

### Test 4: Investments

1. Navigate to the Investments screen
2. Verify available investment options are displayed
3. Try purchasing some shares of an investment
4. Verify that your cash balance updates
5. Try selling some shares
6. Verify the transaction completes correctly

**Expected result**: Investment transactions work correctly.

### Test 5: End Turn & Game Progress

1. Click the "End Turn" button
2. Verify that a turn summary appears
3. Check that the summary shows reasonable financial results
4. Close the summary
5. Verify that the game advances to the next turn
6. Check that financial metrics are updated

**Expected result**: Turn progression works and produces meaningful simulation results.

### Test 6: Save & Load

1. Use the Save/Load screen (or keyboard shortcuts Ctrl+S to save)
2. Save your game
3. Make some changes (adjust premiums, investments)
4. Load the previous save
5. Verify that the game state reverts to the saved state

**Expected result**: Save and load functionality works using browser localStorage.

### Test 7: Responsive Layout

1. Resize the browser window to different dimensions
2. Verify that the canvas and UI remain usable
3. Try on a mobile device if possible
4. Check that buttons and controls are accessible at different sizes

**Expected result**: Game layout should adapt reasonably to different screen sizes.

## Reporting Issues

When reporting issues:
1. Note the exact steps to reproduce
2. Include browser console logs (F12 > Console)
3. Describe expected vs. actual behavior
4. Include screenshots if possible

## Browser Console Logging

To view debug output:
1. Open browser developer tools (F12 or right-click > Inspect)
2. Navigate to the Console tab
3. Look for any error messages in red
4. Check for game-specific log messages 