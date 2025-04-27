# Telegram Bot Setup Instructions

## Setting up the Telegram Bot Token

Based on the screenshot, you have successfully created a Telegram bot through BotFather. To properly configure the Linkly application to work with this bot, follow these steps:

1. Copy the token provided by BotFather:
   ```
   8059305719:AAEeyTwcSEY1Po7RJMntaCu-d0r6qxEbyw
   ```

2. Add this token to your environment variables:
   - For local development, add to your `.env` file:
     ```
     TELEGRAM_BOT_TOKEN=8059305719:AAEeyTwcSEY1Po7RJMntaCu-d0r6qxEbyw
     ```
   - For production deployment, add to your environment variables in your hosting platform (Railway, Heroku, etc.)

3. Make sure the bot username in your frontend code matches the username from BotFather:
   - Username: `linkly_ai_bot`
   - This has been updated in the PlatformConnect.jsx file

4. Verify the backend can properly validate Telegram login data:
   - The token consists of two parts separated by a colon (`:`):
     - Bot ID: `8059305719`
     - Secret part: `AAEeyTwcSEY1Po7RJMntaCu-d0r6qxEbyw`

5. If Telegram login widget doesn't appear:
   - Ensure your domain is allowed by CORS settings
   - Check browser console for any errors related to script loading
   - Verify that the bot token is correctly set in the backend
   - Try using the "Open Telegram Bot" fallback button

## How Telegram Login Works

Unlike other social platforms that use OAuth, Telegram's login process is different:

1. The Telegram Login Widget gets embedded in your page
2. When a user clicks it, Telegram authenticates them directly
3. User data is returned with a hash that your backend can verify using your bot token
4. The backend verifies this hash to ensure the data wasn't tampered with
5. If valid, the user's Telegram account gets connected to their Linkly account

Make sure to keep your bot token secure - anyone with this token can impersonate your bot. 