# Update an issue

> **WARNING: TEST ENVIRONMENT ONLY.**
> This document contains credentials in plain text. Use it only against a test system with test accounts. Never use this approach in a production system.

## Goal

Log in, click the name with a link under the column issues, in the form select a different status and priority then click **Save changes**

## Environment and credentials

| Item     | Value              |
| -------- | ------------------ |
| Site URL | `{{LOGIN_URL}}`    |
| Email    | `{{APP_EMAIL}}`    |
| Password | `{{APP_PASSWORD}}` |

## Instructions

Work through these in order. After each step, note what you saw. Take a screenshot at every step marked 📷.

### Login

1. Open the Site URL. 📷
   Note whether the login page loads.
2. Enter the email and password, then click the **Sign in** button. 📷
   Note what page appears after login.
3. If there is a message **Invalid email or password.**, don't proceed to the next step and close the browser

### Update an issue

4. On the issues page, look for a table with the second column labeled **ISSUE**. Inside the first row under this column, locate the anchor tag link and click it to view the issue details📷
   Note whether the page redirects to a another page containing that specific issue's details.
5. Fill in the form with different status and priority values and click **Save changes** to submit the form. 📷
   Note whether the text besides **Current status** and **Current priority** has changed .

## What to observe and record

For every step, record visible text, field states, messages and statuses exactly as shown. Do not decide pass or fail yourself. Report what you saw.

## Expected results

- After login, the issues page loads.
- Clicking one of the issue names under the issues column in the issues table opens a new page with the issues details
- Replace the original fields in the form with new values and submit, which should present new text besides the Current status and Current priority

## Report format

1. **Steps:** each step, what you did, and what you observed.
2. **Errors:** each error with field, message, screenshot path and attempts made.
3. **Adjustments made:** yes or no, and which fields.
4. **Completed:** yes or no, and if no, where you stopped and why.
5. **Screenshots:** list of file paths.
