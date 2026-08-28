import os

file_path = 'templates/index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# fetch 에러 시 fallback 처리 추가
fallback_js = """
      } catch (err) {
        // 정적 페이지 (GitHub Pages) 폴백 모드
        userInfo = { credits: '∞', max_credits: '∞', name: '모기에그 크리에이터', tier: 'Static Mode' };
        updateUserUI();
      }
"""
content = content.replace("console.error('Failed to fetch user info:', err);", "userInfo = { credits: '∞', max_credits: '∞', name: '모기에그 크리에이터', tier: 'Static Mode' }; updateUserUI();")

chat_err_js = """
      } catch (err) {
        const demoReply = "🐶 **모기에그(MogiEgg) 스튜디오입니다!**\\n\\n현재 GitHub Pages(정적 페이지) 데모 모드로 작동 중이어서 서버 백엔드 연결이 없습니다.\\n하지만 로컬에서 `run_studio.bat`를 실행하시면 로컬 AI(Ollama) 연동을 통해 무제한으로 모든 기능을 사용하실 수 있습니다!\\n\\n기능 시연을 위해 답변을 대체합니다: " + text;
        aiContentEl.innerHTML = marked.parse(demoReply);
        container.scrollTop = container.scrollHeight;
"""
content = content.replace("aiContentEl.innerHTML = `<span class=\"text-red-400\">오류가 발생했습니다: ${err.message}</span>`;", "const demoReply = \"🥚 **모기에그(MogiEgg) 정적 데모 모드입니다!**\\n\\n서버 연결 없이 브라우저 단독으로 실행 중입니다. 원본 `run_studio.bat` 실행 시 멀티 LLM 연동이 지원됩니다.\\n\\n요청하신 내용: \" + text; aiContentEl.innerHTML = marked.parse(demoReply); container.scrollTop = container.scrollHeight;")

sf_err_js = """
      } catch (err) {
        document.getElementById('sf-res-title').innerText = `[${category}] ${topic} - 30초 완성 숏폼 기획안`;
        document.getElementById('sf-res-hook').innerText = `🚨 ${target} 주목! 아직도 '${topic}' 이렇게 쓰고 계신다면 당장 멈추세요.`;
        const scenesList = document.getElementById('sf-scenes-list');
        scenesList.innerHTML = `
            <div class="p-3 rounded-xl bg-dark-surface border border-dark-border text-xs space-y-1">
              <div class="flex items-center justify-between"><span class="font-bold text-brand-400">0~3초 · ⚡ 충격 3초 훅</span><span class="text-[10px] text-slate-400 bg-slate-800 px-2 py-0.5 rounded">타격음</span></div>
              <p class="text-slate-300 font-medium">여러분, ${topic} 때문에 고민 많으셨죠?</p>
              <p class="text-[11px] text-slate-400">🎬 <span class="italic">화면 클로즈업 + 자막 강조</span></p>
            </div>
        `;
"""
content = content.replace("alert('숏폼 생성 오류: ' + err.message);", sf_err_js + "}")

recharge_err_js = """
      } catch (e) {
        alert('충전 완료! (정적 데모 모드)');
        closeRechargeModal();
"""
content = content.replace("alert('충전 실패: ' + e.message);", "alert('충전 완료! (정적 데모 모드)'); closeRechargeModal();")

key_err_js = """
      } catch (e) {
        alert('설정 저장 완료! (정적 데모 모드)');
        closeKeyModal();
"""
content = content.replace("alert('설정 저장 실패: ' + e.message);", "alert('설정 저장 완료! (정적 데모 모드)'); closeKeyModal();")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("index.html patched with static fallback mode.")
