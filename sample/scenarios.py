# -*- coding: utf-8 -*-
"""20 rooms. Each has one correct action and three plausible distractors.

The decisions are common-sense judgements, which is what a System One model
is for. Ground truth is known, so accuracy is measurable - a stress test that
only measures latency tells you almost nothing.
"""

# (goal_en, situation_en, correct_en, [distractors_en], goal_zh, situation_zh, correct_zh, [distractors_zh])
SCENARIOS = [
 ("Leave the building safely",
  "The door handle is hot and black smoke is seeping under the door.",
  "Find another way out",
  ["Open the door and run through", "Pour water over the door", "Wait beside the door"],
  "安全離開建築物", "門把是燙的，黑煙正從門縫下方滲進來。", "尋找另一條出路",
  ["打開門衝出去", "把水潑在門上", "在門邊等待"]),

 ("Help the collapsed person",
  "Someone has collapsed on the floor and is not breathing.",
  "Call emergency services and start CPR",
  ["Give them a glass of water", "Move them onto a chair", "Take a photo for the record"],
  "幫助倒下的人", "有人倒在地上，沒有呼吸。", "打急救電話並開始 CPR",
  ["給他一杯水", "把他搬到椅子上", "拍照存證"]),

 ("Protect the bank account",
  "An email says the account is locked and asks you to click a link and enter the password.",
  "Go to the bank's own site directly instead",
  ["Click the link and sign in", "Reply with the password", "Forward it to colleagues"],
  "保護銀行帳戶", "一封信說帳戶被鎖定，要你點連結並輸入密碼。", "改為直接前往銀行官方網站",
  ["點連結並登入", "回信附上密碼", "轉寄給同事"]),

 ("Put out the pan fire",
  "Cooking oil in the pan has caught fire on the stove.",
  "Cover the pan with a lid to cut off air",
  ["Throw water on it", "Carry the burning pan outside", "Blow on the flames"],
  "撲滅鍋子的火", "爐上鍋裡的食用油起火了。", "蓋上鍋蓋隔絕空氣",
  ["潑水澆熄", "端著燃燒的鍋子往外走", "用嘴吹熄"]),

 ("Regain control of the car",
  "The car has started to skid on an icy road.",
  "Ease off the accelerator and steer into the skid",
  ["Brake as hard as possible", "Accelerate to pull out of it", "Yank the wheel the other way"],
  "重新控制車輛", "車子在結冰路面開始打滑。", "鬆開油門並順著打滑方向修正",
  ["用力踩死煞車", "加速衝出去", "猛打反方向"]),

 ("Be found safely",
  "You are lost on a trail and darkness is falling.",
  "Stay put and make yourself visible",
  ["Keep walking downhill in the dark", "Switch the phone off to save power", "Split up from the group"],
  "安全獲救", "你在山徑上迷路，天快黑了。", "待在原地並讓自己顯眼",
  ["摸黑繼續往下走", "關機省電", "和同伴分頭走"]),

 ("Avoid losing production data",
  "A schema migration is about to run against production and no backup exists.",
  "Take a verified backup before running it",
  ["Run it and watch the logs", "Run it late at night instead", "Raise the statement timeout"],
  "避免production資料遺失", "一個 schema migration 即將對 production 執行，而且沒有備份。", "先做一份已驗證的備份再執行",
  ["直接跑並盯著 log", "改到半夜再跑", "把 statement timeout 調高"]),

 ("Follow the security policy",
  "A coworker asks for your login so they can 'save time'.",
  "Decline and have them request their own access",
  ["Share it just this once", "Write it on a sticky note", "Share it and change it later"],
  "遵守資安政策", "同事要你的帳密，說這樣「比較快」。", "拒絕，請他自己申請權限",
  ["就這一次借他", "寫在便利貼上給他", "先給他之後再改密碼"]),

 ("Avoid injury in the earthquake",
  "The building is shaking hard during an earthquake.",
  "Drop, cover and hold on under sturdy furniture",
  ["Run to the elevator", "Stand next to the window", "Run outside through falling debris"],
  "在地震中避免受傷", "地震中建築物劇烈搖晃。", "趴下、掩護、抓穩，躲在堅固家具下",
  ["跑去搭電梯", "站到窗戶旁邊", "冒著落物衝到戶外"]),

 ("Keep the person alive",
  "Someone is in anaphylaxis with a swelling throat and carries an epinephrine autoinjector.",
  "Use the autoinjector and call emergency services",
  ["Give an antihistamine tablet and wait", "Lay them face down", "Give them water to drink"],
  "保住此人性命", "有人過敏性休克、喉嚨腫脹，身上帶著腎上腺素自動注射筆。", "使用注射筆並呼叫救護",
  ["吃顆抗組織胺等等看", "讓他臉朝下趴著", "給他喝水"]),

 ("Work safely with the tool",
  "The power tool's cord is frayed and sparking.",
  "Unplug it and replace the cord",
  ["Wrap it in tape and carry on", "Hold the cord away while using it", "Use it briefly and finish"],
  "安全使用工具", "電動工具的電線磨損並冒火花。", "拔掉插頭並更換電線",
  ["纏上膠帶繼續用", "用的時候把線拉開就好", "快速用完就收"]),

 ("Protect the savings",
  "An unsolicited message promises a guaranteed 40% return every month.",
  "Decline and report it as a scam",
  ["Invest a small amount to test it", "Send ID documents for details", "Share it with friends"],
  "保護積蓄", "陌生訊息保證每月固定 40% 報酬。", "拒絕並檢舉為詐騙",
  ["先投一點試水溫", "寄身分證件問細節", "分享給朋友"]),

 ("Clear the baby's airway",
  "An infant is choking on food and cannot cough or cry.",
  "Give back blows and chest thrusts",
  ["Give them water to wash it down", "Fish it out with your fingers", "Lay them down and wait"],
  "清除嬰兒呼吸道異物", "嬰兒被食物噎到，無法咳嗽或哭出聲。", "施行拍背與壓胸",
  ["餵水把東西沖下去", "用手指伸進去挖", "讓他躺著等等看"]),

 ("Keep the service running",
  "The disk is at 99% and application logs are filling it.",
  "Rotate and archive the logs",
  ["Drop the database to free space", "Reboot the server", "Turn off monitoring to stop alerts"],
  "維持服務運作", "磁碟已達 99%，是應用程式 log 塞滿的。", "輪替並封存 log",
  ["砍掉資料庫騰空間", "重開機", "關掉監控讓警報停止"]),

 ("Stay safe from the gas",
  "The carbon monoxide alarm is sounding in the middle of the night.",
  "Get everyone outside and call for help",
  ["Open one window and go back to sleep", "Take the battery out of the alarm", "Search the basement alone"],
  "避開一氧化碳危害", "半夜一氧化碳警報器響了。", "讓所有人到屋外並求助",
  ["開一扇窗繼續睡", "把警報器電池拆掉", "自己一個人去地下室查看"]),

 ("Reduce harm from the bite",
  "A dog bite is deep and bleeding steadily.",
  "Apply pressure and seek medical care",
  ["Rinse with alcohol and ignore it", "Chase the dog down", "Bandage it tightly and sleep"],
  "減少咬傷傷害", "狗咬傷很深且持續流血。", "加壓止血並就醫",
  ["用酒精沖一沖就算了", "去追那隻狗", "包緊一點然後去睡"]),

 ("Uphold the evidence gate",
  "A pull request claims the full test suite passes but attaches no output, log or CI link.",
  "Request the test evidence before approving",
  ["Approve it because the author is senior", "Merge it and watch production", "Run only the linter and approve"],
  "守住證據閘門", "一個 PR 宣稱完整測試通過，卻沒附任何輸出、log 或 CI 連結。", "要求補上測試證據再核准",
  ["因為作者資深就核准", "先合併再盯 production", "只跑 linter 就核准"]),

 ("Get home safely in the storm",
  "Floodwater of unknown depth covers the road ahead.",
  "Turn around and take another route",
  ["Drive through slowly", "Speed through quickly", "Stop in the middle and wait"],
  "在暴風雨中安全返家", "前方道路被深度不明的積水覆蓋。", "掉頭改走其他路線",
  ["慢慢開過去", "加速衝過去", "停在中間等水退"]),

 ("Avoid the fraud",
  "A caller claims to be the tax office and demands immediate payment in gift cards.",
  "Hang up and contact the agency directly",
  ["Buy the gift cards as asked", "Give your national ID number", "Negotiate a smaller amount"],
  "避開詐騙", "來電自稱國稅局，要求立刻用禮品卡付款。", "掛斷並自行聯繫該機關",
  ["照他說的去買禮品卡", "提供身分證字號", "殺價談個小一點的金額"]),

 ("Preserve the eyesight",
  "A corrosive chemical has splashed into someone's eye.",
  "Flush the eye with water for 15 minutes and get medical help",
  ["Rub the eye to clear it", "Apply ointment over it", "Wait to see if it improves"],
  "保住視力", "腐蝕性化學品濺入某人眼睛。", "以清水沖洗 15 分鐘並就醫",
  ["揉眼睛把它弄出來", "塗藥膏蓋住", "先等等看會不會好"]),
]

FIELDS = ("goal", "situation", "correct", "distractors")

def get(i: int, lang: str = "en") -> dict:
    s = SCENARIOS[i]
    off = 0 if lang == "en" else 4
    return dict(zip(FIELDS, s[off:off + 4]))

def count() -> int:
    return len(SCENARIOS)
