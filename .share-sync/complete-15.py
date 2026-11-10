from pathlib import Path
import re,json
def read(p):return Path(p).read_text()
def save(p,s):Path(p).write_text(s)
def rep(p,old,new,count=1):
 s=read(p)
 assert s.count(old)>=count, f"missing target {p}: {old[:110]}"
 save(p,s.replace(old,new,count))
def append(p,t):save(p,read(p).rstrip()+"\n\n"+t.strip()+"\n")
motion="lib/photo-deck-motion.ts"
rep(motion,"const center = (active - (count - 1) / 2) * 13;","const center = active === 0 ? -3 : active === count - 1 ? 3 : 0;")
rep(motion,"x += side * (distance === 1 ? 24 : 41);","x += side * (distance === 1 ? 7 : 12);")
rep(motion,"rotation = side * (distance === 1 ? 2.3 : 4);","rotation = side * (distance === 1 ? 1.15 : 1.85);")
rep(motion,"scale -= distance * .024;","scale -= Math.min(distance, 2) * .015;")
tick=chr(96); dollar=chr(36)
rep("components/chat/message-bubble.tsx",'if (expanded) return <div className="chat-photo-deck-expanded" onClick={event => event.stopPropagation()}>','if (expanded) return <div className={'+tick+'chat-photo-deck-expanded '+dollar+'{mine ? "chat-photo-deck-expanded--mine" : "chat-photo-deck-expanded--artist"}'+tick+'} onClick={event => event.stopPropagation()}>')
rep("components/lysn/lysn-app.tsx",'if (expanded) return <div className={styles.photoExpanded}>','if (expanded) return <div className={'+tick+dollar+'{styles.photoExpanded} '+dollar+'{mine ? "lysn-photo-expanded--mine" : "lysn-photo-expanded--artist"}'+tick+'}>')
append("styles/chat.css", """
/* Shared from verified resource 038 (photo shuffle and expansion). */
.chat-photo-deck{gap:7px;max-width:100%;min-width:0;padding:4px 2px;box-sizing:border-box}
.chat-photo-deck-stack{flex:0 0 min(44vw,180px);width:min(44vw,180px);height:min(56vw,228px);min-width:0}
.chat-photo-deck-card{top:8px;left:15px;width:calc(100% - 38px);height:calc(100% - 18px);border-radius:15px}
.chat-photo-deck-controls{flex:0 0 auto;min-width:0}
.chat-photo-deck-toggle{padding:6px 9px;background:#ebecef;color:#555b66}
.chat-photo-deck-expanded{width:fit-content;max-width:min(74vw,250px)}
.chat-photo-deck-grid{display:flex;flex-direction:column;width:fit-content;max-width:100%;gap:8px}
.chat-photo-deck-item{display:block;width:fit-content;max-width:100%;height:auto;overflow:visible;background:transparent;border-radius:15px;flex:none;align-self:inherit}
.chat-photo-deck-item .chat-photo-card{display:block;width:fit-content;max-width:100%;height:auto;min-width:0;margin:0;border-radius:15px;overflow:hidden}
.chat-photo-deck-item .chat-photo-card-image,.chat-photo-deck-item .chat-photo-card--image .chat-photo-card-image{display:block;width:auto;height:auto;max-width:min(74vw,250px);max-height:320px;object-fit:contain}
.chat-photo-deck-item .chat-generated-image-retry-stack{width:fit-content;max-width:100%;height:auto}
.chat-photo-deck-item .chat-photo-card--text{width:min(180px,68vw);height:240px}
.chat-photo-deck-expanded--mine .chat-photo-deck-grid{align-items:flex-end}
.chat-photo-deck-expanded--artist .chat-photo-deck-grid{align-items:flex-start}
.chat-photo-deck-expanded--mine>.chat-photo-deck-toggle{align-self:flex-end}
.chat-photo-deck-expanded--artist>.chat-photo-deck-toggle{align-self:flex-start}
.chat-photo-deck-card .chat-photo-card-image,.chat-photo-deck-card .chat-photo-card--image .chat-photo-card-image{object-fit:cover!important;object-position:50% 50%!important}
.chat-photo-deck--mine{flex-direction:row-reverse}
.chat-photo-deck:not(.chat-photo-deck--mine){flex-direction:row}
""")
append("components/lysn/lysn-app.module.css", """
/* Resource 038 Lysn compact cards, original photo ratios, sender avatar alignment */
.stackWrap{gap:7px;max-width:100%;min-width:0;box-sizing:border-box}
.photoDeck{flex:0 0 min(44vw,180px);width:min(44vw,180px);height:min(56vw,228px);min-width:0}
.photoDeck .photoCard{top:8px;left:15px;width:calc(100% - 38px);height:calc(100% - 18px);border-radius:15px}
.photoDeckControls{flex:0 0 auto;min-width:0}
.photoExpanded{width:fit-content;max-width:min(74vw,250px)}
.photoExpandedGrid{display:flex;flex-direction:column;width:fit-content;max-width:100%;gap:8px}
.photoExpandedGrid button{display:block;flex:none;width:fit-content;max-width:100%;height:auto;aspect-ratio:auto;padding:0;overflow:hidden;background:transparent;border:0;border-radius:15px}
.photoExpandedGrid img,.photoExpandedGrid .fallback{display:block;width:auto;max-width:min(74vw,250px);height:auto;max-height:320px;object-fit:contain;border-radius:15px}
.photoExpandedGrid .photoTextCard{width:min(180px,68vw);height:240px}
.photoExpanded>.photoViewAll{width:auto;min-width:96px}
.photoExpanded:global(.lysn-photo-expanded--mine){align-items:flex-end}
.photoExpanded:global(.lysn-photo-expanded--artist){align-items:flex-start}
:global(.lysn-photo-expanded--mine) .photoExpandedGrid{align-items:flex-end}
:global(.lysn-photo-expanded--artist) .photoExpandedGrid{align-items:flex-start}
:global(.lysn-photo-expanded--mine) .photoExpandedGrid>button{align-self:flex-end}
:global(.lysn-photo-expanded--artist) .photoExpandedGrid>button{align-self:flex-start}
.photoDeck .photoCard img{object-fit:cover!important;object-position:50% 50%!important}
.stackWrap.stackMine{flex-direction:row-reverse}
.stackWrap:not(.stackMine){flex-direction:row}
""")
# Existing 1.4 media intent choices preserved, only add delivery controls.
p="lib/media-preferences.ts";s=read(p)
rep(p,'export type MediaPreference = "text" | "balanced" | "free";','export type MediaPreference = "text" | "balanced" | "free";\nexport type PhotoDeliveryMode = "text" | "auto";')
rep(p,'export type MediaPreferences = { global: MediaPreference; apps: Partial<Record<MediaApp, MediaPreference>> };','export type MediaPreferences = { global: MediaPreference; apps: Partial<Record<MediaApp, MediaPreference>>; delivery: Partial<Record<MediaApp, PhotoDeliveryMode>> };')
anchor='const KEY = "ai_phone_media_preferences_v1";'
rep(p,anchor,'''export const DEFAULT_PHOTO_DELIVERY: Record<MediaApp, PhotoDeliveryMode> = { chat: "text", lysn: "text", moments: "auto", twitter: "auto", weverse: "auto" };
export function effectivePhotoDelivery(appId: string): PhotoDeliveryMode {
  if (!(appId in DEFAULT_PHOTO_DELIVERY)) return "text";
  const value = loadMediaPreferences().delivery[appId as MediaApp];
  return value === "text" || value === "auto" ? value : DEFAULT_PHOTO_DELIVERY[appId as MediaApp];
}
'''+anchor)
rep(p,'apps: Object.fromEntries(Object.entries(value.apps || {}).filter(([key, mode]) => key in MEDIA_APPS && valid(mode)))','apps: Object.fromEntries(Object.entries(value.apps || {}).filter(([key, mode]) => key in MEDIA_APPS && valid(mode))), delivery: Object.fromEntries(Object.entries(value.delivery || {}).filter(([key, mode]) => key in MEDIA_APPS && (mode === "text" || mode === "auto")))')
rep(p,'catch { return { global: "text", apps: {} }; }','catch { return { global: "text", apps: {}, delivery: {} }; }')
# Share edition restores the screen-effects UI, explicitly OFF by default.
p="lib/chat-screen-effects.ts"
rep(p,'const BUILTIN_SETTINGS_KEY = "chat-screen-effect-builtins";','const BUILTIN_SETTINGS_KEY = "chat-screen-effect-builtins";\nconst TOTAL_EFFECTS_KEY = "chat-screen-effects-master-enabled-v1";\nexport function screenEffectsEnabled(): boolean { try { return kvGet(TOTAL_EFFECTS_KEY) === "true"; } catch { return false; } }\nexport function setScreenEffectsEnabled(value: boolean): void { kvSet(TOTAL_EFFECTS_KEY, String(value)); notifyRulesUpdated(); }')
rep(p,'export function isDiceOnlyMessage(text: string): boolean {\n','export function isDiceOnlyMessage(text: string): boolean {\n    if (!screenEffectsEnabled()) return false;\n')
start=read(p).index('/** 注入聊天提示词的特效说明')
end=read(p).index('function keywordHit(',start)
prompt='''/** The master switch controls BOTH render and AI prompt injection. */
export function buildScreenEffectPromptHint(): string {
    if (!screenEffectsEnabled()) return "";
    try {
        const selected = BUILTIN_SCREEN_EFFECTS.filter(effect => loadBuiltinScreenEffectSettings()[effect.type].enabled);
        const enabledRules = loadChatScreenEffectRules().filter(rule => rule.enabled && rule.keyword.trim());
        if (!selected.length && !enabledRules.length) return "";
        const names = selected.map(effect => effect.name + "「" + effect.icon + "」").join("、");
        const dice = selected.some(effect => effect.type === "dice");
        return "\\n\\n### 聊天室全屏特效\\n"
            + (selected.length ? "仅以下已启用的特效可用（单独发送图标触发）："+names+"。图标夹在普通文字中不会触发。\\n" : "")
            + (enabledRules.length ? "已启用的表情雨触发词：" + enabledRules.map(rule => rule.keyword).join("、") + "。\\n" : "")
            + (dice ? "掷骰点数由系统生成并公布，请以实际结果回应，不要编造。\\n" : "");
    } catch { return ""; }
}

'''
save(p,read(p)[:start]+prompt+read(p)[end:])
rep(p,'export function matchChatScreenEffectRule(text: string): ChatScreenEffectMatch | null {\n','export function matchChatScreenEffectRule(text: string): ChatScreenEffectMatch | null {\n    if (!screenEffectsEnabled()) return null;\n')
p="components/chat/emoji-panel.tsx"
rep(p,'import { BUILTIN_SCREEN_EFFECTS, loadBuiltinScreenEffectSettings }','import { BUILTIN_SCREEN_EFFECTS, loadBuiltinScreenEffectSettings, screenEffectsEnabled }')
rep(p,'const showEffectTab = false;','const showEffectTab = Boolean(onEffectSend) && screenEffectsEnabled() && enabledEffects.length > 0;')
p="components/chat/screen-effect-settings-modal.tsx"
rep(p,'import { useState } from "react";','import { useState } from "react";')
rep(p,'    BUILTIN_SCREEN_EFFECTS,','    BUILTIN_SCREEN_EFFECTS,\n    screenEffectsEnabled, setScreenEffectsEnabled,')
rep(p,'    const [tab, setTab] = useState<"rain" | "builtin">("rain");','    const [tab, setTab] = useState<"rain" | "builtin">("rain");\n    const [masterEnabled, setMasterEnabled] = useState(() => screenEffectsEnabled());')
rep(p,'                <div className="screen-fx-tabs" role="tablist">','                <div className="screen-fx-card screen-fx-master" style={{display:"flex",alignItems:"center",justifyContent:"space-between",padding:12,marginBottom:10}}><div><strong>启用全屏特效</strong><p className="screen-fx-note" style={{margin:0}}>关闭时动画停用，AI提示词也不注入</p></div><Toggle checked={masterEnabled} onChange={value=>{ setMasterEnabled(value); setScreenEffectsEnabled(value); }} /></div>\n                <div className="screen-fx-tabs" role="tablist">')
rep(p,'onClick={() => playPreview("emoji_rain", rule.emojis)}','onClick={() => { if(masterEnabled) playPreview("emoji_rain", rule.emojis); }}')
rep(p,'onClick={() => playPreview(effect.type, "")}','onClick={() => { if(masterEnabled) playPreview(effect.type, ""); }}')
p="components/chat/chat-settings-panel.tsx"
rep(p,'            {/* Modal: Screen Effects */}','            {/* Modal: Screen Effects */}')
# Ensure a visible settings entry, not just the formerly orphaned modal.
rep(p,'                {/* Backgrounds & UI */}','''                <div className="menu-group">
                    <button type="button" className="menu-item" onClick={() => setShowScreenEffects(true)}>
                        <div className="menu-label-group"><span className="menu-label">全屏特效</span><span className="menu-desc">总开关、表情雨及内置特效；关闭后不会注入AI提示词</span></div>
                        <div className="menu-right"><ChevronRight size={16} /></div>
                    </button>
                </div>

                {/* Backgrounds & UI */}''')
# Share version must not disclose private internal project details or reintroduce excluded apps.
p="package.json"
data=json.loads(read(p));data["version"]="1.5.0";save(p,json.dumps(data,ensure_ascii=False,indent=2)+"\n")
p="package-lock.json";data=json.loads(read(p));data["version"]="1.5.0";data["packages"][""]["version"]="1.5.0";save(p,json.dumps(data,ensure_ascii=False,indent=2)+"\n")
p="README.md";s=read(p).replace("Tutuma Float Phone 1.4","Tutuma Float Phone 1.5",1);save(p,s)
Path("docs/1.5更新说明.md").write_text("# Tutuma 1.5 更新\n\n- Chat、LYSN 叠图更新：轻微倾角、洗牌切换、居中裁切与按头像侧对齐，展开图片保持原始比例。\n- 单张照片及实况消息样式优化。\n- 配图策略区分文字图与自动生图；泡泡消息更符合面向大量订阅者的交流。\n- 相册保存、截图提示、电话与短信设置样式完善。\n- 全屏特效入口重新开放，新增默认关闭的总开关；关闭时既不触发动画，也不注入AI提示词。\n\n保留原有分享版功能取舍，不新增浏览器、YouTube或幕后应用；本版不修改跨平台事件流或美化图标。\n")
# Source-only guards and validation
assert "buildScreenEffectPromptHint()" in read("lib/chat-engine.ts")
assert "buildScreenEffectPromptHint()" in read("lib/group-chat-engine.ts")
assert "chat-photo-deck-expanded--mine" in read("components/chat/message-bubble.tsx")
assert "lysn-photo-expanded--mine" in read("components/lysn/lysn-app.tsx")
print("1.5 selected modules merged and content verified.")
