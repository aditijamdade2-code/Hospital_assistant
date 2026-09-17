export type WebSocketCallback = (event: string, data: any) => void;

export class StaffWebSocketClient {
  private ws: WebSocket | null = null;
  private url: string;
  private listeners: WebSocketCallback[] = [];
  private reconnectTimer: any = null;
  private isConnected = false;

  constructor(url?: string) {
    this.url = url || (process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/api/v1/ws/staff');
  }

  public connect(): void {
    if (typeof window === 'undefined') return;
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        this.isConnected = true;
        this.notifyListeners('STATUS', { connected: true });
      };

      this.ws.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          this.notifyListeners(parsed.event, parsed.data);
        } catch (e) {
          // Ignored non-JSON messages
        }
      };

      this.ws.onclose = () => {
        this.isConnected = false;
        this.notifyListeners('STATUS', { connected: false });
        this.scheduleReconnect();
      };

      this.ws.onerror = () => {
        this.isConnected = false;
        if (this.ws) this.ws.close();
      };
    } catch (e) {
      this.scheduleReconnect();
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, 3000);
  }

  public subscribe(callback: WebSocketCallback): () => void {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter(l => l !== callback);
    };
  }

  private notifyListeners(event: string, data: any): void {
    this.listeners.forEach(listener => {
      try {
        listener(event, data);
      } catch (e) {
        console.error('Error in WS listener:', e);
      }
    });
  }

  public disconnect(): void {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export const staffWsClient = new StaffWebSocketClient();
