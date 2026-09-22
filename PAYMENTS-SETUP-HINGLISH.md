# 💳 Payment Setup Guide (Hinglish) — HonestMRR me paise kaise accept karein

Site par **Sponsor page** live hai: https://honestmrr.surge.sh/pricing.html
Us page par payment buttons **automatically** appear ho jate hai jab aap neeche wali cheezein set karke `data/config.json` me daalte hai (ya mujhe chat me bata dete ho — main laga ke redeploy kar dunga).

```json
"upi_id": "aapka@upi",              ← UPI button + QR code
"razorpay_link": "https://...",     ← Card/NetBanking button
"paypal_link": "https://paypal.me/...",  ← International button
"wise_link": "https://wise.com/..."      ← Wire transfer button
```

---

## Rail 1: UPI — AAJ se, 0 minute, 0 KYC ✅

1. Phone me koi bhi UPI app kholo (Google Pay / PhonePe / Paytm)
2. Apni **UPI ID** note karo (jaise `rahul@okhdfcbank`, `rahul@ybl`, `rahul@paytm`)
   - Business ke liye alag rakhna ho to naya bank-linked UPI ID bana lo
3. **Wo UPI ID mujhe chat me bhejo** — main site par laga dunga:
   - "Pay via UPI" button (phone par tap karte hi UPI app khul jayega, amount ready)
   - **QR code** page par generate hoga — scan karo, pay karo
4. Limit: personal UPI me koi receiving limit nahi (income tax alag baat hai, neeche dekho)

## Rail 2: Razorpay Payment Links — serious mode (2-3 din KYC)

Kab chahiye: jab card/netbanking/international cards se payment lena ho (sponsors zyada trust karte hai).

1. [razorpay.com](https://razorpay.com) → Sign up (email + phone)
2. KYC documents (sole proprietor / individual ke liye):
   - PAN card
   - Bank account (cancelled cheque / statement)
   - Aadhaar (address proof)
   - Business declaration letter (Razorpay template deta hai — "sole proprietor" select karo)
3. Approval: 2-3 working days
4. Dashboard → **Payment Links** → "Create link": amount ₹15,000, description "Homepage Sponsor Slot - 1 month" → link copy
5. Aise 3 links banao (sponsor ₹15,000 / featured ₹3,000 / fast-track ₹1,500) — ya ek open-amount link
6. Link mujhe bhejo → main config me laga dunga → site par "💳 Card / NetBanking" button aa jayega
- Fees: ~2% per successful transaction. Paise seedha aapke bank me (T+3 days).

## Rail 3: PayPal / Wise — foreign sponsors ($ me)

- **PayPal.me**: [paypal.me](https://paypal.me) par free link banao (`paypal.me/aapkanaam`) — US/EU sponsor click karke dollars me bhejta hai. India PayPal account me PAN + bank link karna padta hai (purpose code auto).
- **Wise** ([wise.com](https://wise.com)): business account free — foreign bank transfer (USD/EUR) saste me receive karo, invoice PDF bhi ban sakta hai.
- Dono me se jo pehle ban jaye uska link mujhe de do.

---

## ⚖️ Tax / legal (chhota sa, par zaroori)

- Jo bhi kamayo wo **income hai** — ITR me dikhana hota hai ("business income" ya "other sources")
- **GST**: services me ₹20 lakh/sal tak registration zaroori nahi — shuruaat me tension nahi
- ₹50K+ mahina hone par ek **sole proprietorship + current account** khol lena (₹0 cost, bank me PAN se ban jata hai) — business banking clean rehti hai
- Records: har payment ka screenshot/receipt ek folder me rakho (main Sheet bana deta hu chahiye to)

---

## 🎯 Abhi kya karna hai (priority order)

1. **Abhi:** UPI ID mujhe bhejo → 5 minute me live
2. **Is hafte:** Razorpay signup + KYC submit karo (approval wait)
3. **Jab approval aaye:** payment links bhejo → main laga dunga
4. **Pehla foreign sponsor aane par:** PayPal.me/Wise bana lena

Pehla payment aate hi batana — milestone celebrate karenge! 🎉
