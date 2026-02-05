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
            overflow: hidden;
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
            transition: transform 0.2s linear;
            z-index: 2;
        }
        body.compact-mode #progress-container {
            position: absolute; top: 0; left: 0;
            height: 100%; width: 100%;
            background: #eee;
            z-index: 1;
            display: block !important;
        }
        body.compact-mode #progress-bar {
            background: rgba(0, 122, 255, 0.25);
            height: 100%;
        }
        body.compact-mode #next-line {
            font-size: 12px; color: #555;
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

        #top-timer-container {
            padding: 20px 0;
            text-align: center;
            min-height: 80px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            border-bottom: 1px solid #eee;
        }

        body.compact-mode #top-timer-container {
            min-height: auto;
            padding: 0;
            border-bottom: none;
        }

        #top-timer {
            font-size: 32px; font-weight: bold;
            font-variant-numeric: tabular-nums;
        }
        .timer-red { color: var(--accent-red) !important; }

        #adjust-controls {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 20px;
            margin-top: 10px;
        }

        .adjust-btn {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            border: 2px solid var(--accent-blue);
            background: white;
            color: var(--accent-blue);
            font-size: 20px;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
        }

        .adjust-btn:hover {
            background: var(--accent-blue);
            color: white;
        }

        #adjusted-total-time {
            font-size: 14px;
            color: var(--text-main);
            font-weight: 500;
        }

        #speed-controls {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 15px;
            margin-top: 15px;
        }

        .speed-btn {
            padding: 8px 16px;
            border: 1px solid #ddd;
            border-radius: 20px;
            background: white;
            cursor: pointer;
        }

        .speed-btn.active {
            background: var(--accent-blue);
            color: white;
            border-color: var(--accent-blue);
        }

        #speed-value {
            font-size: 16px;
            color: var(--text-main);
            font-weight: 500;
        }

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

        .hide {
            display: none !important;
        }
    </style>
</head>
<body>

    <div id="file-gate">
        <button onclick="pywebview.api.open_file()">-> TTML...</button>
    </div>

    <div id="teleprompter-view">
        <div id="top-timer-container">
            <div id="top-timer">00:00</div>
            
            <div id="adjust-controls" class="hide">
                <div class="adjust-btn" onclick="adjustTime(-1000)">-</div>
                <div id="adjusted-total-time">00:00</div>
                <div class="adjust-btn" onclick="adjustTime(1000)">+</div>
            </div>
            
            <div id="speed-controls" class="hide">
                <div class="speed-btn" onclick="setSpeed(0.8)">0.8×</div>
                <div class="speed-btn active" onclick="setSpeed(1.0)">1.0×</div>
                <div class="speed-btn" onclick="setSpeed(1.2)">1.2×</div>
                <div class="speed-btn" onclick="setSpeed(1.5)">1.5×</div>
                <div id="speed-value">1.0×</div>
            </div>
        </div>
        
        <div id="content-area">
            <div id="current-line-wrapper">
                <div id="progress-container"><div id="progress-bar"></div></div>
                <div id="current-line">准备就绪</div>
            </div>
            <div id="next-line">↘</div>
        </div>

        <div id="pause-overlay">⏸</div>

        <div id="bottom-status">
            <span id="status-text">[Space] 3s</span>
        </div>
    </div>
    
    <button id="compact-btn" title="切换极小模式" onclick="toggleCompactMode()">
        <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 3 21 3 21 9"></polyline><polyline points="9 21 3 21 3 15"></polyline><line x1="21" y1="3" x2="14" y2="10"></line><line x1="3" y1="21" x2="10" y2="14"></line></svg>
    </button>

    <script>
        let lines = [];
        let originalTotalDuration = 0;
        let adjustedTotalDuration = 0;
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
        
        let playbackRate = 1.0;
        let adjustedLines = [];

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
            originalTotalDuration = cursor;
            adjustedTotalDuration = originalTotalDuration;
            
            // 计算调整后的时间线
            updateAdjustedLines();
            
            document.getElementById('file-gate').style.display = 'none';
            document.getElementById('teleprompter-view').style.display = 'flex';
            resetApp();
        }

        function updateAdjustedLines() {
            adjustedLines = lines.map(line => ({
                text: line.text,
                start: line.start / playbackRate,
                end: line.end / playbackRate,
                duration: line.duration / playbackRate
            }));
            adjustedTotalDuration = originalTotalDuration / playbackRate;
            
            // 更新显示
            document.getElementById('adjusted-total-time').innerText = formatTime(adjustedTotalDuration);
            document.getElementById('speed-value').innerText = playbackRate.toFixed(1) + '×';
            
            // 更新按钮状态
            document.querySelectorAll('.speed-btn').forEach(btn => {
                btn.classList.remove('active');
                const btnSpeed = parseFloat(btn.textContent);
                if (btnSpeed === playbackRate || (btn.textContent.includes('×') && Math.abs(btnSpeed - playbackRate) < 0.01)) {
                    btn.classList.add('active');
                }
            });
        }

        function adjustTime(ms) {
            adjustedTotalDuration = Math.max(1000, adjustedTotalDuration + ms);
            playbackRate = originalTotalDuration / adjustedTotalDuration;
            updateAdjustedLines();
        }

        function setSpeed(rate) {
            playbackRate = rate;
            updateAdjustedLines();
        }

        window.addEventListener('keydown', (e) => {
            if (e.code !== 'Space' || e.repeat) return;
            e.preventDefault();
            spaceKeyDownTime = performance.now();

            if (appState === 'READY_WAIT' || appState === 'IDLE') {
                startReadyCountdown();
            } else if (appState === 'RUNNING' || appState === 'PAUSED') {
                updateStatus("⏹ 3s", "status-warn");
                resetHoldTimer = setTimeout(() => { resetApp(); }, 3000);
            }
        });

        window.addEventListener('keyup', (e) => {
            if (e.code !== 'Space') return;
            e.preventDefault();

            const pressDuration = performance.now() - spaceKeyDownTime;
            clearTimers();

            if (appState === 'READY_WAIT' || appState === 'IDLE') {
                updateStatus("[Space] 3s");
            } else if (appState === 'COUNTDOWN') {
                startPresentation();
            } else if (appState === 'RUNNING') {
                if (pressDuration < 500) pausePresentation();
                else updateStatus("▶");
            } else if (appState === 'PAUSED') {
                if (pressDuration < 500) resumePresentation();
                else updateStatus("⏸ [Space]");
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
            updateStatus(`[Space] ${count}`);
            spaceTimer = setInterval(() => {
                count--;
                if (count > 0) updateStatus(`[Space] ${count}`);
                else {
                    clearInterval(spaceTimer);
                    updateStatus("▶", "status-ready");
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
            playbackRate = 1.0;
            adjustedTotalDuration = originalTotalDuration;
            
            // 显示调整控件
            document.getElementById('adjust-controls').classList.remove('hide');
            document.getElementById('speed-controls').classList.remove('hide');
            document.getElementById('top-timer').innerText = formatTime(adjustedTotalDuration);
            
            // 重新计算调整线
            updateAdjustedLines();
            
            // 更新UI显示第一行
            updateUIForReadyState();
            
            document.getElementById('top-timer').classList.remove('timer-red');
            document.getElementById('current-line').classList.remove('paused-text');
            document.getElementById('current-line').style.transform = "translateX(0px)";
            document.getElementById('pause-overlay').style.display = 'none';
            document.getElementById('progress-bar').style.width = '0%';
            updateStatus("[Space] 3s");
        }

        function updateUIForReadyState() {
            if (adjustedLines.length > 0) {
                document.getElementById('current-line').innerText = adjustedLines[0].text;
                if (adjustedLines.length > 1) {
                    document.getElementById('next-line').innerText = adjustedLines[1].text;
                } else {
                    document.getElementById('next-line').innerText = "";
                }
            } else {
                document.getElementById('current-line').innerText = "准备就绪";
                document.getElementById('next-line').innerText = "";
            }
        }

        function startPresentation() {
            appState = 'RUNNING';
            startTime = performance.now();
            updateStatus("▶");
            
            // 隐藏调整控件
            document.getElementById('adjust-controls').classList.add('hide');
            document.getElementById('speed-controls').classList.add('hide');
            tick();
        }

        function pausePresentation() {
            appState = 'PAUSED';
            pauseStartTime = performance.now();
            cancelAnimationFrame(animationId);
            document.getElementById('current-line').classList.add('paused-text');
            document.getElementById('pause-overlay').style.display = 'block';
            updateStatus("⏸ [Space]");
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
            const remaining = adjustedTotalDuration - elapsed;

            if (remaining <= 0) { finish(); return; }

            const timerEl = document.getElementById('top-timer');
            timerEl.innerText = formatTime(remaining);
            if (remaining < 30000) timerEl.classList.add('timer-red');

            while (currentIndex < adjustedLines.length && elapsed >= adjustedLines[currentIndex].end) {
                currentIndex++;
            }

            if (currentIndex < adjustedLines.length) updateUI(elapsed);
            animationId = requestAnimationFrame(tick);
        }

        function updateUI(elapsed) {
            const line = adjustedLines[currentIndex];
            const nextLine = adjustedLines[currentIndex + 1];
            
            const currentEl = document.getElementById('current-line');
            const nextEl = document.getElementById('next-line');
            const barEl = document.getElementById('progress-bar');

            currentEl.innerText = line ? line.text : "✓";
            nextEl.innerText = nextLine ? nextLine.text : "";

            if (line) {
                const lineElapsed = elapsed - line.start;
                const progress = Math.max(0, Math.min((lineElapsed / line.duration) * 100, 100));
                barEl.style.width = progress + "%";

                // 极小化模式下的滚动逻辑
                if (isCompact) {
                    const containerWidth = currentEl.parentElement.offsetWidth;
                    const textWidth = currentEl.scrollWidth;
                    
                    if (textWidth > containerWidth - 16) {
                        if (progress > 20) {
                            const scrollFactor = (progress - 20) / 80;
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
            document.getElementById('top-timer').innerText = "✓";
            document.getElementById('current-line').innerText = "✓";
            document.getElementById('next-line').innerText = "";
            document.getElementById('progress-bar').style.width = "100%";
            updateStatus("[Space]");
        }

        function toggleCompactMode() {
            isCompact = !isCompact;
            document.body.classList.toggle('compact-mode');
            pywebview.api.toggle_compact_window(isCompact);
            document.getElementById('current-line').style.transform = "translateX(0px)";
            
            // 极小模式下隐藏顶部控件面板
            if (isCompact) {
                document.getElementById('adjust-controls').classList.add('hide');
                document.getElementById('speed-controls').classList.add('hide');
            }
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
