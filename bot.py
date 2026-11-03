"""LYRA AI STUDIO Telegram controller.

Runs as a separate long-polling process and talks to the existing FastAPI
backend. It does not start or host the AI engines itself.
"""
from __future__ import annotations

import logging
import os
from io import BytesIO
from functools import wraps
from typing import Any, Awaitable, Callable

import httpx
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputFile, Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("lyra.telegram")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
API_BASE_URL = os.getenv(
    "LYRA_API_BASE_URL",
    "https://lyra-ai-studio.vercel.app",
).strip().rstrip("/")
REQUEST_TIMEOUT = float(os.getenv("LYRA_API_TIMEOUT", "12"))
INTERNAL_API_TOKEN = os.getenv("LYRA_TELEGRAM_API_TOKEN", "").strip()

try:
    ADMIN_IDS = {
        int(value.strip())
        for value in os.getenv("ADMIN_IDS", "").split(",")
        if value.strip()
    }
except ValueError as exc:
    raise RuntimeError("ADMIN_IDS harus berisi Telegram numeric user ID.") from exc

if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN belum diatur.")
if not ADMIN_IDS:
    raise RuntimeError(
        "ADMIN_IDS wajib diatur. Masukkan Telegram numeric user ID "
        "agar bot tidak terbuka untuk publik."
    )
if not API_BASE_URL.startswith(("https://", "http://")):
    raise RuntimeError("LYRA_API_BASE_URL harus berupa URL http:// atau https://.")


def restricted(
    handler: Callable[..., Awaitable[None]],
) -> Callable[..., Awaitable[None]]:
    """Allow bot commands only for configured Telegram user IDs."""
    @wraps(handler)
    async def wrapper(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        user = update.effective_user
        if user is None or user.id not in ADMIN_IDS:
            message = update.effective_message
            if message:
                await message.reply_text("Akses ditolak. Bot ini bersifat pribadi.")
            if update.callback_query:
                await update.callback_query.answer("Akses ditolak.", show_alert=True)
            return
        await handler(update, context)
    return wrapper


async def api_get(path: str) -> Any:
    """Fetch a JSON endpoint from the LYRA FastAPI backend."""
    url = f"{API_BASE_URL}{path}"
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


async def send(
    update: Update,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    message = update.effective_message
    if message:
        await message.reply_text(text, reply_markup=reply_markup)


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📡 Status", callback_data="menu:status"),
            InlineKeyboardButton("⚙️ Engines", callback_data="menu:engines"),
        ],
        [
            InlineKeyboardButton("🎙 Voicebox", callback_data="menu:voice"),
            InlineKeyboardButton("ℹ️ Info", callback_data="menu:info"),
        ],
        [InlineKeyboardButton("🔨 MANUAL CREATE", callback_data="menu:create")],
        [InlineKeyboardButton("❔ Help", callback_data="menu:help")],
    ])


def api_error_message(exc: Exception) -> str:
    if isinstance(exc, httpx.HTTPStatusError):
        return (
            f"Backend mengembalikan HTTP {exc.response.status_code}. "
            "Periksa deployment API LYRA."
        )
    if isinstance(exc, httpx.RequestError):
        return (
            "Backend LYRA tidak dapat dijangkau. Periksa URL deployment "
            "dan koneksi jaringan."
        )
    return "Terjadi kesalahan saat membaca respons backend LYRA."


@restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop("awaiting_manual_prompt", None)
    await send(
        update,
        "🔷 LYRA AI STUDIO\n"
        "Telegram Control Center\n\n"
        "Pilih pemeriksaan sistem dari menu berikut. "
        "Bot ini mengendalikan API yang sudah ada; engine yang belum "
        "terintegrasi akan tetap ditandai belum aktif.",
        main_menu(),
    )


@restricted
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send(
        update,
        "📘 PERINTAH LYRA AI STUDIO\n\n"
        "/start — menu utama\n"
        "/help — bantuan\n"
        "/status — status backend dan ringkasan engine\n"
        "/engines — daftar seluruh engine\n"
        "/voice — pemeriksaan koneksi Voicebox\n"
        "/info — informasi aplikasi\n\n"
        "Catatan: Image Studio, Video Studio, dan OpenMontage "
        "belum memiliki integrasi produksi pada repository saat ini."
    )



def detect_creation_type(prompt: str) -> str | None:
    value = prompt.lower()
    if any(word in value for word in ("video", "film", "animasi", "klip")):
        return "video"
    if any(word in value for word in ("audio", "suara", "narasi", "voice", "bicara", "ucapan")):
        return "audio"
    if any(word in value for word in ("gambar", "foto", "ilustrasi", "image", "poster")):
        return "image"
    return None


@restricted
async def manual_create_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.user_data.get("awaiting_manual_prompt"):
        return
    message = update.effective_message
    if message is None or not message.text:
        return
    prompt = message.text.strip()
    creation_type = detect_creation_type(prompt)
    if creation_type is None:
        await message.reply_text("Tambahkan kata gambar, video, atau audio agar jenis konten dapat dikenali.")
        return
    context.user_data.pop("awaiting_manual_prompt", None)
    if creation_type == "image":
        await message.reply_text("🖼️ Perintah gambar dikenali, tetapi Image Studio belum memiliki provider generator. Belum ada gambar yang dibuat.")
        return
    if creation_type == "video":
        await message.reply_text("🎬 Perintah video dikenali, tetapi Video Studio belum memiliki provider generator. Belum ada video yang dibuat.")
        return
    if not INTERNAL_API_TOKEN:
        await message.reply_text("🎙️ Perintah audio dikenali, tetapi LYRA_TELEGRAM_API_TOKEN belum dikonfigurasi. Audio belum dibuat.")
        return
    await message.reply_text("🎙️ Permintaan audio diterima. Memeriksa Voicebox...")
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.post(
                f"{API_BASE_URL}/api/engines/voicebox/generate",
                json={"text": prompt, "profile_id": None},
                headers={"X-Lyra-Internal-Token": INTERNAL_API_TOKEN},
            )
            response.raise_for_status()
            audio_bytes = response.content
            content_type = response.headers.get("content-type", "application/octet-stream")
        if not audio_bytes:
            await message.reply_text("Voicebox mengembalikan file kosong. Audio tidak dikirim.")
            return
        suffix = ".mp3" if "mpeg" in content_type or "mp3" in content_type else ".wav"
        audio_file = InputFile(BytesIO(audio_bytes), filename=f"lyra-generated{suffix}")
        if content_type.startswith("audio/"):
            await message.reply_audio(audio=audio_file, caption="✅ Audio dari LYRA AI STUDIO")
        else:
            await message.reply_document(document=audio_file, caption="✅ File Voicebox dari LYRA AI STUDIO")
    except httpx.HTTPStatusError as exc:
        logger.warning("Voice generation failed with HTTP %s", exc.response.status_code)
        await message.reply_text(f"⚠️ Pembuatan audio gagal (HTTP {exc.response.status_code}). Periksa Voicebox dan profile.")
    except httpx.RequestError as exc:
        logger.warning("Voice generation backend request failed: %s", exc)
        await message.reply_text("⚠️ Backend LYRA tidak dapat dijangkau. Audio belum dibuat.")


@restricted
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        data = await api_get("/api/status")
        engines = data.get("engines") or {}
        connected = sum(1 for item in engines.values() if item.get("connected"))
        await send(
            update,
            "📡 STATUS LYRA AI STUDIO\n\n"
            f"Backend: {data.get('backend', 'unknown')}\n"
            f"Engine terdaftar: {len(engines)}\n"
            f"Engine terhubung: {connected}\n"
            f"API: {API_BASE_URL}"
        )
    except Exception as exc:
        logger.warning("Status request failed: %s", exc)
        await send(update, f"⚠️ {api_error_message(exc)}")


@restricted
async def engines_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        engines = await api_get("/api/engines")
        labels = {
            "planned": "Belum diintegrasikan",
            "adapter_available": "Adapter tersedia, koneksi belum diverifikasi",
            "configuration_required": "Konfigurasi diperlukan",
            "connected": "Terhubung",
            "unavailable": "Tidak tersedia",
        }
        lines = ["⚙️ ENGINE REGISTRY\n"]
        for key, item in engines.items():
            status = item.get("status", "unknown")
            connected = "🟢" if item.get("connected") else "⚪"
            description = labels.get(status, status)
            lines.append(
                f"{connected} {item.get('name', key)}\n"
                f"   Status: {description}"
            )
        await send(update, "\n".join(lines))
    except Exception as exc:
        logger.warning("Engine registry request failed: %s", exc)
        await send(update, f"⚠️ {api_error_message(exc)}")


@restricted
async def voice_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        data = await api_get("/api/engines/voicebox/health")
        connected = bool(data.get("connected"))
        if connected:
            result = "🟢 Voicebox dapat dijangkau."
        else:
            result = (
                "⚪ Voicebox belum terhubung atau belum dapat dijangkau. "
                "Periksa VOICEBOX_BASE_URL dan pastikan layanan Voicebox aktif."
            )
        await send(
            update,
            "🎙 PEMERIKSAAN VOICEBOX\n\n"
            f"{result}\n"
            f"Status code: {data.get('status_code', 'tidak tersedia')}"
        )
    except Exception as exc:
        logger.warning("Voicebox health request failed: %s", exc)
        await send(update, f"⚠️ {api_error_message(exc)}")


@restricted
async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        data = await api_get("/api/info")
        await send(
            update,
            "ℹ️ INFORMASI APLIKASI\n\n"
            f"Nama: {data.get('name', 'LYRA AI STUDIO')}\n"
            f"Versi: {data.get('version', 'unknown')}\n"
            f"Environment: {data.get('environment', 'unknown')}"
        )
    except Exception as exc:
        logger.warning("Info request failed: %s", exc)
        await send(update, f"⚠️ {api_error_message(exc)}")


@restricted
async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None:
        return
    await query.answer()
    action = (query.data or "").partition(":")[2]
    if action == "create":
        context.user_data["awaiting_manual_prompt"] = True
        await query.message.reply_text(
            "🔨 MANUAL CREATE\n\n"
            "Tulis instruksi pembuatan konten. Sebutkan gambar, video, atau audio.\n"
            "Contoh: Buat audio narasi bahasa Indonesia tentang teknologi AI.\n\n"
            "Ketik /start untuk membatalkan."
        )
        return
    handlers = {
        "status": status_command,
        "engines": engines_command,
        "voice": voice_command,
        "info": info_command,
        "help": help_command,
    }
    handler = handlers.get(action)
    if handler:
        await handler(update, context)


async def post_init(application: Application) -> None:
    await application.bot.set_my_commands([
        ("start", "Buka menu utama"),
        ("help", "Bantuan dan daftar perintah"),
        ("status", "Periksa status backend"),
        ("engines", "Lihat status engine"),
        ("voice", "Periksa koneksi Voicebox"),
        ("info", "Informasi aplikasi"),
    ])
    logger.info("LYRA Telegram Controller started; API=%s", API_BASE_URL)


async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    logger.exception("Unhandled Telegram update error", exc_info=context.error)


def build_application() -> Application:
    application = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("engines", engines_command))
    application.add_handler(CommandHandler("voice", voice_command))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manual_create_message))
    application.add_handler(CallbackQueryHandler(menu_callback, pattern=r"^menu:"))
    application.add_error_handler(error_handler)
    return application


if __name__ == "__main__":
    build_application().run_polling(drop_pending_updates=True)
