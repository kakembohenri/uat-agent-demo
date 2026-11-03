# Create an issue

> **WARNING: TEST ENVIRONMENT ONLY.**
> This document contains credentials in plain text. Use it only against a test system with test accounts. Never use this approach in a production system.

## Goal

Log in, click the create issue button, fill in the form and submit

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

### Click the Create Issue button

4. On the issues page, click the **+ Create issue** button on the right side of the screen 📷
   Note whether the page redirects to new page with **Create an Issue** title.
5. Fill in the form and click the **Create issue** button to submit the form. 📷
   Prefix each title with **QA-Agent-.** Note the page redirect whether the new pages title is the title of the issue.

## What to observe and record

For every step, record visible text, field states, messages and statuses exactly as shown. Do not decide pass or fail yourself. Report what you saw.

## Expected results

- After login, the issues page loads.
- **Create issues** opens a new page with a title **Create title**.
- Fill in the form and submit, redirects to a new page with the title being the title of the issue being viewed

## Report format

1. **Steps:** each step, what you did, and what you observed.
2. **Errors:** each error with field, message, screenshot path and attempts made.
3. **Adjustments made:** yes or no, and which fields.
4. **Completed:** yes or no, and if no, where you stopped and why.
5. **Screenshots:** list of file paths.
