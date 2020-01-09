# Website 網站

[Expires Next Day - Share if you agree](https://expires-next-day-2020.web.app/archive)
隔日作廢｜認同請分享

## Introduction 簡介

This is the data behind the analysis of eight elections from 2008 to 2018 in Taiwan on the webpage above. We added unique village ID to the vote data. It helps us to connect the village data of different years.  這是上方網頁內，針對台灣 2008-2018 的八次選舉的資料分析，背後的資料。我們在資料中加上了村里代碼，方便將不同年度的村里資料串接起來。

## Data 資料

### Source 來源

[Election Database, Central Election Comission](http://data.cec.gov.tw/)
中選會選舉資料庫

### Format/Schema 資料長相

- All raw and processed data is csv format. 原始及處理過的資料均為 csv 格式。
- Raw data from CEC database is under `vote/raw/` folder. Processed data is under `vote/proc/` folder. The scripts converting from `raw` to `proc` and how-to-run-the-script explanation can be found in `proc/` folder. 中選會資料庫下載的原始資料位於 `vote/raw/` 資料夾，處理過的資料在 `vote/proc/` 資料夾，而處理資料的程式碼，可以在 `proc/` 資料夾找到， 包含程式碼本身以及如何執行。
- The data format follows the original format from CEC database. The format readme document from CEC is `vote/raw/選舉資料庫格式.odt`. We only added one more column: `villID`. 所有資料均遵照中選會原始格式，中選會的格式說明請見 `vote/raw/選舉資料庫格式.odt`，我們只加上村里代碼`villID`欄位。

## I have a question! 我有問題！

Please kindly send us a pull request if there is anything wrong. We will review it soon. If something wrong happens but you don't know how to fix it, then buy us a coffee would be a good way to solve it, maybe? 如果你發現哪裡不對，懇請發個 pull request 過來，我們會跟資料好好談談，並盡快處理。如果你覺得哪裡怪怪的，想叫我們修，請投幣：venmo / @amossclaire 或 PayPal / amoss.claire@gmail.com，我們有空會修，大概？
