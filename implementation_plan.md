# Dashboard Updates - Attendance UI and Branding

## Goal Description
The goal is to rename the original "Awards" node to "Attendance", and build an interactive UI panel inside the popup for taking attendance. This attendance panel will include a date selector, student selection or tracking line, present/absent toggles, and a save button. Finally, the "Holbos" branding text will be updated to feature an attractive gradient that matches the original logo style.

## User Review Required
No major user review should be required for these UI additions.

## Proposed Changes
### Frontend Modifications
#### [MODIFY] [dashboard.html](file:///c:/Users/AAKRIST%20SHARMA/OneDrive/Desktop/HolbosIndia/accounts/templates/accounts/dashboard.html)
- Change `.brand-name` and `.footer-brand` CSS to use `var(--grad)` with text-clipping to restore the attractive, colorful logo text matching the `navLogoImg`.
- Update `node4` content: Change icon to a calendar, text to "Attendance", and `onclick` attribute to trigger [openPopup('attendance')](file:///c:/Users/AAKRIST%20SHARMA/OneDrive/Desktop/HolbosIndia/accounts/templates/accounts/dashboard.html#2162-2303).
- Add an `} else if (type === 'attendance') {` block inside the [openPopup](file:///c:/Users/AAKRIST%20SHARMA/OneDrive/Desktop/HolbosIndia/accounts/templates/accounts/dashboard.html#2162-2303) JavaScript logic.
- Design and inject an HTML template for the Attendance UI containing inputs for Date, Student Name, a toggle button row for Present/Absent, and a Save button.
- Create JavaScript handlers for toggling attendance status and saving the data with visual feedback.

## Verification Plan
### Automated Tests
- No automated backend tests are currently available for this frontend dashboard.
### Manual Verification
- Click on the Attendance node in the Spider Web layout to ensure the newly formulated popup modal opens properly.
- Interact with the Date dropdown and Present/Absent toggle switches to confirm styling behavior.
- Click the "Save Attendance" button and verify that the success toast appears and the modal closes gracefully.
- Visually verify that the navigation header and footer "Holbos" texts render with an attractive gradient.
