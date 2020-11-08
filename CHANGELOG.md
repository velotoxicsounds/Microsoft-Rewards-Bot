**2020.11.08**
    - Fixed bug: get_point_total works again 
    - Started to rewrite XPath


**2020.11.04**
    - Logging Info customized, new text structure
    - New user agent for PC/EDGE
    - New login method / cookie query imelemented
    - Time Sleep re-adjusted, BOT IS NUN SUPER FAST!
    - Random search count, looks significantly more human
    - Wait_until_visible activated!
    - Sleep Timer for Daily Poll customized, BOT SUPER FAST!!
    - Sleep Timer customized for Click Quiz, BOT SUPER FAST!!
    - Sleep timer for drag ang drop customized, BOT SUPER FAST!!
    - Sleep timer for drag ang drop customized, BOT SUPER FAST!!
    - Points are now read correctly at Level 2 Account - Account Level 1 still needs to be implemented
    - ensure_pc_mode_logged_in rewritten, BOT SUPER FAST!!
    - ensure_mobile_mode_logged_in rewritten, BOT SUPER FAST!!
    - Points are now carried in the log
**2020.10.26**
    - Second login function built-in for Bing search (name: log_in_2(email_address, pass_word)
    - Microsoft Edge Search works again, new UserAgent is inserted. Idea: implement ua.random as well as filters for Edge Browser useragents
    - Current error: The Bing Rewards queries for mobile devices have a gateway error, where the new login (log_in_2) must be implemented.
    - New login method works with any language (Works via link URL)
    - Ensure_mobile_mode_logged_in/ensure_pc_mode_logged_in function revised. New login function implemented. Thus, the account is logged in again for the Bing search. As a result, the points are again allocated
    - Update Readme (Add Windows Function)
    - daily_poll(): TimeSleep built-in, must not be removed
    - sign_in_prompt() Revised. NewStyle XPath
    - #ua.update(). Requires timer for maximum every 12h update
    - Login Password TimeSleep Set to 1
    - Add Telegram E-Mail Output
    - Telegram version now outputs DEBUG data. (TextFormat implemented)
    - Time Sleep removed from Ensure_mobile_mode_logged_in/ensure_pc_mode_logged_in, faster login
    - Login2 function TimeSleep extended for the correct finding of the elements

**2020.10.25**

    - Login Fixed [USE NOW ID LOCATOR], Read Points FIX [USE NOW XPATH], OPEN ERROR: Unlimited Mobile Searches, Need Useragent FIX

**2020-09-27**

    - General code revision. Telegram Bot. Fix for registration query, PC points FIX, mobile points FIX, EDGE points FIX, PC fakeuseragent random integrated

**2019-07-09**

    - Fixed sporadic crashes caused by geolocation requests

**2019-07-02**

    - Fixed browser refresh loop caused by login errors
    - Fixed password-based login in headless mode

**2019-06-25**

    - Added support for 2FA, passwordless login via Microsoft Authenticator

**2019-04-03**

    - Added fix for wait_until_visible from .find_element to .find_elements

**2019-04-02**

    - Added adreo00's code for setting log level with argparse

**2019-04-01**

    - Added fix for detecting pcpoints element during point status check
    - Removed edge points as the status screen no longer displays them

**2019-03-01**

    - Incorporated ShoGinn's lightning quiz fix
    - Fixed .cico quiz close patch
    - Added const for logging level

**2019-02-02**

    - Fixed open offer link to target the link

**2019-02-01**

    - Added chromedriver auto-downloading

**2019-01-29**

    - Added error handling for 'credits2', function should exit and script should continue to execute.
    - Changed automation from firefox/geckodriver to chrome/chromedriver
        - Immediate improvement in speed and stability over firefox/geckodriver
        - Appears to use less RAM than firefox (suprisingly..)
        - May be possible to run on raspberrypi (rpi has chromedriver)
    - Mitigated credits2 error by performing an action before going to search URL

**2018-12-20**

    - Performance improvements
    - Fixed login, now waits until page is fully loaded
    - Replaced urllib api call with requests
    - Updated get points with chrome extension source, less prone to error (credit to Shoginn for the url!)
    - Updated quizzes to log open quiz offers, completed quiz offers, all points
    - Modified error catching for alerts, combined with timeoutexception
    - Misc fixes

**2018-11-28**

    - Fixed issue with daily poll IDs changing
    - Added check for sign-in prompt after click on a quiz
    - Misc fixes

**2018-10-20**

    - Added argparse
    - Added points from email links
    - Added randomized account login order
    - Reworked newsapi.org API to google trends
    - Fixed logging
    - Fixed issue with dropped searches

**2018-10-08**

    - Initial release
    - Basic functionality for completing searches and quizzes.
