# Alert Engine

## Ringkasan

Alert Engine (dalam tahap perencanaan) akan menyediakan sistem notifikasi dan alert untuk berbagai event trading. Engine ini akan memonitor perubahan kondisi pasar, sinyal baru, dan status portfolio, lalu mengirimkan notifikasi melalui berbagai channel.

---

## Status Saat Ini

Saat ini, fungsionalitas alert dasar sudah tersedia melalui **Safety System** pada MT5 Bridge yang menyediakan proteksi otomatis.

### SafetySystem

**File**: `apps/mt5-bridge/src/al_syaka_mt5/safety.py`

Multi-layer protection system untuk auto trading.

```python
class SafetySystem:
    def __init__(self, initial_balance=10_000):
        self.config = SafetyConfig()
        self.peak_balance = initial_balance
        self.current_balance = initial_balance
```

**SafetyConfig**:
```python
@dataclass
class SafetyConfig:
    max_daily_loss: float = 500.0
    max_drawdown_percent: float = 10.0
    max_consecutive_losses: int = 5
    max_positions: int = 5
    circuit_breaker_cooldown_minutes: int = 30
    kill_switch_engaged: bool = False
```

**Fungsi Proteksi**:

| Proteksi | Mekanisme | Aksi |
|----------|-----------|------|
| Kill Switch | Manual | Menghentikan semua trading |
| Circuit Breaker | Otomatis setelah 5 losses berturut-turut | Cooldown 30 menit |
| Daily Loss Limit | Jika loss harian >= $500 | Blokir trading |
| Max Drawdown | Jika drawdown >= 10% dari peak | Blokir trading |
| Max Positions | Maksimum 5 posisi bersamaan | Tolak order baru |

**Safety Status**:
```python
{
    "can_trade": true/false,
    "kill_switch": false,
    "circuit_breaker_active": false,
    "current_balance": 10250.00,
    "peak_balance": 10500.00,
    "drawdown_percent": 2.38,
    "daily_loss": 150.00,
    "consecutive_losses": 2,
}
```

---

## Rencana Pengembangan Alert Engine

### 1. Event-Based Triggers

Alert akan dipicu oleh berbagai event:

**Market Events**:
- Harga mencapai level support/resistance kunci.
- Break of structure (BOS) atau Change of character (CHOCH) terdeteksi.
- Fair Value Gap (FVG) terbentuk atau terisi.
- Liquidity sweep terdeteksi.
- Volatilitas melebihi threshold.

**Signal Events**:
- Sinyal BUY/SELL baru dengan confidence tinggi (>= 80%).
- Perubahan market regime (contoh: RANGE -> TRENDING).
- Konflik antara teknikal dan makro.
- AI prediction dengan confidence tinggi.

**Portfolio Events**:
- Posisi mencapai SL atau TP.
- Drawdown melebihi threshold.
- Daily loss limit mendekati batas.
- Margin level rendah.

**System Events**:
- Data collector error / disconnect.
- Model AI membutuhkan retraining.
- Celery task failure.

### 2. Notification Channels

**Rencana Channel**:
- **In-App Notifications** -- Notifikasi di dashboard (via WebSocket).
- **Email** -- Notifikasi email untuk event penting (signal harian, drawdown).
- **Push Notifications** -- Mobile push (via Firebase/APNs).
- **Telegram/Discord** -- Bot integration untuk komunitas.
- **Webhook** -- Custom webhook untuk integrasi eksternal.

### 3. Alert Configuration

Pengguna dapat mengkonfigurasi:

```yaml
alerts:
  signal_confidence_threshold: 80
  drawdown_warning: 5%       # Peringatan saat drawdown 5%
  drawdown_critical: 10%     # Alert kritis saat drawdown 10%
  daily_loss_warning: 300    # Peringatan saat loss harian $300
  max_daily_alerts: 10       # Maksimum alert per hari
  channels:
    - dashboard
    - email
    - telegram

  events:
    new_signal:              # Sinyal baru
      enabled: true
      min_confidence: 75
    market_structure:        # Perubahan struktur pasar
      enabled: true
      types: [BOS, CHOCH, FVG]
    portfolio_risk:          # Risiko portfolio
      enabled: true
      drawdown_threshold: 5
```

### 4. Alert History & Analytics

Riwayat alert untuk analisis:
- Timestamp dan tipe alert.
- Response time.
- Alert effectiveness (apakah alert diikuti).
- Pattern analysis.

---

## Integrasi dengan Engine Lain

```
[Market Structure Engine]   -- BOS, CHOCH, FVG events
        |
[Signal Engine]            -- New signal, regime change
        |
[Portfolio Engine]         -- SL/TP hit, drawdown, balance
        |
[Risk Engine]              -- Risk threshold breached
        |
        v
[Alert Engine]
        |
        +---> Dashboard (WebSocket)
        +---> Email (SMTP)
        +---> Telegram/Discord (Bot API)
        +---> Webhook (HTTP POST)
```

---

## Dependensi Eksternal (Rencana)

- **WebSocket** -- FastAPI WebSocket untuk real-time dashboard.
- **SMTP** -- Email notification (sendgrid/smtplib).
- **Telegram Bot API** -- Bot Telegram untuk notifikasi.
- **Redis Pub/Sub** -- Event bus untuk distribusi alert.
