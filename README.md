# ⚠️ WARNING / هشدار جدی مالی

> **[FA] هشدار مهم:** 
> این اسکریپت صرفاً برای اهداف آموزشی و آزمایشی توسعه یافته است. **اکیداً توصیه می‌شود از این نرم‌افزار روی حساب اصلی ترید خود با دارایی‌های اصلی‌تان استفاده نکنید.** بازارهای مالی و معاملات خودکار همواره با ریسک بالای از دست رفتن سرمایه همراه هستند. در صورت تمایل به تست، حتماً عملکرد آن را روی یک حساب فرعی (Sub-account)، دارایی بسیار ناچیز و مدیریت‌شده یا سیستم‌های شبیه‌ساز (دمو) ارزیابی کنید. توسعه‌دهنده(گان) این پروژه هیچ‌گونه مسئولیتی در قبال سود یا زیان‌های احتمالی ناشی از اجرای این اسکریپت بر عهده نمی‌گیرند.

---

> **[EN] FINANCIAL DISCLAIMER:**
> This script is developed purely for educational and experimental purposes. **Do not run this script on your primary trading account or with your main trading funds.** Automated trading systems carry a high risk of capital loss due to market volatility, network latency, or unexpected execution behavior. If you wish to test this bot, please do so strictly on sub-accounts, with highly managed/minimal test funds, or within a simulated/sandbox environment. The developer(s) assume no responsibility for any financial gains or losses incurred from using this codebase.

---

# ربات ترید خودکار و آربیتراژ نوبیتکس (فارسی)

این پروژه یک ربات معامله‌گر خودکار چندرشته‌ای (Multithreaded) است که برای صرافی ایرانی **نوبیتکس (Nobitex)** توسعه یافته است. این ربات با رصد همزمان قیمت‌ها در صرافی‌های معتبر بین‌المللی و صرافی نوبیتکس، به دنبال شناسایی تفاوت قیمت‌ها (آربیتراژ آماری) و نوسان‌گیری از دارایی‌های مستعد رشد بر اساس ترند قیمتی بازارهای جهانی است.

## 🌟 امکانات کلیدی ربات

- **پایش قیمت جهانی (Global Price Aggregator):** دریافت و میانگین‌گیری خودکار قیمت‌ها از ۶ صرافی بزرگ دنیا (Binance, Coinbase, Bybit, Huobi, Kraken, Gate.io).
- **تحلیل عمق دفترچه سفارشات (Orderbook Depth Analysis):** ربات برای تضمین سودآور بودن معاملات، به جای تکیه بر قیمت آخرین معامله، میانگین قیمت قابل اجرا را با تحلیل عمق دفترچه سفارشات صرافی نوبیتکس متناسب با حجم دارایی شما محاسبه می‌کند.
- **معاملات چندرشته‌ای همزمان (Multithreaded Execution):** ربات برای هر جفت‌ارز به صورت کاملاً مستقل یک ترد (Thread) معاملاتی مجزا اجرا می‌کند که سرعت پایش و پاسخ‌دهی را افزایش می‌دهد.
- **مدیریت هوشمند پوزیشن‌ها (Trade Monitoring):**
  - اعمال حد سود (Take Profit) بر اساس برابری یا غلبه قیمت داخلی بر بازارهای جهانی.
  - اعمال حد ضرر ترکیبی (Stop Loss) بر اساس افت قیمت در بازار جهانی یا داخلی.
  - خروج زمانی (Timeout Exit) جهت نقد کردن دارایی‌هایی که در بازه مشخصی به سود نرسیده‌اند.
- **پاکسازی روزانه دارایی‌های خرد (Dust Liquidation):** اجرای یک پروسه پس‌زمینه روزانه (بین ۳ تا ۵ صبح به وقت تهران) جهت متوقف کردن موقت روند خرید و تبدیل دارایی‌های خرد (ارزش بین ۰ تا ۱ تتر) به تتر (USDT) برای بهینه‌سازی کیف پول.
- **کلید خروج اضطراری (Emergency Kill Switch):** قابلیت نقد کردن آنی تمام دارایی‌های مجاز کیف پول و بستن فوری برنامه در زمان نوسانات شدید بازار.
- **مدیریت ثبت رویدادها (Rotational Logging):** سیستم ذخیره‌سازی لاگ‌های معاملاتی به صورت چرخشی با محدودیت حجم مشخص جهت جلوگیری از پر شدن حافظه هارد دیسک.

---

## 📁 ساختار فایل‌های پروژه

- **`main.py`**: نقطه ورود و راه‌اندازی اصلی برنامه (ایجاد رشته‌ها به ازای هر جفت‌ارز).
- **`tradebot.py`**: هسته و منطق معاملاتی ربات (پایش شروط خرید، فروش، حد سود و ضرر).
- **`parallel_thread_funcs.py`**: ماژول مدیریت موازی برای کارهای نگهداری، پاکسازی دارایی‌های خرد و به‌روزرسانی لیست جفت‌ارزها.
- **`variables_func.py`**: فایل اصلی تنظیمات و پارامترها (توکن صرافی، کارمزدها، لیست سیاه جفت‌ارزها، اهداف سود و ضرر).
- **`buy_sell_func.py`**: وظیفه ارسال سفارشات خرید و فروش، پیگیری وضعیت سفارش و لغو معاملات فعالِ بی‌نتیجه.
- **`get_crypto_price_func.py`**: واکشی و اعتبارسنجی قیمت‌ها از صرافی‌های جهانی و نوبیتکس.
- **`get_orderbook_amount_and_price_func.py`**: محاسبه قیمت واقعی قابل معامله بر اساس عمق اردر بوک صرافی‌ها.
- **`get_tradable_crypto_pairs_and_detail_func.py`**: فیلتر کردن دارایی‌های مجاز نوبیتکس و کش کردن اطلاعات اعشاری حجم و قیمت آن‌ها روی هارد دیسک.
- **`validation_token_checker_func.py`**: اعتبارسنجی مداوم صحت توکن دسترسی حساب کاربری شما.
- **`float_truncator_func.py`**: برش ریاضی اعشار حجم و قیمت‌ها بر اساس قوانین صرافی جهت جلوگیری از خطای ارسال سفارش.
- **`logger_func.py`**: سیستم چرخشی پیشرفته لاگ‌نویسی برای هر جفت‌ارز.
- **`except_exit_func.py`**: مدیریت خروج ایمن و کامل برنامه از حافظه رم در زمان وقوع خطا یا انصراف کاربر.

---

## 🛠️ پیش‌نیازها

برای اجرای این پروژه به موارد زیر نیاز دارید:
- **پایتون (Python) نسخه ۳.۹ یا بالاتر** (به جهت استفاده از کتابخانه بومی `zoneinfo` برای مناطق زمانی).
- نصب کتابخانه ارسال درخواست‌های HTTP:
  ```bash
  pip install requests
  ```
- **توکن API صرافی نوبیتکس** با دسترسی سفارش‌گذاری (سفارش جدید و لغو سفارش) و مشاهده موجودی کیف پول.

---

## 🚀 روش راه‌اندازی و استفاده

۱. پروژه را در سیستم یا سرور خود شبیه‌سازی (Clone) کنید یا فایل‌های آن را دانلود نمایید:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

۲. فایل پیکربندی **`variables_func.py`** را با یک ویرایشگر متنی باز کرده و فیلدهای زیر را پر کنید:
   - در فیلد `"token"`، عبارت `"YOUR_NOBITEX_API_TOKEN"` را پاک کرده و توکن دسترسی اختصاصی نوبیتکس خود را وارد کنید.
   - دارایی تتر پایه خود را در `"my_usdt_balance"` و حداقل‌های دلاری ترید خود را تنظیم نمایید.
   - لیست کوین‌های استثنا (Exceptions) را در صورت تمایل تغییر دهید (به طور پیش‌فرض پایداری کوین‌ها و ارزهای بزرگ مسدود شده‌اند تا ربات روی آربیتراژ کوین‌های کوچکتر تمرکز کند).

۳. برنامه را با اجرای فایل اصلی استارت بزنید:
   ```bash
   python main.py
   ```

۴. برای متوقف کردن موقت و خروج امن از برنامه، کلیدهای ترکیبی `Ctrl + C` را در ترمینال فشار دهید. گزارش معاملات هر جفت‌ارز به صورت خودکار در پوشه `log_files` با پسوند `.txt` ذخیره خواهد شد.

---
---

# Automated Trading & Arbitrage Bot for Nobitex (English)

This project is a multithreaded automated trading bot developed specifically for the Iranian cryptocurrency exchange, **Nobitex**. By concurrently monitoring price feeds from several reputable international exchanges alongside Nobitex, the bot identifies statistical price spreads (arbitrage opportunities) and trend movements, initiating market buy and sell cycles based on global price momentum.

## 🌟 Key Features

- **Global Price Aggregation:** Automatically fetches and averages asset prices from 6 top-tier international exchanges (Binance, Coinbase, Bybit, Huobi, Kraken, Gate.io).
- **Orderbook Depth Analysis:** Rather than executing trades based on the last transaction price, the bot calculates real expected execution rates by parsing the target exchange's order book depth according to your active trade volume.
- **Simultaneous Multithreading:** Spawns and manages independent execution threads for each active trading pair, ensuring fast market updates and transaction response times.
- **Intelligent Position Management:**
  - **Take Profit:** Closes position when the local exchange price matches or exceeds global levels.
  - **Stop Loss:** Multi-layered risk containment based on local or global asset price dips.
  - **Timeout Exit:** Volatility prevention by exiting inactive trades that fail to yield profits within a set time limit.
- **Daily Dust Liquidation:** A background manager runs daily (between 3:00 AM and 5:00 AM Tehran Time) to pause purchases and market-sell trace balances valued between 0 and 1 USDT back to the base trading currency (USDT).
- **Emergency Kill Switch:** Immediately liquidates all active non-excepted wallet balances back to USDT and shuts down the application safely during extreme market events.
- **Rotational File Logging:** Log updates are managed dynamically per asset with automated rotational constraints to prevent hard disk overflow.

---

## 📁 Project Directory Structure

- **`main.py`**: The application's entry point. Initializes individual tracking threads for each active asset pair.
- **`tradebot.py`**: The core execution loop. Handles active buy scans, stop losses, profit targets, and exit timeouts.
- **`parallel_thread_funcs.py`**: Handles background maintenance, token verification, dynamic pair discoveries, and dust liquidation.
- **`variables_func.py`**: System settings including credentials, trade sizes, risk tolerance parameters, and excluded coin blacklists.
- **`buy_sell_func.py`**: Directly communicates order placements, tracks order status, and handles cancellations.
- **`get_crypto_price_func.py`**: Resolves and validates market prices from Nobitex and international exchanges.
- **`get_orderbook_amount_and_price_func.py`**: Processes deep orderbook volume checks to evaluate real-time weighted prices.
- **`get_tradable_crypto_pairs_and_detail_func.py`**: Filters active Nobitex markets and caches decimal requirements locally on disk.
- **`validation_token_checker_func.py`**: Monitors and validates the authentication status of the configured API token.
- **`float_truncator_func.py`**: Mathematical float precision tool to prevent exchange order size validation errors.
- **`logger_func.py`**: Rotation-enabled event logging mechanism per trading asset.
- **`except_exit_func.py`**: Performs safe and immediate process exits from memory upon interruptions.

---

## 🛠️ Prerequisites

To run this codebase, you need:
- **Python 3.9 or higher** (Required for native `zoneinfo` support).
- Install the requests dependency:
  ```bash
  pip install requests
  ```
- **A Nobitex API Token** configured with orders (add and cancel) and wallet balance read permissions.

---

## 🚀 Setup & Usage Instructions

1. Clone or download the repository to your system:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Open the configuration file **`variables_func.py`** in a text editor of your choice:
   - Locate the `"token"` field, erase `"YOUR_NOBITEX_API_TOKEN"`, and paste your actual Nobitex API token.
   - Adjust `"my_usdt_balance"` to reflect your allocated simulation or production funds.
   - Fine-tune exclusions inside `"crypto_list_exceptions"` if you wish to trade larger assets (stablecoins and highly capitalized assets are excluded by default to focus on micro-arbitrage pairs).

3. Start the application by running the main entry script:
   ```bash
   python main.py
   ```

4. To stop the bot cleanly, issue a `Ctrl + C` keyboard interrupt in your terminal. Execution logs for each tracked asset will be compiled inside the `log_files/` directory in standard `.txt` format.
