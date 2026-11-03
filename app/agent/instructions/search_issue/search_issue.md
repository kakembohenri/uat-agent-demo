# Search for an issue

> **WARNING: TEST ENVIRONMENT ONLY.**
> This document contains credentials in plain text. Use it only against a test system with test accounts. Never use this approach in a production system.

## Goal

Log in, copy the first name in the **ISSUE** column of the table on the issues page then paste it in the search field just above the table and click **Search**

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

### Search for an issue

4. Look for a table with a column labeled **ISSUE**. Inside the first row under this column, locate the anchor tag link copy the text of the link. 📷
   Note whether you managed to locate and copy the text
5. Fill in the input field with the name called **q** and click **Search**. 📷
   Note whether the table returns a row or rows with the anchor tag under the **ISSUE** having the same text as the one in the search field above the table.

## What to observe and record

For every step, record visible text, field states, messages and statuses exactly as shown. Do not decide pass or fail yourself. Report what you saw.

## Expected results

- After login, the issues page loads.
- The copied anchor tag text in the table is copied into the fiedl just above the table
- The returned row or rows in the table must have the anchor tag under the **ISSUE** having the same text as the one in the search field above the table

## Report format

1. **Steps:** each step, what you did, and what you observed.
2. **Errors:** each error with field, message, screenshot path and attempts made.
3. **Adjustments made:** yes or no, and which fields.
4. **Completed:** yes or no, and if no, where you stopped and why.
5. **Screenshots:** list of file paths.
