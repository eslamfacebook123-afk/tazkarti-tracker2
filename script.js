// ضع هنا رابط Google Apps Script بتاعك
const APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyxiLKqrSUbpeEEk3IEpU-sPjszeSn9S5pTB2XHXjbvSjzs7QijEGobe8VI8DrYFeYYZw/exec";

async function subscribe() {
  const email = document.getElementById("emailInput").value.trim();
  const msg = document.getElementById("msg");
  const btn = document.getElementById("btn");

  if (!email || !email.includes("@")) {
    msg.textContent = "⚠️ اكتب إيميل صح";
    msg.className = "err";
    return;
  }

  btn.disabled = true;
  btn.textContent = "جاري التسجيل...";
  msg.textContent = "";

  try {
    const res = await fetch(APPS_SCRIPT_URL + "?email=" + encodeURIComponent(email));
    const data = await res.json();

    if (data.status === "ok") {
      msg.textContent = "✅ تم التسجيل! هنبعتلك إشعار لما تنزل التذاكر";
      msg.className = "ok";
      document.getElementById("emailInput").value = "";
    } else if (data.status === "exists") {
      msg.textContent = "📧 الإيميل ده مسجل قبل كده";
      msg.className = "ok";
    } else {
      throw new Error("server error");
    }
  } catch (e) {
    msg.textContent = "❌ في مشكلة، حاول تاني";
    msg.className = "err";
  }

  btn.disabled = false;
  btn.textContent = "🔔 اشترك في التنبيهات";
}