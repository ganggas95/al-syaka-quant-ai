# Spesifikasi WebSocket Al-Syaka Quant AI

## Status Saat Ini

WebSocket belum diimplementasikan di versi saat ini. Dokumen ini berisi spesifikasi dan rencana implementasi untuk fase selanjutnya.

---

## Rencana Implementasi WebSocket

### Endpoint WebSocket

```
ws://localhost:8000/ws/{channel}
```

### Channel yang Direncanakan

| Channel | Prefix | Deskripsi |
|---------|--------|-----------|
| Market Data | `/ws/market/{symbol}` | Data OHLC real-time |
| Signals | `/ws/signals/{symbol}` | Sinyal trading real-time |
| Indicators | `/ws/indicators/{symbol}` | Update indikator |
| Account | `/ws/account` | Update akun dan posisi |
| System | `/ws/system` | Notifikasi sistem |

---

## Format Pesan

### Format Umum

Semua pesan WebSocket menggunakan format JSON:

```json
{
  "type": "string",
  "channel": "string",
  "data": {},
  "timestamp": "ISO8601",
  "event_id": "uuid"
}
```

### Market Data Channel (`/ws/market/{symbol}`)

**Event Types:**

#### `ohlc_update`
Dikirim setiap kali ada candle baru.

```json
{
  "type": "ohlc_update",
  "channel": "market",
  "symbol": "EURUSD",
  "data": {
    "timeframe": "H1",
    "timestamp": "2026-07-15T10:00:00",
    "open": 1.0850,
    "high": 1.0870,
    "low": 1.0830,
    "close": 1.0860,
    "volume": 1234
  },
  "timestamp": "2026-07-15T10:00:00.000Z",
  "event_id": "evt_abc123"
}
```

#### `tick_update`
Dikirim untuk setiap tick harga baru.

```json
{
  "type": "tick_update",
  "channel": "market",
  "symbol": "EURUSD",
  "data": {
    "timestamp": "2026-07-15T10:00:05.123",
    "bid": 1.0858,
    "ask": 1.0862,
    "last": 1.0860,
    "volume": 5
  },
  "timestamp": "2026-07-15T10:00:05.123Z",
  "event_id": "evt_def456"
}
```

#### `price_update`
Diringkas untuk dashboard (bid, ask, change, high, low).

```json
{
  "type": "price_update",
  "channel": "market",
  "symbol": "EURUSD",
  "data": {
    "bid": 1.0858,
    "ask": 1.0862,
    "change": 0.15,
    "high": 1.0870,
    "low": 1.0830,
    "volume": 15000
  },
  "timestamp": "2026-07-15T10:00:05.123Z",
  "event_id": "evt_ghi789"
}
```

### Signals Channel (`/ws/signals/{symbol}`)

**Event Types:**

#### `signal_generated`
Dikirim ketika sinyal trading baru dihasilkan.

```json
{
  "type": "signal_generated",
  "channel": "signals",
  "symbol": "EURUSD",
  "data": {
    "signal_id": "SIG-42",
    "timeframe": "H1",
    "signal": "BUY",
    "confidence": 75.0,
    "entry_price": 1.0860,
    "stop_loss": 1.0830,
    "take_profit": 1.0920,
    "risk_reward": 2.0,
    "risk_level": "MEDIUM",
    "trade_quality": "GOOD",
    "reasons": [
      "Market Trend: BULLISH",
      "RSI oversold bounce",
      "Bullish MACD crossover"
    ],
    "market_regime": "TRENDING",
    "final_decision": "BUY"
  },
  "timestamp": "2026-07-15T10:00:00.000Z",
  "event_id": "evt_sig_001"
}
```

#### `signal_outcome`
Dikirim ketika outcome sinyal diperbarui.

```json
{
  "type": "signal_outcome",
  "channel": "signals",
  "symbol": "EURUSD",
  "data": {
    "signal_id": "SIG-42",
    "result": "WIN",
    "profit": 50.00,
    "profit_pips": 50,
    "exit_price": 1.0910,
    "exit_time": "2026-07-15T20:00:00"
  },
  "timestamp": "2026-07-15T20:00:00.000Z",
  "event_id": "evt_out_001"
}
```

### Indicators Channel (`/ws/indicators/{symbol}`)

**Event Types:**

#### `indicator_update`
Dikirim ketika indikator diperbarui (setelah candle baru ditutup).

```json
{
  "type": "indicator_update",
  "channel": "indicators",
  "symbol": "EURUSD",
  "data": {
    "timeframe": "H1",
    "timestamp": "2026-07-15T10:00:00",
    "indicators": {
      "rsi_14": 55.2,
      "ema_12": 1.0855,
      "ema_20": 1.0845,
      "ema_50": 1.0820,
      "macd_macd": 0.0005,
      "macd_signal": 0.0003,
      "adx_adx": 28.0,
      "atr_14": 0.0020
    }
  },
  "timestamp": "2026-07-15T10:00:00.000Z",
  "event_id": "evt_ind_001"
}
```

### Account Channel (`/ws/account`)

**Event Types:**

#### `position_update`
Dikirim ketika ada perubahan posisi (open/close/modify).

```json
{
  "type": "position_update",
  "channel": "account",
  "data": {
    "position_id": "pos_001",
    "symbol": "EURUSD",
    "direction": "LONG",
    "status": "OPEN",
    "entry_price": 1.0860,
    "current_price": 1.0880,
    "stop_loss": 1.0830,
    "take_profit": 1.0920,
    "lot_size": 0.1,
    "profit": 20.00,
    "profit_pips": 20,
    "unrealized_pnl": 20.00
  },
  "timestamp": "2026-07-15T10:30:00.000Z",
  "event_id": "evt_pos_001"
}
```

#### `account_summary`
Dikirim periodik atau setelah perubahan signifikan.

```json
{
  "type": "account_summary",
  "channel": "account",
  "data": {
    "balance": 10000.00,
    "equity": 10050.00,
    "margin": 100.00,
    "free_margin": 9950.00,
    "margin_level": 10050.0,
    "open_positions": 1,
    "total_pnl": 50.00,
    "daily_pnl": 20.00,
    "daily_trades": 1
  },
  "timestamp": "2026-07-15T10:30:00.000Z",
  "event_id": "evt_acct_001"
}
```

### System Channel (`/ws/system`)

**Event Types:**

#### `notification`
Notifikasi sistem umum.

```json
{
  "type": "notification",
  "channel": "system",
  "data": {
    "level": "info",
    "title": "Data Updated",
    "message": "New OHLC data available for EURUSD",
    "category": "data"
  },
  "timestamp": "2026-07-15T10:00:00.000Z",
  "event_id": "evt_notif_001"
}
```

#### `error`
Notifikasi error.

```json
{
  "type": "error",
  "channel": "system",
  "data": {
    "code": "CONNECTOR_ERROR",
    "message": "Yahoo Finance connector failed",
    "details": "Rate limit exceeded"
  },
  "timestamp": "2026-07-15T10:00:00.000Z",
  "event_id": "evt_err_001"
}
```

#### `service_status`
Status layanan (periodic heartbeat).

```json
{
  "type": "service_status",
  "channel": "system",
  "data": {
    "services": {
      "database": "connected",
      "redis": "connected",
      "celery": "active",
      "mt5": "disconnected"
    },
    "uptime_seconds": 3600
  },
  "timestamp": "2026-07-15T10:00:00.000Z",
  "event_id": "evt_heartbeat_001"
}
```

---

## Client-Side Messages

### Subscribe

Untuk berlangganan channel tertentu, client mengirim:

```json
{
  "action": "subscribe",
  "channels": [
    "market:EURUSD",
    "signals:EURUSD",
    "account",
    "system"
  ]
}
```

### Unsubscribe

Untuk berhenti berlangganan:

```json
{
  "action": "unsubscribe",
  "channels": [
    "market:EURUSD"
  ]
}
```

### Ping/Pong

Client dapat mengirim ping untuk menjaga koneksi:

```json
{
  "action": "ping"
}
```

Response dari server:

```json
{
  "action": "pong",
  "timestamp": "2026-07-15T10:00:00.000Z"
}
```

---

## Implementasi di Dashboard (Next.js)

### Contoh Koneksi WebSocket

```typescript
class WebSocketClient {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectInterval: number = 5000;
  private subscriptions: string[] = [];

  constructor(baseUrl: string = "ws://localhost:8000") {
    this.url = baseUrl;
  }

  connect() {
    this.ws = new WebSocket(this.url);
    this.ws.onopen = () => {
      console.log("WebSocket connected");
      this.resubscribe();
    };
    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };
    this.ws.onclose = () => {
      console.log("WebSocket disconnected, reconnecting...");
      setTimeout(() => this.connect(), this.reconnectInterval);
    };
  }

  subscribe(channel: string, symbol?: string) {
    const ch = symbol ? `${channel}:${symbol}` : channel;
    this.subscriptions.push(ch);
    this.send({ action: "subscribe", channels: [ch] });
  }

  private resubscribe() {
    if (this.subscriptions.length > 0) {
      this.send({ action: "subscribe", channels: this.subscriptions });
    }
  }

  private send(message: object) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  private handleMessage(message: any) {
    switch (message.channel) {
      case "market":
        this.onMarketData?.(message);
        break;
      case "signals":
        this.onSignal?.(message);
        break;
      case "account":
        this.onAccountUpdate?.(message);
        break;
      case "system":
        this.onSystemNotification?.(message);
        break;
    }
  }

  // Callbacks
  onMarketData?: (data: any) => void;
  onSignal?: (data: any) => void;
  onAccountUpdate?: (data: any) => void;
  onSystemNotification?: (data: any) => void;

  disconnect() {
    this.ws?.close();
  }
}
```

---

## Catatan Implementasi

1. **Auto-Reconnect:** Client WebSocket harus mengimplementasikan auto-reconnect dengan exponential backoff.

2. **Heartbeat:** Server akan mengirim ping setiap 30 detik. Jika client tidak merespon dalam 3 kali heartbeat, koneksi akan ditutup.

3. **Rate Limiting:** Maksimal 100 pesan per detik per koneksi.

4. **Message Ordering:** Setiap pesan memiliki `event_id` UUID untuk memudahkan deduplication di sisi client.

5. **Backpressure:** Jika client lambat memproses pesan, server akan buffer hingga 1000 pesan sebelum memutus koneksi.

6. **Security:** Di production, WebSocket harus menggunakan WSS (WebSocket Secure) dengan autentikasi token JWT.
