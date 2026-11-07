"use client";
import { kvGet, kvSet, registerKvMigration } from "./kv-db";
// Existing key preserved so users do not lose screen-chat settings after migration.
const SCREEN_CHAT_KEY = "ai_phone_reality_bridge_screen_chat_v1";
registerKvMigration(SCREEN_CHAT_KEY);
export type ScreenChatSettings = {
  enabled: boolean;
  /** 弹窗里回话的角色 */
  characterId: string;
};

const DEFAULT_SCREEN_CHAT: ScreenChatSettings = { enabled: false, characterId: "" };
const SCREEN_CHAT_ACK_PREFIX = "screen_chat_ack_v1:";

export function loadScreenChatSettings(): ScreenChatSettings {
  try {
    const raw = kvGet(SCREEN_CHAT_KEY);
    if (!raw) return { ...DEFAULT_SCREEN_CHAT };
    const parsed = JSON.parse(raw) as Partial<ScreenChatSettings>;
    return {
      enabled: parsed.enabled === true,
      characterId: typeof parsed.characterId === "string" ? parsed.characterId : "",
    };
  } catch {
    return { ...DEFAULT_SCREEN_CHAT };
  }
}

/** 最近已经完整合并进小手机聊天记录的云端屏幕速聊轮次。 */
export function loadScreenChatAck(characterId: string): number {
  const value = Number(kvGet(`${SCREEN_CHAT_ACK_PREFIX}${characterId}`));
  return Number.isSafeInteger(value) && value > 0 ? value : 0;
}

export function saveScreenChatAck(characterId: string, sequence: number): void {
  if (!characterId || !Number.isSafeInteger(sequence) || sequence <= loadScreenChatAck(characterId)) return;
  kvSet(`${SCREEN_CHAT_ACK_PREFIX}${characterId}`, String(sequence));
  if (typeof window !== "undefined") {
    // 立即重传带确认序号的新快照；下一次云端请求便会裁掉已回端的增量，避免上下文重复。
    window.dispatchEvent(new CustomEvent("screen-chat-settings-updated"));
  }
}

export function saveScreenChatSettings(settings: ScreenChatSettings): void {
  kvSet(SCREEN_CHAT_KEY, JSON.stringify(settings));
  // 快照走离线联动同一条同步链路：设置变了通知同步器重传
  if (typeof window !== "undefined") {
    window.dispatchEvent(new CustomEvent("screen-chat-settings-updated"));
  }
}

