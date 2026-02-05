import webview
import json

html_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        :root {
            --bg-color: #ffffff;
            --text-main: #222222;
            --text-sub: #888888;
            --accent-blue: #007AFF;
            --accent-red: #FF3B30;
            --ui-padding: 40px;
        }

        body, html {
            margin: 0; padding: 0;
            height: 100%; width: 100%;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-color);
            overflow: hidden;
            display: flex; flex-direction: column;
            user-select: none;
        }

        /* --- 紧凑模式 CSS --- */
        body.compact-mode {
            --ui-padding: 8px;
        }
        body.compact-mode #top-timer {
            position: fixed; left: 8px; bottom: 4px;
            font-size: 11px; padding: 0; color: #888;
            text-align: left; z-index: 10;
        }
        body.compact-mode #content-area {
            padding: 5px;
            justify-content: center;
            align-items: flex-start;
        }
        body.compact-mode #current-line-wrapper {
            width: 100%;
            height: 32px;
            position: relative;
            overflow: hidden; /* 关键：裁剪滚动的文字 */
            display: flex;
            align-items: center;
            background: rgba(0,0,0,0.03);
            border-radius: 4px;
        }
        body.compact-mode #current-line {
            font-size: 18px; font-weight: 500;
            margin-bottom: 0;
            padding: 0 8px;
            white-space: nowrap;
            position: absolute;
            left: 0;
            transition: transform 0.2s linear; /* 平滑滚动 */
        }
        body.compact-mode #progress-container {
            position: absolute; top: 0; left: 0;
            height: 100%; width: 100%;
            background: #eee; margin: 0;
            z-index: -1; 
            display: block !important;
        }
        body.compact-mode #progress-bar {
            background: rgba(0, 122, 255, 0.25);
        }
        body.compact-mode #next-line {
            font-size: 12px; color: #aaa;
            padding-left: 8px; margin-top: 4px;
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        }
        body.compact-mode #bottom-status { display: none; }
        body.compact-mode #compact-btn svg { transform: rotate(180deg); }

        /* --- 常规界面 --- */
        #file-gate {
            display: flex; flex-direction: column; 
            justify-content: center; align-items: center;
            height: 100%; gap: 20px;
        }

        button {
            padding: 10px 20px; font-size: 14px; cursor: pointer;
            border-radius: 6px; border: 1px solid #ddd; background: #fff;
            transition: all 0.2s; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        button:hover { background: #f5f5f5; }

        #teleprompter-view { display: none; flex-direction: column; height: 100%; position: relative; }

        #top-timer {
            text-align: center; font-size: 32px; font-weight: bold;
            padding: 20px 0 10px 0; font-variant-numeric: tabular-nums;
        }
        .timer-red { color: var(--accent-red) !important; }

        #content-area {
            flex: 1; display: flex; flex-direction: column;
            justify-content: center; align-items: center;
            padding: 0 var(--ui-padding); text-align: center;
        }

        #current-line-wrapper { width: 100%; position: relative; }

        #current-line {
            font-size: 42px; font-weight: 800; line-height: 1.3;
            margin-bottom: 20px; color: var(--text-main);
            transition: font-size 0.3s;
        }
        .paused-text { opacity: 0.5; }

        #progress-container {
            width: 100%; height: 6px; background: #eee;
            border-radius: 3px; overflow: hidden; margin-bottom: 20px;
        }
        #progress-bar {
            width: 0%; height: 100%; background: var(--accent-blue);
        }

        #next-line {
            font-size: 20px; color: var(--text-sub);
        }

        #bottom-status {
            height: 60px; display: flex; justify-content: center; align-items: center;
            background: #fafafa; border-top: 1px solid #eee;
            font-size: 14px; color: #666;
        }

        .status-ready { color: var(--accent-blue) !important; font-weight: bold; }
        .status-warn { color: var(--accent-red) !important; font-weight: bold; }

        #compact-btn {
            position: fixed; bottom: 10px; right: 10px;
            width: 32px; height: 32px; padding: 0;
            display: flex; align-items: center; justify-content: center;
            border: none; background: transparent; color: #999; z-index: 20;
        }

        #pause-overlay {
            display: none;
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: rgba(0,0,0,0.7); color: white; padding: 10px 20px;
            border-radius: 20px; font-size: 14px; z-index: 100;
        }
    </style>
</head>
<body>

    <div id="file-gate">
        <button onclick="pywebview.api.open_file()">打开题词文件 (TTML)</button>
    </div>

    <div id="teleprompter-view">
        <div id="top-timer">00:00</div>
        
        <div id="content-area">
            <div id="current-line-wrapper">
                <div id="progress-container"><div id="progress-bar"></div></div>
                <div id="current-line">准备就绪</div>
            </div>
            <div id="next-line">下一句将显示在这里</div>
        </div>

        <div id="pause-overlay">已暂停</div>

        <div id="bottom-status">
            <span id="status-text">按下空格键 3 秒以准备</span>
        </div>
    </div>
    
    <button id="compact-btn" title="切换极小模式" onclick="toggleCompactMode()">
        <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 3 21 3 21 9"></polyline><polyline points="9 21 3 21 3 15"></polyline><line x1="21" y1="3" x2="14" y2="10"></line><line x1="3" y1="21" x2="10" y2="14"></line></svg>
    </button>

    <script>
        let lines = [];
        let totalDuration = 0;
        let currentIndex = 0;
        let appState = 'IDLE'; 
        
        let startTime = 0;
        let pauseStartTime = 0;
        let totalPausedTime = 0;
        let animationId = null;
        
        let spaceKeyDownTime = null;
        let spaceTimer = null;
        let resetHoldTimer = null;
        let isCompact = false;

        function loadTTML(xmlString) {
            const parser = new DOMParser();
            const xmlDoc = parser.parseFromString(xmlString, "text/xml");
            const pTags = xmlDoc.getElementsByTagName("p");
            
            let cursor = 0;
            lines = [];
            for (let p of pTags) {
                const begin = timeToMs(p.getAttribute("begin"));
                const end = timeToMs(p.getAttribute("end"));
                const duration = end - begin;
                lines.push({
                    text: p.textContent.trim(),
                    start: cursor,
                    end: cursor + duration,
                    duration: duration
                });
                cursor += duration;
            }
            totalDuration = cursor;

            document.getElementById('file-gate').style.display = 'none';
            document.getElementById('teleprompter-view').style.display = 'flex';
            resetApp();
        }

        window.addEventListener('keydown', (e) => {
            if (e.code !== 'Space' || e.repeat) return;
            e.preventDefault();
            spaceKeyDownTime = performance.now();

            if (appState === 'READY_WAIT') {
                startReadyCountdown();
            } else if (appState === 'RUNNING' || appState === 'PAUSED') {
                updateStatus("长按 3 秒重置...", "status-warn");
                resetHoldTimer = setTimeout(() => { resetApp(); }, 3000);
            }
        });

        window.addEventListener('keyup', (e) => {
            if (e.code !== 'Space') return;
            e.preventDefault();

            const pressDuration = performance.now() - spaceKeyDownTime;
            clearTimers();

            if (appState === 'READY_WAIT') {
                updateStatus("按下空格键 3 秒以准备");
            } else if (appState === 'COUNTDOWN') {
                startPresentation();
            } else if (appState === 'RUNNING') {
                if (pressDuration < 500) pausePresentation();
                else updateStatus("演讲中...");
            } else if (appState === 'PAUSED') {
                if (pressDuration < 500) resumePresentation();
                else updateStatus("已暂停 - 按空格继续");
            }
        });

        function clearTimers() {
            if (spaceTimer) clearInterval(spaceTimer);
            if (resetHoldTimer) clearTimeout(resetHoldTimer);
            spaceTimer = null;
            resetHoldTimer = null;
        }

        function startReadyCountdown() {
            let count = 3;
            updateStatus(`保持按住…… ${count}`);
            spaceTimer = setInterval(() => {
                count--;
                if (count > 0) updateStatus(`保持按住…… ${count}`);
                else {
                    clearInterval(spaceTimer);
                    updateStatus(">>> 松开空格开始 <<<", "status-ready");
                    appState = 'COUNTDOWN';
                }
            }, 1000);
        }

        function resetApp() {
            clearTimers();
            cancelAnimationFrame(animationId);
            appState = 'READY_WAIT';
            currentIndex = 0;
            totalPausedTime = 0;
            updateUI(0);
            document.getElementById('top-timer').innerText = isCompact ? "0s" : "00:00";
            document.getElementById('top-timer').classList.remove('timer-red');
            document.getElementById('current-line').classList.remove('paused-text');
            document.getElementById('current-line').style.transform = "translateX(0px)";
            document.getElementById('pause-overlay').style.display = 'none';
            document.getElementById('progress-bar').style.width = '0%';
            updateStatus("按下空格键 3 秒以准备");
        }

        function startPresentation() {
            appState = 'RUNNING';
            startTime = performance.now();
            updateStatus("演讲中...");
            tick();
        }

        function pausePresentation() {
            appState = 'PAUSED';
            pauseStartTime = performance.now();
            cancelAnimationFrame(animationId);
            document.getElementById('current-line').classList.add('paused-text');
            document.getElementById('pause-overlay').style.display = 'block';
            updateStatus("已暂停 - 按空格继续");
        }

        function resumePresentation() {
            appState = 'RUNNING';
            totalPausedTime += (performance.now() - pauseStartTime);
            document.getElementById('current-line').classList.remove('paused-text');
            document.getElementById('pause-overlay').style.display = 'none';
            tick();
        }

        function tick() {
            if (appState !== 'RUNNING') return;
            const now = performance.now();
            const elapsed = now - startTime - totalPausedTime;
            const remaining = totalDuration - elapsed;

            if (remaining <= 0) { finish(); return; }

            const timerEl = document.getElementById('top-timer');
            timerEl.innerText = formatTime(remaining);
            if (remaining < 30000) timerEl.classList.add('timer-red');

            while (currentIndex < lines.length && elapsed >= lines[currentIndex].end) {
                currentIndex++;
            }

            if (currentIndex < lines.length) updateUI(elapsed);
            animationId = requestAnimationFrame(tick);
        }

        function updateUI(elapsed) {
            const line = lines[currentIndex];
            const nextLine = lines[currentIndex + 1];
            
            const currentEl = document.getElementById('current-line');
            const nextEl = document.getElementById('next-line');
            const barEl = document.getElementById('progress-bar');

            currentEl.innerText = line ? line.text : "演讲结束";
            nextEl.innerText = nextLine ? (isCompact ? nextLine.text : "下一句：" + nextLine.text) : " ";

            if (line) {
                const lineElapsed = elapsed - line.start;
                const progress = Math.max(0, Math.min((lineElapsed / line.duration) * 100, 100));
                barEl.style.width = progress + "%";

                // 极小化模式下的滚动逻辑
                if (isCompact) {
                    const containerWidth = currentEl.parentElement.offsetWidth;
                    const textWidth = currentEl.scrollWidth;
                    
                    if (textWidth > containerWidth - 16) { // 减去padding
                        // 进度超过 50% 时开始滚动
                        if (progress > 50) {
                            const scrollFactor = (progress - 50) / 45; // 在 50% 到 95% 进度期间滚完
                            const maxScroll = textWidth - containerWidth + 16;
                            const offset = Math.min(maxScroll, scrollFactor * maxScroll);
                            currentEl.style.transform = `translateX(-${offset}px)`;
                        } else {
                            currentEl.style.transform = "translateX(0px)";
                        }
                    } else {
                        currentEl.style.transform = "translateX(0px)";
                    }
                } else {
                    currentEl.style.transform = "none";
                }
            }
        }

        function finish() {
            appState = 'IDLE';
            document.getElementById('top-timer').innerText = "DONE";
            document.getElementById('current-line').innerText = "演讲结束";
            document.getElementById('progress-bar').style.width = "100%";
            updateStatus("按空格键重置");
        }

        function toggleCompactMode() {
            isCompact = !isCompact;
            document.body.classList.toggle('compact-mode');
            pywebview.api.toggle_compact_window(isCompact);
            // 切换后立即重置偏移量
            document.getElementById('current-line').style.transform = "translateX(0px)";
        }

        function timeToMs(timeStr) {
            if (!timeStr) return 0;
            const parts = timeStr.split(':');
            let sec = 0;
            if (parts.length === 3) sec = (+parts[0]) * 3600 + (+parts[1]) * 60 + (+parts[2]);
            else sec = (+parts[0]) * 60 + (+parts[1]);
            return sec * 1000;
        }

        function formatTime(ms) {
            const totalSec = Math.ceil(ms / 1000);
            if (isCompact) return totalSec + "s";
            const m = Math.floor(totalSec / 60);
            const s = totalSec % 60;
            return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
        }

        function updateStatus(text, className = "") {
            const el = document.getElementById('status-text');
            if(el) { el.innerText = text; el.className = className; }
        }
    </script>
</body>
</html>
"""

class Api:
    def open_file(self):
        file_types = ('TTML files (*.ttml)', 'All files (*.*)')
        result = window.create_file_dialog(webview.OPEN_DIALOG, allow_multiple=False, file_types=file_types)
        
        if result:
            file_path = result[0]
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                window.evaluate_js(f"loadTTML({json.dumps(content)})")

    def toggle_compact_window(self, is_compact):
        if is_compact:
            window.resize(230, 120)
        else:
            window.resize(1000, 600)

if __name__ == '__main__':
    api = Api()
    window = webview.create_window(
        'SpeechNote', 
        html=html_content, 
        js_api=api,
        width=1000, height=600,
        min_size=(230, 120)
    )
    webview.start()