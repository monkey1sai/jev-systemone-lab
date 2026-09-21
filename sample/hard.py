# -*- coding: utf-8 -*-
"""Twelve rooms where every option is defensible and only one is right.

The easy set saturates at 100%, which measures nothing. Here each distractor
is a near miss: standard-sounding advice that is wrong by one decisive detail.
This is where a difference between extraction shapes or languages, if there is
one, has room to show up.
"""

SCENARIOS = [
    ("Prevent double charges",
     "A pull request wraps the payment API call in a retry loop because the endpoint times out intermittently.",
     "Give the request an idempotency key before retrying it",
     ["Add exponential backoff between the retries",
      "Retry only when the response is a 5xx",
      "Cap the number of retries at three"],
     "避免重複扣款",
     "一個 PR 把付款 API 呼叫包進重試迴圈，因為該端點偶爾逾時。",
     "在重試前讓該請求帶上 idempotency key",
     ["在重試之間加上指數退避", "只在回應為 5xx 時才重試", "把重試次數上限設為三次"]),

    ("Restore service latency",
     "Latency spiked right after a deploy whose only change was adding an index to a 900 million row table.",
     "Check whether the index build is still running and holding locks",
     ["Roll the deploy back immediately",
      "Add more read replicas to spread the load",
      "Raise the database connection pool size"],
     "讓延遲恢復正常",
     "一次部署後延遲暴增，該部署唯一的變更是對一張九億列的表加索引。",
     "確認索引建立是否仍在進行並持有鎖",
     ["立刻回滾這次部署", "增加唯讀副本分散負載", "調高資料庫連線池大小"]),

    ("Treat the anaphylaxis correctly",
     "An adult in anaphylaxis has an epinephrine autoinjector and you are about to use it.",
     "Inject into the outer thigh, then call emergency services",
     ["Inject into the upper arm, then call emergency services",
      "Call emergency services and let them do the injection",
      "Inject, then drive the person to hospital yourself"],
     "正確處理過敏性休克",
     "一名成人過敏性休克，身上有腎上腺素自動注射筆，你正要使用。",
     "注射於大腿外側，然後呼叫救護",
     ["注射於上臂，然後呼叫救護", "先呼叫救護，讓救護人員來注射", "注射後自己開車送他去醫院"]),

    ("Give the best chance of survival",
     "An adult is unresponsive and not breathing normally. You are alone and help is coming.",
     "Start chest compressions straight away",
     ["Spend up to a minute checking for a pulse first",
      "Give two rescue breaths before anything else",
      "Put them in the recovery position and monitor"],
     "給予最大存活機會",
     "一名成人失去反應且呼吸不正常。你獨自一人，救援正在路上。",
     "立刻開始胸外按壓",
     ["先花最多一分鐘確認脈搏", "先給兩次人工呼吸", "先擺成復甦姿勢並觀察"]),

    ("Stop the bleeding",
     "A forearm wound is bleeding steadily. There is no sign of arterial spurting.",
     "Press firmly on the wound and keep pressing without lifting to check",
     ["Apply a tourniquet above the wound straight away",
      "Raise the arm above the heart and wait",
      "Clean the wound thoroughly before covering it"],
     "止住出血",
     "前臂傷口持續穩定流血，沒有動脈噴射的跡象。",
     "在傷口上持續加壓，不要中途鬆手查看",
     ["立刻在傷口上方綁止血帶", "把手臂舉過心臟並等待", "先徹底清洗傷口再包紮"]),

    ("Avoid the payment fraud",
     "An urgent email that looks like it is from the CEO asks you to buy gift cards. The domain differs by one character.",
     "Confirm with the CEO on a phone number you already have",
     ["Reply to the email and ask them to confirm",
      "Check that the sender display name matches",
      "Forward it to the team and ask if it looks real"],
     "避開付款詐騙",
     "一封看似來自執行長的急件要你去買禮品卡，寄件網域只差一個字元。",
     "用你原本就有的電話號碼向執行長確認",
     ["回信請對方確認", "檢查寄件者顯示名稱是否相符", "轉寄給團隊問大家覺得像不像真的"]),

    ("Limit the burn damage",
     "Someone has spilled boiling water over their forearm. The skin is red and painful but unbroken.",
     "Hold it under cool running water for twenty minutes",
     ["Press ice against the burn to numb it",
      "Cover it with a dry dressing right away",
      "Spread ointment over it to seal the skin"],
     "減少燙傷損害",
     "有人把滾水潑到前臂上，皮膚發紅疼痛但未破皮。",
     "以流動冷水沖二十分鐘",
     ["用冰塊敷在燙傷處止痛", "立刻用乾敷料蓋住", "塗上藥膏把皮膚封住"]),

    ("Contain the leaked credential",
     "An API key was committed and pushed to the team's private repository an hour ago.",
     "Rotate the key first, then clean the history",
     ["Delete the file and push a new commit",
      "Rewrite the history to remove the commit",
      "Confirm the repository is private and move on"],
     "控制外洩的憑證",
     "一把 API key 在一小時前被 commit 並推送到團隊的私有 repository。",
     "先輪替金鑰，再清理歷史",
     ["刪掉檔案再推一個新 commit", "改寫歷史把那個 commit 移除", "確認 repository 是私有的就好"]),

    ("Know the backup actually works",
     "The nightly backup job has reported success every night for six months.",
     "Restore it into a scratch environment and check the data",
     ["Confirm the job exit code is zero",
      "Check the backup file size is not zero",
      "Increase the backup frequency to twice daily"],
     "確認備份真的能用",
     "夜間備份工作已連續六個月每晚回報成功。",
     "還原到一個臨時環境並檢查資料",
     ["確認工作的 exit code 為零", "檢查備份檔大小不為零", "把備份頻率提高到一天兩次"]),

    ("Protect the player's brain",
     "A player took a blow to the head, is briefly dizzy, and insists on continuing.",
     "Take them out for the rest of the day regardless of how they feel",
     ["Let them return once the dizziness passes",
      "Let them continue if they answer memory questions correctly",
      "Give painkillers and watch them closely"],
     "保護球員的大腦",
     "一名球員頭部受到撞擊，短暫暈眩，堅持要繼續上場。",
     "不論他感覺如何，當天都不得再上場",
     ["等暈眩過去就讓他回場", "若能正確回答記憶問題就讓他繼續", "給止痛藥並密切觀察"]),

    ("Free the person from the current",
     "Someone is gripping a live electrical cable and cannot let go.",
     "Switch off the power at the source before touching them",
     ["Pull them clear by their clothing",
      "Check whether they are breathing first",
      "Throw water over the cable to break the contact"],
     "讓人脫離電流",
     "有人抓著帶電的電纜無法鬆手。",
     "先從電源處切斷電力再碰觸他",
     ["抓著衣服把他拉開", "先確認他是否還有呼吸", "潑水到電纜上切斷接觸"]),

    ("Slow the venom",
     "A venomous snake has bitten someone on the lower leg and you are forty minutes from a hospital.",
     "Keep the leg still and below heart level while getting them to hospital",
     ["Tie a tight tourniquet above the bite",
      "Cut the bite and draw the venom out",
      "Pack ice around the bite to slow absorption"],
     "延緩毒液擴散",
     "有人小腿被毒蛇咬傷，距離醫院四十分鐘車程。",
     "保持該腿不動且低於心臟高度，同時送醫",
     ["在咬傷上方綁緊止血帶", "切開傷口把毒液吸出", "用冰塊包住傷口延緩吸收"]),
]

FIELDS = ("goal", "situation", "correct", "distractors")


def get(i, lang="en"):
    s = SCENARIOS[i]
    off = 0 if lang == "en" else 4
    return dict(zip(FIELDS, s[off:off + 4]))


def count():
    return len(SCENARIOS)
