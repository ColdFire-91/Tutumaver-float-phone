"use client";
import { buildChatPromptMessages } from "./chat-engine";
import { buildProviderRequest, toLlmRequestMessages } from "./llm-provider-adapter";
import { CHAT_MESSAGES_DELETED_EVENT, CHAT_MESSAGE_PUSHED_EVENT, createOrGetSession, addChatContact, loadChatContacts, loadChatMessages, type ChatMessage } from "./chat-storage";
import { loadCharacters } from "./character-storage";
import { kvGet, kvSet } from "./kv-db";
import { SCREEN_CHAT_SENTINEL, SCREEN_CHAT_SNAPSHOT_ID } from "./screen-chat-shared";
import { isPersonalPushCloudActive, isPersonalScreenChatCloudReady, personalPushFetch } from "./personal-push-cloud";
import { loadScreenChatSettings, loadScreenChatAck } from "./screen-chat-storage";

const SYNC_KEY = "tutuma_screen_chat_sync_v1";
let syncing = false;
let timer: number | null = null;
function ensureSessionFor(characterId: string) {
  if (!loadChatContacts().some(c => c.characterId === characterId)) addChatContact(characterId);
  return createOrGetSession(characterId);
}
async function buildScreenChatSnapshot(): Promise<Record<string, unknown> | null> {
    const screen = loadScreenChatSettings();
    if (!screen.enabled || !screen.characterId) return null;
    try {
        const session = ensureSessionFor(screen.characterId);
        const history = loadChatMessages(session.id);
        const synthetic: ChatMessage = {
            id: "_screen_chat_sentinel",
            sessionId: session.id,
            role: "user",
            content: SCREEN_CHAT_SENTINEL,
            status: "sent",
            createdAt: new Date().toISOString(),
        };
        const { llmMessages, character, config, preset, regexes, userIdentity } = await buildChatPromptMessages(
            session,
            [...history, synthetic],
            { appTags: ["chat", "text"] },
        );
        const request = buildProviderRequest(config, preset, toLlmRequestMessages(llmMessages));
        return {
            replyRequest: {
                url: request.url,
                headers: request.headers,
                body: request.body,
                providerKind: request.providerKind,
            },
            // 图像识别开关跟随该角色绑定的 API 配置：开 = 服务端注入截图，关 = 代入 OCR 文字
            enableVision: config.enableImageRecognition === true,
            // 每日上限已取消。新函数不读这个字段；还没重新部署的旧函数会把它钳到 500——
            // 传 500 让老部署立刻从默认 120 提到它能达到的最大值，重新部署后彻底无限
            dailyCap: 500,
            // 云端只保留尚未回端的增量；已合并轮次由该水位裁掉，避免和完整本地历史重复。
            ackSequence: loadScreenChatAck(screen.characterId),
            chat: { characterId: screen.characterId, sessionId: session.id, characterName: character.name },
            reply: {
                sessionId: session.id,
                regexes,
                characterName: character.name,
                userName: userIdentity?.name ?? "用户",
                appId: "chat",
                appTags: ["chat", "text"],
            },
        };
    } catch (err) {
        console.warn("[ScreenChatSync] screen chat snapshot build failed", err);
        return null;
    }
}


async function runSync(): Promise<void> {
  if (syncing || typeof window === "undefined") return;
  if (!isPersonalPushCloudActive() || !isPersonalScreenChatCloudReady()) return;
  syncing = true;
  try {
    const screen = loadScreenChatSettings();
    const snapshot = await buildScreenChatSnapshot();
    const snapshots = snapshot ? [{ruleId:SCREEN_CHAT_SNAPSHOT_ID,payload:snapshot}] : [];
    const deleteRuleIds = snapshot ? [] : [SCREEN_CHAT_SNAPSHOT_ID];
    const serialized = JSON.stringify({snapshots,deleteRuleIds});
    if (kvGet(SYNC_KEY) === serialized) return;
    // Personal cloud's screen-chat still uses the existing bridge-sync action for snapshots.
    // We intentionally send no bridge rules or real-world shortcut actions.
    const response = await personalPushFetch("bridge-sync", {method:"POST",body:serialized}).catch(()=>null);
    if (response?.ok) kvSet(SYNC_KEY,serialized);
  } catch(e) {console.warn("[ScreenChatSync]",e)} finally {syncing=false;}
}
function scheduleSync(ms:number) {
  if(timer!==null) window.clearTimeout(timer);
  timer=window.setTimeout(()=>{timer=null;void runSync()},ms);
}
export function installScreenChatSync():void {
  if(typeof window==="undefined")return;
  window.addEventListener("screen-chat-settings-updated",()=>scheduleSync(3000));
  window.addEventListener(CHAT_MESSAGE_PUSHED_EVENT,()=>scheduleSync(3000));
  window.addEventListener(CHAT_MESSAGES_DELETED_EVENT,()=>scheduleSync(3000));
  window.addEventListener("chat-messages-updated",()=>scheduleSync(3000));
  document.addEventListener("visibilitychange",()=>{if(document.hidden)void runSync()});
  scheduleSync(15000);
}
