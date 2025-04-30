# Step-by-Step Guide: Configure Gmail for Python Scripts

This guide details how to set up your Gmail account to allow Python scripts to securely send emails or interact with your account.

## Prerequisites

- **Gmail Account:** You will need access to the Gmail account you want the script to use.

## Configuration Steps (VERY IMPORTANT)

**Use App Passwords (Recommended Method):** For security reasons, Gmail requires using specific "App Passwords" for scripts instead of your main password.

1.  Go to your [Google Account](https://myaccount.google.com/).
2.  Navigate to **Security** on the left-hand menu.
3.  Under the "Signing in to Google" section, click on **2-Step Verification**. (You must have 2-Step Verification enabled to use App Passwords).
4.  Scroll down to the bottom and click on **App passwords**. You might need to sign in again.
5.  Under "Select app", choose **Other (Custom name)**.
6.  Give it a descriptive name (e.g., "Python Email Script") and click **Generate**.
7.  **Copy the generated 16-character password.** This is the specific password for your script.
8.  **Paste the generated 16-character password** as the value for the `GMAIL_APP_PASSWORD` variable inside your project's `.env` file.
    _(Note: Python script needs to load variables from this `.env` file.)_
9.  Set the value of the `SENDER_EMAIL` variable in the `.env` file with this configured email.

## Security Reminder

- **Protect Your App Password:** Treat it like a regular password, but remember it's _different_ from your main Gmail password. Do not share it, and do not hardcode it directly in your script or commit it to version control (like Git).
- **Use Secure Methods:** Storing secrets like App Passwords in environment variables (via `.env` files or system variables) is a good practice for development
