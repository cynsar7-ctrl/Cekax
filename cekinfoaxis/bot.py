import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# =============== YOUR TOKEN ===================
BOT_TOKEN = "8273797655:AAGFjB7px-1XprLNR_6QNUWuqIFW_qm2owM"
# ==============================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ===================================================
# START COMMAND
# ===================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.first_name

    msg = (
        f"👋 Halo *{username}*!\n\n"
        "Selamat datang di *Axis Info Checker Bot*.\n"
        "Saya dapat membantu mengecek info kartu Axis secara lengkap.\n\n"
        "*Perintah yang tersedia:*\n"
        "• `/infoaxis 628xxxx` — cek detail kartu Axis\n"
        "• `/help` — bantuan\n\n"
        "Silakan pilih perintah dari menu atau ketik manual 😊"
    )

    await update.message.reply_text(msg, parse_mode="Markdown")


# ===================================================
# HELP COMMAND
# ===================================================
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🆘 *Bantuan Bot*\n\n"
        "`/start` — mulai bot\n"
        "`/infoaxis 628xxxx` — cek info kartu Axis\n\n"
        "Pastikan nomor diawali *628* dan minimal 10 digit."
    )
    await update.message.reply_text(msg, parse_mode="Markdown")


# ===================================================
# INFOAXIS COMMAND
# ===================================================
async def infoaxis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if len(context.args) == 0:
            return await update.message.reply_text(
                "❌ Format salah!\nGunakan:\n`/infoaxis 628xxxx`",
                parse_mode="Markdown"
            )

        number = context.args[0].strip()

        if not number.startswith("628") or len(number) < 10:
            return await update.message.reply_text(
                "❌ Nomor tidak valid!\nHarus mulai dengan *628*.",
                parse_mode="Markdown"
            )

        await update.message.reply_text(
            f"⏳ Sedang memproses nomor `{number}`...",
            parse_mode="Markdown"
        )

        # CALL API
        url = f"https://alettarestapi.vestia.icu/alettaendpoint/cardinfo/axis?number={number}"
        response = requests.get(url)
        data = response.json()

        if not data.get("success"):
            return await update.message.reply_text(
                f"❌ Gagal mengambil data.\n{data.get('message', 'Unknown Error')}",
                parse_mode="Markdown"
            )

        d = data["data"]

        # ============================================
        # RAPIKAN FORMAT QUOTA + TERJEMAHAN
        # ============================================
        quota_msg = "📦 *Kuota Aktif*\n"

        if d["quotas"]["success"]:
            for paket in d["quotas"]["value"]:
                quota_msg += f"\n• *Nama Paket:* `{paket.get('name','N/A')}`\n"
                quota_msg += "  _(Nama paket internet yang sedang aktif)_\n"

                quota_msg += f"  • *Tanggal Berakhir:* `{paket.get('date_end','N/A')}`\n"
                quota_msg += "    _(Tanggal ketika paket ini habis)_\n"

                quota_msg += f"  • *UNIX End:* `{paket.get('date_end_unix','N/A')}`\n"
                quota_msg += "    _(Versi waktu dalam UNIX timestamp)_\n"

                quota_msg += f"  • *Persentase Terpakai:* `{paket.get('percent','N/A')}%`\n"
                quota_msg += "    _(Seberapa banyak kuota sudah digunakan)_\n"

                # Detail kuota
                if "detail_quota" in paket:
                    quota_msg += "  • *Rincian Kuota:*\n"
                    for detail in paket["detail_quota"]:
                        nama = detail.get("name", "N/A")
                        total = detail.get("total_text", "N/A")
                        sisa = detail.get("remaining_text", "N/A")
                        tipe = detail.get("data_type", "DATA")

                        quota_msg += (
                            f"    - *{nama}*\n"
                            f"      Total: `{total}` → Sisa: `{sisa}`\n"
                            f"      _(Jenis: {tipe}; {nama} = kategori kuota ini)_\n"
                        )
        else:
            quota_msg += "• Tidak ada paket aktif\n"


        # ============================================
        # FINAL MESSAGE
        # ============================================
        msg = (
            "📱 *AXIS CARD INFORMATION*\n"
            "--------------------------------\n"
            f"• *Nomor:* `{d.get('msisdn', 'N/A')}`\n"
            "   _(Nomor kartu Axis)_\n"
            f"• *Provider:* `{d['prefix'].get('value','N/A')}`\n"
            "   _(Jenis provider berdasarkan prefix)_\n"
            f"• *Dukcapil:* `{d['dukcapil'].get('value','N/A')}`\n"
            "   _(Status registrasi NIK)_\n"
            f"• *4G:* `{d['status_4g'].get('value','N/A')}`\n"
            "   _(Apakah nomor sudah 4G)_\n"
            f"• *Masa Aktif:* `{d['active_card'].get('value','N/A')}`\n"
            f"• *Aktif Sampai:* `{d['active_period'].get('value','N/A')}`\n"
            f"• *Masa Tenggang:* `{d['grace_period'].get('value','N/A')}`\n\n"

            "📶 *VoLTE*\n"
            f"   • Device : `{ 'Yes' if d['volte']['value'].get('device') else 'No' }`\n"
            "     _(Apakah HP mendukung VoLTE)_\n"
            f"   • Area   : `{ 'Yes' if d['volte']['value'].get('area') else 'No' }`\n"
            "     _(Apakah wilayah mendukung VoLTE)_\n"
            f"   • SIM    : `{ 'Yes' if d['volte']['value'].get('simcard') else 'No' }`\n"
            "     _(Apakah kartu mendukung VoLTE)_\n\n"
            f"{quota_msg}\n"
            "🛠 Developer: Purple | Iris"
        )

        await update.message.reply_text(msg, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(
            f"❌ Error internal: `{str(e)}`",
            parse_mode="Markdown"
        )


# ===================================================
# BOT MAIN
# ===================================================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("infoaxis", infoaxis))

    print("BOT RUNNING…")
    app.run_polling()


if __name__ == "__main__":
    main()
