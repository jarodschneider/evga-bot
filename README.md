# evga-bot
If you've been trying to buy an RTX 30-series GPU around launch, you've probably experienced frustration with beating the resellers' bots. Well, if you can't beat 'em...

This bot is intended to help me manage to get just a single card from EVGA. It's not designed to target more than one SKU at a time, and it terminates after successfully ordering a single card.

The bot is relatively simple and uses Selenium Driver to automate the stock checking and checkout processes.

## Dependencies:

### Selenium

Install with `pip install selenium`

### geckodriver

[Get here](https://github.com/mozilla/geckodriver/releases/latest) and add to PATH

### Firefox

You must have [Firefox](https://www.mozilla.org/en-US/firefox/new/) installed.

## Installation:

Running the bot nearly as simple as the original version. However, I've made a few changes to make running the app easier on subsequent executions. Two key changes are the requirement of `evga.key` and `payment.key` files (in the same directory as `evga_bot.py`).

### `evga.key`

This file holds your EVGA.com credentials and should have the following format:

```
username
password
```

### `payment.key`

This file holds your payment information (only credit cards are supported at this time) and should have the following format:

```
Cardholder Name
Card Number
CVV
Expiration Month (MM)
Expiration Year (YYYY)
```

No validation is done locally, so make sure your information is correct. At no point is your account or payment information stored nor transmitted anywhere other than locally in memory and directly to EVGA at checkout.

Obviously, don't share these files with anyone.

### Your EVGA.com account:

This bot relies on your EVGA account having your shipping/billing addresses stored on your account. Additionally, it rejects the "recommended" shipping address, since it removes the apartment/unit number (for my building, at least).

## Usage:

`evga_bot.py [args]`:

- -t, --test: test mode; script will halt prior to clicking the final Place Order button, allowing you to test the program without actually buying something
- -d: delay (sec) between product page refreshes (default: 3.0)
- -s: time (sec) to randomly fluctuate delay by +/-[0, x) (default: 0.8)

To run the bot, simply run `evga_bot.py` in the normal way. Whether the delay "salt" makes any difference to bot pattern detection, I have no idea, but it makes me feel better.

## WARNING:

This script attempts to purchase you an expensive GPU if not run in test mode. Do NOT run if you are not fully aware of the consequences and willing to have your payment card charged. I take no responsibility for accidental purchases made due to code faults or user error.

Here's hoping companies harden their storefronts against scalpers so that these bots are no longer necessary for people just trying to get a single card.

Made with bitter ❤️ by Jarod Schneider
